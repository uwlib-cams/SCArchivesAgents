import xml.etree.ElementTree as ET
import os
import csv

"""Functions"""

def fix_spacing(elem):
	"""Remove unnecessary spacing from original EAD"""
	if elem == None:
		pass
	else:
		elem_list = elem.split(' ') # split by space
		content_list = [] # empty list
		for item in elem_list: # iterate through words in original element
			if item == '': # if it's a blank space, ignore it
				pass
			else: # if it has characters in it, remove whitespace and add it to list
				item = item.strip()
				content_list.append(item)
		elem = ' '.join(content_list) # condense list back into a single string
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
	# look for persname
	for elem in root.findall('archdesc/did/origination/persname'):
		elem = elem.text # convert to string
		if elem != None:
			elem = fix_spacing(elem)
			elem = remove_marc_fields(elem)
			origname_list.append(elem)
	# look for famname
	for elem in root.findall('archdesc/did/origination/famname'):
		elem = elem.text # convert to string
		if elem != None:
			elem = fix_spacing(elem)
			elem = remove_marc_fields(elem)
			origname_list.append(elem)
	origname = ' '.join(origname_list) # create single string out of all found names # only one name should be found but just in case
	origname = origname.strip() # remove unnecessary whitespace
	if origname == '': # if string is blank, i.e. no orignames were found
		origname = 'no origination name found'
	else: # if string is not blank, i.e. orignames were found
		origname = remove_marc_fields(origname) # remove marc fields
	return origname

def find_unittitle():
	"""Look for unittitle; used for 'qualifier named as' (P1810)"""
	for elem in root.findall('archdesc/did/unittitle'):
		elem = fix_spacing(elem.text)
		return elem

def find_unitid():
	"""Look for unitid; used for 'qualifier inventory number' (P217)"""
	for elem in root.findall('archdesc/did/unitid'):
		elem = elem.text
		return elem

def find_url():
	"""Look for url; used for 'qualifier described at URL' (P973)"""
	for elem in root.findall('eadheader/eadid[@url]'):
		url = elem.attrib['url']
		url = url.rstrip('.xml')
		return url

def find_Qid(origname):
	"""See if origname was reconciled; if so, return Qid"""
	Qid = '' # blank
	with open("data_reconciliation/reconciledValuesWithQNumbers-2021-01-20-cec.csv") as reconciliation_csv: # reconciliation data
		csv_reader = csv.reader(reconciliation_csv, delimiter=',')
		line_count = 0
		for line in csv_reader:
			if line_count == 0: # skip header row
				pass
			else:
				if line[0] in origname: # if origname in reconciliation data matches origname from EAD file
					Qid = line[1] # take the Qid from the next column over
			line_count += 1
		if Qid == '': # if the Qid is blank, because the origname was not in reconciliation data OR because there was no Qid in the reconciliation data
			Qid = 'CREATE'
	return Qid

###

# put EAD files into a list
ead_files = os.listdir('data_received/LaborArchivesEADLinkedDataProject')

if not os.path.exists('quickstatements_csv.csv'): # if output file does not exist, create it
	os.system('touch quickstatements_csv.csv')

with open("quickstatements_csv.csv", mode='w') as csv_output: # open csv writer
	csv_writer = csv.writer(csv_output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

	# write header row
	csv_writer.writerow(['','QID or create new','Property (or label, alias, description)','Property value','Qualifier property','Qualifier value','Qualifier property','Qualifier value','Qualifier property','Qualifier value'])

	# iterate through EAD files
	for file in ead_files:
		# open xml parser
		tree = ET.parse(f'data_received/LaborArchivesEADLinkedDataProject/{file}')
		root = tree.getroot()

		# get origname
		origname = find_origname()
		if origname == 'no origination name found': # if no origname found
			print(file) # print so we know which file is getting skipped
			continue # skip the file

		# look for Qid, if it already exists
		Qid = find_Qid(origname)
		csv_writer.writerow(['',f'{Qid}','','','','','','','',''])

		unittitle = find_unittitle()
		if unittitle == None: # if none found, make it an empty string
			unittitle = ''
		unitid = find_unitid()
		if unitid == None:
			unitid = ''
		url = find_url()
		if url == None:
			url = ''

		if Qid == 'CREATE': # if we're creating a new item
			other_lines = 'LAST'
		else: # if we're not creating a new item
			other_lines = Qid

		if Qid == 'CREATE': # if this is a new wikidata item
			csv_writer.writerow(['Label',f'{other_lines}','Len',f'{origname}','','','','','','']) # create English label
			#csv_writer.writerow(['Description',f'{other_lines}','Den','','','','','','','']) # create English description
			#csv_writer.writerow(['Also known as',f'{other_lines}','Aen','','','','','','','']) # create English aliases
		csv_writer.writerow(['on focus list of Wikimedia project',f'{other_lines}','P5008','Q98970039','','','','','','']) # on focus list
		csv_writer.writerow(['archives at',f'{other_lines}','P485','Q22096098','P1810',f'"{unittitle}"','P217',f'"{unitid}"','P973',f'"{url}"']) # archives data
