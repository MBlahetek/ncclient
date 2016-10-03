from Tkinter import *
from ncclient import manager
from ncclient.operations.subscribe_yangpush import *
from datetime import datetime
import sys, os, warnings
import Tkinter as tk
import ttk
import tkFont
import xml.etree.ElementTree as ET


class MainApplication:
	def __init__(self, master):
		self.master = master

		self.calc_window_size(self.master)

		self.mainframe = tk.Frame(self.master)
		self.buttonframe = tk.Frame(self.master)
		

		
		self.tree = ttk.Treeview(self.mainframe, height=20)
		self.tree['show'] = 'headings'

		self.tree["columns"]=("Server","Subscription ID", "Configured Subscription", 
			"Status", "Stream", "Filter", "Replay start time", "Replay stop time",
			"Encoding", "Start time", "Stop time", "Update-trigger", "Period", "DSCP", "Priority",
			"Dependency")
		self.tree.column("Server", width=150, minwidth=150)
		self.tree.column("Subscription ID", width=160, minwidth=150)
		self.tree.column("Configured Subscription", width=170, minwidth=150)
		self.tree.column("Status", width=140, minwidth=140)
		self.tree.column("Stream", width=140, minwidth=140)
		self.tree.column("Filter", width=140, minwidth=130)
		self.tree.column("Replay start time", width=170, minwidth=130)
		self.tree.column("Replay stop time", width=170, minwidth=130)
		self.tree.column("Encoding", width=140, minwidth=130)
		self.tree.column("Start time", width=140, minwidth=130)
		self.tree.column("Stop time", width=140, minwidth=130)
		self.tree.column("Update-trigger", width=150, minwidth=130)
		self.tree.column("Period", width=150, minwidth=130)
		self.tree.column("DSCP", width=110, minwidth=100)
		self.tree.column("Priority", width=110, minwidth=100)
		self.tree.column("Dependency", width=130, minwidth=120)

		self.tree.heading("Server", text="Server")
		self.tree.heading("Subscription ID", text="Subscription ID")
		self.tree.heading("Configured Subscription", text="Configured Subscription")
		self.tree.heading("Status", text="Status")
		self.tree.heading("Stream", text="Stream")
		self.tree.heading("Filter", text="Filter")
		self.tree.heading("Replay start time", text="Replay start time")
		self.tree.heading("Replay stop time", text="Replay stop time")
		self.tree.heading("Encoding", text="Encoding")
		self.tree.heading("Start time", text="Start time")
		self.tree.heading("Stop time", text="Stop time")
		self.tree.heading("Update-trigger", text="Update-trigger")
		self.tree.heading("Period", text="Period")
		self.tree.heading("DSCP", text="DSCP")
		self.tree.heading("Priority", text="Priority")
		self.tree.heading("Dependency", text="Dependency")

		self.tree.grid()

		self.mainframe.grid()

		self.B_NewSubscription = tk.Button(self.buttonframe, text="New Subscription", command=self.new_Subscription).grid(row=1, column=0)
		self.B_DeleteSubscription = tk.Button(self.buttonframe, text="Delete Subscription", command=self.delete_Subscription).grid(row=1, column=1)
		self.B_GetSubscription = tk.Button(self.buttonframe, text="Get Subscription", command=self.get_Subscription).grid(row=1, column=2)
		self.B_Exit = tk.Button(self.buttonframe, text="Exit", command=self.close_window).grid(row=1, column=3)

		self.buttonframe.grid()

		self.subscriptions = []



	def callback(self, notification):
		print("callback called")
		print("print notification:")
		print(notification)
		print("print notification.data_xml:")
		print(notification.data_xml)

	def errback(self, ex):
		print("errback called. msg:")
		print(ex)
		print("errback called. msg end")

	def add_new_subscription(self, subID, server, session):
			
		FILTER_SNIPPET = """<subscriptions xmlns="urn:ietf:params:xml:ns:yang:ietf-event-notifications"><subscription><subscription-id>%s</subscription-id></subscription></subscriptions>""" % subID

		rpc_reply = session.get(filter=("subtree", FILTER_SNIPPET))
		
		root = ET.fromstring(rpc_reply.xml)
		subxml = root[0][0][0]
		self.parse_to_treeview(subxml, server, session)
	
	def add_subscription(self, singlenode, rpc_reply, server, session):
		
		root = ET.fromstring(rpc_reply.xml)
		
		if singlenode:
			subxml = root[0][0][0]
			self.parse_to_treeview(subxml, server, session)
		else:
			subxml = root[0][0]
			for child in subxml:
				self.parse_to_treeview(child, server, session)

	def parse_to_treeview(self, xml, server, session):	
		configSub = ""
		filter = ""
		for child in xml:
			if child.tag[-len("subscription-id"):] == "subscription-id":
				subID = child.text
				if self.tree.exists(subID):
					return
			if child.tag[-len("subscription-start-time"):] == "subscription-start-time":
				subStartTime = child.text
			if child.tag[-len("subscription-stop-time"):] == "subscription-stop-time":
				subStopTime = child.text
				if subStopTime is None:
					subStopTime = "not set"
			if child.tag[-len("dscp"):] == "dscp":
				dscp = child.text
			if child.tag[-len("subscription-priority"):] == "subscription-priority":
				priority = child.text
			if child.tag[-len("subscription-dependency"):] == "subscription-dependency":
				dependency = child.text
			if child.tag[-len("encoding"):] == "encoding":
				encoding = child.text
			if child.tag[-len("stream"):] == "stream":
				stream = child.text
			if child.tag[-len("startTime"):] == "startTime":
				startTime = child.text
				if startTime == "-1":
					startTime = "not set"
			if child.tag[-len("stopTime"):] == "stopTime":
				stopTime = child.text
				if stopTime == "-1":
					stopTime = "not set"
			if child.tag[-len("period"):] == "period":
				period = child.text
				updateTrigger = "periodic"
			if child.tag[-len("dampening-period"):] == "dampening-period":
				period = child.text
				updateTrigger = "on-change"
		
		self.tree.insert(parent="", index="end", iid=subID, 
			values=(server, 
				subID, 
				configSub, 
				"active", 
				stream, 
				filter, 
				startTime, 
				stopTime, 
				encoding, 
				subStartTime, 
				subStopTime, 
				updateTrigger, 
				period, 
				dscp, 
				priority, 
				dependency))
		

	def update_Subscription(self):
		""" .set(iid, column=None, value=None)
		Use this method to retrieve or set the column values of the item specified by iid. 
		With one argument, the method returns a dictionary: the keys are the column identifiers, 
		and each related value is the text in the corresponding column.

		With two arguments, the method returns the data value from the column of 
		the selected item whose column identifier is the column argument. With three arguments, 
		the item's value for the specified column is set to the third argument.
		"""
		
	def get_Subscription(self):
		self.newWindow = tk.Toplevel(self.master)
		self.app = GetSubscriptionWindow(self.newWindow, self)
		
	def new_Subscription(self):
		self.newWindow = tk.Toplevel(self.master)
		self.app = NewSubscriptionWindow(self.newWindow, self)
		
	def delete_Subscription(self):
		self.newWindow = tk.Toplevel(self.master)
		self.app = DeleteSubscriptionWindow(self.newWindow, self)

	def calc_window_size(self, master):

		self.screen_width = master.winfo_screenwidth()
		self.screen_height = master.winfo_screenheight()
		if self.screen_width > 2100 and self.screen_height > 1200:
			self.default_font = tkFont.nametofont("TkDefaultFont")
			self.default_font.configure(size=11)
			self.master.option_add("*Font", self.default_font)
			self.default_style = ttk.Style()
			self.default_style.configure(".", font=("Helvetica",11), rowheight=28)
			self.default_style.configure("Treeview", font=("Helvetica", 11), rowheight=28)
			self.default_style.configure("Treeview.Heading", font=("Helvetica", 11), rowheight=28)		
		
	def close_window(self):
		self.master.destroy()

