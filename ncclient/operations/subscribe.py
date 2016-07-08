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

from ncclient.operations.rpc import *

SIMPLE_SUBSCRIPTION = """
	<create-subscription
        xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0">
    </create-subscription>
"""

class Notification(object):
    pass

class CreateSubscription(RPC):
	def request(self, filter=None, stream=None):
		node = to_ele(SIMPLE_SUBSCRIPTION)
		self.subscription = self._request(node)
		self._session.add_listener(NotificationListener())
		return self.subscription

class NotificationListener(SessionListener):
    def callback(self, root, raw):
    	tag, attrs = root
    	# print raw

    def errback(self, ex):
    	pass