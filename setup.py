
# Use this command for deploy.
#   python3 setup.py sdist bdist_wheel && python3 -m twine upload --skip-existing dist/*

import io
from setuptools import find_packages, setup

setup(name='yaml_template',
      version='0.3',
      description='쿠버네티스처럼 YAML 파일로 이루어진 템플릿을 쉽게 템플릿의 타입에 따라 다르게 처리해주는 패키지입니다.',
      long_description="Please refer to the https://github.com/da-huin/yaml_template",
      long_description_content_type="text/markdown",
      url='https://github.com/da-huin/yaml_template',
      download_url= 'https://github.com/da-huin/yaml_template/archive/master.zip',
      author='JunYeong Park',
      author_email='dahuin000@gmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires=["jsonschema", "pyyaml"],
      classifiers=[
          'Programming Language :: Python :: 3',
    ]
)
