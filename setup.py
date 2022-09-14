from setuptools import setup

setup(
    name="pydarts",
    version="0.1",
    license="MIT",
    url="https://github.com/sufio/pydarts",
    description="Darts game",
    author="Sufio.com",
    author_email="sufio@sufio.com",
    packages=["pydarts"],
    install_requires=["bleak==0.15.1", "pygame==2.1.2"],
)