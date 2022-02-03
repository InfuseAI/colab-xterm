#!/usr/bin/env python
from distutils.core import setup
from setuptools import find_packages  # type: ignore

result = find_packages()

setup(name='colab-xterm',
      version="0.1.0",
      description='Open a terminal in colab, including the free tier.',
      long_description_content_type="text/markdown",
      long_description=open('README.md').read(),
      url='https://github.com/InfuseAI/colab-xterm',
      python_requires=">=3.6",
      packages=["colabxterm"],
      package_data={
          'colabxterm': ['client/dist/*']
      },
      include_package_data=False,
      install_requires=['ptyprocess~=0.7.0', 'tornado>5.1']
      )
