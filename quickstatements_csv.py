import csv
import os
from sys import argv
import xml.etree.ElementTree as ET

"""Functions"""

def fix_spacing(elem):
	"""Remove unnecessary spacing from original EAD"""
	if elem != None:
		elem = elem.replace("\n", " ") # remove newline
		elem = elem.replace("\t", " ") # remove tab
		elem = elem.replace("     ", " ") # remove remaining spaces
	return elem

def remove_marc_fields(elem):
	"""Remove MARC fields from literals"""
	if elem != None:
		if '$' in elem:
			elem_list = elem.split('$') # split by $ character
			content_list = [] # empty list
			content_list.append(elem_list[0]) # add first part of string to list
			for item in elem_list[1:]: # iterate through remaining parts of string
				content_list.append(item[1:]) # append to list without MARC field label
			elem = ' '.join(content_list) # join items in list back to one string
	return elem

def find_origname():
	"""Look for corpname, persname, or famname as a child element of origination; used for item label"""
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
	origname = ' '.join(origname_list) # create single string out of all found names # only one name should be found, but keep all just in case
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

def find_Qid(unittitle, recon_csv):
	"""See if origname was reconciled; if so, return Qid"""
	Qid = '' # blank
	with open(f"{recon_csv}") as reconciliation_csv: # reconciliation data
		csv_reader = csv.reader(reconciliation_csv, delimiter=',')
		line_count = 0
		for line in csv_reader:
			if line_count == 0: # skip header row
				pass
			else:
				if line[2] == unittitle: # if unittitle in reconciliation data matches unittitle from EAD file
					Qid = line[1] # take the Qid from the previous column
			line_count += 1
		if Qid == '': # if the Qid is blank, because the origname was not in reconciliation data OR because there was no Qid in the reconciliation data
			Qid = 'CREATE'
	return Qid

###

script, EAD_dir, recon_csv = argv
# EAD_dir = directory containing EAD
# recon_csv = CSV file containing reconciliation data

output_location = EAD_dir

# put EAD files into a list
ead_files = os.listdir(f'{EAD_dir}')

if not os.path.exists(f'{output_location}/quickstatements_csv.csv'): # if output file does not exist, create it
	os.system(f'touch {output_location}/quickstatements_csv.csv')

with open(f"{output_location}/quickstatements_csv.csv", mode='w') as csv_output: # open csv writer
	csv_writer = csv.writer(csv_output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

	# write header row
	csv_writer.writerow(['','QID or create new','Property (or label, alias, description)','Property value','Qualifier property','Qualifier value','Qualifier property','Qualifier value','Qualifier property','Qualifier value'])

	# iterate through EAD files
	for file in ead_files:
		if ".xml" not in file:
			continue # skip any files that are not XML files

		# open xml parser
		tree = ET.parse(f'{EAD_dir}/{file}')
		root = tree.getroot()

		# get name of origination agent
		origname = find_origname()
		if origname == 'no origination name found': # if no origname found
			print("SKIPPED: " + file) # print so we know which file is getting skipped
			continue # skip the file

		unittitle = find_unittitle()
		if unittitle == None: # if none found, make it an empty string
			unittitle = ''

		# look for Qid, if it already exists
		Qid = find_Qid(unittitle, recon_csv)
		csv_writer.writerow(['',f'{Qid}','','','','','','','',''])
		
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
			csv_writer.writerow(['Label',f'{other_lines}','Len',f'"{origname}"','','','','','','']) # create English label
			#csv_writer.writerow(['Description',f'{other_lines}','Den','','','','','','','']) # create English description
			#csv_writer.writerow(['Also known as',f'{other_lines}','Aen','','','','','','','']) # create English aliases
		csv_writer.writerow(['on focus list of Wikimedia project',f'{other_lines}','P5008','Q98970039','','','','','','']) # on focus list
		csv_writer.writerow(['archives at',f'{other_lines}','P485','Q22096098','P1810',f'"{unittitle}"','P217',f'"{unitid}"','P973',f'"{url}"']) # archives data
