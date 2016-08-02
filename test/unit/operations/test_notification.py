import unittest
from ncclient.operations.subscribe import Notification, NotificationType
from lxml import etree
from datetime import datetime
from dateutil.parser import parse
from ncclient.operations.util import *
# from ncclient.operations.rpc import *
# from ncclient.xml_ import *
# from xml.etree.ElementTree import *

from ncclient.manager import Manager
from ncclient.transport import Session

NETCONF_CONFIG_CHANGE = """
<?xml version="1.0" encoding="UTF-8"?>
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
<?xml version="1.0" encoding="UTF-8"?>
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
<?xml version="1.0" encoding="UTF-8"?>
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
<?xml version="1.0" encoding="UTF-8"?>
<netconf-session-end xmlns='urn:ietf:params:xml:ns:yang:ietf-netconf-notifications'>
	<username>admin</username>
	<session-id>124</session-id>
	<source-host>127.0.0.1</source-host>
	<termination-reason>dropped</termination-reason>
</netconf-session-end>
"""

REPLAY_COMPLETE = """
<?xml version="1.0" encoding="UTF-8"?>
<notification xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0">
	<eventTime>2016-07-29T14:28:25.793194-07:00</eventTime>
	<replayComplete xmlns="urn:ietf:params:xml:ns:netmod:notification"/>
</notification>
"""

REPLAY_COMPLETE_DATA = """
<?xml version="1.0" encoding="UTF-8"?>
<replayComplete xmlns="urn:ietf:params:xml:ns:netmod:notification"/>
"""

NOTIFICATION_COMPLETE = """
<?xml version="1.0" encoding="UTF-8"?>
<notification xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0">
	<eventTime>2016-07-29T14:28:25.793421-07:00</eventTime>
	<notificationComplete xmlns="urn:ietf:params:xml:ns:netmod:notification"/>
</notification>
"""

NOTIFICATION_COMPLETE_DATA = """
<?xml version="1.0" encoding="UTF-8"?>
<notificationComplete xmlns="urn:ietf:params:xml:ns:netmod:notification"/>
"""

def normalize_xml(xml):
	parser = etree.XMLParser(recover=True, remove_blank_text=True)
	if type(xml) is not str:
		xml = etree.tostring(xml)
	return etree.tostring(etree.fromstring(xml, parser=parser))

class TestNotification(unittest.TestCase):

	@classmethod
	def setUpClass(self):
		self.notifications = [Notification(NETCONF_CONFIG_CHANGE), Notification(NETCONF_SESSION_END),
								Notification(REPLAY_COMPLETE), Notification(NOTIFICATION_COMPLETE)]

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

if __name__ == '__main__':
    unittest.main()