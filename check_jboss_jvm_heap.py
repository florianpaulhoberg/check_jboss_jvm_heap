#!/usr/bin/env python
# check_jboss_jvm_heap.py
# monitor JBoss / Wildfly JVM heap space
# Florian Paul Hoberg <florian [at] hoberg.ch>

import subprocess
import os
import sys
import json
import tempfile
import argparse
from jbossply.jbossparser import JbossParser

# Change to your settings 
JBOSS_CLI = "/opt/wildfly-10.1.0.Final/bin/jboss-cli.sh"
TMP_PATH  = "/tmp/jboss_cli.tmp"

# Do not change anything below here
JBOSS_MEM = "-c \"/core-service=platform-mbean/type=memory:read-attribute(name=heap-memory-usage)\""
parser = JbossParser()
argparser = argparse.ArgumentParser(description='Following options are possible:')

def write_file():
    """ write jboss content to file """
    try:
        with open(TMP_PATH, 'w') as file:
            test = subprocess.Popen(JBOSS_CLI + " " + JBOSS_MEM, shell=True, stdout=file)
            test.communicate()[0]
    except IOError as e:
        print "I/O error({0}): {1}".format(e.errno, e.strerror)


def open_file():
    """ open file to buffer and convert jboss output to json """
    try:
        with open(TMP_PATH, 'r') as file:
            buffer = file.read()
            json = parser.parse(buffer)
            heap_max  = json['result']['max']
            heap_used = json['result']['used']
            return heap_max, heap_used 
    except IOError as e:
        print "I/O error({0}): {1}".format(e.errno, e.strerror)


def main():
    """ Check JBoss JVM heap space """

    argparser.add_argument('-w', type=int, help='Define value in MB to raise warn state. (default: 150 MB)')
    argparser.add_argument('-c', type=int, help='Define value in MB to raise critical state. (default: 80 MB)')
    cliargs = argparser.parse_args()

    if  cliargs.w is None:
        cliargs.w = 80

    if cliargs.c is None:
        cliargs.c = 150

    HEAP_WARN = cliargs.w * 1024 * 1024
    HEAP_CRIT = cliargs.c * 1024 * 1024

    write_file()
    heap_max, heap_used = open_file()
    heap_free = int(heap_max) - int(heap_used)
    heap_max_calc = heap_free + heap_used

    if heap_free < HEAP_WARN and heap_free > HEAP_CRIT:
        print("WARN: JVM heap is warn - SIZE:", heap_max_calc / 1024 / 1024, "MB | Free:", heap_free / 1024 / 1024, "MB | Used:", heap_used / 1024 / 1024, "MB")
        exit(1)
    if heap_free < HEAP_CRIT:
        print("CRIT: JVM heap is critical - SIZE:", heap_max_calc / 1024 / 1024, "MB | Free:", heap_free / 1024 / 1024, "MB | Used:", heap_used / 1024 / 1024, "MB")
        exit(2)

    print("OK: JVM heap is ok - SIZE:", heap_max_calc / 1024 / 1024, "MB | Free:", heap_free / 1024 / 1024, "MB | Used:", heap_used / 1024 / 1024, "MB")
 
main()
