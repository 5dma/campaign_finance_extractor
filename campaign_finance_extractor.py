import os
import re
from enum import Enum
class LineType(Enum):
	UNKNOWN = 0
	EXPENSE_NAME = 1
	EXPENSE_STREET_CITY = 1
	EXPENSE_STATE_ZIP = 1
	EXPENSE_SECTION = 1

class Expense:
	def __init__(self):
		date = None
		name = None
		street = None
		city = None
		state = None
		zip_code = None
		method = None
		amount = None
		purpose = None
		
	def print_name(self):
		print("Date: {0}\nMethod: {1}\nName: {2}\nAmount: {3}".format(self.date,self.method,self.name,self.amount))

	def print_more(self):
		print("Date: {0}\nMethod: {1}\nName: {2}\nAmount: {3}\nAddress 1: {4}\nCity: {5}".format(self.date,self.method,self.name,self.amount,self.street, self.city))

	def print_more2(self):
		print("Date: {0}\nMethod: {1}\nName: {2}\nAmount: {3}\nAddress 1: {4}\nCity: {5}\nState: {6}\nZip: {7}".format(self.date,self.method,self.name,self.amount,self.street, self.city, self.state, self.zip_code))

	def print_more3(self):
		print("Date: {0}\nMethod: {1}\nName: {2}\nAmount: {3}\nAddress 1: {4}\nCity: {5}\nState: {6}\nZip: {7}\nPurpose: {8}".format(self.date,self.method,self.name,self.amount,self.street, self.city, self.state, self.zip_code, self.purpose))
	def set_street_city(self,street_city):
		[street,city] = street_city.split(", ")
		self.street = street
		self.city = city
	def set_state_zip(self,state,zip_code):
		self.state = state.strip()
		self.zip_code= zip_code


TARGET_FILE = '/tmp/extracted_text.txt'
os.system('pdftotext -nopgbrk -layout report_2022-11-16_to_2023-01-11.pdf ' + TARGET_FILE)
file = open(TARGET_FILE, 'r')
Lines = file.readlines()
file.close()
expenditure_section = re.compile('^ {71}Expenditures')
expenditure_name = re.compile('^ {7}(\d{2}/\d{2}/\d{4}) (\w*)(.*)\$([\d.,]*)')
expenditure_street_city = re.compile('^ {41}(.*),')
expenditure_state_zip = re.compile('^ {41}([A-Za-z ]+)(\d+)')
expenditure_purpose = re.compile('^Expenditure Purpose:(.*)')

line_type = LineType.UNKNOWN

expense = Expense()
for line in Lines:
	if line_type == LineType.UNKNOWN and expenditure_section.match(line):
		print("Matrch")
		line_type = LineType.EXPENSE_SECTION
	if line_type == LineType.EXPENSE_SECTION and expenditure_name.match(line):
		m = expenditure_name.match(line)
		line_type = LineType.EXPENSE_NAME
		print("Entry")
		#print(m.group(1))
		#print(m.group(2))
		#print(m.group(3).strip())
		#print(m.group(4))
		expense.date = m.group(1)
		expense.method = m.group(2)
		expense.name = m.group(3).strip()
		expense.amount = m.group(4)
		#expense.print_name()
		#print(expense)
	if line_type == LineType.EXPENSE_NAME and expenditure_street_city.match(line):
		print("match_street_city")
		m = expenditure_street_city.match(line)
		line_type = LineType.EXPENSE_STREET_CITY
		expense.set_street_city(m.group(1))
		#expense.print_more()
		#print("address1")
		#print(m.group(1))
	if line_type == LineType.EXPENSE_STREET_CITY and expenditure_state_zip.match(line):
		print("match_state_zip")
		m = expenditure_state_zip.match(line)
		line_type = LineType.EXPENSE_STATE_ZIP
		expense.set_state_zip(m.group(1),m.group(2))
		#expense.print_more2()
	if line_type == LineType.EXPENSE_STATE_ZIP and expenditure_purpose.match(line):
		m = expenditure_purpose.match(line)
		line_type = LineType.EXPENSE_SECTION
		expense.purpose=m.group(1).strip()
		expense.print_more3()
	

