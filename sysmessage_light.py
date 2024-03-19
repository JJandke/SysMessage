#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This is a lightweight version of the sysmessage.py without logging for better readability of the code. While it seems
# more clearly arranged, it might be harder to debug/ maintain as there is less feedback in case of errors.

# Importing required libraries
from email.message import EmailMessage
import configparser
import datetime
import smtplib
import shutil
import sys
import os

# Setup configparser, variables for commands to be executed and time-settings
now = datetime.datetime.now()
current_directory = os.getcwd()
cfp = configparser.RawConfigParser()
cfp.read(current_directory + '/configs.cfg')
backup_directory = current_directory + '/old-logs'
numer_of_commands = int(cfp.get('commands-config', 'number_of_commands'))

# Setup variables for logging, catch exception, if configs.cfg is not available
try:
    loglevel = cfp.get('logfile-config', 'loglevel')
    timeformat = cfp.get('logfile-config', 'timeformat')
    logfile = cfp.get('logfile-config', 'logfile')

except Exception as e_nolog:
    (print("\t{0}\tFATAL ERROR! e_nolog: {1}".format(now, e_nolog)))
    sys.exit(1)

logtime = now.strftime(timeformat)


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
            # Backup the old message, if versioning is set to 'true'
            versioning = cfp.get('logfile-config', 'versioning')
            if versioning == 'enabled':
                backup_logfile()

            os.remove(logfile)
            create_header()

        else:
            create_header()

    except Exception as e_nopath:
        print("\t{0}\tFATAL ERROR! e_nopath: {1}".format(logtime, e_nopath))
        sys.exit(1)


def execute_commands():
    # For-Loop to execute every command
    # For each command in range of number_of_commands, the command will be read, saved to command_value and printed
    # into the daily-message.md file.
    # Then command_value will be executed, and it's output will also be printed into daily-message.md
    # In addition, some formatting ensures that the file is compliant with Markdown.
    try:
        for i in range(1, numer_of_commands + 1):
            new_command = f'command{i}'
            command_value = cfp.get('commands-config', new_command)

            f = open(logfile, "a")
            f.write("### Output of `{0}`\n```\n".format(command_value))
            f.close()

            os.system(command_value + " >> " + logfile)

            f = open(logfile, "a")
            f.write("```\n\n".format(command_value))
            f.close()

    except Exception as e_badcommand:
        print("\t{0}\tFATAL ERROR! - e_badcommand: {1}".format(logtime, e_badcommand))
        sys.exit(1)


def compose_email():
    # If no custom subject is specified, the default header from the logfile will be used
    subject = cfp.get('email-config', 'subject')
    if subject == 'default':
        subject = cfp.get('logfile-config', 'header') + ' ' + logtime
    # Setting up the E-Mail service: Receiver, Sender, SMTP-Server and Password...
    receiver = cfp.get('email-config', 'receivers')
    smtp_server = cfp.get('email-config', 'smtp_server')
    password = cfp.get('email-config', 'password')
    sender = cfp.get('email-config', 'sender')
    port = cfp.get('email-config', 'port')

    # The logfile will be opened as lf, and it's content will be read into 'message' which is then used to print the
    # file-content into the E-Mail
    with open(logfile, 'r') as lf:
        content = lf.readlines()
        message = "".join(content)
        lf.close()
        
        # Calling the function with expected variables, to send the E-Mail
        try:
            send_md_email(smtp_server, subject, sender, receiver, message)
        except Exception as e_nosend:
            print("\t{0}\tFATAL ERROR! - e_nosend: {1}".format(logtime, e_nosend))
            sys.exit(1)


def send_md_email(smtp_server, subject, sender, receiver, message):
    # Importing the EmailMessage-library and setting up the sender, receiver, subject and the message
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = receiver
    msg.set_content(message)

    # Opening a connection to the defined SMTP-Server, sending the message and closing this connection
    s = smtplib.SMTP(smtp_server)
    s.send_message(msg)
    s.quit()

    # Exiting with status 0 to indicate everything went well
    sys.exit(0)


create_logfile()
execute_commands()
compose_email()
