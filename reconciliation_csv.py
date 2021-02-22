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
	origname = ' '.join(origname_list) # create single string out of all found names # only one name should be found, but keep all just in case
	origname = origname.strip() # remove unnecessary whitespace
	if origname == '': # if string is blank, i.e. no orignames were found
		origname = 'no origination name found'
	else: # if string is not blank, i.e. orignames were found
		origname = remove_marc_fields(origname) # remove marc fields
	return origname

def find_unittitle():
	"""Look for unittitle"""
	for elem in root.findall('archdesc/did/unittitle'):
		elem = fix_spacing(elem.text)
		return elem

def find_bioghist():
	"""Look for bioghist"""
	bioghist = '' # empty string
	for elem in root.findall('archdesc/bioghist/*'): # find values for child elements of bioghist, e.g. <p>
		if elem.text != None:
			elem = fix_spacing(elem.text)
			if bioghist == '': # if bioghist string is empty, add value
				bioghist = bioghist + elem
			else: # if bioghist string is not empty, add value after new line
				bioghist = bioghist + '\n\n' + elem
	if bioghist == '': # bioghist string is still empty, i.e. no child elements found
		for elem in root.findall('archdesc/bioghist'): # find values for bioghist itself
			elem = fix_spacing(elem.text)
			if elem != None:
				if bioghist == '': # if bioghist string is empty, add value
					bioghist = bioghist + elem
				else: # if bioghist string is not empty, add value after new line
					bioghist = bioghist + '\n\n' + elem
	return bioghist

###

script, EAD_dir = argv
# EAD_dir = directory containing EAD

output_location = EAD_dir

# put EAD files into a list
ead_files = os.listdir(f'{EAD_dir}')

if not os.path.exists(f'{output_location}/reconciliation_csv.csv'): # if output file does not exist, create it
	os.system(f'touch {output_location}/reconciliation_csv.csv')

with open(f"{output_location}/reconciliation_csv.csv", mode='w') as csv_output: # open csv writer
	csv_writer = csv.writer(csv_output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

	# write header row
	csv_writer.writerow(['origination_name','unittitle','bioghist'])

	# iterate through EAD files
	for file in ead_files:
		if ".xml" not in file:
			continue # skip any files that are not XML files

		# open xml parser
		tree = ET.parse(f'data_received/LaborArchivesEADLinkedDataProject/{file}')
		root = tree.getroot()

		# get name of origination agent
		origname = find_origname()
		if origname == 'no origination name found': # if no origname found
			print("SKIPPED: " + file) # print so we know which file is getting skipped
			continue # skip the file

		unittitle = find_unittitle()
		if unittitle == None: # if none found, make it an empty string
			unittitle = ''
		bioghist = find_bioghist()
		if bioghist == None:
			bioghist = ''

		csv_writer.writerow([f'{origname}',f'{unittitle}',f'{bioghist}'])
