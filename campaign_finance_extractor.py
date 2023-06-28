#!/bin/python3
import os
import re
from enum import Enum
import csv
import sys

class LineType(Enum):
	UNKNOWN = 0
	EXPENSE_NAME = 1
	EXPENSE_FULL_ADDRESS = 2
	EXPENSE_SECTION = 3
	CONTRIBUTION_SECTION = 4
	CONTRIBUTION_NAME = 5
	CONTRIBUTION_FULL_ADDRESS = 6


class Transaction:
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

class Contribution(Transaction):
	def __init__(self):
		aggregate_to_date = None

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
		aggregate_to_date = None

	def write_record(self):
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

		writer_contribution.writerow({'Name':self.name,'Address Line 1':self.address_line_1,'Address Line 2':self.address_line_2,'City':self.city,'State':self.state,'Zip':self.zip_code,'Method':self.method,'Amount':self.amount,'Aggregate to Date':self.aggregate_to_date,'Category':'Contribution','Report':PDF_FILE})

class Expense(Transaction):
	def __init__(self):
		purpose = None
		

	def write_record(self):
		address_components = self.full_address.split(', ')
		#print(self.full_address)
		if (len(address_components) == 1):
			self.address_line_1 = address_components[0]
			self.address_line_2 = ''
			self.city = ''
			self.state = ''
			self.zip_code = ''
		if (len(address_components) == 3):
			self.address_line_1 = address_components[0]
			self.address_line_2 = ''
			self.city = address_components[1]
			m = expenditure_state_zip.match(address_components[2])
			try:
				self.state = m.group(1)
				self.zip_code = m.group(2)
			except AttributeError:
				self.state = ''
				self.zip_code = ''

		if (len(address_components) == 4):
			self.address_line_1 = address_components[0]
			self.address_line_2 = address_components[1]
			self.city = address_components[2]
			m = expenditure_state_zip.match(address_components[3])
			self.state = m.group(1)
			self.zip_code = m.group(2)

		writer_expense.writerow({'Name':self.name,'Address Line 1':self.address_line_1,'Address Line 2':self.address_line_2,'City':self.city,'State':self.state,'Zip':self.zip_code,'Method':self.method,'Amount':self.amount,'Purpose':self.purpose,'Category':'Expenditure','Report':PDF_FILE})


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


if len(sys.argv) < 2:
	print("\nUsage:\npython3 campaign_finance_extractor.py <path_to_pdf>\n")
	sys.exit()

TEXT_FILE = '/tmp/extracted_text.txt'
CSV_FILE_EXPENSE = '/tmp/campaign_finance_expense.csv'
CSV_FILE_CONTRIBUTE = '/tmp/campaign_finance_contributions.csv'
PDF_FILE = sys.argv[1]
pdftotext_command = 'pdftotext -nopgbrk -layout {0} {1} '.format(PDF_FILE, TEXT_FILE)
os.system(pdftotext_command)
file = open(TEXT_FILE, 'r')
Lines = file.readlines()
file.close()

csv_file_expense = open(CSV_FILE_EXPENSE,'w')
fieldnames_expense = ['Name','Address Line 1','Address Line 2','City','State','Zip','Method','Amount','Purpose','Category','Report']
writer_expense = csv.DictWriter(csv_file_expense, fieldnames=fieldnames_expense,delimiter='\t')
writer_expense.writeheader()

csv_file_contribution = open(CSV_FILE_CONTRIBUTE,'w')
fieldnames_contribution = ['Name','Address Line 1','Address Line 2','City','State','Zip','Method','Amount','Aggregate to Date','Category','Report']
writer_contribution = csv.DictWriter(csv_file_contribution, fieldnames=fieldnames_contribution,delimiter='\t')
writer_contribution.writeheader()

