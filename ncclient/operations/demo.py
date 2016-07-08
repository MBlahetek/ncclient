from ncclient import manager
import time

def demo(host, user):
    with manager.connect(host="127.0.0.1",
    	port=2022,
    	username=user,
    	password="admin",
    	hostkey_verify=False,
    	look_for_keys=False,
    	allow_agent=False) as m:
    	m.create_subscription()
    	time.sleep(100)

if __name__ == '__main__':
    demo("127.0.0.1", "admin")