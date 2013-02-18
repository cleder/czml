from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='czml',
      version=version,
      description="Read and write CZML in Python",
      long_description=open('README.rst').read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='GIS JOSN CZML Cesium Globe',
      author='Christian Ledermann',
      author_email='christian.ledermann@gmail.com',
      url='https://github.com/cleder/czml',
      license='LGPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          "pygeoif",
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
