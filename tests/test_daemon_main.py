"""
Copyright (C) 2022 Intel Corporation
SPDX-License-Identifier: BSD-3-Clause

"""
import pytest
import daemon_main
from unittest.mock import patch
from tests.test_common import (
    MockLog
)


test_value = ""


@patch('daemon_main.parseCommandlineArgs')
def test_main(mock_parse):
    def throw_error():
        raise Exception()
    # Without exception
    daemon_main.main()
    assert mock_parse.called


@patch('daemon_main.deamonIns.releaseResources')
@patch('daemon_main.deamonIns', return_value="test")
@patch('daemon_main.sys.exit')
def test_exitTCSClientDaemon(mock_exit, mock_daemon_ins, mock_daemon_ins_work):
    def daemonInsResources():
        global test_value
        test_value = "release Resources called"
    # Patches value of daemon_main.deamonIns and checks if it has been called
    mock_daemon_ins_work.side_effect = daemonInsResources()
    global test_value
    daemon_main.exitTCSClientDaemon(1)
    assert mock_exit.called
    assert test_value == "release Resources called"

class MockRun:
      returncode=-1
      def __init__(self, status):
          returncode=status

@pytest.mark.parametrize(
    "input", [
        (1),
        (0)
])
@patch('daemon_main.run')
@patch('daemon_main.logger')
@patch('daemon_main.exitTCSClientDaemon')
def test_startTCSClientDaemon(mock_exit, mock_log, mock_run, input):
    mock_run.return_value=MockRun(input)
    mock_log.return_value=MockLog()
    daemon_main.startTCSClientDaemon()
    assert mock_exit.called

@pytest.mark.parametrize(
    "input", [
        (1),
        (0)
])
@patch('daemon_main.run')
@patch('daemon_main.logger')
@patch('daemon_main.exitTCSClientDaemon')
def test_statusTCSClientDaemon(mock_exit, mock_log, mock_run, input):
    mock_run.return_value=MockRun(input)
    mock_log.return_value=MockLog()
    daemon_main.statusTCSClientDaemon()
    assert mock_exit.called


@pytest.mark.parametrize(
    "input", [
        (1),
        (0)
])
@patch('daemon_main.run')
@patch('daemon_main.logger')
@patch('daemon_main.exitTCSClientDaemon')
def test_stopTCSClientDaemon(mock_exit, mock_log, mock_run, input):
    mock_run.return_value=MockRun(input)
    mock_log.return_value=MockLog()
    daemon_main.stopTCSClientDaemon()
    assert mock_exit.called

@patch('daemon_main.logger')
@patch('daemon_main.exitTCSClientDaemon')
def test_deamonSignalHandler(mock_exit, mock_log):
    daemon_main.deamonSignalHandler("test", "test")
    assert mock_exit.called


@patch('daemon_main.exitTCSClientDaemon')
def test_displayHelpMsgAndExit(mock_exit):
    daemon_main.displayHelpMsgAndExit()
    assert mock_exit.called


@patch('daemon_main.config')
@patch('daemon_main.logger')
@patch('daemon_main.exitTCSClientDaemon')
def test_displayDaemonVersion(mock_exit, mock_log, mock_config):
    config = dict()
    config['tcsDaemon'] = dict()
    config['tcsDaemon']['version'] = 'version'
    mock_config.return_value = config
    daemon_main.displayDaemonVersion()
    assert mock_exit.called

class MockSignal:
      def signal(self, val1, val2):
          return None
      def pause(self):
          return None

class MockTCSClientDaemon:
      def startTimer(self):
          global test_value
          test_value = "signal received"
          return None

@pytest.mark.parametrize(
    "input", [
        (None),
        (MockTCSClientDaemon())
])
@patch('daemon_main.signal')
@patch('daemon_main.config')
@patch('daemon_main.logger')
@patch('daemon_main.exitTCSClientDaemon')
@patch('daemon_main.TCSClientDaemon.getInstance')
def test_runTCSClientDaemon(mock_instance, mock_exit, mock_log, mock_config, mock_signal, input):
    config = dict()
    config['tcsDaemon'] = dict()
    config['tcsDaemon']['version'] = 'version'
    mock_config.return_value = config
    mock_instance.return_value = input
    mock_signal.return_value = MockSignal()
    daemon_main.runTCSClientDaemon()
    if daemon_main.deamonIns == None:
       assert mock_exit.called
    else:
       global test_value
       assert test_value == "signal received"
    

@pytest.mark.parametrize(
    "cmdInput", [
        (['app', '-h']),
        (['app', '-s']),
        (['app', '-r']),
        (['app', '-t']),
        (['app', '-u']),
        (['app', '-v']),
        (['app', '-f']),
        (['app', '-z']),
        (['-z'])
])
@patch('daemon_main.displayDaemonVersion')
@patch('daemon_main.statusTCSClientDaemon')
@patch('daemon_main.uninstallTCSClientDaemon')
@patch('daemon_main.stopTCSClientDaemon')
@patch('daemon_main.runTCSClientDaemon')
@patch('daemon_main.startTCSClientDaemon')
@patch('daemon_main.displayHelpMsgAndExit')
@patch('daemon_main.getSysArgument')
@patch('daemon_main.config')
@patch('daemon_main.logger')
def test_parseCommandlineArgs(mock_log, mock_config, mock_sysarg, mock_display, mock_start, mock_run, mock_stop, mock_uninstall, mock_status, mock_version, cmdInput):
    def throw_error():
        raise Exception()
    # Without exception
    config = dict()
    mock_config.return_value = config
    mock_sysarg.return_value=cmdInput
    daemon_main.parseCommandlineArgs()
    if '-h' in cmdInput:
        assert mock_display.called
    if cmdInput == '-s':
        assert mock_start.called
    if cmdInput == '-r':
        assert mock_run.called
    if cmdInput == '-u':
        assert mock_uninstall.called
    if cmdInput == '-v':
        assert mock_version.called
    if cmdInput == '-f':
        assert mock_status.called
    if len(cmdInput) < 2:
        assert mock_display.called

