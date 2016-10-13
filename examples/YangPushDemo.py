from Tkinter import *
from ncclient import manager
from ncclient.operations.subscribe_yangpush import *
from datetime import datetime
import sys, os, warnings
import Tkinter as tk
import time
import ttk
import tkFont
import tkMessageBox
import xml.etree.ElementTree as ET


class MainApplication:
	def __init__(self, master):
		self.master = master
		self.sessions = []
		self.filters = []
		
		self.calc_window_size(self.master)

		self.mainframe = tk.Frame(self.master)
		self.buttonframe = tk.Frame(self.master)
		
		self.tree = ttk.Treeview(self.mainframe, height=20)
		self.tree['show'] = 'headings'

		self.tree["columns"]=("Server","Subscription ID", "Status", "Stream", "Filter", 
							"Replay start time", "Replay stop time", "Encoding", "Start time", 
							"Stop time", "Update-trigger", "Period", "Priority", "Dependency")
		minwidth=100
		self.tree.column("Server", width=130, minwidth=minwidth)
		self.tree.column("Subscription ID", width=160, minwidth=minwidth)
		self.tree.column("Status", width=200, minwidth=minwidth)
		self.tree.column("Stream", width=190, minwidth=minwidth)
		self.tree.column("Filter", width=210, minwidth=minwidth)
		self.tree.column("Replay start time", width=120, minwidth=minwidth)
		self.tree.column("Replay stop time", width=120, minwidth=minwidth)
		self.tree.column("Encoding", width=140, minwidth=minwidth)
		self.tree.column("Start time", width=310, minwidth=minwidth)
		self.tree.column("Stop time", width=310, minwidth=minwidth)
		self.tree.column("Update-trigger", width=150, minwidth=minwidth)
		self.tree.column("Period", width=120, minwidth=minwidth)
		self.tree.column("Priority", width=100, minwidth=minwidth)
		self.tree.column("Dependency", width=130, minwidth=minwidth)

		self.tree.heading("Server", text="Server")
		self.tree.heading("Subscription ID", text="Subscription ID")
		self.tree.heading("Status", text="Status")
		self.tree.heading("Stream", text="Stream")
		self.tree.heading("Filter", text="Filter")
		self.tree.heading("Replay start time", text="Replay start time")
		self.tree.heading("Replay stop time", text="Replay stop time")
		self.tree.heading("Encoding", text="Encoding")
		self.tree.heading("Start time", text="Start time")
		self.tree.heading("Stop time", text="Stop time")
		self.tree.heading("Update-trigger", text="Update-trigger")
		self.tree.heading("Period", text="Period (ms)")
		self.tree.heading("Priority", text="Priority")
		self.tree.heading("Dependency", text="Dependency")

		self.tree.grid()
		
		#basis for the subscription filter message box
		self.tree.bind("<Double-1>", self.OnDoubleClick)
		
		self.tree.tag_configure("waiting", background="Khaki")
		self.tree.tag_configure("active", background="LightGreen")
		self.tree.tag_configure("resumed", background="LightGreen")
		self.tree.tag_configure("suspended", background="Khaki")
		self.tree.tag_configure("terminated", background="OrangeRed")	
		self.tree.tag_configure("modified", background="Khaki")
		self.tree.tag_configure("started", background="LightGreen")
		self.tree.tag_configure("complete", background="Green")
		self.tree.tag_configure("replay complete", background="Green")
		
		self.mainframe.grid()

		self.B_NewSubscription = tk.Button(self.buttonframe, text="New subscription", command=self.new_Subscription).grid(row=1, column=0)
		self.B_ModifySubscription = tk.Button(self.buttonframe, text="Modify subscription", command=self.modify_Subscription).grid(row=1, column=1)
		self.B_DeleteSubscription = tk.Button(self.buttonframe, text="Delete subscription", command=self.delete_Subscription).grid(row=1, column=2)
		self.B_GetSubscription = tk.Button(self.buttonframe, text="Get subscription", command=self.get_Subscription).grid(row=1, column=3)		
		self.B_Exit = tk.Button(self.buttonframe, text="Exit", command=self.close_window).grid(row=1, column=4)

		self.buttonframe.grid()

	def callback(self, notification):
		
		"""
		This callback receives all the notifications. At the moment it just prints them
		and calls a update method to display the status of a subscription.
		"""
		
		print("callback called")
		print(notification)

		self.update_Subscription(notification)
				
	def errback(self, ex):
		
		"""
		This errback handles incoming messages not of type notification.
		"""
		
		print("errback called.")
		print(ex)

	def add_to_treeview(self, subID, server, stream, encoding, updateTrigger, period, filter=None, 
					startTime=None, stopTime=None, subStartTime=None, subStopTime=None, priority=None, dependency=None):
		
		"""
		Takes the arguments from the establish and modify subscription classes to display them in the treeview widget.
		"""

		if self.tree.exists(subID):			
			self.tree.set(subID, column="Stream", value=stream)
			self.tree.set(subID, column="Encoding", value=encoding)
			self.tree.set(subID, column="Update-trigger", value=updateTrigger)
			self.tree.set(subID, column="Period", value=period)
			if filter is not None:			
				self.tree.set(subID, column="Filter", value=filter)
				for entry in self.filters:
					if entry[0] == subID:
						self.filters.remove(entry)
						self.filters.append((subID, filter))
						break	
			if startTime is not None:
				startTime = startTime.strftime('%Y-%m-%dT%H:%M:%S.%fZ')	
				self.tree.set(subID, column="Replay start time", value=startTime)
			if stopTime is not None:
				stopTime = stopTime.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
				self.tree.set(subID, column="Replay stop time", value=stopTime)
			if subStartTime is not None:
				subStartTime = subStartTime.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
				self.tree.set(subID, column="Start time", value=subStartTime)
			if subStopTime is not None:
				subStopTime = subStopTime.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
				self.tree.set(subID, column="Stop time", value=subStopTime)
			if priority is not None:
				self.tree.set(subID, column="Priority", value=priority)
			if dependency is not None:
				self.tree.set(subID, column="Dependency", value=dependency)
							
		else:
			if filter is None:
				filter = "not set"
				
			if startTime is None:
				startTime = "not set"
			else:
				startTime = startTime.strftime('%Y-%m-%dT%H:%M:%S.%fZ')	
				
			if stopTime is None:
				stopTime = "not set"
			else:
				stopTime = stopTime.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
					
			if subStartTime is None:
				timestr = datetime.now()
				subStartTime = timestr.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
			else:
				subStartTime = subStartTime.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
				
			if subStopTime is None:
				subStopTime = "not set"
			else:
				subStopTime = subStopTime.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
				
			if priority is None:
				priority = "not set"
				
			if dependency is None:
				dependency = "not set"
				
			self.tree.insert(parent="", index="end", iid=subID, 
							values=(
								server, 
								subID, 
								"waiting", 
								stream, 
								filter, 
								startTime, 
								stopTime, 
								encoding, 
								subStartTime, 
								subStopTime, 
								updateTrigger, 
								period, 
								priority, 
								dependency))
			
			self.filters.append((subID, filter))
			self.tree.item(subID, tags=("waiting"))		
			
	def add_subscriptions(self, singlenode, rpc_reply, server):
		
		"""
		takes the arguments from the get subscription rpc and invokes the
		parse_to_treeview method for parsing the received xml string.
		"""
		
		root = ET.fromstring(rpc_reply.xml)
		if singlenode:
			subxml = root[0][0][0]
			self.parse_to_treeview(subxml, server)
		else:
			subxml = root[0][0]
			for child in subxml:
				self.parse_to_treeview(child, server)

	def parse_to_treeview(self, xml, server):
		
		"""
		processes the xml string from the get subcription rpc for displaying in the GUI
		"""
		
		existing = False
		filter = ""
		for child in xml:
			if child.tag[-len("subscription-id"):] == "subscription-id":
				subID = child.text
				if self.tree.exists(subID):
					existing = True
			if child.tag[-len("subscription-start-time"):] == "subscription-start-time":
				subStartTime = child.text
			if child.tag[-len("subscription-stop-time"):] == "subscription-stop-time":
				subStopTime = child.text
			if child.tag[-len("subscription-priority"):] == "subscription-priority":
				priority = child.text
			if child.tag[-len("subscription-dependency"):] == "subscription-dependency":
				dependency = child.text
			if child.tag[-len("encoding"):] == "encoding":
				encoding = child.text
			if child.tag[-len("stream"):] == "stream":
				stream = child.text
			if child.tag[-len("filter-1"):] == "filter-1":
				filter = child.text	
			if child.tag[-len("startTime"):] == "startTime":
				startTime = child.text
			if child.tag[-len("stopTime"):] == "stopTime":
				stopTime = child.text
			if child.tag[-len("period"):] == "period":
				period = child.text
				updateTrigger = "periodic"
			if child.tag[-len("dampening-period"):] == "dampening-period":
				period = child.text
				updateTrigger = "on-change"
				
		if existing:
			self.tree.set(subID, column="Server", value=server)
			self.tree.set(subID, column="Stream", value=stream)
			self.tree.set(subID, column="Filter", value=filter)
			self.tree.set(subID, column="Replay start time", value=startTime)
			self.tree.set(subID, column="Replay stop time", value=stopTime)
			self.tree.set(subID, column="Encoding", value=encoding)
			self.tree.set(subID, column="Start time", value=subStartTime)
			self.tree.set(subID, column="Stop time", value=subStopTime)
			self.tree.set(subID, column="Update-trigger", value=updateTrigger)
			self.tree.set(subID, column="Period", value=period)
			self.tree.set(subID, column="Priority", value=priority)
			self.tree.set(subID, column="Dependency", value=dependency)
			for entry in self.filters:
				if entry[0] == subID:
					self.filters.remove(entry)
					self.filters.append((subID, filter))
					break	
		else:
			if subStartTime is None:
				subStartTime = "not set"
			if subStopTime is None:
				subStopTime = "not set"
			if startTime is None:
				startTime = "not set"	
			if stopTime is None:
				stopTime = "not set"	
			self.tree.insert(parent="", index="end", iid=subID, 
				values=(server, 
					subID,  
					"different session", 
					stream, 
					filter, 
					startTime, 
					stopTime, 
					encoding, 
					subStartTime, 
					subStopTime, 
					updateTrigger, 
					period,  
					priority, 
					dependency))
			self.filters.append((subID, filter))
			self.tree.item(subID, tags=("waiting"))
		

	def update_Subscription(self, notification):
		
		"""
		changes the subscription status depending on the incoming notification
		"""
		
		subID = ET.fromstring(notification.data_xml)[0].text
		type = notification.type
		status = ""
		if self.tree.exists(subID):			
			if type == 11 or type == 12:
				status = "active"
			elif type == 10:
				status = "resumed"
			elif type == 9:
				status = "suspended"
			elif type == 8:
				status = "terminated"
			elif type == 7:
				status = "modified"
			elif type == 6:
				status = "started"
			elif type == 5:
				status = "complete"
			elif type == 4:
				status = "replay complete"
			self.tree.set(subID, column="Status", value=status)
			self.tree.item(subID, tags=(status))

		else:
			return

	def get_Session(self, server, user, password):
		
		"""
		takes care that there's only one session per server
		"""
		
		sessionUp = False
				
		for entry in self.sessions:
			if entry[0] == server:
				session = entry[1]
				sessionUp = True
				break
			
		if sessionUp is False:
			session = manager.connect(
				host=server, port=2830, 
				username=user, 
				password=password, 
				device_params={'name':'opendaylight'}, 
				hostkey_verify=False, 
				look_for_keys=False, 
				allow_agent=False)
			self.sessions.append((server, session))
			
		return (session, sessionUp)
	
	def OnDoubleClick(self, event):
		subID = self.tree.focus()
		header = "ID: " + subID + " - Filter"
		filter = ""
		if subID != "":
			for entry in self.filters:
				if entry[0] == subID:
					filter = entry[1]
					break
			self.filter_Message_Box(subID, filter)
			
	def filter_Message_Box(self, subID, filter):
		self.newWindow = tk.Toplevel(self.master)
		self.app = FilterMessageBox(self.newWindow, self, subID, filter)

	def get_Subscription(self):
		self.newWindow = tk.Toplevel(self.master)
		self.app = GetSubscriptionWindow(self.newWindow, self)
		
	def new_Subscription(self):
		self.newWindow = tk.Toplevel(self.master)
		self.app = NewSubscriptionWindow(self.newWindow, self)
		
	def modify_Subscription(self):
		self.newWindow = tk.Toplevel(self.master)
		self.app = ModifySubscriptionWindow(self.newWindow, self)
		
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
		width=25

		self.L_ServerIP = Label(self.topframe, text="Server IP: ").grid(row=0, column=0, sticky=W)
		self.E_ServerIP = Entry(self.topframe, width=width)
		self.E_ServerIP.insert(END, "127.0.0.1")
		self.E_ServerIP.grid(row=0, column=1, sticky=E)

		self.L_UserName = Label(self.topframe, text="User Name: ").grid(row=1, column=0, sticky=W)
		self.E_UserName = Entry(self.topframe, width=width)
		self.E_UserName.insert(END, "admin")
		self.E_UserName.grid(row=1, column=1, sticky=E)

		self.L_Password = Label(self.topframe, text="Password: ").grid(row=2, column=0, sticky=W)
		self.E_Password = Entry(self.topframe, show="*", width=width)
		self.E_Password.insert(END, "admin")
		self.E_Password.grid(row=2, column=1, sticky=E)

		self.encodings = ("XML", "JSON")
		self.L_Encoding = Label(self.topframe, text="encoding: ").grid(row=3, sticky=W)
		self.SB_Encoding = Spinbox(self.topframe, values=self.encodings, wrap=True, state='readonly', width=width-2)
		self.SB_Encoding.grid(row=3, column=1, sticky=E)

		self.streams = ("YANG-PUSH", "OPERATIONAL", "CONFIGURATION")
		self.L_Stream = Label(self.topframe, text="stream: ").grid(row=4, sticky=W)
		self.SB_Stream = Spinbox(self.topframe, values=self.streams, wrap=True, state='readonly', width=width-2)
		self.SB_Stream.grid(row=4, column=1, sticky=E)

		self.L_StartTime = Label(self.topframe, text="startTime: ").grid(row=5, sticky=W)
		self.L_TimeFormat1 = Label(self.topframe, text="(YYYY/MM/DD HH:MM:SS.ffffff)").grid(row=6, sticky=W)
		self.E_StartTime = Entry(self.topframe, state='disabled', width=width)
		self.E_StartTime.grid(row=5, column=1, sticky=E)

		self.L_StopTime = Label(self.topframe, text="stopTime: ").grid(row=7, sticky=W)
		self.L_TimeFormat2 = Label(self.topframe, text="(YYYY/MM/DD HH:MM:SS.ffffff)").grid(row=8, sticky=W)
		self.E_StopTime = Entry(self.topframe, state='disabled', width=width)
		self.E_StopTime.grid(row=7, column=1, sticky=E)

		self.L_UpdateFilter = Label(self.topframe, text="update-filter: ").grid(row=9, sticky=W)
		self.updateFilters = ("subtree", "None")
		self.SB_UpdateFilter = Spinbox(self.topframe, values=self.updateFilters, wrap=True, state='readonly', width=width-2)
		self.SB_UpdateFilter.grid(row=9, column=1, sticky=E)
		self.L_Criteria = Label(self.topframe, text="    criteria: ").grid(row=10, sticky=NW)
		self.T_Criteria = Text(self.topframe, height=8, width=width)
		self.T_Criteria.grid(row=10, column=1, sticky=E)

		self.L_SubStartTime = Label(self.topframe, text="subscription-start-time: ").grid(row=11, sticky=W)
		self.L_TimeFormat3 = Label(self.topframe, text="(YYYY/MM/DD HH:MM:SS.ffffff)").grid(row=12, sticky=W)
		self.E_SubStartTime = Entry(self.topframe, width=width)
		self.E_SubStartTime.grid(row=11, column=1, sticky=E)

		self.L_SubStopTime = Label(self.topframe, text="subscription-stop-time: ").grid(row=13, sticky=W)
		self.L_TimeFormat4 = Label(self.topframe, text="(YYYY/MM/DD HH:MM:SS.ffffff)").grid(row=14, sticky=W)
		self.E_SubStopTime = Entry(self.topframe, width=width)
		self.E_SubStopTime.grid(row=13, column=1, sticky=E)

		self.L_SubPriority = Label(self.topframe, text="subscription-priority: ").grid(row=15, sticky=W)
		self.E_SubPriority = Entry(self.topframe, state='disabled', width=width)
		self.E_SubPriority.grid(row=15, column=1, sticky=E)

		self.L_SubDependency = Label(self.topframe, text="subscription-dependency: ").grid(row=16, sticky=W)
		self.E_SubDependency = Entry(self.topframe, state='disabled', width=width)
		self.E_SubDependency.grid(row=16, column=1, sticky=E)

		self.L_UpdateTrigger = Label(self.topframe, text="update-trigger: ").grid(row=17, sticky=W)
		self.updateTriggers = ("periodic", "on-change")
		self.updateVar = StringVar()
		self.SB_UpdateTrigger = Spinbox(self.topframe, values=self.updateTriggers, wrap=True, state='readonly', textvariable=self.updateVar, width=width-2)
		self.SB_UpdateTrigger.grid(row=17, column=1, sticky=E)
		self.updateVar.trace("w", self.updateTriggerChange)
		
		self.L_Period = Label(self.topframe, text="    period (ms): ").grid(row=18, sticky=W)
		self.E_Period = Entry(self.topframe, width=width)
		self.E_Period.insert(END, "5000")
		self.E_Period.grid(row=18, column=1, sticky=E)

		self.L_NoSyncOnStart = Label(self.topframe, text="    no-synch-on-start: ").grid(row=19, sticky=W)
		self.varSync = IntVar()
		self.CB_NoSyncOnStart = Checkbutton(self.topframe, onvalue=1, offvalue=0, variable=self.varSync, state='disabled')
		self.CB_NoSyncOnStart.grid(row=19, column=1)

		self.L_DampeningPeriod = Label(self.topframe, text="    dampening-period (ms): ").grid(row=20, sticky=W)
		self.E_DampeningPeriod = Entry(self.topframe, state='disabled', width=width)
		self.E_DampeningPeriod.grid(row=20, column=1, sticky=E)

		self.L_ExcludedChange = Label(self.topframe, text="    excluded-change: ").grid(row=21, sticky=W)
		self.varCr = IntVar()
		self.varMod = IntVar()
		self.varDel = IntVar()
		self.CB_ExcludedChangeCr = Checkbutton(self.topframe, text="creation", onvalue=1, offvalue=0, variable=self.varCr, state='disabled')
		self.CB_ExcludedChangeCr.grid(row=21, column=1)
		self.CB_ExcludedChangeMod = Checkbutton(self.topframe, text="modify", onvalue=1, offvalue=0, variable=self.varMod, state='disabled')
		self.CB_ExcludedChangeMod.grid(row=22, column=1)
		self.CB_ExcludedChangeDel = Checkbutton(self.topframe, text="deletion", onvalue=1, offvalue=0, variable=self.varDel, state='disabled')
		self.CB_ExcludedChangeDel.grid(row=23, column=1)


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
		
		if self.SB_Encoding.get() == "XML":
			self.encoding = "encode-xml"
		elif self.SB_Encoding.get() == "JSON":
			self.encoding = "encode-json"
		else:
			self.encoding = None

		if self.SB_Stream.get() != "None":
			self.stream = self.SB_Stream.get()
		else:
			self.stream = None

		if self.E_StartTime.get() != "":
			self.startTime = datetime.strptime(self.E_StartTime.get(), '%Y/%m/%d %H:%M:%S.%f')
		else:
			self.startTime = None

		if self.E_StopTime.get() != "":
			self.stopTime = datetime.strptime(self.E_StopTime.get(), '%Y/%m/%d %H:%M:%S.%f')
		else:
			self.stopTime = None

		self.updateFilter = self.SB_UpdateFilter.get()
		self.updateCriteria = self.T_Criteria.get('1.0', 'end')

		if self.updateFilter == "None" and self.updateCriteria != "\n":
			self.updateCriteria = None
			print("filter type not set")
			return
		elif self.updateFilter != "None" and self.updateCriteria != "\n":
			if self.updateFilter == "subtree":
				if self.updateCriteria[0] == "<":
					self.filterTuple = (self.updateFilter, self.updateCriteria)
				else:
					print("Criteria not in a proper format!")
					return
			else:
				if self.updateCriteria[0] != "<":
					self.filterTuple = (self.updateFilter, self.updateCriteria.rstrip('\n'))
				else:
					print("Criteria not in a proper format!")
					return
		else:
			self.filterTuple = None

		if self.E_SubStartTime.get() != "":
			self.subStartTime = datetime.strptime(self.E_SubStartTime.get(), '%Y/%m/%d %H:%M:%S.%f')
			print(self.subStartTime)
		else:
			self.subStartTime = None

		if self.E_SubStopTime.get() != "":
			self.subStopTime = datetime.strptime(self.E_SubStopTime.get(), '%Y/%m/%d %H:%M:%S.%f')
		else:
			self.subStopTime = None			

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
			self.noSynchOnStart = None
			self.excludeStr = None
		else:
			self.noSynchOnStart = self.varSync.get()
			if self.noSynchOnStart == 0:
				self.noSynchOnStart = None
			self.period = self.E_DampeningPeriod.get()
			if self.period == "":
				print("dampeningPeriod mandatory")
				return
			if self.varCr.get():
				self.exclude.append("create")
			if self.varMod.get():
				self.exclude.append("modify")
			if self.varDel.get():
				self.exclude.append("delete")
			self.excludeStr = ', '.join(self.exclude)
			if self.excludeStr == "":
				self.excludeStr = None
				
		self.session = self.controller.get_Session(self.host, self.user, self.password)

		self.rpc_reply = self.session[0].establish_subscription(
			callback=self.controller.callback, 
			errback=self.controller.errback,
			notifListening=self.session[1],
			encoding=self.encoding, 
			stream=self.stream, 
			start_time=self.startTime, 
			stop_time=self.stopTime, 
			update_filter=self.filterTuple,	
			sub_start_time=self.subStartTime, 
			sub_stop_time=self.subStopTime,	
			priority=self.subPriority, 
			dependency=self.subDependency, 
			update_trigger=self.updateTrigger, 
			period=self.period, 
			no_synch_on_start=self.noSynchOnStart, 
			excluded_change=self.excludeStr)
		
		xmlroot = ET.fromstring(self.rpc_reply.xml)	
		
		for child in xmlroot:
			if child.tag[-len("subscription-id"):] == "subscription-id":
				self.subID = child.text
			if child.tag[-len("subscription-result"):] == "subscription-result":
				self.result = child.text
		
		if self.result == "ok":
			self.controller.add_to_treeview(
				subID=self.subID, 
				server=self.host, 
				stream=self.stream, 
				encoding=self.encoding, 
				updateTrigger=self.updateTrigger, 
				period=self.period, 
				filter=self.updateCriteria, 
				startTime=self.startTime, 
				stopTime=self.stopTime, 
				subStartTime=self.subStartTime, 
				subStopTime=self.subStopTime, 
				priority=self.subPriority, 
				dependency=self.subDependency)
			self.close_window()
		else:
			print("subscription-result: " + self.result)

	def updateTriggerChange(self, a, b, c):
		if self.SB_UpdateTrigger.get() == "periodic":
			intvar = self.E_DampeningPeriod.get()
			self.E_DampeningPeriod.delete(0,END)
			self.E_DampeningPeriod.configure(state='disabled')
			self.CB_NoSyncOnStart.configure(state='disabled')
			self.E_Period.configure(state='normal')
			self.E_Period.insert(0, intvar)
		else:
			intvar = self.E_Period.get()
			self.E_Period.delete(0,END)
			self.E_Period.configure(state='disabled')
			self.CB_NoSyncOnStart.configure(state='normal')
			self.E_DampeningPeriod.configure(state='normal')
			self.E_DampeningPeriod.insert(0, intvar)

	def close_window(self):
		self.master.destroy()

