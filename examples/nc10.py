from ncclient import manager
from ncclient.operations.subscribe_yangpush import *
import sys, os, warnings


def callback(notification):
	print("callback called")
	print(notification)
	print(notification.data_xml)

def errback(ex):
	print("errback called")
	print(ex)

def demo(host, user, password):

	session = manager.connect(host=host, port=2830,
		username=user, password=password, hostkey_verify=False,
		look_for_keys=False, allow_agent=False)
	
	rpc_reply = session.establish_subscription(callback, errback, 
		manager=session, encoding="encode-xml", stream="push-update", 
		period="30")

if __name__ == '__main__':
    demo("127.0.0.1", "admin", "admin")
