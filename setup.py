import os

from setuptools import setup, find_packages

version = '1.0.0'


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='django-cas',
      version=version,
      description="Django Cas Client",
      long_description=read('README.md'),
      classifiers=[
          "Development Status :: Development",
          "Environment :: Console",
          "Intended Audience :: End Users/Desktop",
          "Natural Language :: English",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries",
          "Topic :: Utilities",
          "License :: OSI Approved :: Private",
          ],
      keywords='k-state-common',
      author='Derek Stegelman, Garrett Pennington',
      author_email='derekst@k-state.edu, garrett@k-state.edu',
      url='http://github.com/kstateome/django-cas/',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=True,
      )
