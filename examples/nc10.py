from ncclient import manager
from ncclient.operations.subscribe import *

def callback(notification):
	print("callback called")
	print(notification)
	print(notification.data_xml)

def errback(ex):
	print("errback called")
	print(ex)

def demo(host, user, password):

	session = manager.connect(host=host, port=830,
		username=user, password=password, hostkey_verify=False,
		look_for_keys=False, allow_agent=False)

	subscribe = manager.connect(host=host, port=830,
		username=user, password=password, hostkey_verify=False,
		look_for_keys=False, allow_agent=False)
	
	subscribe.establish_subscription(callback, errback, manager=session)

if __name__ == '__main__':
    demo(sys.argv[1], sys.argv[2], sys.argv[3])