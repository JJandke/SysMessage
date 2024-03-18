#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This script should execute several commands at start. The output is written to the file script.log, which will then
# be emailed. No variables should be adjusted in this script. For configuration, the file script.yml is used,
# in which the individual parameters are defined.

# Importing required libraries
from email.message import EmailMessage
import configparser
import datetime
import logging
import smtplib
import shutil
import sys
import os

# Setup configparser
cfp = configparser.RawConfigParser()
current_directory = os.getcwd()
cfp.read(current_directory + '/configs.cfg')

# Setup variables for logging, catch exception, if configs.cfg is not available
now = datetime.datetime.now()
try:
    loglevel = cfp.get('logfile-config', 'loglevel')
    timeformat = cfp.get('logfile-config', 'timeformat')
    logfile = cfp.get('logfile-config', 'logfile')

except Exception as e:
    (print("\t{0}\tFATAL ERROR!: {1}".format(now, e)))
    sys.exit(-1)

logtime = now.strftime(timeformat)
backup_directory = current_directory + '/old-logs'

# Setup variables for commands to be executed
numer_of_commands = int(cfp.get('commands-config', 'number_of_commands'))


def create_logfile():
    # Read header from Logfile and format it for better readability
    header = cfp.get('logfile-config', 'header')
    header = "# " + header + " *" + logtime + "*\n\n"

    def backup_logfile():
        # If versioning is enabled, then the old logfile will be moved to the 'old-logs' folder before deleting it
        # Using shutil.copy2 as it supports to also copy metadata and file-permissions
        # Note, that only one copy per day will be saved
        if not os.path.isdir(backup_directory):
            os.mkdir(backup_directory)

        old_log = backup_directory + '/' + now.strftime('%Y-%m-%d_') + 'daily-message.md'
        shutil.copy2(logfile, old_log)

    def create_header():
        # Opening the file and inserting the header
        # The file will be automatically created, if it does not exist
        f = open(logfile, "a")
        f.write(header)
        f.close()

    # Create log file if it does not exist, either way, the header will be written to the logfile
    try:
        if os.path.isfile(logfile):
            # Delete old logfile, which is not needed anymore
            # Backup the old message, of versioning is set to 'true'
            versioning = cfp.get('logfile-config', 'versioning')
            if versioning == 'enabled':
                backup_logfile()

            os.remove(logfile)
            create_header()

        else:
            create_header()

    except Exception as e_nopath:
        print("\t{0}\tFATAL ERROR!: {1}".format(logtime, e_nopath))
        sys.exit(-1)

    # Once the log file has been successfully created, the next step is to define the logging functionality.
    setup_logging()


def setup_logging():
    # Set up logging
    try:
        logging.basicConfig(filename=logfile, encoding='utf-8', level=loglevel)

    except Exception as e_noconf:
        print(e_noconf)
        print("FATAL ERROR! - Could not set up logging, exiting!")
        sys.exit(-1)


def execute_commands():
    # For-Loop to execute every command
    # For each command in range of number_of_commands, the command will be read, saved to command_value and printed
    # into the daily-message.md file.
    # Then command_value will be executed, and it's output will also be printed into daily-message.md
    # In addition, some formatting ensures that the file is compliant with Markdown.
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

    except Exception as e_badcommand:
        logging.error("\t{0}\t".format(logtime), e_badcommand)
        logging.error("\t{0}\tCould not execute the command: {1}".format(logtime, command_value))
        sys.exit(-1)


def send_email():
    # If no custom subject is specified, the default header from the logfile will be used
    subject = cfp.get('email-config', 'subject')
    if subject == 'default':
        subject = cfp.get('logfile-config', 'header') + ' ' + logtime

    # Reading the content of the logfile
    with open(logfile, 'r') as lf:
        content = lf.readlines()
        message = "".join(content)
        lf.close()

    # Setting up the E-Mail service
    receiver = cfp.get('email-config', 'receivers')
    smtp_server = cfp.get('email-config', 'smtp_server')
    password = cfp.get('email-config', 'password')
    sender = cfp.get('email-config', 'sender')
    port = cfp.get('email-config', 'port')

    msg = EmailMessage()
    msg['Subject'] = message
    msg['From'] = sender
    msg['To'] = receiver
    msg.set_content(message)

    s = smtplib.SMTP(smtp_server)
    s.send_message(msg)
    s.quit()


create_logfile()
execute_commands()
send_email()
