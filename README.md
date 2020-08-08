<p align="center">
  <a href="" rel="noopener">
 <img width=200px height=200px src="./static/icon.png" alt="Project logo" ></a>
 <br>

 
</p>

<h3 align="center">TEMPLATE MANAGER</h3>

<div align="center">

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![GitHub Issues](https://img.shields.io/github/issues/da-huin/template_manager.svg)](https://github.com/da-huin/template_manager/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/da-huin/template_manager.svg)](https://github.com/da-huin/template_manager/pulls)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](/LICENSE)

</div>

---

<p align="center"> 쿠버네티스처럼 YAML 파일로 이루어진 템플릿을 쉽게 관리하고, 템플릿의 타입에 따라 다르게 처리해주는 패키지입니다.
    <br> 
</p>

## 📝 Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Usage](#usage)
- [Acknowledgments](#acknowledgement)

## 🧐 About <a name = "about"></a>

쿠버네티스처럼 YAML 파일로 이루어진 템플릿을 쉽게 관리하고, 템플릿의 타입에 따라 다르게 처리해주는 패키지입니다.

가장 간단한 예시를 들어보겠습니다.

1. 어딘가에서 1 + 2, 3 + 5 의 결과와 "Hello World" 라는 문장의 첫 단어를 가져오고 싶다고 해봅시다.

1. 그렇다면 템플릿 타입(kind)는 plus 와 first_word_getter 가 필요합니다.

1. 템플릿은 아래와 같이 만들 수 있습니다.

    ```yaml
    kind: plus
    name: one_plus_two
    spec: 
        number_a: 1
        number_b: 2
    ```

    ```yaml
    kind: plus
    name: three_plus_five
    spec: 
        number_a: 3
        number_b: 5
    ```

    ```yaml
    kind: first_word_getter
    name: any_name
    spec:
        default_sentence: "Hello World"
    ```

1. 이제 개발자는 템플릿 타입인 `plus` 와 `first_word_getter` 를 처리하는 함수를 만듭니다. 

1. 이제 어딘가에서 템플릿의 `name` 또는 `tags`, `category`, `meta` 등으로 템플릿을 검색해서 그에 맞는 처리를 해달라고 요청을 할 수 있습니다.

    * 요청을 할 때 사용자 매개변수를 받아서 처리 할 수도 있습니다.

1. `name` 으로 `one_plus_two` 인 템플릿을 찾아서 처리해달라고 요청했다고 가정해봅시다.

1. 이제 프로그램은 아래의 스텝을 따라서 처리합니다.

    1. 템플릿 목록에서 `name` 이 `one_plus_two`인 템플릿을 찾는다.
    
    1. `kind`에 따라서 처리하는데, 여기에서는 `kind` 가 `plus` 이므로 사용자가 만든 `plus` 처리 함수를 호출해서 결과값을 받아온다.

    1. 받은 결과값을 요청자에게 돌려준다.

1. 요청자는 결과값을 받을 수 있게 됩니다. 자세한 내용은 아래를 참조하세요.

## 🏁 Getting Started <a name = "getting_started"></a>

### Installing

```
pip install template_manager
```

### 🌱 Tutorial

1. YAML 템플릿들을 저장할 폴더를 생성해야합니다. 원하는 곳에 `templates` 폴더를 생성하세요.

1. YAML 파일을 아래와 같이 생성하세요.

    * `templates` 폴더 안에 파일을 recursive 하게 돌면서 파일을 찾아내기 때문에 깊숙한 곳에 넣어두어도 상관 없습니다.
    * 파일명은 어떤 것으로 해도 상관 없습니다.

    your_templates_directory/첫번째 파일.yaml

    ```yaml
    kind: plus
    name: one_plus_two
    spec: 
        number_a: 1
        number_b: 2
    ---
    kind: plus
    name: three_plus_five
    spec: 
        number_a: 3
        number_b: 5
    ```   

    your_templates_directory/두번째 파일.yaml

    ```yaml
    kind: first_word_getter
    meta: 
        getter: True
        order: first
    spec:
        default_sentence: "Hello World"
    ```

1. 아래의 코드를 실행하세요.

    ```python
    from pprint import pprint
    import template_manager

    handler = template_manager.YAMLTemplate("your_templates_directory/")

    pprint(handler.get("one_plus_two"))
    ```

    결과는 다음과 같습니다.

    ```python
    {'category': 'default',
    'kind': 'plus',
    'meta': {},
    'name': 'one_plus_two',
    'origin': {'category': 'default',
                'kind': 'plus',
                'meta': {},
                'name': 'one_plus_two',
                'spec': {'number_a': 1, 'number_b': 2},
                'tags': []},
    'path': 'templates/first_word_getter_list.yaml',
    'random_name': False,
    'tags': []}
    ```

1. `plus` 를 처리하기 위해서 등록을 하고 처리 요청을 하는 아래의 코드를 실행하세요.

    ```python
    # worker 는 반드시 spec 과 args 매개변수를 받아야 합니다.
    #   spec 은 템플릿에서 spec 키의 값들입니다.
    #   args 는 유저가 보내는 파라미터입니다.    
    handler.register("plus", lambda spec, args: spec["number_a"] + spec["number_b"])
    
    print(handler.process("one_plus_two"))
    print(handler.process("three_plus_five"))
    ```

    결과는 다음과 같습니다.
    ```
    3
    8
    ```

1. 아까 만든 템플릿 중 하나는 `name` 키가 없는 아래와 같은 형식이었습니다. 이 템플릿을 불러와서 처리해보겠습니다.

    ```yaml
    kind: first_word_getter
    meta: 
        getter: True
        order: first
    spec:
        default_sentence: "Hello World"
    ```

    ```python
    # first_word_getter 를 처리 할 함수를 생성하고 등록합니다.
    def first_word_getter_worker(spec, args):
        sentence = spec["default_sentence"]
        if "sentence" in args:
            sentence = args["sentence"]

        return sentence.split(" ")[0]

    handler.register("first_word_getter", first_word_getter_worker)


    # meta 에서 "order" 키가 있는 모든 템플릿 중에서 값이 "first" 인 템플릿 이름을 전부 가져옵니다.
    found_template_name_list = handler.find(kind="first_word_getter", meta={
        "order": "first",
    })
    
    print("name: ", found_template_name_list[0])
    print(handler.process(found_template_name_list[0]))
    print(handler.process(found_template_name_list[0], {"sentence": "Yellow Monkey"}))
    ```

    결과는 다음과 같습니다.

    * `name` 을 지정하지 않았기 때문에 랜덤으로 생성되었습니다.

    ```python
    name: dGVtcGxhdGVzL3BsdXNfbGlzdC55YW1sMA==
    Hello
    Yellow
    ```

1. 튜토리얼이 끝났습니다.

## 🎈 Usage <a name="usage"></a>

#### 🌱 register

템플릿을 처리할 방식을 등록 할 때 사용합니다.

**Parameters**

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

    패키지가 경량화되며 deprecated 되었습니다.


**Returns**

오류가 없다면 항상 True 를 반환합니다.

#### 🌱 get

템플릿의 정보를 가져올 때 사용합니다.

**Parameters**

* `(required) name`: str

    템플릿의 이름입니다.

**Returns**

`템플릿 정보`: dict


#### 🌱 find

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


#### 🌱 process

Register 에서 등록한 방식대로 템플릿을 처리 할 때 사용합니다.

**Parameters**

* `(required) name`: str

    템플릿의 이름입니다.

* `(required) args`: dict

    Worker 에게 보낼 매개변수입니다.

**Returns**

`Wokrer 가 처리한 결과`


## Reference

#### 🌱 스키마를 사용하는 방법 (#how_to_use_schmea)

```python
{
    // schema 에 사용하는 값에 대해 자세하게 알고싶다면 https://json-schema.org/ 를 참조하세요.
    "schema": {
        "properties": {
            "number_a": {
                "type": "integer"
            },
            "number_b_list": {
                "type": "array"
            },
            "name": {}
        },
        // 반드시 필요한 매개변수는 여기에 추가하세요.
        "required": [
            "number_a",
            "number_b_list"
        ]
    },
    // 이 부분은 위에서 정한 스키마의 속성의 기본값을 정하는 등의 json schema 라이브러리가 하지 못하는 역할을 보조합니다. 
    "properties": {
        "name": {
            "default": "hello"
        }
    }
}
```

## 🎉 Acknowledgements <a name = "acknowledgement"></a>

- Title icon made by [Freepik](https://www.flaticon.com/kr/authors/freepik).

- If you have a problem. please make [issue](https://github.com/da-huin/template_manager/issues).

- Please help develop this project 😀

- Thanks for reading 😄
