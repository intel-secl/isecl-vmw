
"""
Copyright (C) 2022 Intel Corporation
SPDX-License-Identifier: BSD-3-Clause

"""
import os
import pytest
import logging
import tcsclient.utils.utils as u
import tcsclient.constants as c
from unittest.mock import patch
from tests.test_common import (
    mockConfig, MockPythonLogger
)


@pytest.mark.parametrize(
    "return_configObj, output",[
        (mockConfig, MockPythonLogger()),
        (None, None),
        (mockConfig, 'exp'),
])
@patch('tcsclient.utils.utils.RotatingFileHandler')
@patch('tcsclient.utils.utils.logging.getLogger')
@patch('tcsclient.utils.utils.TCSClientUtils.getConfigObj')
def test_initLogger(mock_config, mock_logging, mock_rfh, return_configObj, output):
    """
    Unit test for initLogger method.
    """
    u.TCSClientUtils.logger=None
    u.TCSClientUtils.config=None
    mock_config.return_value = return_configObj
    if output == 'exp':
         mock_rfh.side_effect=Exception(IOError)
         u.TCSClientUtils.initLogger()
         assert u.TCSClientUtils.logger == None
    else:
         if return_configObj != None:
             mock_logging.return_value = output
         u.TCSClientUtils.initLogger()
         assert u.TCSClientUtils.logger == output

def test_loadTCSClientConf():
    """
    Unit test for loadTCSClientConf method.
    """
    u.TCSClientUtils.loadTCSClientConf()
    assert u.TCSClientUtils.config != None


def test_getLoggerObj():
    """
    Unit test for getLoggerObj method.
    """
    u.TCSClientUtils.logger=None
    u.TCSClientUtils.config=None

    u.TCSClientUtils.getLoggerObj()
    assert u.TCSClientUtils.logger != None


def test_getConfigObj():
    """
    Unit test for getConfigObj method.
    """
    u.TCSClientUtils.logger=None
    u.TCSClientUtils.config=None

    u.TCSClientUtils.getConfigObj()
    assert u.TCSClientUtils.config != None


@pytest.mark.parametrize(
    "env_var, env_value, output",[
        (c.ENV_DB_HOST, None, None),
        (c.ENV_DB_NAME, None, None),
        (c.ENV_DB_USER, None, None),
        (c.ENV_Admin_Name, None, None),
        (c.ENV_RegistrationURL, None, None),
        (c.ENV_VCenterIP, None, None),
        (c.ENV_VCenterPort, None, None),
        (c.ENV_TCSURL, None, None),
        (c.ENV_SessionURL, None, None),
        (c.ENV_TaskURL, None, None),
        (c.ENV_LOG_LEVEL, 'info', mockConfig),
        (c.ENV_LOG_LEVEL, 'invalid', mockConfig),
        (c.ENV_TIMER_MINS, None, mockConfig),
        (c.ENV_TIMER_MINS, -1, None),
])
@patch('tcsclient.utils.utils.TCSClientUtils.getEnvValue')
def test_loadConfValuesFromEnv(mock_env, env_var, env_value, output):
    """
    Unit test for loadConfValuesFromEnv method.
    """
    u.TCSClientUtils.logger=None
    u.TCSClientUtils.config=None

    def mockEnv(varname):
        if varname == env_var:
            return env_value
        else:
            return os.environ[varname]

    mock_env.side_effect=mockEnv
    conf = u.TCSClientUtils.loadConfValuesFromEnv()
    if output != None:
       assert conf 
    else:
       assert conf == None

def test_getTCSClientDBURL():
    """
    Unit test for getTCSClientDBURL method.
    """
    u.TCSClientUtils.logger=None
    u.TCSClientUtils.config=None

    dburl = u.TCSClientUtils.getTCSClientDBURL()
    assert dburl != None
