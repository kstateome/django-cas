import os

from setuptools import setup, find_packages

version = '1.3.1'


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='tadonis-django-cas',
      version=version,
      description="Django Cas Client redesign by Tadonis",
      long_description=read('README.md'),
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Environment :: Web Environment",
          "Framework :: Django",
          "Framework :: Django :: 1.8",
          "Framework :: Django :: 1.9",
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
      keywords='django cas SSO',
      author='Derek Stegelman, Garrett Pennington, tadonis',
      author_email='derekst@k-state.edu, garrettp@gmail.com, tanghf1988@126.com',
      url='http://github.com/tadonis/django-cas/',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=True,
      )
