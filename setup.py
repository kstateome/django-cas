import os

from setuptools import setup, find_packages

version = '1.2.0'


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='django-cas-client',
      version=version,
      description="Django Cas Client",
      long_description=read('README.md'),
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Environment :: Web Environment",
          "Framework :: Django",
          "Framework :: Django :: 1.5",
          "Framework :: Django :: 1.6",
          "Framework :: Django :: 1.7",
          "Intended Audience :: Developers",
          "Natural Language :: English",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 2",
          "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries",
          "Topic :: Utilities",
          "License :: OSI Approved :: MIT License",
          ],
      keywords='django cas',
      author='Derek Stegelman, Garrett Pennington',
      author_email='derekst@k-state.edu, garrettp@gmail.com',
      url='http://github.com/kstateome/django-cas/',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=True,
      )
