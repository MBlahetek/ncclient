import time
import unittest
from ncclient.operations.subscribe import *
from mock import patch
from datetime import datetime, timedelta
from ncclient.operations.rpc import *
from ncclient.xml_ import *
from xml.etree.ElementTree import *
from ncclient import manager

SET = """<config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
<devices xmlns="http://tail-f.com/ns/ncs">
<device xc:operation="create"><name>ToR2</name><address>1.3.3.7</address>
<port>10023</port><ssh><host-key><algorithm>ssh-dss</algorithm><key-data>AAAAB3NzaC1kc3MAAACBAN79ur5pT8cJ6N+XOJsIr/qpUnSBNoQqUVNwx3KgAmkmxLYJb/cB
w18grvzQmAFrJoAJx2gRU1ujDf0aboS+GKQsGyqT8SLPutMc5XX5cJDBs8cSlae2v6FuHL0e
YEuv+fce+MbkOTz0oBxPqDGazFVm9WHutroJ5VcMO84HHnpbAAAAFQC3m8RQvYDAFWIClV96
NM1WcZz4JQAAAIA9OM4gy7UCeUbkDFqbzN3nDbxtlRhycY8CYKkd0B1AsnOVOFRjE78dCckQ
08cDYgZ9FTRLXN3Agvr0GepnMkrUY2C49qoJsv0vTBLCdYMNrxPDapCzDEbxgxRrzbLBOFe1
aPq7uxRVy0vMD9BGcs/dPGCrtEi5QtPFu+OAcG9i9wAAAIAaaB8UtHmYqUx/dSQFnEGNPiha
rUTPqywUd583MeqkkVh/eldmlTBD9bFxVe+aa7WtxtrJNFxDNR6QXkPy7JHcIRkWLh1Skm4n
KQlmLRtWx0lLs7igKL28ZiN+Pg/TQc/6WXzz+5QlR/c0TSXx1b/lcE8VBDE2sHAriIvsW/bl
cw==</key-data></host-key></ssh><authgroup>default</authgroup><device-type>
<cli><ned-id xmlns:cisco-nx-id="http://tail-f.com/ned/cisco-nx-id">cisco-nx-id:cisco-nx</ned-id></cli></device-type><state><admin-state>unlocked</admin-state></state>
</device></devices></config>"""

RESET = """<config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
<devices xmlns="http://tail-f.com/ns/ncs">
<device xc:operation="delete"><name>ToR2</name><address>1.3.3.7</address>
</device></devices></config>"""

SUBSCRIBE_DEFAULT = """<ns0:create-subscription xmlns:ns0="urn:ietf:params:xml:ns:netconf:notification:1.0" />"""

def connect_cisco_vts():
	return manager.connect(host="127.0.0.1", port=2022,
			username="admin", password="admin",
			hostkey_verify=False, look_for_keys=False,
			allow_agent=False)

