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

def find_corpname():
	for elem in root.findall('archdesc/did/origination/corpname'):
		elem = elem.text # convert to string
		elem = fix_spacing(elem)
		elem = remove_marc_fields(elem)
		return elem

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

###

ead_files = os.listdir('data_received/LaborArchivesEADLinkedDataProject')

for file in ead_files:
	tree = ET.parse(f'data_received/LaborArchivesEADLinkedDataProject/{file}')
	root = tree.getroot()

	if not os.path.exists(f"csv/{file.split('.xml')[0]}.csv"):
		os.system(f"touch csv/{file.split('.xml')[0]}.csv")

	with open(f"csv/{file.split('.xml')[0]}.csv", mode='w') as csv_output:
		csv_writer = csv.writer(csv_output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		# header row
		csv_writer.writerow(['','QID or create new','Property (or label, alias, description)','Property value','Qualifier property', 'Qualifier value','Qualifier property', 'Qualifier value','Qualifier property', 'Qualifier value'])
		# create
		csv_writer.writerow(['','Q4115189'])

		corpname = find_corpname()
		if corpname == None:
			corpname = ''
		unittitle = find_unittitle()
		if unittitle == None:
			unittitle = ''
		unitid = find_unitid()
		if unitid == None:
			unitid = ''
		url = find_url()
		if url == None:
			url = ''

		csv_writer.writerow(['Label','LAST','Len',f'{corpname}'])
#		csv_writer.writerow(['Description','Den','LAST'])
#		csv_writer.writerow(['Also known as','Aen','LAST'])
		csv_writer.writerow(['on focus list of Wikimedia project','LAST','P5008','Q98970039'])
		csv_writer.writerow(['archives at','LAST','P485','Q22096098','P1810',f'"{unittitle}"','P217',f'"{unitid}"','P973',f'"{url}"'])
