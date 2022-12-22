"""
Copyright (C) 2022 Intel Corporation
SPDX-License-Identifier: BSD-3-Clause

"""
import os
import time
import json
import fcntl
import threading
import string, requests
from requests.auth import HTTPBasicAuth

from types import SimpleNamespace

from pyVmomi import vim, vmodl

import tcsclient.constants as constants
#import tcsclient.utils.service_instance as service_instance
from pyVim.connect import SmartConnect, Disconnect
from tcsclient.utils.db_utils import TCSClientDBUtils
from tcsclient.utils.utils import TCSClientUtils 

"""
TCSClientDaemon has core daemon logic and it has timer function that will run periodically and perform SGX Host registration.
"""
class TCSClientDaemon:

    __config = None
    __logger = None
    __tevent = None
    __app_lock = None
    __daemonInstance = None 
    __sessionId = None
    __timerObj = None

    @staticmethod
    def getInstance(loggerObj, configObj):
        TCSClientDaemon.__logger = loggerObj
        TCSClientDaemon.__config = configObj
        if TCSClientDaemon.__daemonInstance == None and TCSClientDaemon.acquireLock() == True:
            return TCSClientDaemon()
        else:
            loggerObj.info("Instance already running .......................")
            return None

    def __init__(self):
        TCSClientUtils.__daemonInstance=self
        self.__logger.info("Creating TCSClientDaemon Object.......................")

    @classmethod
    def acquireLock(cls):
        try:
            TCSClientDaemon.__app_lock = os.open(TCSClientDaemon.__config['tcsClient']['lockfile'], os.O_WRONLY)
            fcntl.lockf(TCSClientDaemon.__app_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            TCSClientDaemon.__logger.info("Acquired lock to the file")
        except IOError as err:
            TCSClientDaemon.__logger.error("Already another instance of Daemon Running : %s" % str(err))
            return False
        return True

    def releaseLock(self):
        try:
            fcntl.lockf(self.__app_lock, fcntl.LOCK_UN)
            os.close(self.__app_lock)
            self.__logger.info("Cleanup done....")
            return True
        except IOError as err:
            self.__logger.error("ERROR: Unlock failed : %s" % str(err))
            return False

    def timerThreadCb(self):
        self.__logger.debug("In thread CB waiting for signal..................")
        self.vCenterAPI()
        tid = 0
        while self.__tevent.is_set()==False:
            tid=tid+1
            self.__logger.debug("Creating thread:%d" % tid)
            self.__timerObj = threading.Timer(TCSClientDaemon.__config['tcsClient']['timerInterval'], self.vCenterAPI)
            self.__timerObj.start()
            self.__timerObj.join()
            self.__timerObj=None
            self.__logger.debug("Creating thread:%d closed ........." % tid)
        self.__logger.info("Got signal in thread cb and exiting")


    def startTimer(self):
        self.__tevent=threading.Event()
        th = threading.Thread(target=self.timerThreadCb)
        th.start()

    def releaseResources(self):
        self.releaseLock()
        if self.__tevent != None:
            self.__tevent.set()
        if self.__timerObj != None:
            self.__timerObj.cancel()

    
    def registerHost(self, hostId):
        TCSClientDaemon.__logger.debug("registerHost() Entering")

        if TCSClientDaemon.__sessionId == None:
            try:
                sessionURL = TCSClientDaemon.__config['tcsClient']['sessionURL']
                response = requests.post(sessionURL, auth=HTTPBasicAuth(TCSClientDaemon.__config['tcsClient']['adminName'], TCSClientDaemon.__config['tcsClient']['adminPassword']), verify=constants.VMWARE_CERT)

                if response.status_code == requests.codes.created:
                    TCSClientDaemon.__sessionId = response.json()
                    TCSClientDaemon.__logger.debug("registerHost(): Session id created")
                else:
                    TCSClientDaemon.__logger.error("couldn't create session as %s was returned", response.status_code)
                    return None 
            except Exception as err:
                TCSClientDaemon.__logger.error("exception while establishing session: %s", str(err))
                return None 
        else:
            TCSClientDaemon.__logger.debug("registerHost(): Session id exists")

        #Check here if tls certificate exists in path. If yes use it else download it.
        regURL = TCSClientDaemon.__config['tcsClient']['regURL']
        data = {constants.HOST_ID:hostId}
        headers = {constants.API_SESSIONID:TCSClientDaemon.__sessionId,"Content-Type":"application/json"}
        try:
            response = requests.post(regURL, headers=headers, json=data, verify=constants.VMWARE_CERT)
            if response.status_code == requests.codes.accepted:
                return response.json()
            elif response.status_code == requests.codes.unauthorized:
                sessionURL = TCSClientDaemon.__config['tcsClient']['sessionURL']
                response = requests.post(sessionURL, auth=HTTPBasicAuth(TCSClientDaemon.__config['tcsClient']['adminName'], TCSClientDaemon.__config['tcsClient']['adminPassword']), verify=constants.VMWARE_CERT)
                if response.status_code == requests.codes.created:
                    TCSClientDaemon.__sessionId = response.json()
                    response = requests.post(regURL, headers=headers, json=data, verify=constants.VMWARE_CERT)
                    if response.status_code == requests.codes.accepted:
                        return response.json()
                    else:
                        TCSClientDaemon.__logger.error("couldn't register the host: %s", response.status_code)
                        return None 
                else:
                    TCSClientDaemon.__logger.error("couldn't create session as %s was returned", response.status_code)
                    return None 
 
            else:
                TCSClientDaemon.__logger.error("Registration task unsuccessful: %s", response.status_code)
                return None 

        except Exception as err:
               TCSClientDaemon.__logger.error("Exception while establishing session: %s", str(err))
               return None 
        return None 

    def isTaskSuccessful(self, taskId):
        TCSClientDaemon.__logger.debug("isTaskSuccessful() Entering")

        if TCSClientDaemon.__sessionId != None:
            #call RESTT API GETTASK
            taskURL = TCSClientDaemon.__config['tcsClient']['taskURL'] + taskId
            headers = {constants.API_SESSIONID:TCSClientDaemon.__sessionId}
            try:
                response = requests.get(taskURL, headers=headers, verify=constants.VMWARE_CERT)
                if response.status_code == requests.codes.ok and (len(response.json()) > 0):
                    js = response.json()
                    jsonDump = json.loads(json.dumps(js),object_hook=lambda d: SimpleNamespace(**d))
                    return jsonDump.status
                else:
                    TCSClientDaemon.__logger.error("isTaskSuccessful unsuccessful")
                    return None
            except Exception as err:
               TCSClientDaemon.__logger.error("Exception while : %s", str(err))
               return None
        else:
            TCSClientDaemon.__logger.error("sessionId not present to proceed")  
            return None 

    def sendToTCS(self, ppid):
        TCSClientDaemon.__logger.debug("sendToTCS() Entering")

        tcsURL = TCSClientDaemon.__config['tcsClient']['tcsURL']
        data = {constants.PPID:ppid}
        headers = {"Content-Type":"application/json"}
        try:
            response = requests.put(tcsURL, headers=headers, json=data, verify=constants.SCS_CERT)
            if response.status_code == requests.codes.ok:
                TCSClientDaemon.__logger.info("Request to TCS sent successfully")
                return True
            else:
                TCSClientDaemon.__logger.error("request to send data to TCS failed with error code: %s", response.status_code)
                return False
        except Exception as err:
            TCSClientDaemon.__logger.error("Exception while sending data to TCS: %s", str(err))
            return False

    def verifySGXInfo(self, sgxInfo):
        TCSClientDaemon.__logger.debug("verifySGXInfo entering")

        if not sgxInfo:
            TCSClientDaemon.__logger.info('is running an old (< 7.0) version of ESX without ''SGX support.')
            return False
        if not sgxInfo.registrationInfo:
            TCSClientDaemon.__logger.info('is running an old (< 8.0) version of ESX without SGX ' 'registration support.')
            return False
        return True

    def completeRegistrtaionSteps(self, tDict):
        TCSClientDaemon.__logger.debug("completeRegistrtaionSteps entering")

        si = SmartConnect(host=TCSClientDaemon.__config['tcsClient']['vCenterIP'], user=TCSClientDaemon.__config['tcsClient']['adminName'], pwd=os.environ[constants.ENV_Admin_Password], disableSslCertValidation=True)

        updatedDict = {}
        successfulList = []
        content = si.RetrieveContent()
        for center_list in content.rootFolder.childEntity: #this will give us data centers
            for cluster in center_list.hostFolder.childEntity:
                if cluster.host: #to chck if there are hosts in the cluster
                    for host in cluster.host:
                        updatedDict[host._moId] = host

        for x in tDict:
            if self.isTaskSuccessful(x) == constants.SUCCESS_STATUS:
                a = tDict[x]._moId
                successfulList.append(a)
            else:
                TCSClientDaemon.__logger.debug("task unsuccessful. Hence trying another one")

        for x in successfulList:
            if x in updatedDict:
                if self.sendToTCS(updatedDict[x].hardware.sgxInfo.registrationInfo.ppid):
                    #add record in db
                    if TCSClientDBUtils.upsertSGXHostInfo(updatedDict[x].hardware.sgxInfo.registrationInfo.status, updatedDict[x].hardware.sgxInfo.registrationInfo.ppid, updatedDict[x].hardware.sgxInfo.lastRegisteredTime):
                        TCSClientDaemon.__logger.debug("Database update for host %s is successful", updatedDict[x].name)
                    else:
                        TCSClientDaemon.__logger.error("Data update for host %s is unsuccessful", updatedDict[x].name)
                        continue
                else:
                    TCSClientDaemon.__logger.error("sendToTCS() call for host %s failed", updatedDict[x].name)
                    continue

    def vCenterAPI(self):
        TCSClientDaemon.__logger.debug("vCenterAPI() Entering")

        try:
            #TODO: Add exception handling here
            si = SmartConnect(host=TCSClientDaemon.__config['tcsClient']['vCenterIP'], user=TCSClientDaemon.__config['tcsClient']['adminName'], pwd=os.environ[constants.ENV_Admin_Password], disableSslCertValidation=True)

        except Exception as err:
            TCSClientDaemon.__logger.error("Exception in vCenterAPI: %s", str(err))
            return False

        try:
            content = si.RetrieveContent()
            tDict = {}
            RegistrationType = vim.host.SgxRegistrationInfo.RegistrationType
            RegistrationStatus = vim.host.SgxRegistrationInfo.RegistrationStatus 

            for center_list in content.rootFolder.childEntity: #this will give us data centers
                for cluster in center_list.hostFolder.childEntity:
                    TCSClientDaemon.__logger.debug("printing cluster name " + cluster.name)
                    if cluster.host: #to chck if there are hosts in the cluster
                        for host in cluster.host:
                            TCSClientDaemon.__logger.debug('ESX host {} '.format(host.name))
                            if not self.verifySGXInfo(host.hardware.sgxInfo):
                                continue
                            if host.hardware.sgxInfo.registrationInfo.status == RegistrationStatus.incomplete or  host.hardware.sgxInfo.registrationInfo.ppid == None:
                                TCSClientDaemon.__logger.debug("status of host: " + format(host.name) + " is incomplete or PPID is null")
                                if host.hardware.sgxInfo.registrationInfo.type == RegistrationType.manifest:
                                    task_id = self.registerHost(host._moId)
                                    if task_id != None:
                                        tDict[task_id] = host
                                        continue
                                    else:
                                        TCSClientDaemon.__logger.error("registration for host %s unsuccessful", host._moId)
                                        continue
                                else:
                                    TCSClientDaemon.__logger.info("cannot register single package for host: %s", host.name)
                                    continue 
                            elif host.hardware.sgxInfo.registrationInfo.status == RegistrationStatus.complete:
                                TCSClientDaemon.__logger.debug("status of host: " + format(host.name) + " is complete")

                                #if record exists with same ppid then ignore else do accordingly
                                db_instance = TCSClientDBUtils.getSGXHostInfo(host.hardware.sgxInfo.registrationInfo.ppid)
                                if db_instance != None:
                                   ts = host.hardware.sgxInfo.registrationInfo.lastRegisteredTime.replace(tzinfo=None)
                                   if db_instance.registered_time == ts:
                                        TCSClientDaemon.__logger.debug("no change is needed")
                                        continue
                                   else:
                                        TCSClientDaemon.__logger.info("There is a change in data, hence refresh is needed in TCS.")
                                        if self.sendToTCS(host.hardware.sgxInfo.registrationInfo.ppid):
                                            if TCSClientDBUtils.upsertSGXHostInfo(host.hardware.sgxInfo.registrationInfo.status, host.hardware.sgxInfo.registrationInfo.ppid, host.hardware.sgxInfo.registrationInfo.lastRegisteredTime):
                                                 TCSClientDaemon.__logger.info("Data is inserted successfully")
                                            else: 
                                                TCSClientDaemon.__logger.error("Data insertion is unsuccessful")
                                                continue
                                        else:
                                            TCSClientDaemon.__logger.error("sendToTCS() call for host %s failed", host.name)
                                            continue
                                else:
                                    TCSClientDaemon.__logger.debug("No data in database for host %s , hence a new request", host.name)
                                    if self.sendToTCS(host.hardware.sgxInfo.registrationInfo.ppid):
                                        if TCSClientDBUtils.upsertSGXHostInfo(host.hardware.sgxInfo.registrationInfo.status, host.hardware.sgxInfo.registrationInfo.ppid, host.hardware.sgxInfo.registrationInfo.lastRegisteredTime):
                                            TCSClientDaemon.__logger.info("Database update for host %s successful", host.name)
                                        else:
                                            TCSClientDaemon.__logger.error("DataBase update for host %s unsuccessful", host.name)
                                            continue
                                    else:
                                        TCSClientDaemon.__logger.error("sendToTCS() call for host %s failed", host.name)
                            elif host.hardware.sgxInfo.registrationInfo.status == RegistrationStatus.notApplicable:
                                TCSClientDaemon.__logger.warn("cannot register host %s as status is notApplicable", host.name)
                                continue
                        
                        if len(tDict) != 0:
                            TCSClientDaemon.__logger.debug("Dictionary isn't empty. Hence will check status and do accordingly")
                            time.sleep(11)
                            TCSClientDaemon.__logger.debug("sleep finished")
                            self.completeRegistrtaionSteps(tDict)
                        else:
                            TCSClientDaemon.__logger.info("Dictionary containing task ids is empty")
                    else:
                        continue

        except vmodl.MethodFault as error:
            TCSClientDaemon.__logger.error("Caught vmodl fault : " + error.msg)
            return False 

        return True
