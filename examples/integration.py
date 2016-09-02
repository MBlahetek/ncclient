import unittest
import subprocess
from ncclient import manager
from ncclient.operations.subscribe import *
from datetime import datetime
from lxml.etree import *

CREATE = """<config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
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

DELETE = """<config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
<devices xmlns="http://tail-f.com/ns/ncs">
<device xc:operation="delete"><name>ToR2</name><address>1.3.3.7</address>
</device></devices></config>"""

def connect_cisco_vts():
    return manager.connect(host="127.0.0.1", port=2022,
    username="admin", password="admin",
    hostkey_verify=False, look_for_keys=False,
    allow_agent=False)

class TestIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        # subprocess.call(["ncs", "--start-phase0"], cwd="/Users/alheng/ncs")
        # subprocess.call(["ncs", "--start-phase1"], cwd="/Users/alheng/ncs")
        # subprocess.call(["ncs", "--start-phase2"], cwd="/Users/alheng/ncs")
        pass

    def setUp(self):
        self.notification = None
        self.result = {"create": None, "delete": None}
        self.update_session = connect_cisco_vts()
        self.subscribed_session = connect_cisco_vts()

    def test_subscribe_ok(self):
        def callback(): pass
        def errback(): pass
        subcription = self.subscribed_session.create_subscription(callback, errback)
        subcription.parse()
        self.assertTrue(subcription.ok)
        self.assertFalse(subcription.error)

    def test_notification_match_filter(self):
        def callback(notification): self.notification = notification
        def errback(): pass
        try: self.update_session.edit_config(target='running', config=DELETE)
        except: pass
        self.subscribed_session.create_subscription(callback, errback,
        filter=('xpath', '/netconf-config-change/edit/operation[text()=\'create\']'))
        self.update_session.edit_config(target='running', config=CREATE)
        self.assertNotEqual(self.notification, None)

    def test_notification_different_filter(self):
        def callback(notification): self.notification = notification
        def errback(): pass
        try: self.update_session.edit_config(target='running', config=CREATE)
        except: pass
        self.subscribed_session.create_subscription(callback, errback,
        filter=('xpath', '/netconf-config-change/edit/operation[text()=\'create\']'))
        self.update_session.edit_config(target='running', config=DELETE)
        self.assertEquals(self.notification, None)

    def test_stop_time_without_start(self):
        def callback(): pass
        def errback(): pass
        with self.assertRaises(RPCError):
            stop_time = datetime.now()
            self.subscribed_session.create_subscription(callback, errback,
                stream='ncs-events', start_time=None, stop_time=stop_time)

if __name__ == '__main__':
    unittest.main()