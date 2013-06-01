Semafor tools
=============
Semafor tools is a (tiny) project collecting some utilities in order to cope with the [SEMAFOR](http://www.ark.cs.cmu.edu/SEMAFOR/) output. In order to use the semafor tools (which are actually contained in a single module) you need:

* [Python 2.7](http://www.python.org/download/releases/2.7/) or higher
* [lxml](http://lxml.de/index.html)

Usage
-----

Just type `python semafor.py -g|[t] <input> [<output>]` where:

* -g is to have the output in the graphical form
* -t is to have the output in textual form (default)
* <input> is an input file, intended to be a SEMAFOR 1.0 output file
* <output> is the output file (stdout if unspecified)

...and if you liked this help, type `python semafor.py -h` to read it again in your terminal! :-)
