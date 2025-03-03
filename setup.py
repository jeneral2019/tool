from setuptools import setup, find_packages

setup(
    name="jeneral2019-tool",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        'selenium',
        'allure-pytest'
    ],
    author="jeneral2019",
    author_email="yuxiangfeng2017@gmail.com",
    description="A tool",
    url="https://github.com/jeneral2019/tool",
)