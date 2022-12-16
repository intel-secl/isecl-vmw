"""
Copyright (C) 2022 Intel Corporation
SPDX-License-Identifier: BSD-3-Clause

"""
import pytest
import tcsclient.utils.db_utils as du
from tcsclient.models.vmw_sgx_host_info import VMWSGXHostsInfo
from unittest.mock import patch
from tests.test_common import (
    MockLog
)


testVar=None

class MockFilter:
      
      retOneVal=None
      
      def __init__(self, retOne=None):
          self.retOneVal=retOne

      def filter(self, query):
          return self
          
      def one(self):
          global testVar
          testVar = self.retOneVal
          return self.retOneVal

      def all(self):
          global testVar
          testVar = self.retOneVal
          return self.retOneVal


class MockSession:

      mockFilterIns=None

      def __init__(self, retOne=None):
          self.mockFilterIns=MockFilter(retOne)

      def add(self, hostInfo):
          return None

      def commit(self):
          return None

      def close(self):
          return None

      def delete(host):
          return None

      def expunge_all(self):
          return None

      def query(self, data):
          global testVar
          testVar = self.mockFilterIns.retOneVal
          return self.mockFilterIns

@pytest.mark.parametrize(
    "return_session_factory, output",[
        (None, None),
        ("test", 'test'),
        ("exp", None)
])
@patch('tcsclient.utils.db_utils.base.Base.metadata.create_all')
@patch('tcsclient.utils.db_utils.base.session_factory')
@patch('tcsclient.utils.db_utils.logger')
def test_getSessionFactoryObj(mock_logger, mock_factory, mock_create_all, return_session_factory, output):
    """
    Unit test for getSessionFactoryObj method.
    the create_all and session_factory is mocked 
    """
    mock_logger.return_value = MockLog()
    if return_session_factory == 'exp':
        mock_factory.side_effect = Exception('Generic exception')
    else:
        mock_factory.return_value = return_session_factory
    factory = du.TCSClientDBUtils.getSessionFactoryObj()
    assert factory == output

@pytest.mark.parametrize(
    "return_getSGXHostInfo, output, retDbApi, input_status, input_ppid",[
        (None, True, True, 'dummy_status','dummy_ppid'),
        ('testhost', True, True, 'dummy_status', 'dummy_ppid'),
        (None, False, False, '', 'dummy_ppid'),
        (None, False, False, 'dummy_status', ''),
        ('exp', False, False, 'dummy_status', '')
])
@patch('tcsclient.utils.db_utils.TCSClientDBUtils.getSGXHostInfo')
@patch('tcsclient.utils.db_utils.logger')
@patch('tcsclient.utils.db_utils.TCSClientDBUtils.insertSGXHostInfo')
@patch('tcsclient.utils.db_utils.TCSClientDBUtils.updateSGXHostInfoByStatus')
def test_upsertSGXHostInfo(mock_updateSGXHost, mock_insertSGXHost, mock_logger, mock_getSGXHOSTInfo, return_getSGXHostInfo, output, retDbApi, input_status, input_ppid):
    """
    Unit test for upsertSGXHostInfo method.
    """
    mock_logger = MockLog()
    if return_getSGXHostInfo == 'exp':
        mock_getSGXHOSTInfo.side_effect = Exception('Generic exception')
    else:
        mock_getSGXHOSTInfo.return_value = return_getSGXHostInfo
        if return_getSGXHostInfo != None:
            mock_updateSGXHost.return_value = retDbApi
        else:
            mock_insertSGXHost.return_value = retDbApi
    returnval = du.TCSClientDBUtils.upsertSGXHostInfo(input_status, input_ppid, 'dummy_timestamp')
    assert returnval == output