class TestCreateSubscription(unittest.TestCase):

	def setUp(self):
		self.result = {"create": None, "delete": None}
		self.m = connect_cisco_vts()

	def tearDown(self):
		self.m.close_session()

	@patch('ncclient.operations.rpc.RPC._request')
	@patch('ncclient.transport.Session.add_listener')
	def test_CreateSubscription_add_listener(self, mock_listen, mock_subscribe):
		def callback(notification):
			pass
		def errback(notification):
			pass
		self.m.create_subscription(callback, errback)
		mock_listen.assert_called()
		self.assertEquals(type(mock_listen.call_args[0][0]), NotificationListener)

	@patch('ncclient.operations.rpc.RPC._request')
	def test_CreateSubscription_default(self, mock_subscribe):
		def callback(notification):
			pass
		def errback(notification):
			pass
		self.m.create_subscription(callback, errback)
		self.assertEquals(tostring(mock_subscribe.call_args[0][0]), SUBSCRIBE_DEFAULT)

	# def test(self):
	# 	def callback(notification):
	# 		print notification
	# 	session = connect_cisco_vts()
	# 	subscribed_session = connect_cisco_vts()
	# 	# print type(session.get_config("running", filter=('xpath', '/devices/device')))
	# 	subscribed_session.create_subscription(callback)
	# 	session.edit_config(target='running', config=SET)
	# 	session.edit_config(target='running', config=RESET)
	# 	subscribed_session.close_session()
	# 	session.close_session()

	# def test_subscribe_ok(self):
	# 	subscribed_session = connect_cisco_vts()		
	# 	subcription = subscribed_session.create_subscription(None)
	# 	subcription.parse()
	# 	self.assertTrue(subcription.ok)
	# 	self.assertFalse(subcription.error)
	# 	subscribed_session.close_session()

	# def test_notification_filter(self):
	# 	def callback(notification):
	# 		operation = fromstring(notification).find(
	# 				'.//{urn:ietf:params:xml:ns:yang:ietf-netconf-notifications}operation')
	# 		self.result[operation.text] = notification
	# 		print notification

	# 	update_session = connect_cisco_vts()
	# 	subscribed_session = connect_cisco_vts()
	# 	filter = ('xpath', '/netconf-config-change/edit/operation[text()=\'create\']')
	# 	subscribed_session.create_subscription(subscribed_session, callback,
	# 		filter=filter)
	# 	update_session.edit_config(target='running', config=CREATE)
	# 	# time.sleep(1)
	# 	update_session.edit_config(target='running', config=DELETE)
	# 	# time.sleep(1)

	# 	self.assertFalse(self.result["create"] == None)
	# 	self.assertTrue(self.result["delete"] == None)

	# 	subscribed_session.close_session()
	# 	update_session.close_session()

	# def test_notification_stream(self):
	# 	self.assertFalse(True)

	# def test_notification_start_time(self):
	# 	def callback(notification):
	# 		operation = fromstring(notification).find(
	# 				'.//{urn:ietf:params:xml:ns:yang:ietf-netconf-notifications}operation')
	# 		self.result[operation.text] = notification
	# 		print notification

	# 	update_session = connect_cisco_vts()
	# 	subscribed_session = connect_cisco_vts()

	# 	update_session.edit_config(target='running', config=CREATE)
	# 	time.sleep(1)
	# 	start_time = datetime.now() - timedelta(seconds=100)
	# 	time.sleep(1)
	# 	update_session.edit_config(target='running', config=DELETE)

	# 	subscribed_session.create_subscription(subscribed_session, callback, start_time=start_time)

	# 	self.assertTrue(self.result["create"] == None)
	# 	self.assertFalse(self.result["delete"] == None)

	# 	subscribed_session.close_session()
	# 	update_session.close_session()

	# def test_notification_stop_time_valid(self):
	# 	with self.assertRaises(RPCError):
	# 		subscribed_session = connect_cisco_vts()
	# 		stop_time = datetime.now()
	# 		subscribed_session.create_subscription(subscribed_session, None,
	# 			stop_time=stop_time)
	# 		# more assertions look into RPCError w/ try:
	# 		subscribed_session.close_session()

	# 	with self.assertRaises(RPCError):
	# 		subscribed_session = connect_cisco_vts()
	# 		stop_time = datetime.now()
	# 		start_time = datetime(stop_time.year + 1, stop_time.month, stop_time.day,
	# 			stop_time.hour, stop_time.minute, stop_time.second)
	# 		subscribed_session.create_subscription(subscribed_session, None,
	# 			start_time=start_time, stop_time=stop_time)
	# 		# more assertions look into RPCError w/ try:
	# 		subscribed_session.close_session()

	# def test_notification_stop_time(self):
	# 	def callback(notification):
	# 		operation = fromstring(notification).find(
	# 				'.//{urn:ietf:params:xml:ns:yang:ietf-netconf-notifications}operation')
	# 		self.result[operation.text] = notification

	# 	update_session = connect_cisco_vts()
	# 	subscribed_session = connect_cisco_vts()

	# 	time.sleep(1)
	# 	currenttime = datetime.now()
	# 	start_time = currenttime - timedelta(seconds=1)
	# 	stop_time = currenttime + timedelta(seconds=1)
	# 	subscribed_session.create_subscription(subscribed_session, callback,
	# 			start_time=start_time, stop_time=stop_time)
	# 	time.sleep(2)

	# 	update_session.edit_config(target='running', config=CREATE)
	# 	update_session.edit_config(target='running', config=DELETE)

	# 	self.assertFalse(self.result["create"] == None)
	# 	self.assertTrue(self.result["delete"] == None)

	# 	subscribed_session.close_session()
	# 	update_session.close_session()

if __name__ == '__main__':
    unittest.main()