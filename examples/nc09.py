from ncclient import manager
from ncclient.operations.subscribe import *

snippet = """<config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
      <aaa xmlns="http://tail-f.com/ns/aaa/1.1">
        <authentication> <users> <user xc:operation="delete">
        <name>%s</name>
      </user></users></authentication></aaa></config>""" % name

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
	subscribe.create_subscription(callback, errback, manager=subscribed_manager, filter=('xpath', '/*'))
	session.edit_config(target='running', config=snippet)

if __name__ == '__main__':
    demo(sys.argv[1], sys.argv[2], sys.argv[3])