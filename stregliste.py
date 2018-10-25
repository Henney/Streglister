#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import datetime
from Tkinter import *
import math

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'

DEBUG = True

class Stregliste:

	def __init__(self):
		self.undo_stack = []
		
		self.SPREADSHEET_ID = '192q8v_qMEnIrfBtXEKS5BnGDOqvtIL5gl3_0aKD8WUg'
	
		self.reauth()
		
		self.sheet = self.service.spreadsheets().values()
		self.sheet_name = 'Bestyrelsessommerhus (2018-09-28/29)'
		# sheet_name = '(' + datetime.date.today() + ')'
		
		self.init_bartenders_and_drinks()
	
	def reauth(self):
		store = file.Storage('token.json')
		creds = store.get()
		if not creds or creds.invalid:
			flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
			creds = tools.run_flow(flow, store)
		self.service = build('sheets', 'v4', http=creds.authorize(Http()))
		
		
	def init_bartenders_and_drinks(self):		
		result = self.sheet.get(spreadsheetId=self.SPREADSHEET_ID, range=self.sheet_name).execute()
		values = result.get('values', [])
		
		x_offset = 5
		y_offset = 2
		self.bartenders = [x[0] for x in values[y_offset:] if x[0] != '']
		self.drinks = [x for x in values[1][x_offset:] if x != '']
		
		self.recorded = {}
		i = y_offset
		for bartender in self.bartenders:
			self.recorded[bartender] = {}
			j = x_offset
			for drink in self.drinks:
				try:
					self.recorded[bartender][drink] = values[i][j]
				except:
					self.recorded[bartender][drink] = 0
				j = j + 1
			i = i + 1

	def add_drink(self, bartender, drink, amount=1):
		if DEBUG:
			bartender = 'Test'
	
		range_name = self.sheet_name
		
		result = self.sheet.get(spreadsheetId=self.SPREADSHEET_ID, range=range_name).execute()
		values = result.get('values', [])
		
		for i in range(len(values)):
			if values[i][0] == bartender:
				row_no = i
				break
		
		for i in range(len(values[1])):
			if drink in values[1][i]:
				col_no = i
				break
		
		try:
			number = int(values[row_no][col_no]) + amount if values[row_no][col_no] else amount
		except:
			number = amount
			
		# Handle below 0
		number = max(0, number)
				
		cell = str(unichr(ord('A') + col_no)) + str(row_no + 1)
		range_name = range_name + '!' + cell
		
		print(range_name)
		
		self.sheet.update(spreadsheetId=self.SPREADSHEET_ID, range=range_name, valueInputOption='RAW', body={ 'values': [[str(number)]] }).execute()
		self.recorded[bartender][drink] = str(number)
		
		self.undo_stack.append((bartender, drink, amount))
		
	def undo():
		pass # TODO
		
		