expenditure_section = re.compile('^ {60,80}Expenditures')
expenditure_name = re.compile('^ {7}(\d{2}/\d{2}/\d{4}) (\w*)(.*)\$([\d.,]*)')
expenditure_state_zip = re.compile('^([A-Za-z ]+)(\d+)')
expenditure_purpose = re.compile('^Expenditure Purpose:(.*)')
expenditure_full_address = re.compile('^ {41}(.*)|^ {18}Card/Visa(.*)')

contribution_section = re.compile('^ {49}Expenditures')
contribution_name = re.compile('^ {7}(\d{2}/\d{2}/\d{4}) (.*)\$([\d.,]+) ([\w ]+)\$([\d.,]+)')
contribution_full_address = re.compile('^ {18}([\S ]{,63})')
contribution_end = re.compile('^$')
contribution_in_kind = re.compile('^ {7}(\d{2}/\d{2}/\d{4}) (.{30})\s*\$([\d.,]+)\s+\$([\d.,]+).*')

line_type = LineType.UNKNOWN

expense = Expense()
contribution = Contribution()
totals = {"Contributions": 0, "Expenses": 0}


for line in Lines:
	if expenditure_section.match(line):
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
		totals['Expenses'] += float(expense.amount.replace(',',''))
		expense.write_record()
		expense.reset()
		continue
	if contribution_section.match(line):
		line_type = LineType.CONTRIBUTION_SECTION
		continue
	if (line_type == LineType.CONTRIBUTION_SECTION) and contribution_name.match(line):
		m = contribution_name.match(line)
		line_type = LineType.CONTRIBUTION_NAME
		contribution.date = m.group(1)
		contribution.name = m.group(2).strip()
		contribution.aggregate_to_date= m.group(3).strip()
		contribution.method = m.group(4).strip()
		contribution.amount = m.group(5)
		continue
	if line_type == LineType.CONTRIBUTION_FULL_ADDRESS and contribution_name.match(line):
		totals['Contributions'] += float(contribution.amount.replace(',',''))
		contribution.write_record()
		m = contribution_name.match(line)
		line_type = LineType.CONTRIBUTION_NAME
		contribution.date = m.group(1)
		contribution.name = m.group(2).strip()
		contribution.aggregate_to_date= m.group(3).strip()
		contribution.method = m.group(4).strip()
		contribution.amount = m.group(5)
		contribution.reset()
		continue
	if (line_type == LineType.CONTRIBUTION_NAME) and contribution_full_address.match(line):
		m = contribution_full_address.match(line)
		line_type = LineType.CONTRIBUTION_FULL_ADDRESS
		contribution.full_address = m.group(1).strip()
		continue
	if line_type == LineType.CONTRIBUTION_FULL_ADDRESS and contribution_full_address.match(line):
		m = contribution_full_address.match(line)
		line_type = LineType.CONTRIBUTION_FULL_ADDRESS
		contribution.full_address += ' ' + m.group(1).strip()
		continue
	if line_type == LineType.CONTRIBUTION_FULL_ADDRESS and contribution_end.match(line):
		m = expenditure_purpose.match(line)
		line_type = LineType.CONTRIBUTION_SECTION
		totals['Contributions'] += float(contribution.amount.replace(',',''))
		contribution.write_record()
		contribution.reset()
		continue
	if (line_type == LineType.CONTRIBUTION_SECTION) and contribution_in_kind.match(line):
		m = contribution_in_kind.match(line)
		line_type = LineType.CONTRIBUTION_NAME
		contribution.date = m.group(1)
		contribution.method = m.group(2)
		contribution.name = m.group(3).strip()
		contribution.amount = m.group(4)
		continue
	

csv_file_expense.close()
csv_file_contribution.close()
print("\nTotals:\nContributions: {0:10,.2f}\nExpenditures: {1:11,.2f}".format(totals['Contributions'],totals['Expenses']))
print("\nResults in--\n{0}\n{1}\n".format(CSV_FILE_EXPENSE,CSV_FILE_CONTRIBUTE))
