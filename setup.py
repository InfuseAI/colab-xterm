#!/usr/bin/env python
from distutils.core import setup
from setuptools import find_packages  # type: ignore
import os

def _get_version():
    version_file = os.path.normpath(os.path.join(os.path.dirname(__file__), 'colabxterm', 'VERSION'))
    with open(version_file) as fh:
        version = fh.read().strip()
        return version

setup(name='colab-xterm',
      version=_get_version(),
      description='Open a terminal in colab, including the free tier.',
      long_description_content_type="text/markdown",
      long_description=open('README.md').read(),
      url='https://github.com/InfuseAI/colab-xterm',
      project_urls={
          "Bug Tracker": "https://github.com/InfuseAI/colab-xterm/issues",
      },
      python_requires=">=3.6",
      packages=["colabxterm"],
      package_data={
          'colabxterm': ['client/dist/*', 'VERSION']
      },
      include_package_data=False,
      install_requires=['ptyprocess~=0.7.0', 'tornado>5.1'],
      extras_require={
          'dev': [
              'jupyter',
              'twine'
          ],
      }
      )
