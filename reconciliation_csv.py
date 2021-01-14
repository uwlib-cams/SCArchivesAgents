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

def find_origination_name():
	origname_list = []
	for elem in root.findall('archdesc/did/origination/corpname'):
		elem = elem.text
		if elem == None:
			pass
		else:
			origname_list.append(fix_spacing(elem))
	for elem in root.findall('archdesc/did/origination/persname'):
		elem = elem.text
		if elem == None:
			pass
		else:
			origname_list.append(fix_spacing(elem))
	for elem in root.findall('archdesc/did/origination/famname'):
		elem = elem.text
		if elem == None:
			pass
		else:
			origname_list.append(fix_spacing(elem))
	origname = ' '.join(origname_list)
	origname = origname.strip()
	if origname == '':
		origname = '(No origination name found.)'
	else:
		origname = remove_marc_fields(origname)
	return origname

def find_unittitle():
	for elem in root.findall('archdesc/did/unittitle'):
		elem = fix_spacing(elem.text)
		return elem

def find_bioghist():
	bioghist = ''
	for elem in root.findall('archdesc/bioghist/*'):
		if elem.text != None:
			elem = fix_spacing(elem.text)
			if bioghist == '':
				bioghist = bioghist + elem
			else:
				bioghist = bioghist + '\n\n' + elem
	if bioghist == '':
		for elem in root.findall('archdesc/bioghist'):
			elem = fix_spacing(elem.text)
			if elem != None:
				if bioghist == '':
					bioghist = bioghist + elem
				else:
					bioghist = bioghist + '\n\n' + elem
	return bioghist

###

ead_files = os.listdir('data_received/LaborArchivesEADLinkedDataProject')

if not os.path.exists('reconciliation_csv.csv'):
	os.system('touch reconciliation_csv.csv')

with open(f"reconciliation_csv.csv", mode='w') as csv_output:
	csv_writer = csv.writer(csv_output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

	# header row
	csv_writer.writerow(['origination_name','unittitle','bioghist'])

	for file in ead_files:
		tree = ET.parse(f'data_received/LaborArchivesEADLinkedDataProject/{file}')
		root = tree.getroot()

		origname = find_origination_name()
		unittitle = find_unittitle()
		if unittitle == None: # no unittitle found
			unittitle = ''
		bioghist = find_bioghist()
		if bioghist == None: # no bioghist
			bioghist = ''

		csv_writer.writerow([f'{origname}',f'{unittitle}',f'{bioghist}'])
