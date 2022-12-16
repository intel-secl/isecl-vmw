"""
Copyright (C) 2022 Intel Corporation
SPDX-License-Identifier: BSD-3-Clause

"""
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from tcsclient.utils.utils import TCSClientUtils as utils
import ssl

"""
This file contains Database engine instance creation and database session related variable.
"""

ssl_context = ssl.SSLContext()
engine = create_engine(utils.getTCSClientDBURL(), connect_args={'ssl_context': ssl_context}, client_encoding='utf8')
Base = declarative_base()
session_factory= sessionmaker(bind=engine)

