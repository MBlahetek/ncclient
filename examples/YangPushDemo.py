from Tkinter import *
from ncclient import manager
from ncclient.operations.subscribe_yangpush import *
import sys, os, warnings
import Tkinter as tk
import ttk
import tkFont

class MainApplication:
	def __init__(self, master):
		self.master = master

		self.calc_window_size(self.master)

		self.mainframe = tk.Frame(self.master)
		self.buttonframe = tk.Frame(self.master)
		self.tree = ttk.Treeview(self.mainframe)
		self.tree['show'] = 'headings'

		self.tree["columns"]=("Server","Subscription ID", "Status")
		self.tree.column("Server", width=300 )
		self.tree.column("Subscription ID", width=300)
		self.tree.column("Status", width=300)
		self.tree.heading("Server", text="Server")
		self.tree.heading("Subscription ID", text="Subscription ID")
		self.tree.heading("Status", text="Status")

		self.tree.grid()

		self.mainframe.grid()

		self.B_NewSubscription = tk.Button(self.buttonframe, text="New Subscription", command=self.new_Subscription).grid(row=1, column=0)
		self.B_GetSubscription = tk.Button(self.buttonframe, text="Get Subscription", command=self.get_Subscription).grid(row=1, column=1, sticky=E)

		self.buttonframe.grid()

		self.subscriptions = []



	def callback(self, notification):
		print("callback called")
		print(notification)
		print(notification.data_xml)

	def errback(self, ex):
		print("errback called")
		print(ex)

	def add_Subscription(self, rpcReply, server):
		#extract the subID out of the rpcReply XML file
		self.subID = rpcReply
		self.tree.insert(parent="", index="end", iid=self.subID, 
			values=(server, self.subID, "active"))

	def get_Subscription(self):
		self.newWindow = tk.Toplevel(self.master)
		self.app = NewSubscriptionWindow(self.newWindow, self)

	def update_Subscription(self):
		""" .set(iid, column=None, value=None)
		Use this method to retrieve or set the column values of the item specified by iid. 
		With one argument, the method returns a dictionary: the keys are the column identifiers, 
		and each related value is the text in the corresponding column.

		With two arguments, the method returns the data value from the column of 
		the selected item whose column identifier is the column argument. With three arguments, 
		the item's value for the specified column is set to the third argument.
		"""

	def calc_window_size(self, master):

		self.screen_width = master.winfo_screenwidth()
		self.screen_height = master.winfo_screenheight()
		if self.screen_width > 2100 and self.screen_height > 1200:
			self.default_font = tkFont.nametofont("TkDefaultFont")
			self.default_font.configure(size=11)
			self.master.option_add("*Font", self.default_font)
			self.default_style = ttk.Style()
			self.default_style.configure(".", font=("Helvetica",11))
			self.default_style.configure("Treeview", font=("Helvetica", 11))
			self.default_style.configure("Treeview.Heading", font=("Helvetica", 11))

	def new_Subscription(self):
		self.newWindow = tk.Toplevel(self.master)
		self.app = NewSubscriptionWindow(self.newWindow, self)

