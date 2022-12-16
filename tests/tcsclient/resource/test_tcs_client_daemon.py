"""
Copyright (C) 2022 Intel Corporation
SPDX-License-Identifier: BSD-3-Clause
"""
import pytest
import tcsclient.resource.tcs_client_daemon as tcd
import tcsclient.constants as constants
from tcsclient.resource.tcs_client_daemon import TCSClientDaemon
from unittest.mock import patch
from tests.test_common import (
    MockLog, MockResponse, MockThreading, MockEvent, mockConfig
)
from tests.tcsclient.resource.test_tcs_common import (
    MockRegistration, MocksmartConnect, MockDbInstance, MockEventCount
)
import json



@pytest.mark.parametrize(
    "input_daemon, input_lock, output",[
        (None, True, True),
        (None, False, None),
        ("test", False, None)
])
@patch('tcsclient.resource.tcs_client_daemon.TCSClientDaemon.__init__',
       return_value=None)
@patch('tcsclient.resource.tcs_client_daemon.TCSClientDaemon.acquireLock')
def test_getInstance(mock_lock, mock_init, input_daemon, input_lock, output):
    obj = tcd.TCSClientDaemon()
    global daemonIns
    mock_lock.return_value = input_lock
    TCSClientDaemon.daemonInstance = input_daemon
    if output == None:
        assert not obj.getInstance(MockLog(), mockConfig) 
    else:
        daemonIns = obj.getInstance(MockLog(), mockConfig)


@patch('tcsclient.resource.tcs_client_daemon.os.open')
@patch('tcsclient.resource.tcs_client_daemon.fcntl.lockf')
def test_acquireLock(mock_fcntl, mock_open):
    TCSClientDaemon.config = mockConfig
    TCSClientDaemon.__logger = MockLog()
    assert TCSClientDaemon.acquireLock()
    mock_open.side_effect = Exception(IOError)
    with pytest.raises(Exception):
        TCSClientDaemon.acquireLock()

@patch('tcsclient.resource.tcs_client_daemon.os.close')
@patch('tcsclient.resource.tcs_client_daemon.fcntl.lockf')
def test_releaseLock(mock_fcntl, mock_close):
    TCSClientDaemon.config = mockConfig
    TCSClientDaemon.logger = MockLog()
    assert TCSClientDaemon().releaseLock()
    mock_close.side_effect = Exception(IOError)
    with pytest.raises(Exception):
        TCSClientDaemon().releaseLock()


@patch('tcsclient.resource.tcs_client_daemon.threading')
def test_startTimer(mock_threading):
    mockEvent = MockEvent()
    daemonIns.startTimer()


@pytest.mark.parametrize("input_is_set",[(False),(True),])
@patch('tcsclient.resource.tcs_client_daemon.threading')
@patch('tcsclient.resource.tcs_client_daemon.TCSClientDaemon.vCenterAPI')
def test_timerThreadCb(mock_vcenter, mock_threading, input_is_set):
    mockEventCount = MockEventCount(input_is_set)
    mock_threading.side_effect = MockThreading()
    TCSClientDaemon.__config = mockConfig
    daemonIns.__tevent = mockEventCount
    TCSClientDaemon().timerObj = "timer"
    daemonIns.timerThreadCb()
    assert mock_vcenter.called


@patch('tcsclient.resource.tcs_client_daemon.TCSClientDaemon.releaseLock')
def test_releaseResources(mock_releaselock):
    TCSClientDaemon.tevent = MockEvent()
    TCSClientDaemon.timerObj = MockEvent()
    TCSClientDaemon().releaseResources()
    assert mock_releaselock.called


@patch('tcsclient.resource.tcs_client_daemon.requests.post')
def test_registerHost_session_none(mock_request):
    TCSClientDaemon.logger = MockLog()
    TCSClientDaemon.config = mockConfig
    TCSClientDaemon.sessionId = None
    mock_request.return_value.status_code = 400
    mock_request.return_value.json.return_value = 'mock response'
    assert not TCSClientDaemon().registerHost("hostid")
    mock_request.side_effect = Exception()
    assert not TCSClientDaemon().registerHost("hostid")


@patch('tcsclient.resource.tcs_client_daemon.requests.post')
def test_registerHost_session_set(mock_request):
    t1 = TCSClientDaemon()
    t1.logger = MockLog()
    t1.config = mockConfig
    t1.__sessionId = "Test_session"
    mock_request.side_effect = [MockResponse(201), MockResponse(202)]
    assert t1.registerHost("hostid") == 'mocked response'
    mock_request.side_effect = [MockResponse(401),MockResponse(201), MockResponse(202)]
    assert t1.registerHost("hostid") == 'mocked response'
    mock_request.side_effect = [MockResponse(401),MockResponse(201)]
    assert not TCSClientDaemon().registerHost("hostid")
    mock_request.side_effect = [MockResponse(401),MockResponse(200)]
    assert not TCSClientDaemon().registerHost("hostid")
    mock_request.side_effect = [MockResponse(202)]
    assert TCSClientDaemon().registerHost("hostid")
    mock_request.side_effect = Exception()
    assert not TCSClientDaemon().registerHost("hostid")


