from setuptools import setup, find_packages

version = '0.9.1'

setup(name='django-cas',
      version=version,
      description="Django Cas Client",
      long_description=open("./README.md", "r").read(),
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