@pytest.mark.parametrize(
    "return_vmSgxHostsInfo, output, input_status, input_ppid",[
        ('testhost', True, 'dummy_staus', 'dummy_ppid'),
        ('testhost', True, 'dummy_staus', 'dummy_ppid'),
        (None, False, '', 'dummy_ppid'),
        (None, False, 'dummy_status', '')
])
@patch('tcsclient.utils.db_utils.VMWSGXHostsInfo')
@patch('tcsclient.utils.db_utils.TCSClientDBUtils.getSessionFactoryObj')
@patch('tcsclient.utils.db_utils.logger')
def test_insertSGXHostInfo(mock_logger, mock_sessionFactoryObj,mock_vmwsgxhostinfo, return_vmSgxHostsInfo, output, input_status, input_ppid):
    """
    Unit test for insertSGXHostInfo method.
    """

    mock_logger.return_value = MockLog()
    mock_sessionFactoryObj.return_value = MockSession()
    mock_vmwsgxhostinfo.return_value = return_vmSgxHostsInfo
    returnval = du.TCSClientDBUtils.insertSGXHostInfo(input_status, input_ppid, 'dummy_timestamp')
    assert returnval == output


@pytest.mark.parametrize(
    "output, query_output,input_status, input_ppid",[
        (True, VMWSGXHostsInfo('dummy_status', 'dummy_timestamp', 'dummy_ppid', 'dummy_registered_time'), 'dummy_status', 'dummy_ppid'),
        (True, VMWSGXHostsInfo('dummy_status', 'dummy_timestamp', 'dummy_ppid', 'dummy_registered_time'), 'dummy_staus', 'dummy_ppid'),
        (False, None, '', 'dummy_ppid'),
        (False, None, 'dummy_status', '')
])
@patch('tcsclient.utils.db_utils.TCSClientDBUtils.getSessionFactoryObj')
@patch('tcsclient.utils.db_utils.logger')
def test_updateSGXHostInfoByStatus(mock_logger, mock_sessionFactoryObj, output, query_output, input_status, input_ppid):
    """
    Unit test for updateSGXHostInfo method.
    """

    mock_logger.return_value = MockLog()
    mock_sessionFactoryObj.return_value = MockSession(query_output)
    returnval = du.TCSClientDBUtils.updateSGXHostInfoByStatus(input_status, input_ppid, 'dummy_timestamp')
    assert returnval == output

@pytest.mark.parametrize(
    "output, input_ppid",[
        (True, 'dummy_ppid'),
        (False, '')
])
@patch('tcsclient.utils.db_utils.TCSClientDBUtils.getSessionFactoryObj')
@patch('tcsclient.utils.db_utils.logger')
def test_deleteSGXHostInfo(mock_logger, mock_sessionFactoryObj, output, input_ppid):
    """
    Unit test for deleteSGXHostInfo method.
    """

    mock_logger.return_value = MockLog()
    mock_sessionFactoryObj.return_value = MockSession(output)
    returnval = du.TCSClientDBUtils.deleteSGXHostInfoByPPID(input_ppid)
    if output:
        global testVar
        assert testVar == output
    else:
        assert returnval == output


@pytest.mark.parametrize(
    "output, input_ppid",[
        ('dummy_host', 'dummy_ppid'),
        (None, ''),
        ('exp', 'dummy_ppid')
])
@patch('tcsclient.utils.db_utils.TCSClientDBUtils.getSessionFactoryObj')
@patch('tcsclient.utils.db_utils.logger')
def test_getSGXHostInfo(mock_logger, mock_sessionFactoryObj, output, input_ppid):
    """
    Unit test for getSGXHostInfo method.
    """
     
    mock_logger.return_value = MockLog()
    if output == 'exp':
        mock_sessionFactoryObj.side_effect = Exception('Generic exception')
        res = du.TCSClientDBUtils.getSGXHostInfo(input_ppid)
        assert  res == None
    else:
        mock_sessionFactoryObj.return_value = MockSession(output)
        du.TCSClientDBUtils.getSGXHostInfo(input_ppid)
        global testVar
        assert testVar == output


@pytest.mark.parametrize(
    "output",[
        ('dummy_hosts'),
])
@patch('tcsclient.utils.db_utils.TCSClientDBUtils.getSessionFactoryObj')
@patch('tcsclient.utils.db_utils.logger')
def test_getSGXHostInfoAll(mock_logger, mock_sessionFactoryObj, output):
    """
    Unit test for getSGXHostInfoAll method.
    """

    mock_logger.return_value = MockLog()
    mock_sessionFactoryObj.return_value = MockSession(output)
    du.TCSClientDBUtils.getAllSGXHostInfo()
    global testVar
    assert testVar == output
