import json
import re
import jsonschema
import base64
import uuid
import time
import os
import yaml


class YAMLTemplate():
    """
    쿠버네티스처럼 YAML 파일로 이루어진 템플릿을 쉽게 템플릿의 타입에 따라 다르게 처리해주는 패키지입니다.
    """

    def __init__(self, templates_dir):
        """
        Parameters
        ----------

        * `(required) templates_dir`: str

            템플릿들이 있는 폴더 경로입니다.

        """

        self._template_schema = self._get_template_schema()

        self._kinds = {}
        self._templates = {}

        for path in self._find_all_by_name(templates_dir, r".+\.yaml"):
            self._load_template(path, update=False)

    def register(self, kind, worker, options={}, template_schema={}, process_schema={}):
        """
        템플릿을 처리할 방식을 등록 할 때 사용합니다.

        Parameters
        ----------

        * `(required) kind`: str

            템플릿 타입 이름입니다.

        * `(required) worker`: function

            이 타입을 처리해주는 함수입니다. `spec` 과 `args` 매개변수를 반드시 받아야 합니다.

            * `spec`: spec key in YAML
            * `args`: 유저가 보내는 매개변수

            ```
            def worker(spec, args):
                ...
            ```

        * `template_schema`: dict

            템플릿에 사용하는 스키마입니다. 자세한 내용은 [여기](#how_to_use_schmea) 를 참조하세요.

            ```json
            {
                "plus": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "number_a": {},
                            "number_b": {}
                        },
                        "required": [
                            "number_a", "number_b"
                        ]
                    }
                }
            }
            ```

        * `process_schema`: dict

            Process 함수가 사용하는 스키마입니다. 자세한 내용은 [여기](#how_to_use_schmea) 를 참조하세요.

            ```json
            {
                "first_word_getter": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "sentence": {}
                        }
                    },
                    "properties": {
                        "sentence": {
                            "default": "Hello World"
                        }
                    }
                }
            } 
            ```

        * `(deprecated) options`: dict

            패키지가 경량화되며 deprecated 된 옵션입니다.


        Returns
        -------

        오류가 없다면 항상 True 를 반환합니다.        
        """

        self._kinds[kind] = {
            "kind": kind,
            "worker": worker,
            "options": options,
            "template_schema": template_schema,
            "process_schema": process_schema
        }

        return True

    def get(self, name):
        """
        템플릿의 정보를 가져올 때 사용합니다.

        **Parameters**

        * `(required) name`: str

            템플릿의 이름입니다.

        **Returns**

        `템플릿 정보`: dict        
        """
        self._validate_template(name)
        return self._templates[name]

    def find(self, kind="", category=None, tags=[], meta={}):
        """
        템플릿들을 찾을 때 사용합니다.

        **Parameters**

        * `kind`: str

            kind 로 템플릿들을 찾습니다.

            ```python
            "plus"
            ```

        * `category`: str

            category 로 템플릿들을 찾습니다.

            ```python
            "fruit"
            ```

        * `tags`: list

            tags 로 템플릿들을 찾습니다.

            요청한 태그들이 모두 매치되어야 합니다.

            ```json
            ["apple", "banana"]
            ```

        * `meta`: dict

            meta 로 템플릿들을 찾습니다.

            tags 가 배열이라면 meta 는 dict 형식입니다.

            ```json
            {
                "fruit": "apple"
            }
            ```

        **Returns**

        `template name list`: list
        """
        result = []

        for name in self._templates:

            piece = self.get(name)

            if kind != "":
                if kind != piece["kind"]:
                    continue

            if isinstance(category, str):
                if category != piece["category"]:
                    continue

            if len(meta) != 0:
                if not self._is_obj_looking_for(piece["meta"], meta):
                    continue

            if len(tags) != 0:
                if not self._is_array_looking_for(piece["tags"], tags):
                    continue

            result.append(name)

        return result

    def get_spec(self, name):
        self._validate_template(name)
        return self.get(name)["origin"]["spec"]

    def get_kind(self, name):
        self._validate_template(name)

        return self.get(name)["origin"]["kind"]

    def process(self, name, args={}):
        """
        Register 에서 등록한 방식대로 템플릿을 처리 할 때 사용합니다.

        **Parameters**

        * `(required) name`: str

            템플릿의 이름입니다.

        * `(required) args`: dict

            Worker 에게 보낼 매개변수입니다.

        **Returns**

        `Wokrer 가 처리한 결과`
        """

        self._update_template(name)

        if "process_schema" in args and args["process_schema"] != {}:
            args = self._get_validated_obj(args, args["process_schema"])

        kind_info = self._kinds[self.get(name)["kind"]]
        worker = kind_info["worker"]

        if not worker:
            raise ValueError(f"{name}'s worker is not exsists.")

        return worker(self.get(name)["origin"]["spec"], args)

    def _update_template(self, name):
        self._validate_template(name)

        return self._load_template(self.get(name)["path"], update=True)

    def _load_template(self, path, update):
        with open(path, "r", encoding="utf-8") as fp:

            loaded_template = yaml.full_load_all(fp.read())

            for index, raw_template in enumerate(loaded_template):

                self._get_validated_obj(
                    raw_template, self._template_schema)

                kind = raw_template["kind"]
                name = raw_template["name"]
                meta = raw_template["meta"]
                raw_template["spec"] = raw_template.get("spec", {})
                random_name = False

                if name == "random":
                    name = base64.b64encode(
                        (path + str(index)).encode()).decode()
                    random_name = True

                category = raw_template["category"]
                tags = raw_template["tags"]

                if name in self._templates and update == False:
                    raise ValueError(f"name already exists. name is {name}")

                if kind == "":
                    raise ValueError("kind is empty.")

                if name == "":
                    raise ValueError("name is empty.")

                if category == "":
                    raise ValueError("category is empty.")

                if not isinstance(meta, dict):
                    raise ValueError(f"meta is not a dict. meta is {meta}")

                # spec validate
                if "template_schema" in raw_template and raw_template["template_schema"] != {}:
                    raw_template["spec"] = self._get_validated_obj(
                        raw_template["spec"], raw_template["template_schema"])

                self._templates[name] = {
                    "kind": kind,
                    "name": name,
                    "category": category,
                    "tags": tags,
                    "origin": raw_template,
                    "path": path,
                    "meta": meta,
                    "random_name": random_name
                }

    def _validate_template(self, name):
        if name not in self._templates:
            raise ValueError(
                "name is not exists in templates. name is [%s]" % name)

    def _get_validated_obj(self, obj, schema_item):

        schema = schema_item.get("schema", {})
        properties = schema_item.get("properties", {})

        for name in properties:
            prop = properties[name]

            for key in prop:
                if key == "default":
                    default = prop[key]
                    if name not in obj:
                        obj[name] = default

            for key in prop:
                value = obj[name]
                if key == "change_type":
                    type_name = prop[key]
                    obj[name] = self._set_type(type_name, value)
        try:
            jsonschema.validate(obj, schema)
        except Exception as e:
            raise ValueError(f"validate failed. {e}")

        return obj

    def _is_obj_looking_for(self, obj: dict, user_obj: dict):

        o = obj.copy()
        uo = user_obj.copy()

        o.update(uo)

        if o == obj:
            return True

        return False

    def _is_array_looking_for(self, array: list, user_array: list):

        a = array.copy()
        ua = user_array.copy()

        a += ua

        if set(a) == set(array):
            return True

        return False

    def _find_all_by_name(self, start_dir, regex):
        finded_files = []
        compiled_regex = re.compile(regex)

        for root, _, files in os.walk(start_dir):
            for filename in files:
                if compiled_regex.findall(filename):
                    finded_files.append(os.path.join(
                        root, filename).replace("\\", "/"))

        return finded_files

    def _set_type(self, type_name, value):

        if type_name == "int":
            return int(value)
        elif type_name == "float":
            return float(value)
        elif type_name == "string":
            return str(value)
        elif type_name == "bool":
            if value == "true" or value == "True":
                return True
            elif value == "false" or value == "False":
                return False
            else:
                raise ValueError(f"invalid bool value. value is [{value}]")
        else:
            raise ValueError("invalid set type name %s" % (type_name))

    def _get_template_schema(self):
        return {
            "properties": {
                "name": {
                    "default": "random"
                },
                "category": {
                    "default": "default"
                },
                "tags": {
                    "default": []
                },
                "spec": {
                    "default": {}
                },
                "meta": {
                    "default": {}
                }
            },
            "schema": {
                "type": "object",
                "properties": {
                    "kind": {},
                    "name": {},
                    "category": {},
                    "tags": {
                        "type": "array"
                    },
                    "spec": {
                        "type": "object"
                    },
                    "meta": {
                        "type": "object"
                    }
                },
                "required": [
                    "kind"
                ]
            }
        }
