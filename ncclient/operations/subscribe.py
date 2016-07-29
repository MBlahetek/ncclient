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

warnings.simplefilter("ignore", DeprecationWarning)

from ncclient.operations import util
from ncclient.operations.rpc import *
from lxml import etree
from ncclient.operations.subscribe import *

NETCONF_NOTIFICATION_NS = "urn:ietf:params:xml:ns:netconf:notification:1.0"

class NotificationType(object):
	NETCONF_CONFIG_CHANGE = 1
	CONNECTION_DROPPED = 2
	NOTIFICATION_COMPLETE = 3

class Notification(object):

    def __init__(self, raw):
        self._raw = raw
        self._parsed = False
        self._root = None
        self._type = None
        # self._eventtime = None
        # self._xpath = ""
        # self._message = None

    def __repr__(self):
        return self._raw

    def _parse(self):
    	if self._parsed: return
    	root = self._root = to_ele(self._raw)
    	notification = root.find(qualify("notification"))
    	if notification:
    		end = notification.find(qualify("netconf-session-end"))
    		if end:
    			# parse termination-reason, dropped
    			# TODO look at notification for dropped connection
    			self._type = NotificationType.CONNECTION_DROPPED
    		else:
    			self._type = NotificationType.NETCONF_CONFIG_CHANGE
    	self._parsed = True

    @property
    def xml(self):
    	return self._raw

    @property
    def type(self):
    	return self._type
    

class CreateSubscription(RPC):
	def request(self, callback, errback, filter=None, stream=None, start_time=None, stop_time=None):
		subscription_node = etree.Element(qualify("create-subscription", NETCONF_NOTIFICATION_NS))

		if stream is not None:
			streamTag = etree.Element(qualify("stream"))
			streamTag.text = stream
			subscription_node.append(streamTag)
		if filter is not None:
			subscription_node.append(util.build_filter(filter))
		if start_time is not None:
			startTime = etree.Element("startTime")
			startTime.text = start_time.isoformat() + "Z"
			subscription_node.append(startTime)
		if stop_time is not None:
			stopTime = etree.Element("stopTime")
			stopTime.text = stop_time.isoformat() + "Z"
			subscription_node.append(stopTime)

		self.session.add_listener(NotificationListener(callback, errback))

		print toString(subscription_node)

		return self._request(subscription_node)

class NotificationListener(SessionListener):

	def __init__(self, user_callback, user_errback):
		self.user_callback = user_callback
		self.user_errback = user_errback

	def callback(self, root, raw):
		tag, attrs = root
		if tag != qualify("notification", NETCONF_NOTIFICATION_NS):
			return
		# element = etree.fromstring(raw)
		# event_time = element.find(qualify("eventTime", NETCONF_NOTIFICATION_NS))
		# event = event_time.getnext()
		# self.user_callback(event_time.text, event)
		self.user_callback(raw)

	def errback(self, ex):
		self.user_errback(ex)