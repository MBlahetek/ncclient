import unittest
from ncclient import manager
from ncclient.operations.subscribe import Notification, NotificationType
from lxml import etree
from dateutil.parser import parse
from ncclient.operations.util import *

NETCONF_CONFIG_CHANGE = """
<notification xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0">
    <eventTime>2016-08-02T10:40:40.014291-07:00</eventTime>
    <netconf-config-change xmlns='urn:ietf:params:xml:ns:yang:ietf-netconf-notifications'>
        <changed-by>
            <username>admin</username>
            <session-id>32</session-id>
            <source-host>127.0.0.1</source-host>
        </changed-by>
        <datastore>running</datastore>
        <edit>
            <target xmlns:ncs="http://tail-f.com/ns/ncs">/ncs:devices/ncs:device[ncs:name='ToR2']</target>
            <operation>delete</operation>
        </edit>
    </netconf-config-change>
</notification>
"""

NETCONF_CONFIG_CHANGE_DATA = """
<netconf-config-change xmlns='urn:ietf:params:xml:ns:yang:ietf-netconf-notifications'>
    <changed-by>
        <username>admin</username>
        <session-id>32</session-id>
        <source-host>127.0.0.1</source-host>
    </changed-by>
    <datastore>running</datastore>
    <edit>
    <target xmlns:ncs="http://tail-f.com/ns/ncs">/ncs:devices/ncs:device[ncs:name='ToR2']</target>
    <operation>delete</operation>
    </edit>
</netconf-config-change>
"""

NETCONF_SESSION_END = """
<notification xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0">
    <eventTime>2016-07-29T14:26:58.519605-07:00</eventTime>
    <netconf-session-end xmlns='urn:ietf:params:xml:ns:yang:ietf-netconf-notifications'>
        <username>admin</username>
        <session-id>124</session-id>
        <source-host>127.0.0.1</source-host>
        <termination-reason>dropped</termination-reason>
    </netconf-session-end>
</notification>
"""

NETCONF_SESSION_END_DATA = """
<netconf-session-end xmlns='urn:ietf:params:xml:ns:yang:ietf-netconf-notifications'>
    <username>admin</username>
    <session-id>124</session-id>
    <source-host>127.0.0.1</source-host>
    <termination-reason>dropped</termination-reason>
</netconf-session-end>
"""

REPLAY_COMPLETE = """
<notification xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0">
    <eventTime>2016-07-29T14:28:25.793194-07:00</eventTime>
    <replayComplete xmlns="urn:ietf:params:xml:ns:netmod:notification"/>
</notification>
"""

REPLAY_COMPLETE_DATA = """
<replayComplete xmlns="urn:ietf:params:xml:ns:netmod:notification"/>
"""

NOTIFICATION_COMPLETE = """
<notification xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0">
    <eventTime>2016-07-29T14:28:25.793421-07:00</eventTime>
    <notificationComplete xmlns="urn:ietf:params:xml:ns:netmod:notification"/>
</notification>
"""

NOTIFICATION_COMPLETE_DATA = """
<notificationComplete xmlns="urn:ietf:params:xml:ns:netmod:notification"/>
"""

INVALID = """
<notification xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0">
    <replayComplete xmlns="urn:ietf:params:xml:ns:netmod:notification"/>
</notification>
"""

def normalize_xml(xml):
    parser = etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8', remove_blank_text=True)
    element = etree.fromstring(xml, parser=parser)
    if type(xml) is not str:
        xml = etree.tostring(xml)
    return etree.tostring(element)

class TestNotification(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.notifications = [Notification(NETCONF_CONFIG_CHANGE), Notification(NETCONF_SESSION_END),
        Notification(REPLAY_COMPLETE), Notification(NOTIFICATION_COMPLETE)]
        self.valid = [Notification(NETCONF_CONFIG_CHANGE), Notification(NETCONF_SESSION_END),
        Notification(REPLAY_COMPLETE), Notification(NOTIFICATION_COMPLETE),
        Notification(INVALID)]

    def test_Notification_xml(self):
        xml = [NETCONF_CONFIG_CHANGE, NETCONF_SESSION_END, REPLAY_COMPLETE, NOTIFICATION_COMPLETE]
        for (actual, expected) in zip(self.notifications, xml):
            self.assertEquals(normalize_xml(actual.xml), normalize_xml(expected))

    def test_Notification_eventtime(self):
        datetimes = [parse('2016-08-02T10:40:40.014291-07:00').isoformat(),
        parse('2016-07-29T14:26:58.519605-07:00').isoformat(),
        parse('2016-07-29T14:28:25.793194-07:00').isoformat(),
        parse('2016-07-29T14:28:25.793421-07:00').isoformat()]
        for (actual, expected) in zip(self.notifications, datetimes):
            self.assertEquals(actual.eventTime.isoformat(), expected)

    def test_Notification_type(self):
        types = [NotificationType.NETCONF_CONFIG_CHANGE, NotificationType.NETCONF_SESSION_END,
        NotificationType.REPLAY_COMPLETE, NotificationType.NOTIFICATION_COMPLETE]
        for (actual, expected) in zip(self.notifications, types):
            self.assertEquals(actual.type, expected)

    def test_Notification_data_ele(self):
        data_ele = [to_ele(NETCONF_CONFIG_CHANGE_DATA), to_ele(NETCONF_SESSION_END_DATA),
        to_ele(REPLAY_COMPLETE_DATA), to_ele(NOTIFICATION_COMPLETE_DATA)]
        for (actual, expected) in zip(self.notifications, data_ele):
            self.assertEquals(normalize_xml(actual.data_ele), normalize_xml(expected))

    def test_Notification_data_xml(self):
        data_xml = [NETCONF_CONFIG_CHANGE_DATA, NETCONF_SESSION_END_DATA,
        REPLAY_COMPLETE_DATA, NOTIFICATION_COMPLETE_DATA]
        for (actual, expected) in zip(self.notifications, data_xml):
            self.assertEquals(normalize_xml(actual.data_xml), normalize_xml(expected))

    def test_Notification_connected(self):
        connected = [True, False, True, True]
        for (actual, expected) in zip(self.notifications, connected):
            self.assertEquals(actual.connected, expected)

    def test_Notification_invalid(self):
        invalid = [False, False, False, False, True]
        for (actual, expected) in zip(self.valid, invalid):
            self.assertEquals(actual.invalid, expected)

if __name__ == '__main__':
    unittest.main()