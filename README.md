# ttime - Time tracking with simple text files

Record your work time in plain text files with any text editor (see example_times.txt).
Analyze your work time with `ttime FILE_NAME`. 

## features

* extendable output formats with jinja2 templates
* optional multi language support
* VCS friendly format

## setup

* clone the repository
* `cd ttime`
* `python setup.py install --user`

## run the sample

* `ttime [PATH_TO_REPOSITORY_CLONE]/example_times.txt`

## use it

* create a time tracking text file with the same format as example_times.txt
* run `ttime.py FILE_NAME` to see a working summary
