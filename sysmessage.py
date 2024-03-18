#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This script should execute several commands at start. The output is written to the file script.log, which will then
# be emailed. No variables should be adjusted in this script. For configuration, the file script.yml is used,
# in which the individual parameters are defined.

# Importing required libraries
import configparser
import datetime
import logging
import sys
import os

# Setup configparser
cfp = configparser.RawConfigParser()
current_directory = os.getcwd()
cfp.read(current_directory + '/configs.cfg')

# Setup variables for logging
now = datetime.datetime.now()
try:
    loglevel = cfp.get('logfile-config', 'loglevel')
    timeformat = cfp.get('logfile-config', 'timeformat')
    logfile = cfp.get('logfile-config', 'logfile')

except Exception as e:
    (print("\t{0}\tFATAL ERROR!: {1}".format(now, e)))
    sys.exit(-1)

logtime = now.strftime(timeformat)

# Setup variables for commands to be executed
numer_of_commands = int(cfp.get('commands-config', 'number_of_commands'))


def create_logfile():
    # Read header from Logfile and format it for better readability
    header = cfp.get('logfile-config', 'header')
    header = "# " + header + " *" + logtime + "*\n\n"

    def create_header():
        # Opening the file and inserting the header
        f = open(logfile, "a")
        f.write(header)
        f.close()

    # Create log file if it does not exist.
    try:
        if os.path.isfile(logfile):
            # Delete old logfile, which is not used anymore
            # TODO: Backup the old logfile before deleting it
            os.remove(logfile)
            create_header()

        else:
            create_header()

    except Exception as e:
        print("\t{0}\tFATAL ERROR!: {1}".format(logtime, e))
        sys.exit(-1)

    # Once the log file has been successfully created, the next step is to define the logging functionality.
    setup_logging()


def setup_logging():
    # Set up logging
    try:
        logging.basicConfig(filename=logfile, encoding='utf-8', level=loglevel)

    except Exception as e:
        print(e)
        print("FATAL ERROR! - Could not set up logging, exiting!")
        sys.exit(-1)


def execute_commands():
    try:
        for i in range(1, numer_of_commands + 1):
            new_command = f'command{i}'
            logging.debug("\t{0}\tNew command: {1} has been read.".format(logtime, new_command))
            command_value = cfp.get('commands-config', new_command)
            logging.debug("\t{0}\tNew value for command: {1} has been read.".format(logtime, command_value))

            f = open(logfile, "a")
            f.write("### Output of `{0}`\n```\n".format(command_value))
            f.close()

            os.system(command_value + " >> " + logfile)
            logging.debug("\t{0}\tCommand: {1} has been executed.".format(logtime, new_command))

            f = open(logfile, "a")
            f.write("```\n\n".format(command_value))
            f.close()

    except Exception as e:
        logging.error("\t{0}\t".format(logtime), e)
        logging.error("\t{0}\tCould not execute the command: {1}".format(logtime, command_value))
        sys.exit(-1)


create_logfile()
execute_commands()
