
# Use this command for deploy.
#   python3 setup.py sdist bdist_wheel && python3 -m twine upload --skip-existing dist/*

import io
from setuptools import find_packages, setup

setup(name='template_manager',
      version='1.0',
      description='쿠버네티스처럼 YAML 파일로 이루어진 템플릿을 쉽게 관리하고, 템플릿의 타입에 따라 다르게 처리해주는 패키지입니다.',
      long_description="Please refer to the https://github.com/da-huin/template_manager",
      long_description_content_type="text/markdown",
      url='https://github.com/da-huin/template_manager',
      download_url= 'https://github.com/da-huin/template_manager/archive/master.zip',
      author='JunYeong Park',
      author_email='dahuin000@gmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires=["jsonschema", "pyyaml"],
      classifiers=[
          'Programming Language :: Python :: 3',
    ]
)
