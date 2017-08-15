#from distutils.core import setup
from setuptools import setup

setup(
    name='ttime',
    version='0.1',
    description='a text filed base Time Tracking tool',
    author='Berthold Frank',
    author_email='frankbe@web.de',
    url='https://github.com/frankbe/ttime',
    py_modules=['ttime'],
    install_requires=[
        'Jinja2',
    ],
    python_requires=">=3.4"
    #scripts=['scripts/ttime']
    #entry_points = { 'console_scripts': [ 'ttime = ttime:main', ], },
)

#packages=['ttime']
# TODO: license, classifiers, keywords, ...see sampleproject...
