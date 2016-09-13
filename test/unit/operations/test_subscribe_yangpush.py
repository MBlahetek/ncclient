import unittest
try:
    from mock import patch
except ImportError:
    from unittest.mock import patch

from ncclient.operations.rpc import *
from ncclient import manager
from ncclient.operations.subscribe_yangpush import EstablishSubscription, YangPushNotificationListener
from ncclient.manager import Manager
from ncclient.transport import Session

from datetime import datetime
from lxml import etree
from dateutil.parser import parse

SUBSCRIBE_DEFAULT = """
<ns0:establish-subscription xmlns:ns0="urn:ietf:params:xml:ns:yang:ietf-yang-push:1.0">
"""

SUBSCRIBE_STREAM = """
<ns0:establish-subscription xmlns:ns0="urn:ietf:params:xml:ns:yang:ietf-yang-push:1.0">
    <stream>push-update</stream>
</ns0:establish-subscription>
"""

SUBSCRIBE_START = """
<ns0:establish-subscription xmlns:ns0="urn:ietf:params:xml:ns:yang:ietf-yang-push:1.0">
    <startTime>2016-08-01T13:28:57.740194Z</startTime>
</ns0:establish-subscription>
"""

SUBSCRIBE_STOP = """
<ns0:establish-subscription xmlns:ns0="urn:ietf:params:xml:ns:yang:ietf-yang-push:1.0">
    <startTime>2016-08-01T13:28:57.740194Z</startTime>
    <stopTime>2016-08-01T13:28:59.740208Z</stopTime>
</ns0:establish-subscription>
"""

def callback(notification): pass

def errback(notification): pass

def normalize_xml(xml):
    parser = etree.XMLParser(recover=True, remove_blank_text=True)
    if type(xml) is not str:
        xml = etree.tostring(xml)
    return etree.tostring(etree.fromstring(xml, parser=parser))

class TestEstablishSubscription(unittest.TestCase):

    def setUp(self):
        self.m = Manager(Session(None), None)

if __name__ == '__main__':
    unittest.main()