class NewSubscriptionWindow:
	def __init__(self, master, controller):
		self.master = master
		self.topframe = tk.Frame(self.master)
		self.bottomframe = tk.Frame(self.master)
		self.controller = controller

		self.L_ServerIP = Label(self.topframe, text="Server IP: ").grid(row=0, column=0, sticky=W)
		self.E_ServerIP = Entry(self.topframe)
		self.E_ServerIP.insert(END, "127.0.0.1")
		self.E_ServerIP.grid(row=0, column=1, sticky=E)

		self.L_UserName = Label(self.topframe, text="User Name: ").grid(row=1, column=0, sticky=W)
		self.E_UserName = Entry(self.topframe)
		self.E_UserName.insert(END, "admin")
		self.E_UserName.grid(row=1, column=1, sticky=E)

		self.L_Password = Label(self.topframe, text="Password: ").grid(row=2, column=0, sticky=W)
		self.E_Password = Entry(self.topframe, show="*")
		self.E_Password.insert(END, "admin")
		self.E_Password.grid(row=2, column=1, sticky=E)

		self.L_Encoding = Label(self.topframe, text="encoding: ").grid(row=3, sticky=W)
		self.E_Encoding = Entry(self.topframe)
		self.E_Encoding.insert(END, "encode-xml")
		self.E_Encoding.grid(row=3, column=1, sticky=E)

		self.L_Stream = Label(self.topframe, text="stream: ").grid(row=4, sticky=W)
		self.E_Stream = Entry(self.topframe)
		self.E_Stream.insert(END, "NETCONF")
		self.E_Stream.grid(row=4, column=1, sticky=E)

		self.L_StartTime = Label(self.topframe, text="startTime: ").grid(row=5, sticky=W)
		self.E_StartTime = Entry(self.topframe)
		self.E_StartTime.insert(END, "YYYY/MM/DD HH:MM:SS.ffffff")
		self.E_StartTime.grid(row=5, column=1, sticky=E)

		self.L_StopTime = Label(self.topframe, text="stopTime: ").grid(row=6, sticky=W)
		self.E_StopTime = Entry(self.topframe)
		self.E_StopTime.insert(END, "YYYY/MM/DD HH:MM:SS.ffffff")
		self.E_StopTime.grid(row=6, column=1, sticky=E)

		self.L_UpdateFilter = Label(self.topframe, text="update-filter: ").grid(row=7, sticky=W)
		self.updateFilters = ("None", "subtree", "xpath")
		self.SB_UpdateFilter = Spinbox(self.topframe, values=self.updateFilters, wrap=True, state='readonly')
		self.SB_UpdateFilter.grid(row=7, column=1, sticky=E)
		self.L_Criteria = Label(self.topframe, text="    criteria: ").grid(row=8, sticky=W)
		self.E_Criteria = Entry(self.topframe)
		self.E_Criteria.grid(row=8, column=1, sticky=E)

		self.L_SubStartTime = Label(self.topframe, text="subscription-start-time: ").grid(row=9, sticky=W)
		self.E_SubStartTime = Entry(self.topframe)
		self.E_SubStartTime.insert(END, "YYYY/MM/DD HH:MM:SS.ffffff")
		self.E_SubStartTime.grid(row=9, column=1, sticky=E)

		self.L_SubStopTime = Label(self.topframe, text="subscription-stop-time: ").grid(row=10, sticky=W)
		self.E_SubStopTime = Entry(self.topframe)
		self.E_SubStopTime.insert(END, "YYYY/MM/DD HH:MM:SS.ffffff")
		self.E_SubStopTime.grid(row=10, column=1, sticky=E)

		self.L_Dscp = Label(self.topframe, text="dscp: ").grid(row=11, sticky=W)
		self.E_Dscp = Entry(self.topframe)
		self.E_Dscp.grid(row=11, column=1, sticky=E)

		self.L_SubPriority = Label(self.topframe, text="subscription-priority: ").grid(row=12, sticky=W)
		self.E_SubPriority = Entry(self.topframe)
		self.E_SubPriority.grid(row=12, column=1, sticky=E)

		self.L_SubDependency = Label(self.topframe, text="subscription-dependency: ").grid(row=13, sticky=W)
		self.E_SubDependency = Entry(self.topframe)
		self.E_SubDependency.grid(row=13, column=1, sticky=E)

		self.L_UpdateTrigger = Label(self.topframe, text="update-trigger: ").grid(row=14, sticky=W)
		self.updateTriggers = ("periodic", "on-change")
		self.updateVar = StringVar()
		self.SB_UpdateTrigger = Spinbox(self.topframe, values=self.updateTriggers, wrap=True, state='readonly', textvariable=self.updateVar)
		self.SB_UpdateTrigger.grid(row=14, column=1, sticky=E)
		self.updateVar.trace("w", self.updateTriggerChange)
		
		self.L_Period = Label(self.topframe, text="    period: ").grid(row=15, sticky=W)
		self.E_Period = Entry(self.topframe)
		self.E_Period.insert(END, "1000")
		self.E_Period.grid(row=15, column=1, sticky=E)

		self.L_NoSyncOnStart = Label(self.topframe, text="    no-synch-on-start: ").grid(row=16, sticky=W)
		self.varSync = IntVar()
		self.CB_NoSyncOnStart = Checkbutton(self.topframe, onvalue=1, offvalue=0, variable=self.varSync)
		self.CB_NoSyncOnStart.grid(row=16, column=1)

		self.L_DampeningPeriod = Label(self.topframe, text="    dampening-period: ").grid(row=17, sticky=W)
		self.E_DampeningPeriod = Entry(self.topframe, state='disabled')
		self.E_DampeningPeriod.grid(row=17, column=1, sticky=E)

		self.L_ExcludedChange = Label(self.topframe, text="    excluded-change: ").grid(row=18, sticky=W)
		self.varCr = IntVar()
		self.varMod = IntVar()
		self.varDel = IntVar()
		self.CB_ExcludedChangeCr = Checkbutton(self.topframe, text="creation", onvalue=1, offvalue=0, variable=self.varCr)
		self.CB_ExcludedChangeCr.grid(row=18, column=1)
		self.CB_ExcludedChangeMod = Checkbutton(self.topframe, text="modify", onvalue=1, offvalue=0, variable=self.varMod)
		self.CB_ExcludedChangeMod.grid(row=19, column=1)
		self.CB_ExcludedChangeDel = Checkbutton(self.topframe, text="deletion", onvalue=1, offvalue=0, variable=self.varDel)
		self.CB_ExcludedChangeDel.grid(row=20, column=1)


		self.sendButton = tk.Button(self.bottomframe, text = 'Send', width = 10, command = self.send_request)
		self.sendButton.grid(row=0,column=0)
		self.quitButton = tk.Button(self.bottomframe, text = 'Cancel', width = 10, command = self.close_window)
		self.quitButton.grid(row=0,column=1)
		
		self.topframe.grid(row=0)
		self.bottomframe.grid(row=1)

	def send_request(self):
		self.host = self.E_ServerIP.get()
		self.user = self.E_UserName.get()
		self.password = self.E_Password.get()
		
		if self.E_Encoding.get != "":
			self.encoding = self.E_Encoding.get()
		else:
			self.encoding = None

		if self.E_Stream.get() != "":
			self.stream = self.E_Stream.get()
		else:
			self.stream = None

		if self.E_StartTime.get() != ("" or "YYYY/MM/DD HH:MM:SS.ffffff"):
			self.startTime = datetime.strptime(self.E_StartTime.get(), '%Y/%m/%d %H:%M:%S.%f')
		else:
			self.startTime = None

		if self.E_StopTime.get() != ("" or "YYYY/MM/DD HH:MM:SS.ffffff"):
			self.stopTime = datetime.strptime(self.E_StopTime.get(), '%Y/%m/%d %H:%M:%S.%f')
		else:
			self.stopTime = None

		self.updateFilter = self.SB_UpdateFilter.get()
		self.updateCriteria = self.E_Criteria.get()

		if self.updateFilter != "None" and self.updateCriteria == "":
			self.updateCriteria = None
		elif self.updateFilter != "None" and self.updateCriteria != None:
			if self.updateFilter == "subtree":
				if self.updateCriteria[0] == "<":
					self.filterTuple = (self.updateFilter, self.updateCriteria)
				else:
					print("Criteria not in a proper format!")
					return
			else:
				if self.updateCriteria[0] != "<":
					self.filterTuple = (self.updateFilter, self.updateCriteria)
				else:
					print("Criteria not in a proper format!")
					return
		else:
			self.filterTuple = None

		if self.E_SubStartTime.get() != ("" or "YYYY/MM/DD HH:MM:SS.ffffff"):
			self.subStartTime = datetime.strptime(self.E_SubStartTime.get(), '%Y/%m/%d %H:%M:%S.%f')
		else:
			self.subStartTime = None

		if self.E_SubStopTime.get() != ("" or "YYYY/MM/DD HH:MM:SS.ffffff"):
			self.subStopTime = datetime.strptime(self.E_SubStopTime.get(), '%Y/%m/%d %H:%M:%S.%f')
		else:
			self.subStopTime = None			

		if self.E_Dscp.get() != "":
			self.dscp = self.E_Dscp.get()
		else:
			self.dscp = None

		if self.E_SubPriority.get() != "":
			self.subPriority = self.E_SubPriority.get()
		else:
			self.subPriority = None

		if self.E_SubDependency.get() != "":
			self.subDependency = self.E_SubDependency.get()
		else:
			self.subDependency = None

		self.updateTrigger = self.SB_UpdateTrigger.get()
		self.exclude = []
		if self.updateTrigger == "periodic":
			self.period = self.E_Period.get()
			if self.period == "":
				print("period mandatory")
				return
			self.noSyncOnStart = None
			self.excludeStr = None
		else:
			self.noSyncOnStart = self.varSync.get()
			if self.noSyncOnStart == 0:
				self.noSyncOnStart = None
			self.period = self.E_DampeningPeriod.get()
			if self.period == "":
				print("dampeningPeriod mandatory")
				return
			if self.varCr.get():
				self.exclude.append("creation")
			if self.varMod.get():
				self.exclude.append("modify")
			if self.varDel.get():
				self.exclude.append("deletion")
			self.excludeStr = ', '.join(self.exclude)
			if self.excludeStr == "":
				self.excludeStr = None
				

		self.session = manager.connect(
			host=self.host, port=2830, 
			username=self.user, 
			password=self.password, 
			device_params={'name':'opendaylight'}, 
			hostkey_verify=False, 
			look_for_keys=False, 
			allow_agent=False)

		self.rpc_reply = self.session.establish_subscription(
			callback=self.controller.callback, 
			errback=self.controller.errback, 
			manager=self.session, 
			encoding=self.encoding, 
			stream=self.stream, 
			start_time=self.startTime, 
			stop_time=self.stopTime, 
			update_filter=self.filterTuple,	
			sub_start_time=self.subStartTime, 
			sub_stop_time=self.subStopTime,	
			dscp=self.dscp, 
			priority=self.subPriority, 
			dependency=self.subDependency, 
			update_trigger=self.updateTrigger, 
			period=self.period, 
			no_sync_on_start=self.noSyncOnStart, 
			excluded_change=self.excludeStr)
		
		xmlroot = ET.fromstring(self.rpc_reply.xml)	
		
		for child in xmlroot:
			if child.tag[-len("subscription-id"):] == "subscription-id":
				self.subID = child.text
		
		if self.rpc_reply.ok:
			self.controller.add_new_subscription(self.subID, self.host, self.session)
			self.close_window()

	def updateTriggerChange(self, a, b, c):
		if self.SB_UpdateTrigger.get() == "periodic":
			intvar = self.E_DampeningPeriod.get()
			self.E_DampeningPeriod.delete(0,END)
			self.E_DampeningPeriod.configure(state='disabled')
			self.E_Period.configure(state='normal')
			self.E_Period.insert(0, intvar)
		else:
			intvar = self.E_Period.get()
			self.E_Period.delete(0,END)
			self.E_Period.configure(state='disabled')
			self.E_DampeningPeriod.configure(state='normal')
			self.E_DampeningPeriod.insert(0, intvar)

	def close_window(self):
		self.master.destroy()
		