@patch('tcsclient.resource.tcs_client_daemon.requests.get')
def test_isTaskSuccessful_session_none(mock_get):
    TCSClientDaemon.logger = MockLog()
    assert not TCSClientDaemon().isTaskSuccessful("taskid")
    TCSClientDaemon.__sessionId = "Test_session"
    mock_get.side_effect = [MockResponse(200, {"status": "status"})]
    assert TCSClientDaemon().isTaskSuccessful("taskid")
    mock_get.side_effect = [MockResponse(400)]
    assert not TCSClientDaemon().isTaskSuccessful("taskid")
    mock_get.side_effect = Exception()
    assert not TCSClientDaemon().isTaskSuccessful("hostid")


@patch('tcsclient.resource.tcs_client_daemon.requests.put')
def test_sendToTCS(mock_put):
    TCSClientDaemon.logger = MockLog()
    mock_put.side_effect = [MockResponse(200)]
    assert TCSClientDaemon().sendToTCS("ppid")
    mock_put.side_effect = [MockResponse(400)]
    assert not TCSClientDaemon().sendToTCS("ppid")
    mock_put.side_effect = Exception()
    assert not TCSClientDaemon().sendToTCS("ppid")


@patch('tcsclient.resource.tcs_client_daemon.SmartConnect')
def test_vCenterAPI_error_in_connection(mock_smart_connect):
    mock_smart_connect.side_effect = Exception()
    assert not TCSClientDaemon().vCenterAPI()


# ********* When tdict is not set **********

@pytest.mark.parametrize(
    "input_db_get, input_db_update, input_send_tcs, output_db_updated, output_send_tcs",[
        (None, None, None, False, True),
        (None, None, True, True, True),
        (None, True, True, True, True),
        (MockDbInstance("timezone"), False, False, False, False),
        (MockDbInstance("nottimezone"), False, False, False, True),
        (MockDbInstance("nottimezone"), False, True, True, True),
        (MockDbInstance("nottimezone"), True, True, True, True),
])
@patch('tcsclient.resource.tcs_client_daemon.TCSClientDaemon.sendToTCS')   
@patch('tcsclient.resource.tcs_client_daemon.TCSClientDBUtils.upsertSGXHostInfo')
@patch('tcsclient.resource.tcs_client_daemon.TCSClientDBUtils.getSGXHostInfo')
@patch('tcsclient.resource.tcs_client_daemon.vim')
#@patch('tcsclient.resource.tcs_client_daemon.service_instance.connect')
@patch('tcsclient.resource.tcs_client_daemon.SmartConnect')
def test_vCenterAPI_status_complete(mock_sc, mock_vi, mock_db_get, mock_update, mock_send_tcs,
                                    input_db_get, input_db_update, input_send_tcs,
                                    output_db_updated, output_send_tcs):
    TCSClientDaemon.logger = MockLog()
    TCSClientDaemon.config = mockConfig
    mock_sc.return_value = MocksmartConnect("complete")
    mock_vi.host.SgxInfo.SgxStates = "SGXStates"
    mock_vi.host.SgxRegistrationInfo.RegistrationType = MockRegistration()
    mock_vi.host.SgxRegistrationInfo.RegistrationStatus = MockRegistration()
    mock_db_get.return_value = input_db_get
    mock_update.return_value = input_db_update
    mock_send_tcs.return_value = input_send_tcs
    assert TCSClientDaemon().vCenterAPI()
    assert mock_update.called == output_db_updated
    assert mock_send_tcs.called == output_send_tcs


@patch('tcsclient.resource.tcs_client_daemon.vim')
@patch('tcsclient.resource.tcs_client_daemon.SmartConnect')
def test_vCenterAPI_status_not_applicable(mock_sc, mock_vi):
    TCSClientDaemon.logger = MockLog()
    TCSClientDaemon.config = mockConfig
    mock_sc.return_value = MocksmartConnect("not_applicable")
    mock_vi.host.SgxInfo.SgxStates = "SGXStates"
    mock_vi.host.SgxRegistrationInfo.RegistrationType = MockRegistration()
    mock_vi.host.SgxRegistrationInfo.RegistrationStatus = MockRegistration()
    assert TCSClientDaemon().vCenterAPI()


