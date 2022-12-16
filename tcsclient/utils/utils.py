#!/usr/bin/env python
"""
Copyright (C) 2022 Intel Corporation
SPDX-License-Identifier: BSD-3-Clause

"""

import os
import yaml
import logging
from logging.handlers import RotatingFileHandler
import tcsclient.constants as c


"""
TCSClientUtils class contains static utility functions for logger and configuration manipulation. 
And this class has other utility functions like get logger and config object, loading configuration 
from env variables, function for framing database url etc.,

"""
class TCSClientUtils:
    logger=None
    config=None

    @staticmethod
    def initLogger():
        logLevelDict={'info': logging.INFO, 'debug': logging.DEBUG, 'warn': logging.WARNING, 'error': logging.ERROR}
        configObj = TCSClientUtils.getConfigObj()
        if configObj != None:
            TCSClientUtils.logger = logging.getLogger('TCSClient')
            TCSClientUtils.logger.propagate = False
            TCSClientUtils.logger.setLevel(logLevelDict[configObj['tcsClient']['logLevel']])
            try:
                fhandler = RotatingFileHandler(c.TCS_CLIENT_LOG_FILE, maxBytes=10000000, backupCount=5)
                fformat = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                fhandler.setFormatter(fformat)
                TCSClientUtils.logger.addHandler(fhandler)
            except IOError:
                TCSClientUtils.logger = None
            except Exception:
                TCSClientUtils.logger = None
        else:
            print("Init logger failed")

    @staticmethod
    def loadTCSClientConf():
        with open(c.TCS_CLIENT_CONF_PATH, 'r') as file:
            TCSClientUtils.config=yaml.safe_load(file)

    @staticmethod
    def getLoggerObj():
        if not TCSClientUtils.logger:
            TCSClientUtils.initLogger()
        return TCSClientUtils.logger

    @staticmethod
    def getConfigObj():
        if not TCSClientUtils.config:
            return TCSClientUtils.loadConfValuesFromEnv()
        else:
            return TCSClientUtils.config

    @staticmethod
    def getEnvValue(envVarName):
        if os.environ.get(envVarName) != None:
            return os.environ[envVarName]
        else:
            return  None
        
    @staticmethod
    def loadConfValuesFromEnv():
        secs = 0
        mins = 0
        host = user = dbname = adminName = rURL = vIP = vPort = tcsURL = sessionURL = taskURL = ''
        logLevel = c.TCS_CLIENT_DEFAULT_LOG

        tmins = TCSClientUtils.getEnvValue(c.ENV_TIMER_MINS)
        if tmins != None:
            mins = int(tmins)
            if mins > 2880 or mins <= 0:
               print("Invalid Timer Mins provided")
               return None
            secs = mins * 60
        else:
            secs = c.TCS_CLIENT_DEFAULT_TIMER_MINS * 60

        host = TCSClientUtils.getEnvValue(c.ENV_DB_HOST)
        if host == None:
            print("Invalid DB HOST")
            return None

        dbname = TCSClientUtils.getEnvValue(c.ENV_DB_NAME)
        if dbname == None:
            print("Invalid DB Name")
            return None

        user = TCSClientUtils.getEnvValue(c.ENV_DB_USER)
        if user == None:
            print("Invalid DB Username")
            return None

        adminName = TCSClientUtils.getEnvValue(c.ENV_Admin_Name)
        if adminName == None:
            print("Invalid Admin Name")
            return None

        adminPassword = TCSClientUtils.getEnvValue(c.ENV_Admin_Password)
        if adminPassword == None:
            print("Invalid Admin Password")
            return None

        rURL = TCSClientUtils.getEnvValue(c.ENV_RegistrationURL)
        if rURL == None:
            print("Invalid registration URL")
            return None

        vIP = TCSClientUtils.getEnvValue(c.ENV_VCenterIP)
        if vIP == None:
            print("Invalid VCenter IP")
            return None

        vPort = TCSClientUtils.getEnvValue(c.ENV_VCenterPort)
        if vPort == None:
            print("Invalid VCenter Port")
            return None

        tcsURL = TCSClientUtils.getEnvValue(c.ENV_TCSURL)
        if tcsURL  == None:
            print("Invalid tcs url")
            return None

        sessionURL = TCSClientUtils.getEnvValue(c.ENV_SessionURL)
        if sessionURL == None:
            print("Invalid session url")
            return None

        taskURL = TCSClientUtils.getEnvValue(c.ENV_TaskURL)
        if taskURL == None:
            print("Invalid task url")
            return None

        logLevel = TCSClientUtils.getEnvValue(c.ENV_LOG_LEVEL)
        if logLevel != None:
            logLevel = str(logLevel)
            if logLevel.lower() not in [ 'debug', 'info', 'warning', 'error']:
                logLevel = c.TCS_CLIENT_DEFAULT_LOG
        else:
            logLevel = c.TCS_CLIENT_DEFAULT_LOG

        TCSClientUtils.config = {'tcsClient': {'version': c.TCS_CLIENT_VERION, 
                        'lockfile': c.TCS_CLIENT_LOCK_FILE,
                        'logLevel': logLevel,
                        'timerInterval': secs,
                        'adminName':  adminName,
                        'adminPassword' : adminPassword,
                        'regURL': rURL,
                        'sessionURL': sessionURL,
                        'taskURL': taskURL,
                        'tcsURL': tcsURL,
                        'vCenterIP': vIP,
                        'vCenterPort': vPort,
                        'clientDb': { 'host': host, 'db': dbname, 'user': user }}}

        try:
            if TCSClientUtils.config:
                with open(c.TCS_CLIENT_CONF_PATH,'w') as yamlfile:
                     yaml.safe_dump(TCSClientUtils.config, yamlfile)
        except:
            print("exception in loading yaml")
            TCSClientUtils.config = None
        return TCSClientUtils.config
                
    
    @staticmethod
    def getTCSClientDBURL():
        config = TCSClientUtils.getConfigObj()
        if config == None:
           print("Error in loading config object")
           return None
        dbname = config['tcsClient']['clientDb']['db']
        host = config['tcsClient']['clientDb']['host']
        user = config['tcsClient']['clientDb']['user']
        passwd = ''

        tpasswd = TCSClientUtils.getEnvValue(c.ENV_DB_PASSWD)
        if tpasswd != None:
            passwd = str(tpasswd)
        else:
            return None
        return 'postgresql+pg8000://'+user+':'+passwd+'@'+host+':5432/'+dbname