class DeleteSubscriptionWindow:
	def __init__(self, master, controller):
		self.master = master
		self.topframe = tk.Frame(self.master)
		self.bottomframe = tk.Frame(self.master)
		self.controller = controller

		self.L_Operation = Label(self.topframe, text="Delete subscription:").grid(row=0, column=0, sticky=W)

		self.L_ServerIP = Label(self.topframe, text="Server IP: ").grid(row=1, column=0, sticky=W)
		self.E_ServerIP = Entry(self.topframe)
		self.E_ServerIP.insert(END, "127.0.0.1")
		self.E_ServerIP.grid(row=1, column=1, sticky=E)

		self.L_UserName = Label(self.topframe, text="User Name: ").grid(row=2, column=0, sticky=W)
		self.E_UserName = Entry(self.topframe)
		self.E_UserName.insert(END, "admin")
		self.E_UserName.grid(row=2, column=1, sticky=E)

		self.L_Password = Label(self.topframe, text="Password: ").grid(row=3, column=0, sticky=W)
		self.E_Password = Entry(self.topframe, show="*")
		self.E_Password.insert(END, "admin")
		self.E_Password.grid(row=3, column=1, sticky=E)
		
		self.L_SubID = Label(self.topframe, text="Subscription ID: ").grid(row=4, column=0, sticky=W)
		self.E_SubID = Entry(self.topframe)
		self.E_SubID.grid(row=4, column=1, sticky=E)
	
		self.sendButton = tk.Button(self.bottomframe, text = 'Send', width = 10, command = self.send_request)
		self.sendButton.grid(row=0,column=0)
		self.quitButton = tk.Button(self.bottomframe, text = 'Cancel', width = 10, command = self.close_window)
		self.quitButton.grid(row=0,column=1)
		
		self.topframe.grid(row=0)
		self.bottomframe.grid(row=1)
	
	def send_request(self):
		self.host = self.E_ServerIP.get()
		self.user = self.E_UserName.get()
		self.password = self.E_Password.get()
		self.subID = self.E_SubID.get()
	
		self.session = manager.connect(host=self.host, port=2830, username=self.user,
									password=self.password, device_params={'name':'opendaylight'}, 
									hostkey_verify=False, look_for_keys=False, allow_agent=False)
			
		if self.subID == "":
			print("Missing subscription-ID!")
			return
		else:
			self.rpc_reply = self.session.delete_subscription(self.subID)
	
		self.close_window()
		
	def close_window(self):
		self.master.destroy()
		

