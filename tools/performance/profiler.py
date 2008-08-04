#!/usr/bin/env python
#
# Measure execution time of various Property List Parsing.
#
import os
import sys
import gc
import time

# From timeit module.
if sys.platform == "win32":
    # On Windows, the best timer is time.clock()
    timer = time.clock
else:
    # On most other platforms the best timer is time.time()
    timer = time.time

def timeit(number, func):
    elapsed = 0.0
    for i in range(0, number):
        gc.disable()
        t = timer()
        func()
        elapsed += (timer() - t)
        gc.enable()
        gc.collect()
    return elapsed

# Make libraries visible
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import commands
from cStringIO import StringIO
import plistlib
import etree_parser
from plist_parser import XmlPropertyListParser


PLIST_FILEPATH = os.path.expanduser('~/Music/iTunes/iTunes Music Library.xml')
PROG_C_COMMAND = os.path.abspath(os.path.join(os.path.dirname(__file__), 'core_foundation_parser'))

# number of pre-execution
WARMUP_TIMES = 5
REPEAT_TIMES = 20


# Read the property list contents in memory
filein = open(PLIST_FILEPATH)
try:
    bytes = filein.read()
finally:
    filein.close()

def exec_core_foundation_code(times):
    """CoreFoundation"""
    return commands.getoutput('%s "%s" %d' % (PROG_C_COMMAND, PLIST_FILEPATH, times))

def parse_using_etree():
    """xml.etree.ElementTree"""
    xmlin = StringIO(bytes)
    return etree_parser.parse_using_etree(xmlin)

def parse_using_cetree():
    """xml.etree.cElementTree"""
    xmlin = StringIO(bytes)
    return etree_parser.parse_using_cetree(xmlin)

def parse_using_plistlib():
    """plistlib"""
    xmlin = StringIO(bytes)
    return plistlib.readPlist(xmlin)

def parse_using_plist_parser_sax():
    """plist_parser with SAX parser"""
    xmlin = StringIO(bytes)
    return XmlPropertyListParser()._parse_using_sax_parser(xmlin)

def parse_using_plist_parser_etree():
    """plist_parser with xml.etree.cElementTree"""
    xmlin = StringIO(bytes)
    return XmlPropertyListParser()._parse_using_etree(xmlin)

COMMANDS = [
    parse_using_etree,
    parse_using_cetree,
    parse_using_plistlib,
    parse_using_plist_parser_sax,
    parse_using_plist_parser_etree,
]

# Measure execution time of c implementation
exec_core_foundation_code(WARMUP_TIMES)
base_time = timeit(1, lambda: exec_core_foundation_code(REPEAT_TIMES))/REPEAT_TIMES

print "CoreFoundation: %.2f sec/pass" % base_time
for f in COMMANDS:
    timeit(WARMUP_TIMES, f)
    t = timeit(REPEAT_TIMES, f) / REPEAT_TIMES
    print "%s: %.2f sec/pass, %.2f costs" % (f.__doc__, t, t / base_time)
