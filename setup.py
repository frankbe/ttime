#from distutils.core import setup
from setuptools import setup

setup(
    name='ttime',
    version='0.2-SNAPSHOT',
    description='a text filed base Time Tracking tool',
    author='Berthold Frank',
    author_email='frankbe@web.de',
    url='https://github.com/frankbe/ttime',
    py_modules=['ttime'],
    install_requires=[
        'configparser',
        'Jinja2',
    ],
    include_package_data=True,
    data_files=[('templates', ['templates/week_report.txt', 'templates/week_report.txt.config'])]
    #data_files=[('.', ['text_de_template.txt'])]
    # ,package_data={'ttime': ['text_de_template.txt']}
    #python_requires=">=2.7"
    #scripts=['scripts/ttime']
    #entry_points = { 'console_scripts': [ 'ttime = ttime:main', ], },
)

#packages=['ttime']
# TODO: license, classifiers, keywords, ...see sampleproject...