class GetSubscriptionWindow:
	def __init__(self, master, controller):
		self.master = master
		self.topframe = tk.Frame(self.master)
		self.bottomframe = tk.Frame(self.master)
		self.controller = controller

		self.L_Operation = Label(self.topframe, text="Get subscription(s):").grid(row=0, column=0, sticky=W)

		self.L_ServerIP = Label(self.topframe, text="Server IP: ").grid(row=1, column=0, sticky=W)
		self.E_ServerIP = Entry(self.topframe)
		self.E_ServerIP.insert(END, "127.0.0.1")
		self.E_ServerIP.grid(row=1, column=1, sticky=E)

		self.L_UserName = Label(self.topframe, text="User Name: ").grid(row=2, column=0, sticky=W)
		self.E_UserName = Entry(self.topframe)
		self.E_UserName.insert(END, "admin")
		self.E_UserName.grid(row=2, column=1, sticky=E)

		self.L_Password = Label(self.topframe, text="Password: ").grid(row=3, column=0, sticky=W)
		self.E_Password = Entry(self.topframe, show="*")
		self.E_Password.insert(END, "admin")
		self.E_Password.grid(row=3, column=1, sticky=E)
		
		self.L_SubID = Label(self.topframe, text="Subscription ID: ").grid(row=4, column=0, sticky=W)
		self.E_SubID = Entry(self.topframe)
		self.E_SubID.grid(row=4, column=1, sticky=E)

		self.sendButton = tk.Button(self.bottomframe, text = 'Send', width = 10, command = self.send_request)
		self.sendButton.grid(row=0,column=0)
		self.quitButton = tk.Button(self.bottomframe, text = 'Cancel', width = 10, command = self.close_window)
		self.quitButton.grid(row=0,column=1)
		
		self.topframe.grid(row=0)
		self.bottomframe.grid(row=1)

	def send_request(self):
		self.host = self.E_ServerIP.get()
		self.user = self.E_UserName.get()
		self.password = self.E_Password.get()
		self.subID = self.E_SubID.get()

		self.session = manager.connect(host=self.host, port=2830, username=self.user, 
			password=self.password, device_params={'name':'opendaylight'}, hostkey_verify=False, look_for_keys=False, allow_agent=False)
		
		FILTERXML = """<subscriptions xmlns="urn:ietf:params:xml:ns:yang:ietf-event-notifications"></subscriptions>"""
		FILTERXMLID = """<subscriptions xmlns="urn:ietf:params:xml:ns:yang:ietf-event-notifications"><subscription><subscription-id>%s</subscription-id></subscription></subscriptions>""" % self.subID

		if self.subID == "":
			self.rpc_reply = self.session.get(filter=("subtree", FILTERXML))
			singlenode = False
		else:
			self.rpc_reply = self.session.get(filter=("subtree", FILTERXMLID))
			singlenode = True	
		
		self.controller.add_subscription(singlenode, self.rpc_reply, self.host, self.session)

		self.close_window()

	def close_window(self):
		self.master.destroy()
				

def main(): 
	root = tk.Tk()
	root.title("NCClient")
	app = MainApplication(root)
	root.mainloop()

if __name__ == '__main__':
	main()