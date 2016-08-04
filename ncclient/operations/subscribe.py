# Copyright 2009 Shikhar Bhushan
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# TODO

import sys, os, warnings
import re
import ncclient.manager

warnings.simplefilter("ignore", DeprecationWarning)

from ncclient.operations import util
from ncclient.operations.rpc import *
from lxml import etree
from datetime import datetime
from dateutil.parser import parse

NETCONF_NOTIFICATION_NS = "urn:ietf:params:xml:ns:netconf:notification:1.0"
IETF_NETCONF_NOTIFICATIONS = "urn:ietf:params:xml:ns:yang:ietf-netconf-notifications"

class NotificationType(object):
	NETCONF_CONFIG_CHANGE = 1
	NETCONF_SESSION_END = 2
	REPLAY_COMPLETE = 3
	NOTIFICATION_COMPLETE = 4

	@classmethod
	def str_to_type(cls, string):
		lookup = {"netconf-config-change": NotificationType.NETCONF_CONFIG_CHANGE,
					"netconf-session-end": NotificationType.NETCONF_SESSION_END,
					"replayComplete": NotificationType.REPLAY_COMPLETE,
					"notificationComplete": NotificationType.NOTIFICATION_COMPLETE}
		return lookup[string]

class Notification(object):

    def __init__(self, raw):
        self._raw = raw
        self._parsed = False
        self._root = None
        self._eventTime = None
        self._type = None
        self._data = None
        self._connected = True
        self.parse()

    def __repr__(self):
        return self._raw

    def parse(self):
    	if self._parsed: return
    	
    	root = self._root = to_ele(self._raw)
    	eventTime = root.find(qualify("eventTime", NETCONF_NOTIFICATION_NS))
    	data = eventTime.getnext()
    	reason = data.find(qualify("termination-reason", IETF_NETCONF_NOTIFICATIONS))

    	self._eventTime = parse(eventTime.text)
    	self._type = NotificationType.str_to_type(re.sub("{.*}", "", data.tag))
    	self._data = data

    	if reason is not None:
    		self._connected = reason.text != "dropped"
    	self._parsed = True

    @property
    def xml(self):
    	return self._raw

    @property
    def eventTime(self):
    	if not self._parsed:
    		self.parse()
    	return self._eventTime

    @property
    def type(self):
    	if not self._parsed:
    		self.parse()
    	return self._type

    @property
    def data_ele(self):
    	if not self._parsed:
    		self.parse()
    	return self._data

    @property
    def data_xml(self):
    	if not self._parsed:
    		self.parse()
    	return to_xml(self._data)

    # @property
    # def xpath(self):
    # 	if not self._parsed:
    # 		self.parse()
    # 	return self._xpath
    
    @property
    def connected(self):
    	if not self._parsed:
    		self.parse()
    	return self._connected
    
class CreateSubscription(RPC):
	def request(self, callback, errback, manager=None,
		stream=None, filter=None, start_time=None, stop_time=None):

		if callback is None or errback is None:
			raise Exception

		subscription_node = etree.Element(qualify("create-subscription", NETCONF_NOTIFICATION_NS))

		if stream is not None:
			streamTag = etree.Element(qualify("stream"))
			streamTag.text = stream
			subscription_node.append(streamTag)
		if filter is not None:
			subscription_node.append(util.build_filter(filter))
		if start_time is not None:
			if type(start_time) is not datetime:
				raise Exception
			startTime = etree.Element("startTime")
			startTime.text = start_time.isoformat() + "Z"
			subscription_node.append(startTime)
		if stop_time is not None:
			if type(stop_time) is not datetime:
				raise Exception
			stopTime = etree.Element("stopTime")
			stopTime.text = stop_time.isoformat() + "Z"
			subscription_node.append(stopTime)

		self.session.add_listener(NotificationListener(callback, errback,
			manager, stream, filter, start_time, stop_time))
		return self._request(subscription_node)

class NotificationListener(SessionListener):

	def __init__(self, user_callback, user_errback, manager=None,
		filter=None, stream=None, start_time=None, stop_time=None):
		self.user_callback = user_callback
		self.user_errback = user_errback
		self.manager = manager
		self.stream, self.filter, self.start_time, self.stop_time = stream, filter, start_time, stop_time

	def callback(self, root, raw):
		tag, attrs = root
		if tag != qualify("notification", NETCONF_NOTIFICATION_NS):
			return
		notification = Notification(raw)
		if notification.connected:
			self.user_callback(notification)
		else:
			self.user_errback(notification)

	def errback(self, ex):
		while self.manager is not None:
			try:
				session = ncclient.manager.connect(**self.manager.kwargs)
				session.create_subscription(self.user_callback, self.user_errback, manager=self.manager,
					stream=self.stream, filter=self.filter, start_time=self.start_time, stop_time=self.stop_time)
				break
			except Exception as e:
				# print e
				continue
		self.user_errback(ex)