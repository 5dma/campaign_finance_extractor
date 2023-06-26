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

		writer_contribution.writerow({'Name':self.name,'Address Line 1':self.address_line_1,'Address Line 2':self.address_line_2,'City':self.city,'State':self.state,'Zip':self.zip_code,'Method':self.method,'Amount':self.amount,'Aggregate to Date':self.aggregate_to_date,'Category':'Contribution'})

class Expense(Transaction):
	def __init__(self):
		purpose = None
		

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

		writer.writerow({'Name':self.name,'Address Line 1':self.address_line_1,'Address Line 2':self.address_line_2,'City':self.city,'State':self.state,'Zip':self.zip_code,'Method':self.method,'Amount':self.amount,'Purpose':self.purpose,'Category':'Expenditure'})


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
fieldnames_expense = ['Name','Address Line 1','Address Line 2','City','State','Zip','Method','Amount','Purpose','Category']
writer_expense = csv.DictWriter(csv_file_expense, fieldnames=fieldnames_expense,delimiter='\t')
writer_expense.writeheader()

csv_file_contribution = open(CSV_FILE_CONTRIBUTE,'w')
fieldnames_contribution = ['Name','Address Line 1','Address Line 2','City','State','Zip','Method','Amount','Aggregate to Date','Category']
writer_contribution = csv.DictWriter(csv_file_contribution, fieldnames=fieldnames_contribution,delimiter='\t')
writer_contribution.writeheader()

expenditure_section = re.compile('^ {71}Expenditures')
expenditure_name = re.compile('^ {7}(\d{2}/\d{2}/\d{4}) (\w*)(.*)\$([\d.,]*)')
expenditure_state_zip = re.compile('^([A-Za-z ]+)(\d+)')
expenditure_purpose = re.compile('^Expenditure Purpose:(.*)')
expenditure_full_address = re.compile('^ {41}(.*)|^ {18}Card/Visa(.*)')

contribution_section = re.compile('^ {49}Expenditures')
contribution_name = re.compile('^ {7}(\d{2}/\d{2}/\d{4}) (.*)\$([\d.,]+ ([\w ]+)\$)([\d.,]+)')
contribution_full_address = re.compile('^ {18}(.*)')
contribution_end = re.compile('^$')

line_type = LineType.UNKNOWN

expense = Expense()
contribution = Contribution()
totals = {"Contributions": 0, "Expenses": 0}


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
		totals['Expenses'] += float(expense.amount.replace(',',''))
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
	if (line_type == LineType.UNKNOWN) and contribution_section.match(line):
		line_type = LineType.CONTRIBUTION_SECTION
		print("Contibution")
		continue
	if (line_type == LineType.CONTRIBUTION_SECTION) and contribution_name.match(line):
		print("Name")
		m = contribution_name.match(line)
		line_type = LineType.CONTRIBUTION_NAME
		contribution.date = m.group(1)
		contribution.name = m.group(2).strip()
		contribution.aggregate_to_date= m.group(3).strip()
		contribution.method = m.group(4).strip()
		contribution.amount = m.group(5)
		totals['Contributions'] += float(contribution.amount.replace(',',''))
		continue
	if (line_type == LineType.CONTRIBUTION_NAME) and contribution_full_address.match(line):
		print("FUll address")
		m = contribution_full_address.match(line)
		line_type = LineType.CONTRIBUTION_FULL_ADDRESS
		contribution.full_address = m.group(1).strip()
		continue
	if line_type == LineType.CONTRIBUTION_FULL_ADDRESS and contribution_full_address.match(line):
		print("FUll address")
		m = contribution_full_address.match(line)
		line_type = LineType.CONTRIBUTION_FULL_ADDRESS
		contribution.full_address += ' ' + m.group(1).strip()
		continue
	if line_type == LineType.CONTRIBUTION_FULL_ADDRESS and contribution_end.match(line):
		print("END")
		m = expenditure_purpose.match(line)
		line_type = LineType.CONTRIBUTION_SECTION
		contribution.write_record()
		contribution.reset()
		continue
	

csv_file_expense.close()
csv_file_contribution.close()
print("\nTotals:\nContributions: {0:10,.2f}\nExpenditures: {1:11,.2f}".format(totals['Contributions'],totals['Expenses']))
print("\nResults in--\n{0}\n{1}\n".format(CSV_FILE_EXPENSE,CSV_FILE_CONTRIBUTE))
