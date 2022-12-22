"""
Copyright (C) 2022 Intel Corporation
SPDX-License-Identifier: BSD-3-Clause

"""
import os
import sys
import shutil
import getopt
import signal
from subprocess import run
import tcsclient.constants as c
from tcsclient.utils.utils import TCSClientUtils as utils
from tcsclient.resource.tcs_client_daemon import TCSClientDaemon
import uuid

"""
TCS Client Daemon main runs from this file and it is responsible for handling command line 
arguments parsing and perform required actions.
"""

config = None
logger = None
deamonIns = None


def exitTCSClientDaemon(status):
    if deamonIns != None:
        deamonIns.releaseResources()
    sys.exit(status);

def deamonSignalHandler(signum, frame):
    logger.info("calling signal handler func....")
    exitTCSClientDaemon(c.EXIT_CODE_SUCCESS)

def displayHelpMsgAndExit():
    print("")
    print("Usage:")
    print("    tcs-client <command> [arguments]")
    print("")
    print("Available Commands:")
    print("     -h|--help | help              Show this help message")
    print("    start                          Start tcs-client")
    print("    status                         Show the status of tcs-client")
    print("    stop                           Stop tcs-client")
    print("    uninstall [--purge]            Uninstall tcs-client. --purge option needs to be applied to remove configuration and data files")
    print("    -v|--version | version         Show the version of tcs-client")
    exitTCSClientDaemon(c.EXIT_CODE_SUCCESS)

def displayDaemonVersion():
    print("TCS Client Daemon: ")
    print("  version: " + config['tcsClient']['version'])
    logger.info("TCS Client Daemon: %s" % config['tcsClient']['version'])
    exitTCSClientDaemon(c.EXIT_CODE_SUCCESS)

def runTCSClientDaemon():
    global deamonIns
    deamonIns = TCSClientDaemon.getInstance(logger, config)
    if deamonIns == None:
        print("TCS-Client already running")
        logger.error("Daemon instance not created so exiting")
        return exitTCSClientDaemon(c.EXIT_CODE_SUCCESS)
    deamonIns.startTimer()
    print("TCS-Client started running")
    signal.signal(signal.SIGTERM, deamonSignalHandler)
    signal.signal(signal.SIGINT, deamonSignalHandler)
    signal.pause()

def startTCSClientDaemon():
    logger.info("Starting TCS Client Daemon.................")
    startProcess = run( [ 'systemctl', 'start', 'tcs-client' ] )
    exitTCSClientDaemon(startProcess.returncode)

def stopTCSClientDaemon():
    logger.info("Stoping TCS Client Daemon.................")
    p = run( [ 'systemctl', 'stop', 'tcs-client' ] )
    exitTCSClientDaemon(p.returncode)

def statusTCSClientDaemon():
    logger.info("Fetching status of TCS Client Daemon.................")
    p = run( [ 'systemctl', 'status', 'tcs-client' ] )
    exitTCSClientDaemon(p.returncode)

def uninstallTCSClientDaemon():
    logger.info("Uninstalling TCS Client Daemon.................")
    shutil.rmtree(c.TCS_CLIENT_LOG_DIR)
    stopTCSClientDaemon()

def getSysArgument():
    return sys.argv

def parseCommandlineArgs():
    sysArg = getSysArgument()
    if(len(sysArg) == 1):
        return displayHelpMsgAndExit()
    argList = sysArg[1:]
    shortOpts = "hstuvfr"
    longOpts = ["Help", "StartDaemon", "StopDaemon", "UninstallDaemon", "Version", "StatusDaemon", "RunDaemon"]
    invalidOpt = True
    global logger
    logger=utils.getLoggerObj()
    global config
    config=utils.getConfigObj()

    try:
        args, vals = getopt.getopt(argList, shortOpts, longOpts)
        for currentArg,currentVal in args:
            if currentArg in ("-h", "--Help"):
                return displayHelpMsgAndExit()
            elif currentArg in ("-s", "--StartDaemon"):
                invalidOpt = False
                startTCSClientDaemon()
            elif currentArg in ("-r", "--RunDaemon"):
                invalidOpt = False
                return runTCSClientDaemon()
            elif currentArg in ("-t", "--StopDaemon"):
                invalidOpt = False
                return stopTCSClientDaemon()
            elif currentArg in ("-u", "--UninstallDaemon"):
                invalidOpt = False
                return uninstallTCSClientDaemon()
            elif currentArg in ("-v", "--Version"):
                invalidOpt = False
                return displayDaemonVersion()
            elif currentArg in ("-f", "--StatusDaemon"):
                invalidOpt = False
                return statusTCSClientDaemon()
    except getopt.error as err:
        print("Error while parsing commandline argument")

    if bool(invalidOpt):
        print("ERROR: Invalid commandLine options provided")
        return displayHelpMsgAndExit()



def main():
    try:
      parseCommandlineArgs()
    except Exception as e:
      print("Exception in main: "  + str(e))
      exitTCSClientDaemon(c.EXIT_CODE_ERROR)

if __name__ == '__main__':
    main()
