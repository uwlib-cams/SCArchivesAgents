import xml.etree.ElementTree as ET
import os
import csv

"""Functions"""

def fix_spacing(elem):
	"""Remove unnecessary spacing from original EAD"""
	if elem == None:
		pass
	else:
		elem_list = elem.split(' ')
		content_list = []
		for item in elem_list:
			if item == '':
				pass
			else:
				item = item.strip()
				content_list.append(item)
		elem = ' '.join(content_list)
	return elem

def remove_marc_fields(elem):
	"""Remove MARC fields from literals"""
	if elem == None:
		pass
	elif '$' in elem:
		elem_list = elem.split('$') # split by $ character
		content_list = [] # empty list
		content_list.append(elem_list[0]) # add first part of string to list
		for item in elem_list[1:]: # iterate through remaining parts of string
			content_list.append(item[1:]) # append to list without MARC field label
		elem = ' '.join(content_list) # join items in list back to one string
	return elem

def find_origname():
	"""Look for corpname, persname, or famname as a child element of origination"""
	origname_list = []
	# look for corpname
	for elem in root.findall('archdesc/did/origination/corpname'):
		elem = elem.text # convert to string
		if elem != None:
			elem = fix_spacing(elem)
			elem = remove_marc_fields(elem)
			origname_list.append(elem)
	for elem in root.findall('archdesc/did/origination/persname'):
		elem = elem.text # convert to string
		if elem != None:
			elem = fix_spacing(elem)
			elem = remove_marc_fields(elem)
			origname_list.append(elem)
	for elem in root.findall('archdesc/did/origination/famname'):
		elem = elem.text # convert to string
		if elem != None:
			elem = fix_spacing(elem)
			elem = remove_marc_fields(elem)
			origname_list.append(elem)
	origname = ' '.join(origname_list)
	origname = origname.strip()
	if origname == '':
		origname = 'no origination name found'
	else:
		origname = remove_marc_fields(origname)
	return origname

def find_unittitle():
	"""archives at (P485), qualifier named as (P1810)"""
	for elem in root.findall('archdesc/did/unittitle'):
		elem = fix_spacing(elem.text)
		return elem

def find_unitid():
	"""archives at (P485), qualifier inventory number (P217)"""
	for elem in root.findall('archdesc/did/unitid'):
		elem = elem.text
		return elem

def find_url():
	"""archives at (P485), qualifier described at URL (P973)"""
	for elem in root.findall('eadheader/eadid[@url]'):
		url = elem.attrib['url']
		url = url.rstrip('.xml')
		return url

def find_Qid(origname):
	"""See if origname was reconciled. If so, return Qid"""
	Qid = ''
	with open("data_reconciliation/reconciledValuesWithQNumbers-2021-01-20-cec.csv") as reconciliation_csv:
		csv_reader = csv.reader(reconciliation_csv, delimiter=',')
		line_count = 0
		for line in csv_reader:
			if line_count == 0:
				pass
			else:
				if line[0] in origname:
					Qid = line[1]
			line_count += 1
		if Qid == '':
			Qid = 'CREATE'
	return Qid

###

ead_files = os.listdir('data_received/LaborArchivesEADLinkedDataProject')

if not os.path.exists('quickstatements_csv.csv'):
	os.system('touch quickstatements_csv.csv')

with open("quickstatements_csv.csv", mode='w') as csv_output:
	csv_writer = csv.writer(csv_output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

	# header row
	csv_writer.writerow(['','QID or create new','Property (or label, alias, description)','Property value','Qualifier property','Qualifier value','Qualifier property','Qualifier value','Qualifier property','Qualifier value'])

	for file in ead_files:
		tree = ET.parse(f'data_received/LaborArchivesEADLinkedDataProject/{file}')
		root = tree.getroot()

		# look for Qid, if it already exists
		origname = find_origname()
		if origname == 'no origination name found':
			print(file)
			continue

		Qid = find_Qid(origname)

		csv_writer.writerow(['',f'{Qid}','','','','','','','',''])

		unittitle = find_unittitle()
		if unittitle == None:
			unittitle = ''
		unitid = find_unitid()
		if unitid == None:
			unitid = ''
		url = find_url()
		if url == None:
			url = ''

		if Qid == 'CREATE':
			other_lines = 'LAST'
		else:
			other_lines = Qid

		csv_writer.writerow(['Label',f'{other_lines}','Len',f'{origname}','','','','','',''])
		if Qid == 'CREATE':
			csv_writer.writerow(['Description',f'{other_lines}','Den','','','','','','',''])
			csv_writer.writerow(['Also known as',f'{other_lines}','Aen','','','','','','',''])
		csv_writer.writerow(['on focus list of Wikimedia project',f'{other_lines}','P5008','Q98970039','','','','','',''])
		csv_writer.writerow(['archives at',f'{other_lines}','P485','Q22096098','P1810',f'"{unittitle}"','P217',f'"{unitid}"','P973',f'"{url}"'])
