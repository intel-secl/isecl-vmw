"""
Copyright (C) 2022 Intel Corporation
SPDX-License-Identifier: BSD-3-Clause

"""
import time 
import tcsclient.utils.db_base as base
from sqlalchemy import func

from tcsclient.models.vmw_sgx_host_info import VMWSGXHostsInfo
from tcsclient.utils.utils import TCSClientUtils as utils

logger=utils.getLoggerObj()

"""
TCSClientDBUtils class has static functions DB sesion object creation and SGX Hosts table CRUD operation functions.
"""
class TCSClientDBUtils:
       
      @staticmethod
      def getSessionFactoryObj():
          factory = None
          try:
             base.Base.metadata.create_all(base.engine)
             factory = base.session_factory()
          except Exception as e:
             logger.error("Error in Get Session Factory Obj:%s", str(e))
             return None
          return factory

      @staticmethod
      def upsertSGXHostInfo(status, ppid, timeStamp):
          ret = False
          try:
              host = TCSClientDBUtils.getSGXHostInfo(ppid)
              if host == None:
                 ret = TCSClientDBUtils.insertSGXHostInfo(status, ppid, timeStamp)
              else:
                 ret = TCSClientDBUtils.updateSGXHostInfoByStatus(status, ppid, timeStamp)
              logger.info("Upsert SGX Host Info successfully")
          except Exception as e:
             logger.error("Error in Upsert SGX Host:%s", str(e))
             return False
          return ret

      @staticmethod
      def insertSGXHostInfo(status, ppid, timeStamp):
          try:
              if not all([ status, ppid, timeStamp ]):
                 raise Exception("Invalid input provided")
              session = TCSClientDBUtils.getSessionFactoryObj()
              hostInfo = VMWSGXHostsInfo(status, func.now(), ppid, timeStamp)
              session.add(hostInfo)
              session.commit()
              session.close() 
              logger.info("Inserting SGX Host Info successfully")
          except Exception as e:
             logger.error("Error in Insert SGX Host:%s", str(e))
             return False
          return True

      @staticmethod
      def updateSGXHostInfoByStatus(status, ppid, timeStamp):
          try:
              if not all([ status, ppid, timeStamp ]):
                 raise Exception("Invalid input provided")
              session = TCSClientDBUtils.getSessionFactoryObj()
              host = session.query(VMWSGXHostsInfo).filter(VMWSGXHostsInfo.ppid == ppid).one()
              host.status = status
              host.ppid = ppid 
              host.updated_on = func.now()
              host.registered_time = timeStamp
              session.add(host)
              session.commit()
              session.close() 
              logger.info("Updating SGX Host Info successfully")
          except Exception as e:
             logger.error("Error in Update SGX Host:%s", str(e))
             return False
          return True

      @staticmethod
      def deleteSGXHostInfoByPPID(ppid):
          try:
              if not ppid:
                 raise Exception("Invalid input provided")
              session = TCSClientDBUtils.getSessionFactoryObj()
              host = session.query(VMWSGXHostsInfo).filter(VMWSGXHostsInfo.ppid == ppid).one()
              session.delete(host)
              session.commit()
              session.close() 
              logger.info("Deleting SGX Host Info successfully")
          except Exception as e:
             logger.error("Error in Delete SGX Host:%s", str(e))
             return False
          return True


      @staticmethod
      def getSGXHostInfo(ppid):
          try:
              session = TCSClientDBUtils.getSessionFactoryObj()
              host = session.query(VMWSGXHostsInfo).filter(VMWSGXHostsInfo.ppid == ppid).one()
              session.expunge_all()
              session.close() 
              logger.info("Retrieved SGX Host Info successfully %s" % host.ppid)
          except Exception as e:
             logger.error("Error in Get SGX Host:%s", str(e))
             return None
          return host

      @staticmethod
      def getAllSGXHostInfo():
          try:
              session = TCSClientDBUtils.getSessionFactoryObj()
              hosts = session.query(VMWSGXHostsInfo).all()
              session.expunge_all()
              session.close() 
              logger.info("Get All SGX Host Info successfully %s" % hosts)
          except Exception as e:
             logger.error("Error in Get All SGX Host:%s", str(e))
             return None
          return hosts
