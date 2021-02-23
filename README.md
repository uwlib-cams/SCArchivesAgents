# Workflow and Feedback
Current local workflow is posted on the Wiki page [WikiProject PCC Wikidata Pilot/University of Washington/Workflow, Trainings, and Resources/EAD to Wikidata Workflow](https://www.wikidata.org/wiki/Wikidata:WikiProject_PCC_Wikidata_Pilot/University_of_Washington/Workflow,_Trainings,_and_Resources/EAD_to_Wikidata_Workflow).

Constructive feedback is welcome; please feel free to create an issue in this repository if you have suggestions for improvement.

# EAD to Wikidata
Extracting agents data from EAD, reconciling agents with Wikidata entities, and adding links to Wikidata items to finding aids.

# quickstatements_csv.py

[quickstatements_csv.py](https://github.com/uwlib-cams/SCArchivesAgents/blob/main/quickstatements_csv.py) is a script that takes in a directory of EAD files and retrieves the values from the following elements:
- [origination](https://www.loc.gov/ead/EAD3taglib/EAD3.html#elem-origination)
- [unittitle](https://www.loc.gov/ead/EAD3taglib/EAD3.html#elem-unittitle)
- [unitid](https://www.loc.gov/ead/EAD3taglib/EAD3.html#elem-unitid)
- eadid/@url

The script takes those values and outputs them in a CSV file that can be uploaded to [Quickstatements](https://quickstatements.toolforge.org/#/) to add that archival data to new or existing Wikidata items. In order to contribute to existing Wikidata items, the script also extracts Wikidata Qids from a CSV file (see reconciliation_csv.py).

## Running the script

_Example_:
```
$ python3.6 quickstatements_csv.py data_received/LaborArchivesEADLinkedDataProject data_reconciliation/reconciledValuesWithQNumbers-2021-01-20-cec.csv
```

The output of this script is [quickstatements_csv.csv](https://github.com/uwlib-cams/SCArchivesAgents/blob/main/quickstatements_csv.csv).

# reconciliation_csv.py

[reconciliation_csv.py](https://github.com/uwlib-cams/SCArchivesAgents/blob/main/reconciliation_csv.py) is a script that takes in a directory of EAD files and retrieves the values from the following elements:
- [origination](https://www.loc.gov/ead/EAD3taglib/EAD3.html#elem-origination)
- [unittitle](https://www.loc.gov/ead/EAD3taglib/EAD3.html#elem-unittitle)
- [bioghist](https://www.loc.gov/ead/EAD3taglib/EAD3.html#elem-bioghist)

The script takes those values and outputs them in a CSV file that can be opened with [OpenRefine](https://openrefine.org/) in order to reconcile the origination agent names with Wikidata items.

Once reconciliation in OpenRefine is complete, the Wikidata Qids should be in their own column, second from the left. See [here](https://github.com/uwlib-cams/SCArchivesAgents/blob/main/data_reconciliation/reconciledValuesWithQNumbers-2021-01-20-cec.csv) for an example. This data should then be exported in a CSV file, which can then be used with [quickstatements_csv.py](https://github.com/uwlib-cams/SCArchivesAgents/blob/main/quickstatements_csv.py) (see above).

## Running the script

_Example_:
```
$ python3.6 reconciliation_csv.py data_received/LaborArchivesEADLinkedDataProject
```

The output of this script is [reconciliation_csv.csv](https://github.com/uwlib-cams/SCArchivesAgents/blob/main/reconciliation_csv.csv).