class GUI:
	
	def __init__(self, stregliste):
		top = Tk()
		top.attributes('-fullscreen', True)
		self.screen_width = top.winfo_screenwidth()
		self.screen_height = top.winfo_screenheight()
		
		self.stregliste = stregliste		
		amount = len(self.stregliste.bartenders)
		
		max_row = 0
		self.button_texts = {}
		i = 0
		for bartender in self.stregliste.bartenders:
			(row, col) = self.calc_layout(i, amount)
			max_row = max(row, max_row)
			Grid.rowconfigure(top, row, weight=1)
			Grid.columnconfigure(top, col, weight=1)
			text = StringVar()
			text.set(bartender)
			# We set a dummy height so that the button doesn't scale with its contents
			b = Button(top, height=10, width=10, textvariable=text, command=lambda bartender=bartender: self.drink_menu(bartender))
			self.set_text(text)
			b.grid(row=row, column=col, sticky=N+S+E+W)
			self.button_texts[bartender] = text
			i = i + 1
			
		Grid.columnconfigure(top, col+1, weight=col/2)
		Label(top, text="LOG", justify=CENTER, font=("Helvetica", self.screen_height/15, "bold")).grid(row=0, column=col+1)
		
		self.log = StringVar()
		Label(top, textvariable=self.log, font=("Helvetica", self.screen_height/60, "bold"), anchor=N, height=20).grid(row=1, column=col+1, rowspan=max_row-1)
		
		top.mainloop()

	def drink_menu(self, bartender):
		menu = Toplevel()
		menu.attributes('-fullscreen', True)
		Grid.columnconfigure(menu, 0, weight=1)
		Grid.rowconfigure(menu, 0, weight=1)
		Grid.rowconfigure(menu, 1, weight=2)
		Grid.rowconfigure(menu, 2, weight=8)		
		
		name_frame = Frame(menu)
		name_frame.grid(row=0, column=0, sticky=N+S+E+W)
		Grid.columnconfigure(name_frame, 0, weight=1)
		Grid.columnconfigure(name_frame, 0, weight=1)
		Label(name_frame, text=bartender, justify=CENTER, font=("Helvetica", self.screen_height/15)).grid(row=0, column=0, sticky=N+S+E+W)
		
		amount_grid = Frame(menu)
		amount_grid.grid(row=1, column=0, sticky=N+S+E+W)
		
		grid = Frame(menu)
		grid.grid(row=2, column=0, sticky=N+S+E+W)
		
		Grid.rowconfigure(amount_grid, 0, weight=1)
		
		amount = StringVar()
		amount.set("1")
		self.amount_text = Entry(amount_grid, width=20, font=("Helvetica", self.screen_height/30), textvariable=amount, justify=CENTER)
		self.amount_text.grid(row=0, column=3, sticky=N+S+E+W)
		self.amount_text.config(state=DISABLED)
		
		i = 0
		for x in [-10, -5, -1, 0, 1, 5, 10]: # 0 is placeholder for the entry field
			if x != 0:
				Button(amount_grid, text=str(x) if x < 0 else "+" + str(x), command=lambda x=x: self.set_amount(x)).grid(row=0, column=i, sticky=N+S+E+W)
			Grid.columnconfigure(amount_grid, i, weight=1)
			i = i + 1
			
		i = 0
		for drink in self.stregliste.drinks:
			(row, col) = self.calc_layout(i, len(self.stregliste.drinks))
			Grid.rowconfigure(grid, row, weight=1)
			Grid.columnconfigure(grid, col, weight=1)
			b = Button(grid, text=drink, command=lambda drink=drink, menu=menu: self.add_drink(bartender, drink, menu))
			b.grid(row=row, column=col, sticky=N+S+E+W)
			i = i + 1
			
		(row, col) = (row + 1, 0)
		Grid.rowconfigure(grid, row, weight=1)
		b = Button(grid, text='Annuller', command=lambda menu=menu: menu.destroy())
		b.grid(row=row, column=col, sticky=N+S+E+W)
			
		menu.mainloop()
		
	def set_amount(self, value):
		self.amount_text.config(state=NORMAL)
		current = self.amount_text.get()
		self.amount_text.delete(0, END)
		self.amount_text.insert(0, str(int(current) + value))
		self.amount_text.config(state=DISABLED)
		
	def set_text(self, text):
		value = text.get()
		bartender = text.get().split("\n")[0]
		record = self.stregliste.recorded[bartender]
		text.set(bartender + "".join(["\n" + drink + ": " + str(amount) for drink, amount in record.iteritems() if amount > 0 and amount != ""]))
		
	def add_drink(self, bartender, drink, menu):
		amount = self.amount_text.get()
		self.stregliste.add_drink(bartender, drink, int(amount))
		self.set_text(self.button_texts[bartender])
		self.log.set(u"%s skrev %s på %s\n%s" % (bartender, amount, drink, self.log.get()))
		menu.destroy()
		
	def calc_layout(self, i, amount, extra_space=False):
		rows = int(math.sqrt(amount))
		row = i % rows + (1 if extra_space else 0) # Add 1 to make way for amount selection
		col = i / rows
		return (row, col)
		
def main():
	stregliste = Stregliste()
	gui = GUI(stregliste)
	

if __name__ == '__main__':
	main()