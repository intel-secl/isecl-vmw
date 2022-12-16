class MockEventCount:
    def __init__(self, input_is_set=True):
        self.input_is_set = input_is_set
        self.count = 0

    def is_set(self):
        if self.count > 0:
            return True
        self.count += 1
        return self.input_is_set

class MockDbInstance:
    def __init__(self, registered_time=None):
        self.registered_time = registered_time

class MockRegistration:
    def __init__(self):
        self.manifest="manifest"
        self.notApplicable="not_applicable"
        self.complete="complete"
        self.incomplete="incomplete"

class MockTime:
    def replace(self, tzinfo):
        return "timezone"

class MockregistrationInfo:
    def __init__(self, status, types=None):
        self.status = status
        self.type = types
        self.lastRegisteredTime = MockTime()
        self.ppid = status

class MocksgxInfo:
    def __init__(self, status, types=None):
        self.registrationInfo = MockregistrationInfo(status, types)
        self.lastRegisteredTime = status

class MockHardware:
    def __init__(self, status, types=None):
        self.sgxInfo = MocksgxInfo(status, types)

class MockHost:
    def __init__(self,  status, name, types=None):
        self._moId = name
        self.name = name
        self.hardware = MockHardware(status, types)

class MockClusterHost:
    def __init__(self, name, host, status, types=None):
        self.name = name
        self.status = status
        if host:
            self.host = [MockHost(status, name, types)]
class MockhostFolder:
    def __init__(self, hostFolder):
        self.hostFolder = hostFolder

class MockchildEntity:
    def __init__(self, childEntity):
        self.childEntity = childEntity

class MockRootFolder:
    def __init__(self, rootFolder):
        self.rootFolder = rootFolder

class MocksmartConnect:
    def __init__(self, status, types=None):
        self.count = 0
        self.status = status
        self.types = types
        return None

    def RetrieveContent(self):
        return MockRootFolder(MockchildEntity([MockhostFolder(MockchildEntity(
            [MockClusterHost(name="cluster1", host="cluster1", status=self.status, types=self.types)]))]))
