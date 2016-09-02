import unittest
from mock import patch
from ncclient.operations.rpc import *
from ncclient import manager
from ncclient.operations.subscribe import CreateSubscription, NotificationListener
from datetime import datetime
from lxml import etree
from dateutil.parser import parse
from ncclient.manager import Manager
from ncclient.transport import Session

SUBSCRIBE_DEFAULT = """
<ns0:create-subscription xmlns:ns0="urn:ietf:params:xml:ns:netconf:notification:1.0"/>
"""

SUBSCRIBE_STREAM = """
<ns0:create-subscription xmlns:ns0="urn:ietf:params:xml:ns:netconf:notification:1.0">
    <nc:stream xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">ncs-events</nc:stream>
</ns0:create-subscription>
"""

SUBSCRIBE_FILTER_XPATH = """
<ns0:create-subscription xmlns:ns0="urn:ietf:params:xml:ns:netconf:notification:1.0">
    <nc:filter xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" type="xpath" select="/devices/device/name"/>
</ns0:create-subscription>"""

SUBSCRIBE_FILTER_SUBTREE = """
<ns0:create-subscription xmlns:ns0="urn:ietf:params:xml:ns:netconf:notification:1.0">
    <nc:filter xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" type="subtree">
        <ns0:devices xmlns:ns0="http://tail-f.com/ns/ncs"><device><name/></device></ns0:devices>
    </nc:filter>
</ns0:create-subscription>"""

SUBSCRIBE_FILTER_STRING = """
<ns0:create-subscription xmlns:ns0="urn:ietf:params:xml:ns:netconf:notification:1.0">
    <nc:filter xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" type="subtree">
        <devices xmlns="http://tail-f.com/ns/ncs"><device><name/></device></devices>
    </nc:filter>
</ns0:create-subscription>"""

SUBSCRIBE_START = """
<ns0:create-subscription xmlns:ns0="urn:ietf:params:xml:ns:netconf:notification:1.0">
    <startTime>2016-08-01T13:28:57.740194Z</startTime>
</ns0:create-subscription>
"""

SUBSCRIBE_STOP = """
<ns0:create-subscription xmlns:ns0="urn:ietf:params:xml:ns:netconf:notification:1.0">
    <startTime>2016-08-01T13:28:57.740194Z</startTime>
    <stopTime>2016-08-01T13:28:59.740208Z</stopTime>
</ns0:create-subscription>
"""

def callback(notification): pass

def errback(notification): pass

def normalize_xml(xml):
    parser = etree.XMLParser(recover=True, remove_blank_text=True)
    if type(xml) is not str:
        xml = etree.tostring(xml)
    return etree.tostring(etree.fromstring(xml, parser=parser))

class TestCreateSubscription(unittest.TestCase):

    def setUp(self):
        self.m = Manager(Session(None), None)

    @patch('ncclient.operations.rpc.RPC._request')
    @patch('ncclient.transport.Session.add_listener')
    def test_CreateSubscription_add_listener(self, mock_add_listener, mock_request):
        self.m.create_subscription(callback, errback)
        mock_add_listener.assert_called()
        self.assertEquals(type(mock_add_listener.call_args[0][0]), NotificationListener)

    @patch('ncclient.operations.rpc.RPC._request')
    def test_CreateSubscription_callback(self, mock_subscribe):
        with self.assertRaises(Exception):
            self.m.create_subscription(None, errback)

    @patch('ncclient.operations.rpc.RPC._request')
    def test_CreateSubscription_errback(self, mock_subscribe):
        with self.assertRaises(Exception):
            self.m.create_subscription(callback, None)

    @patch('ncclient.operations.rpc.RPC._request')
    def test_CreateSubscription_default(self, mock_subscribe):
        self.m.create_subscription(callback, errback)
        actual = normalize_xml(mock_subscribe.call_args[0][0])
        expected = normalize_xml(SUBSCRIBE_DEFAULT)
        self.assertEquals(actual, expected)

    @patch('ncclient.operations.rpc.RPC._request')
    def test_CreateSubscription_stream(self, mock_subscribe):
        self.m.create_subscription(callback, errback,
        stream='ncs-events')
        actual = normalize_xml(mock_subscribe.call_args[0][0])
        expected = normalize_xml(SUBSCRIBE_STREAM)
        self.assertEquals(actual, expected)

    @patch('ncclient.operations.rpc.RPC._request')
    def test_CreateSubscription_xpath_filter(self, mock_subscribe):
        self.m.create_subscription(callback, errback,
        filter=('xpath', '/devices/device/name'))
        actual = normalize_xml(mock_subscribe.call_args[0][0])
        expected = normalize_xml(SUBSCRIBE_FILTER_XPATH)
        self.assertEquals(actual, expected)

    @patch('ncclient.operations.rpc.RPC._request')
    def test_CreateSubscription_subtree_filter(self, mock_subscribe):
        devices_filter = etree.Element(qualify('devices', "http://tail-f.com/ns/ncs"))
        device_filter = etree.Element('device')
        devices_filter.append(device_filter)
        device_filter.append(etree.Element('name'))
        self.m.create_subscription(callback, errback,
        filter=('subtree', devices_filter))
        actual = normalize_xml(mock_subscribe.call_args[0][0])
        expected = normalize_xml(SUBSCRIBE_FILTER_SUBTREE)
        self.assertEquals(actual, expected)

    @patch('ncclient.operations.rpc.RPC._request')
    def test_CreateSubscription_string_filter(self, mock_subscribe):
        devices_filter = """
        <devices xmlns="http://tail-f.com/ns/ncs">
            <device>
                <name/>
            </device>
        </devices>
        """
        self.m.create_subscription(callback, errback,
        filter=('subtree', devices_filter))
        actual = normalize_xml(mock_subscribe.call_args[0][0])
        expected = normalize_xml(SUBSCRIBE_FILTER_STRING)
        self.assertEquals(actual, expected)

    @patch('ncclient.operations.rpc.RPC._request')
    def test_CreateSubscription_start_time(self, mock_subscribe):
        start_time = parse('2016-08-01T13:28:57.740194')
        self.m.create_subscription(callback, errback,
        start_time=start_time)
        actual = normalize_xml(mock_subscribe.call_args[0][0])
        expected = normalize_xml(SUBSCRIBE_START)
        self.assertEquals(actual, expected)

    @patch('ncclient.operations.rpc.RPC._request')
    def test_CreateSubscription_invalid_start_time(self, mock_subscribe):
        with self.assertRaises(TypeError):
            self.m.create_subscription(callback, errback, start_time="")

    @patch('ncclient.operations.rpc.RPC._request')
    def test_CreateSubscription_stop_time(self, mock_subscribe):
        start_time = parse('2016-08-01T13:28:57.740194')
        stop_time = parse('2016-08-01T13:28:59.740208')
        self.m.create_subscription(callback, errback,
        start_time=start_time, stop_time=stop_time)
        actual = normalize_xml(mock_subscribe.call_args[0][0])
        expected = normalize_xml(SUBSCRIBE_STOP)
        self.assertEquals(actual, expected)

    @patch('ncclient.operations.rpc.RPC._request')
    def test_CreateSubscription_invalid_stop_time(self, mock_subscribe):
        with self.assertRaises(TypeError):
            self.m.create_subscription(callback, errback, stop_time="")

if __name__ == '__main__':
    unittest.main()