#!/usr/bin/env python
from distutils.core import setup
from setuptools import find_packages  # type: ignore

setup(name='colab-xterm',
      version="0.1.0",
      description='Run xterm in colab',
      python_requires=">=3.6",
      packages=find_packages(),
      package_data={
          'colabxterm': ['client/dist/*']
      },
      install_requires=['ptyprocess~=0.7.0', 'tornado>5.1']
      )
