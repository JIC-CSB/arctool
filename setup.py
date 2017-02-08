from setuptools import setup

url = ""
version = "0.1.0"
readme = open('README.rst').read()

setup(name="arctool",
      packages=["arctool"],
      version=version,
      description="arctool is a tool for archiving data",
      long_description=readme,
      include_package_data=True,
      author="Tjelvar Olsson",
      author_email="tjelvar.olsson@jic.ac.uk",
      url=url,
      download_url="{}/tarball/{}".format(url, version),
      license="MIT")