class ModifySubscriptionWindow:
	def __init__(self, master, controller):
		self.master = master
		self.topframe = tk.Frame(self.master)
		self.bottomframe = tk.Frame(self.master)
		self.controller = controller
		width=25

		self.L_ServerIP = Label(self.topframe, text="Server IP: ").grid(row=0, column=0, sticky=W)
		self.E_ServerIP = Entry(self.topframe, width=width)
		self.E_ServerIP.insert(END, "127.0.0.1")
		self.E_ServerIP.grid(row=0, column=1, sticky=E)

		self.L_UserName = Label(self.topframe, text="User Name: ").grid(row=1, column=0, sticky=W)
		self.E_UserName = Entry(self.topframe, width=width)
		self.E_UserName.insert(END, "admin")
		self.E_UserName.grid(row=1, column=1, sticky=E)

		self.L_Password = Label(self.topframe, text="Password: ").grid(row=2, column=0, sticky=W)
		self.E_Password = Entry(self.topframe, show="*", width=width)
		self.E_Password.insert(END, "admin")
		self.E_Password.grid(row=2, column=1, sticky=E)
		
		self.L_SubID = Label(self.topframe, text="subscription-id: ").grid(row=3, sticky=W)
		self.E_SubID = Entry(self.topframe, width=width)
		self.E_SubID.grid(row=3, column=1, sticky=E)		

		self.encodings = ("XML", "JSON")
		self.L_Encoding = Label(self.topframe, text="encoding: ").grid(row=4, sticky=W)
		self.SB_Encoding = Spinbox(self.topframe, values=self.encodings, wrap=True, state='readonly', width=width-2)
		self.SB_Encoding.grid(row=4, column=1, sticky=E)

		self.streams = ("YANG-PUSH", "OPERATIONAL", "CONFIGURATION")
		self.L_Stream = Label(self.topframe, text="stream: ").grid(row=5, sticky=W)
		self.SB_Stream = Spinbox(self.topframe, values=self.streams, wrap=True, state='readonly', width=width-2)
		self.SB_Stream.grid(row=5, column=1, sticky=E)

		self.L_StartTime = Label(self.topframe, text="startTime: ").grid(row=6, sticky=W)
		self.L_TimeFormat1 = Label(self.topframe, text="(YYYY/MM/DD HH:MM:SS.ffffff)").grid(row=7, sticky=W)
		self.E_StartTime = Entry(self.topframe, state='disabled', width=width)
		self.E_StartTime.grid(row=6, column=1, sticky=E)

		self.L_StopTime = Label(self.topframe, text="stopTime: ").grid(row=8, sticky=W)
		self.L_TimeFormat2 = Label(self.topframe, text="(YYYY/MM/DD HH:MM:SS.ffffff)").grid(row=9, sticky=W)
		self.E_StopTime = Entry(self.topframe, state='disabled', width=width)
		self.E_StopTime.grid(row=8, column=1, sticky=E)

		self.L_UpdateFilter = Label(self.topframe, text="update-filter: ").grid(row=10, sticky=W)
		self.updateFilters = ("subtree", "None")
		self.SB_UpdateFilter = Spinbox(self.topframe, values=self.updateFilters, wrap=True, state='readonly', width=width-2)
		self.SB_UpdateFilter.grid(row=10, column=1, sticky=E)
		self.L_Criteria = Label(self.topframe, text="    criteria: ").grid(row=11, sticky=NW)
		self.T_Criteria = Text(self.topframe, height=8, width=width)
		self.T_Criteria.grid(row=11, column=1, sticky=E)

		self.L_SubStartTime = Label(self.topframe, text="subscription-start-time: ").grid(row=12, sticky=W)
		self.L_TimeFormat3 = Label(self.topframe, text="(YYYY/MM/DD HH:MM:SS.ffffff)").grid(row=13, sticky=W)
		self.E_SubStartTime = Entry(self.topframe, width=width)
		self.E_SubStartTime.grid(row=12, column=1, sticky=E)

		self.L_SubStopTime = Label(self.topframe, text="subscription-stop-time: ").grid(row=14, sticky=W)
		self.L_TimeFormat4 = Label(self.topframe, text="(YYYY/MM/DD HH:MM:SS.ffffff)").grid(row=15, sticky=W)
		self.E_SubStopTime = Entry(self.topframe, width=width)
		self.E_SubStopTime.grid(row=14, column=1, sticky=E)

		self.L_SubPriority = Label(self.topframe, text="subscription-priority: ").grid(row=16, sticky=W)
		self.E_SubPriority = Entry(self.topframe, state='disabled', width=width)
		self.E_SubPriority.grid(row=16, column=1, sticky=E)

		self.L_SubDependency = Label(self.topframe, text="subscription-dependency: ").grid(row=17, sticky=W)
		self.E_SubDependency = Entry(self.topframe, state='disabled', width=width)
		self.E_SubDependency.grid(row=17, column=1, sticky=E)

		self.L_UpdateTrigger = Label(self.topframe, text="update-trigger: ").grid(row=18, sticky=W)
		self.updateTriggers = ("periodic", "on-change")
		self.updateVar = StringVar()
		self.SB_UpdateTrigger = Spinbox(self.topframe, values=self.updateTriggers, wrap=True, state='readonly', textvariable=self.updateVar, width=width-2)
		self.SB_UpdateTrigger.grid(row=18, column=1, sticky=E)
		self.updateVar.trace("w", self.updateTriggerChange)
		
		self.L_Period = Label(self.topframe, text="    period (ms): ").grid(row=19, sticky=W)
		self.E_Period = Entry(self.topframe, width=width)
		self.E_Period.insert(END, "5000")
		self.E_Period.grid(row=19, column=1, sticky=E)

		self.L_NoSyncOnStart = Label(self.topframe, text="    no-synch-on-start: ").grid(row=20, sticky=W)
		self.varSync = IntVar()
		self.CB_NoSyncOnStart = Checkbutton(self.topframe, onvalue=1, offvalue=0, variable=self.varSync, state='disabled')
		self.CB_NoSyncOnStart.grid(row=20, column=1)

		self.L_DampeningPeriod = Label(self.topframe, text="    dampening-period (ms): ").grid(row=21, sticky=W)
		self.E_DampeningPeriod = Entry(self.topframe, state='disabled', width=width)
		self.E_DampeningPeriod.grid(row=21, column=1, sticky=E)

		self.L_ExcludedChange = Label(self.topframe, text="    excluded-change: ").grid(row=22, sticky=W)
		self.varCr = IntVar()
		self.varMod = IntVar()
		self.varDel = IntVar()
		self.CB_ExcludedChangeCr = Checkbutton(self.topframe, text="creation", onvalue=1, offvalue=0, variable=self.varCr, state='disabled')
		self.CB_ExcludedChangeCr.grid(row=22, column=1)
		self.CB_ExcludedChangeMod = Checkbutton(self.topframe, text="modify", onvalue=1, offvalue=0, variable=self.varMod, state='disabled')
		self.CB_ExcludedChangeMod.grid(row=23, column=1)
		self.CB_ExcludedChangeDel = Checkbutton(self.topframe, text="deletion", onvalue=1, offvalue=0, variable=self.varDel, state='disabled')
		self.CB_ExcludedChangeDel.grid(row=24, column=1)


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
		if self.subID == "":
			print("missing subscription ID")
			return
		if self.SB_Encoding.get() == "XML":
			self.encoding = "encode-xml"
		elif self.SB_Encoding.get() == "JSON":
			self.encoding = "encode-json"
		else:
			self.encoding = None

		if self.SB_Stream.get() != "None":
			self.stream = self.SB_Stream.get()
		else:
			self.stream = None

		if self.E_StartTime.get() != "":
			self.startTime = datetime.strptime(self.E_StartTime.get(), '%Y/%m/%d %H:%M:%S.%f')
		else:
			self.startTime = None

		if self.E_StopTime.get() != "":
			self.stopTime = datetime.strptime(self.E_StopTime.get(), '%Y/%m/%d %H:%M:%S.%f')
		else:
			self.stopTime = None

		self.updateFilter = self.SB_UpdateFilter.get()
		self.updateCriteria = self.T_Criteria.get('1.0', 'end')

		if self.updateFilter == "None" and self.updateCriteria != "\n":
			self.updateCriteria = None
			print("filter type not set")
			return
		elif self.updateFilter != "None" and self.updateCriteria != "\n":
			if self.updateFilter == "subtree":
				if self.updateCriteria[0] == "<":
					self.filterTuple = (self.updateFilter, self.updateCriteria)
				else:
					print("Criteria not in a proper format!")
					return
			else:
				if self.updateCriteria[0] != "<":
					self.filterTuple = (self.updateFilter, self.updateCriteria.rstrip('\n'))
				else:
					print("Criteria not in a proper format!")
					return
		else:
			self.filterTuple = None

		if self.E_SubStartTime.get() != "":
			self.subStartTime = datetime.strptime(self.E_SubStartTime.get(), '%Y/%m/%d %H:%M:%S.%f')
			print(self.subStartTime)
		else:
			self.subStartTime = None

		if self.E_SubStopTime.get() != "":
			self.subStopTime = datetime.strptime(self.E_SubStopTime.get(), '%Y/%m/%d %H:%M:%S.%f')
		else:
			self.subStopTime = None			

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
			self.noSynchOnStart = None
			self.excludeStr = None
		else:
			self.noSynchOnStart = self.varSync.get()
			if self.noSynchOnStart == 0:
				self.noSynchOnStart = None
			self.period = self.E_DampeningPeriod.get()
			if self.period == "":
				print("dampeningPeriod mandatory")
				return
			if self.varCr.get():
				self.exclude.append("create")
			if self.varMod.get():
				self.exclude.append("modify")
			if self.varDel.get():
				self.exclude.append("delete")
			self.excludeStr = ', '.join(self.exclude)
			if self.excludeStr == "":
				self.excludeStr = None
				
		self.session = self.controller.get_Session(self.host, self.user, self.password)

		self.rpc_reply = self.session[0].modify_subscription(
			callback=self.controller.callback, 
			errback=self.controller.errback,
			subID=self.subID,
			notifListening=self.session[1],
			encoding=self.encoding, 
			stream=self.stream, 
			start_time=self.startTime, 
			stop_time=self.stopTime, 
			update_filter=self.filterTuple,	
			sub_start_time=self.subStartTime, 
			sub_stop_time=self.subStopTime,	
			priority=self.subPriority, 
			dependency=self.subDependency, 
			update_trigger=self.updateTrigger, 
			period=self.period, 
			no_synch_on_start=self.noSynchOnStart, 
			excluded_change=self.excludeStr)
		
		xmlroot = ET.fromstring(self.rpc_reply.xml)	
		
		for child in xmlroot:
			if child.tag[-len("subscription-result"):] == "subscription-result":
				self.result = child.text
		
		if self.result == "ok":
			self.controller.add_to_treeview(
				subID=self.subID, 
				server=self.host, 
				stream=self.stream, 
				encoding=self.encoding, 
				updateTrigger=self.updateTrigger, 
				period=self.period, 
				filter=self.updateCriteria, 
				startTime=self.startTime, 
				stopTime=self.stopTime, 
				subStartTime=self.subStartTime, 
				subStopTime=self.subStopTime, 
				priority=self.subPriority, 
				dependency=self.subDependency)
			
			self.close_window()
		else:
			print("subscription-result: " + self.result)

	def updateTriggerChange(self, a, b, c):
		if self.SB_UpdateTrigger.get() == "periodic":
			intvar = self.E_DampeningPeriod.get()
			self.E_DampeningPeriod.delete(0,END)
			self.E_DampeningPeriod.configure(state='disabled')
			self.CB_NoSyncOnStart.configure(state='disabled')
			self.E_Period.configure(state='normal')
			self.E_Period.insert(0, intvar)
		else:
			intvar = self.E_Period.get()
			self.E_Period.delete(0,END)
			self.E_Period.configure(state='disabled')
			self.CB_NoSyncOnStart.configure(state='normal')
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
	
		self.session = self.controller.get_Session(self.host, self.user, self.password)
		
		if self.subID == "":
			print("Missing subscription-ID!")
			return
		else:
			# if subscription is complete the subscription is already removed from the server.
			# a delete subscription RPC would cause an error in that case.
			if self.controller.tree.set(self.subID, column="Status") != "complete":
				self.rpc_reply = self.session[0].delete_subscription(self.subID)
			self.controller.tree.delete(self.subID)
			for entry in self.controller.filters:
				if entry[0] == self.subID:
					self.controller.filters.remove(entry)
					break
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

		self.session = self.controller.get_Session(self.host, self.user, self.password)
		
		FILTERXML = """<subscriptions xmlns="urn:ietf:params:xml:ns:yang:ietf-event-notifications"></subscriptions>"""
		FILTERXMLID = """<subscriptions xmlns="urn:ietf:params:xml:ns:yang:ietf-event-notifications"><subscription><subscription-id>%s</subscription-id></subscription></subscriptions>""" % self.subID

		if self.subID == "":
			self.rpc_reply = self.session[0].get_subscription(
				callback=self.controller.callback, 
				errback=self.controller.errback, 
				notifListening=self.session[1], 
				filter=("subtree", FILTERXML))
			singlenode = False
		else:
			self.rpc_reply = self.session[0].get_subscription(
				callback=self.controller.callback, 
				errback=self.controller.errback, 
				notifListening=self.session[1], 
				filter=("subtree", FILTERXMLID))
			singlenode = True	
		
		self.controller.add_subscriptions(singlenode, self.rpc_reply, self.host)

		self.close_window()

	def close_window(self):
		self.master.destroy()

class FilterMessageBox:
	def __init__(self, master, controller, subID, filter):
		self.master = master
		self.topframe = tk.Frame(self.master)
		self.controller = controller
		self.subID = subID
		self.filter = filter

		self.L_Title = Label(self.topframe, text="Subscription-ID " + self.subID + " - filter:").grid(row=0, sticky=W)
		self.L_Filter = Label(self.topframe, text=self.filter).grid(row=1, sticky=W)
		
		self.quitButton = tk.Button(self.topframe, text = 'Cancel', width = 10, command = self.close_window)
		self.quitButton.grid(row=2)
		
		self.topframe.grid(row=0)
				
	def close_window(self):
		self.master.destroy()				

def main(): 
	root = tk.Tk()
	root.title("NCClient")
	app = MainApplication(root)
	root.mainloop()

if __name__ == '__main__':
	main()