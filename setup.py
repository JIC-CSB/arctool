from setuptools import setup

url = "https://github.com/JIC-CSB/arctool"
version = "0.12.0"
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
      install_requires=[
          "dtool",
          "click",
          "pyyaml",
      ],
      entry_points={
          'console_scripts': ['arctool=arctool.cli:cli']
      },
      license="MIT")
