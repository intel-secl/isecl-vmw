"""
Copyright (C) 2022 Intel Corporation
SPDX-License-Identifier: BSD-3-Clause

"""

import string
import random 

class MockLog:
    def info(self, log, err=None):
        return None
    
    def error(self, log, err=None):
        return None

    def debug(self, log, err=None):
        return None

    def warn(self, log, err=None):
        return None

class MockResponse:
    def __init__(self, status_code, json_data="mocked response"):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data

class MockThreading:
    def Timer(self, a, b):
        return None
    def start(self):
        return None
    def join(self):
        return None

class MockEvent:
    def Event(self):
        return None
    def Thread(self, target):
        return None
    def start():
        return None
    def set(self):
        return None
    def cancel(self):
        return None

class MockPythonLogger:
      propagate=True
      @staticmethod
      def getLogger(name=None):
          return MockPythonLogger()
      def setLevel(self, level):
          return None
      def addHandler(self, handler):
          return None
      def setFormatter(self, formater):
          return None

mockConfig = {
    "tcsClient": {
        "adminName": "user",
        "adminPassword": random.choices(string.ascii_uppercase + string.digits, k=5),
        "regURL": "url",
        "clientDb": {
            "db": "name",
            "host": "host",
            "user": "user",
        },
        "lockfile": "./test_path/lock.file",
        "logLevel": "info",
        "reqURL": "url",
        "sessionURL": "session_url",
        "taskURL": "task_url",
        "tcsURL": "tcs_url",
        "timerInterval": 300,
        "vCenterIP": "ip",
        "vCenterPort": "port",
        "version": "'0.1'",
    }
}
