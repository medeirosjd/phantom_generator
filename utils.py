"""!
\file utils.py

\brief Set of helper functions
"""

import datetime
import psutil
import os


def log_message(text, verbose = True):
    """!
    \brief Prints a log message with a timestamp and resources usage

    \param text Message to be logged
    \param verbose Only logs messages if set to true (default)
    """

    time_now = current_time_for_logging()
    psutil.virtual_memory()
    dict(psutil.virtual_memory()._asdict())
    mem_used_perc = psutil.virtual_memory().percent
    disk_used_perc = psutil.disk_usage(os.getcwd()).percent
    
    if (verbose):
        print("[" + time_now + " Mem/disk usage: " + "%0.2f" %  + mem_used_perc + " % / "  + "%0.2f" %  + disk_used_perc + " %] " + text)

    if (mem_used_perc > 90):
        print("WARNING: Critical resources usage")


def current_time_for_logging():
    """!
    \brief Gets current time in a format suitable for printing

    \return Time with format dd-mm-yyyy hh:mm:ss
    """

    now = datetime.datetime.now()

    return now.strftime('%d-%m-%Y %H:%M:%S')


def current_time_for_filename():
    """!
    \brief Gets current time in a format suitable for printing

    \return Time with format yyyy-mm-dd_hh-mm-ss
    """

    now = datetime.datetime.now()

    return now.strftime('%Y-%m-%d_%H-%M-%S')
