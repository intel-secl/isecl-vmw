"""
Copyright (C) 2022 Intel Corporation
SPDX-License-Identifier: BSD-3-Clause

"""
from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID
from tcsclient.utils.db_base import Base

"""
VMWSGXHostsInfo class is the ORM model for table vmware_sgx_hosts_status used for saving VMWare 
SGX Host information.
"""

class VMWSGXHostsInfo(Base):
   __tablename__ = 'vmware_sgx_hosts_status'
   
   created_on = Column(TIMESTAMP, nullable=False, default=func.now())
   updated_on = Column(TIMESTAMP)
   status = Column(String, nullable=False)
   ppid = Column(String, primary_key=True)
   registered_time = Column(TIMESTAMP, nullable=False)

   def __init__(self, status, timestamp, ppid, registered_time):
       self.ppid = ppid
       self.created_on = timestamp
       self.updated_on = timestamp
       self.status = status
       self.registered_time = registered_time 
