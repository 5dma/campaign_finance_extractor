import os
import re
from enum import Enum
class LineType(Enum):
	UNKNOWN = 0
	EXPENSE_NAME = 1
	EXPENSE_FULL_ADDRESS = 2
	EXPENSE_ADDRESS1 = 3
	EXPENSE_ADDRESS2 = 4
	EXPENSE_SECTION = 5

class Expense:
	def __init__(self):
		date = None
		name = None
		full_address = None
		address_line_1 = None
		address_line_2 = None
		city = None
		state = None
		zip_code = None
		method = None
		amount = None
		purpose = None
		

	def write_record(self):
		print("Date: {0}\nMethod: {1}\nName: {2}\nAmount: {3}\nFull Address: {4}\nPurpose: {5}".format(self.date,self.method,self.name,self.amount,self.full_address, self.purpose))
		address_components = self.full_address.split(', ')
		if (len(address_components) == 3):
			self.address_line_1 = address_components[0]
			self.address_line_2 = ''
			self.city = address_components[1]
			m = expenditure_state_zip.match(address_components[2])
			self.state = m.group(1)
			self.zip_code = m.group(2)
		else:
			self.address_line_1 = address_components[0]
			self.address_line_2 = address_components[1]
			self.city = address_components[2]
			m = expenditure_state_zip.match(address_components[3])
			self.state = m.group(1)
			self.zip_code = m.group(2)

		huge_line = "\t".join([self.name,self.address_line_1,self.address_line_2,self.city,self.state,self.zip_code,self.method,self.amount,self.purpose])
		print(huge_line,file=csv_file)


	def reset(self):
		date = None
		name = None
		full_address = None
		address_line_1 = None
		address_line_2 = None
		city = None
		state = None
		zip_code = None
		method = None
		amount = None
		purpose = None


TEXT_FILE = '/tmp/extracted_text.txt'
CSV_FILE = '/tmp/campaign_finance.csv'
os.system('pdftotext -nopgbrk -layout report_2022-11-16_to_2023-01-11.pdf ' + TEXT_FILE)
file = open(TEXT_FILE, 'r')
Lines = file.readlines()
file.close()
csv_file = open(CSV_FILE,'w')
expenditure_section = re.compile('^ {71}Expenditures')
expenditure_name = re.compile('^ {7}(\d{2}/\d{2}/\d{4}) (\w*)(.*)\$([\d.,]*)')
expenditure_street_city = re.compile('^ {41}(.*),')
expenditure_state_zip = re.compile('^([A-Za-z ]+)(\d+)')
#expenditure_state_zip = re.compile('^ {41}([A-Za-z ]+)(\d+)')
expenditure_purpose = re.compile('^Expenditure Purpose:(.*)')
expenditure_full_address = re.compile('^ {41}(.*)|^ {18}Card/Visa(.*)')

line_type = LineType.UNKNOWN

expense = Expense()
for line in Lines:
	if (line_type == LineType.UNKNOWN) and expenditure_section.match(line):
		line_type = LineType.EXPENSE_SECTION
		continue
	if (line_type == LineType.EXPENSE_SECTION) and expenditure_name.match(line):
		m = expenditure_name.match(line)
		line_type = LineType.EXPENSE_NAME
		expense.date = m.group(1)
		expense.method = m.group(2)
		expense.name = m.group(3).strip()
		expense.amount = m.group(4)
		continue
	if (line_type == LineType.EXPENSE_NAME) and expenditure_full_address.match(line):
		m = expenditure_full_address.match(line)
		line_type = LineType.EXPENSE_FULL_ADDRESS
		expense.full_address = m.group(1).strip() if m.group(1) != None else m.group(2).strip()
		continue
	if line_type == LineType.EXPENSE_FULL_ADDRESS and expenditure_full_address.match(line):
		m = expenditure_full_address.match(line)
		line_type = LineType.EXPENSE_FULL_ADDRESS
		expense.full_address = expense.full_address + ' ' + m.group(1).strip()
		continue
	if line_type == LineType.EXPENSE_FULL_ADDRESS and expenditure_purpose.match(line):
		m = expenditure_purpose.match(line)
		line_type = LineType.EXPENSE_SECTION
		expense.purpose=m.group(1).strip()
		expense.write_record()
		expense.reset()
		continue
	

csv_file.close()