class NewSubscriptionWindow:
	def __init__(self, master, controller):
		self.master = master
		self.topframe = tk.Frame(self.master)
		self.bottomframe = tk.Frame(self.master)
		self.controller = controller

		self.L_ServerIP = Label(self.topframe, text="Server IP: ").grid(row=0, column=0, sticky=W)
		self.E_ServerIP = Entry(self.topframe)
		self.E_ServerIP.grid(row=0, column=1, sticky=E)

		self.L_UserName = Label(self.topframe, text="User Name: ").grid(row=1, column=0, sticky=W)
		self.E_UserName = Entry(self.topframe)
		self.E_UserName.grid(row=1, column=1, sticky=E)

		self.L_Password = Label(self.topframe, text="Password: ").grid(row=2, column=0, sticky=W)
		self.E_Password = Entry(self.topframe, show="*")
		self.E_Password.grid(row=2, column=1, sticky=E)

		self.L_Encoding = Label(self.topframe, text="encoding: ").grid(row=3, sticky=W)
		self.E_Encoding = Entry(self.topframe)
		self.E_Encoding.grid(row=3, column=1, sticky=E)

		self.L_Stream = Label(self.topframe, text="stream: ").grid(row=4, sticky=W)
		self.E_Stream = Entry(self.topframe)
		self.E_Stream.grid(row=4, column=1, sticky=E)

		self.L_StartTime = Label(self.topframe, text="startTime: ").grid(row=5, sticky=W)
		self.E_StartTime = Entry(self.topframe)
		self.E_StartTime.grid(row=5, column=1, sticky=E)

		self.L_StopTime = Label(self.topframe, text="stopTime: ").grid(row=6, sticky=W)
		self.E_StopTime = Entry(self.topframe)
		self.E_StopTime.grid(row=6, column=1, sticky=E)

		self.L_UpdateFilter = Label(self.topframe, text="update-filter: ").grid(row=7, sticky=W)
		self.updateFilters = ("subtree", "xpath")
		self.SB_UpdateFilter = Spinbox(self.topframe, values=self.updateFilters, wrap=True, state='readonly')
		self.SB_UpdateFilter.grid(row=7, column=1, sticky=E)
		self.L_XPath = Label(self.topframe, text="    xpath: ").grid(row=8, sticky=W)
		self.E_XPath = Entry(self.topframe)
		self.E_XPath.grid(row=8, column=1, sticky=E)

		self.L_SubStartTime = Label(self.topframe, text="subscription-start-time: ").grid(row=9, sticky=W)
		self.E_SubStartTime = Entry(self.topframe)
		self.E_SubStartTime.grid(row=9, column=1, sticky=E)

		self.L_SubStopTime = Label(self.topframe, text="subscription-stop-time: ").grid(row=10, sticky=W)
		self.E_SubStopTime = Entry(self.topframe)
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
		self.SB_UpdateTrigger = Spinbox(self.topframe, values=self.updateTriggers, wrap=True, state='readonly')
		self.SB_UpdateTrigger.grid(row=14, column=1, sticky=E)
		
		self.L_Period = Label(self.topframe, text="    period: ").grid(row=15, sticky=W)
		self.E_Period = Entry(self.topframe)
		self.E_Period.grid(row=15, column=1, sticky=E)

		self.L_NoSyncOnStart = Label(self.topframe, text="    no-synch-on-start: ").grid(row=16, sticky=W)
		self.CB_NoSyncOnStart = Checkbutton(self.topframe, onvalue=1, offvalue=0)
		self.CB_NoSyncOnStart.grid(row=16, column=1)

		self.L_DampeningPeriod = Label(self.topframe, text="    dampening-period: ").grid(row=17, sticky=W)
		self.E_DampeningPeriod = Entry(self.topframe)
		self.E_DampeningPeriod.grid(row=17, column=1, sticky=E)

		self.L_ExcludedChange = Label(self.topframe, text="    excluded-change: ").grid(row=18, sticky=W)
		self.CB_ExcludedChangeCr = Checkbutton(self.topframe, text="creation", onvalue=1, offvalue=0)
		self.CB_ExcludedChangeCr.grid(row=18, column=1)
		self.CB_ExcludedChangeMod = Checkbutton(self.topframe, text="modify", onvalue=1, offvalue=0)
		self.CB_ExcludedChangeMod.grid(row=19, column=1)
		self.CB_ExcludedChangeDel = Checkbutton(self.topframe, text="deletion", onvalue=1, offvalue=0)
		self.CB_ExcludedChangeDel.grid(row=20, column=1)


		self.sendButton = tk.Button(self.bottomframe, text = 'Send', width = 10, command = self.send_request)
		self.sendButton.grid(row=0,column=0)
		self.quitButton = tk.Button(self.bottomframe, text = 'Cancel', width = 10, command = self.close_windows)
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

		if self.E_StartTime.get() != "":
			self.startTime = self.E_StartTime.get()
		else:
			self.startTime = None

		if self.E_StopTime.get() != "":
			self.stopTime = self.E_StopTime.get()
		else:
			self.stopTime = None

		self.updateFilter = self.SB_UpdateFilter.get()

		if self.updateFilter == "subtree":
			self.filterTuple = (self.updateFilter, ())
		else:
			self.filterTuple = (self.SB_UpdateFilter.get(), self.E_XPath.get())

		if self.E_SubStartTime.get() != "":
			self.subStartTime = self.E_SubStartTime.get()
		else:
			self.subStartTime = None

		if self.E_SubStopTime.get() != "":
			self.subStopTime = self.E_SubStopTime.get()
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
			self.exclude = None
		else:
			self.noSyncOnStart = self.CB_NoSyncOnStart.get()
			self.period = self.E_DampeningPeriod()
			if self.oeriod == "":
				print("dampeningPeriod mandatory")
				return
			if self.CB_ExcludedChangeCr.get():
				self.exclude.append("creation")
			if self.CB_ExcludedChangeMod.get():
				self.exclude.append("modify")
			if self.CB_ExcludedChangeDel.get():
				self.exclude.append("deletion")

		self.session = manager.connect(host=self.host, port=2830, username=self.user, 
			password=self.password, hostkey_verify=False, look_for_keys=False, allow_agent=False)

		#----------------------------------------------
		self.controller.add_Subscription("101", self.host)
		#----------------------------------------------

		self.rpc_reply = self.session.establish_subscription(callback=self.controller.callback, 
			errback=self.controller.errback, manager=self.session, encoding=self.encoding, 
			stream=self.stream, start_time=self.startTime, stop_time=self.stopTime, 
			update_filter=self.filterTuple,	sub_start_time=self.subStartTime, 
			sub_stop_time=self.subStopTime,	dscp=self.dscp, priority=self.subPriority, 
			dependency=self.subDependency, update_trigger=self.updateTrigger, period=self.period, 
			no_sync_on_start=self.noSyncOnStart, excluded_change=self.exclude)

		print(self.rpc_reply)

		#if self.rpc_reply == "ok":
		#	self.controller.add_Subscription(self.rpc_reply, self.host)
		#	self.master.destroy()
		#else:
		#	print("Failed to subscribe!")

	def close_windows(self):
		self.master.destroy()

def main(): 
	root = tk.Tk()
	root.title("NCClient")
	app = MainApplication(root)
	root.mainloop()

if __name__ == '__main__':
	main()