@patch('tcsclient.resource.tcs_client_daemon.vim')
@patch('tcsclient.resource.tcs_client_daemon.SmartConnect')
def test_vCenterAPI_status_incomplete_manifest_not_equal(mock_sc, mock_vi):
    TCSClientDaemon.logger = MockLog()
    TCSClientDaemon.config = mockConfig
    mock_sc.return_value = MocksmartConnect("incomplete", "different")
    mock_vi.host.SgxInfo.SgxStates = "SGXStates"
    mock_vi.host.SgxRegistrationInfo.RegistrationType = MockRegistration()
    mock_vi.host.SgxRegistrationInfo.RegistrationStatus = MockRegistration()
    assert TCSClientDaemon().vCenterAPI()


@patch('tcsclient.resource.tcs_client_daemon.TCSClientDaemon.registerHost')
@patch('tcsclient.resource.tcs_client_daemon.TCSClientDaemon.completeRegistrtaionSteps')
@patch('tcsclient.resource.tcs_client_daemon.vim')
@patch('tcsclient.resource.tcs_client_daemon.SmartConnect')
def test_vCenterAPI_status_incomplete_manifest_equal_register_host_val_is_0(mock_sc, mock_vi, mock_reg_host,mock_completeRegSteps):
    TCSClientDaemon.logger = MockLog()
    TCSClientDaemon.config = mockConfig
    mock_reg_host.return_value = 0
    mock_completeRegSteps.return_value = 0
    mock_sc.return_value = MocksmartConnect("incomplete", "manifest")
    mock_vi.host.SgxInfo.SgxStates = "SGXStates"
    mock_vi.host.SgxRegistrationInfo.RegistrationType = MockRegistration()
    mock_vi.host.SgxRegistrationInfo.RegistrationStatus = MockRegistration()
    assert TCSClientDaemon().vCenterAPI()

# ********* When tdict is set **********

@patch('tcsclient.resource.tcs_client_daemon.TCSClientDaemon.isTaskSuccessful')
@patch('tcsclient.resource.tcs_client_daemon.time.sleep')
@patch('tcsclient.resource.tcs_client_daemon.TCSClientDaemon.registerHost')
@patch('tcsclient.resource.tcs_client_daemon.vim')
@patch('tcsclient.resource.tcs_client_daemon.SmartConnect')
def test_vCenterAPI_status_tdict_is_set_reg_host_unsuccessful(mock_sc, mock_vi, mock_reg_host,
                                                              mock_sleep, mock_task):
    TCSClientDaemon.logger = MockLog()
    TCSClientDaemon.config = mockConfig
    mock_reg_host.return_value = 1
    mock_task.return_value = "test successful"
    mock_sc.return_value = MocksmartConnect("incomplete", "manifest")
    mock_vi.host.SgxInfo.SgxStates = "SGXStates"
    mock_vi.host.SgxRegistrationInfo.RegistrationType = MockRegistration()
    mock_vi.host.SgxRegistrationInfo.RegistrationStatus = MockRegistration()
    assert TCSClientDaemon().vCenterAPI()


@pytest.mark.parametrize(
    "input_db_update, input_send_tcs, output_db_updated, output_send_tcs",[
        (None, None, False, True),
        (None, True, True, True),
        (True, True, True, True),
])
@patch('tcsclient.resource.tcs_client_daemon.TCSClientDaemon.sendToTCS')   
@patch('tcsclient.resource.tcs_client_daemon.TCSClientDBUtils.upsertSGXHostInfo')
@patch('tcsclient.resource.tcs_client_daemon.TCSClientDaemon.isTaskSuccessful')
@patch('tcsclient.resource.tcs_client_daemon.time.sleep')
@patch('tcsclient.resource.tcs_client_daemon.TCSClientDaemon.registerHost')
@patch('tcsclient.resource.tcs_client_daemon.vim')
@patch('tcsclient.resource.tcs_client_daemon.SmartConnect')
def test_vCenterAPI_status_tdict_is_set_reg_host_unsuccessful(mock_sc, mock_vi, mock_reg_host, mock_sleep, mock_task,
                                                              mock_update, mock_send_tcs, input_db_update,
                                                              input_send_tcs, output_db_updated, output_send_tcs):
    TCSClientDaemon.logger = MockLog()
    TCSClientDaemon.config = mockConfig
    mock_task.return_value = constants.SUCCESS_STATUS
    mock_reg_host.return_value = 1
    mock_sc.return_value = MocksmartConnect("incomplete", "manifest")
    mock_update.return_value = input_db_update
    mock_send_tcs.return_value = input_send_tcs
    mock_vi.host.SgxInfo.SgxStates = "SGXStates"
    mock_vi.host.SgxRegistrationInfo.RegistrationType = MockRegistration()
    mock_vi.host.SgxRegistrationInfo.RegistrationStatus = MockRegistration()
    assert TCSClientDaemon().vCenterAPI()
    assert mock_update.called == output_db_updated
    assert mock_send_tcs.called == output_send_tcs
