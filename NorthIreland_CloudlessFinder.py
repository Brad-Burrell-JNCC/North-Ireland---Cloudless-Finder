# Name: NorthIreland_CloudlessFinder.py
# Author: Bradley Burrell - November 2022
# Description: This script search for XML file in the CEDA directories and return a categorized list of S2 Scenes.
# REQUIREMENTS:
#  1. Python version 3.10

import os
import shutil
from bs4 import BeautifulSoup
import csv

# Path to CEDA S2 home directory
ceda = 'ceda/home/users/directory'
# Users Jasmin Home Directory
jasmin_home = 'jasmin/home/users/directory' #TODO: Currently Hardcode please amend as requires. Will pdate with sys.argv at some point.
# Working Directory for this script, all temp and output file will be processed here.
cloudsearch_pd = '{}/NI-Cloud_Search/'.format(jasmin_home)

# Heads for Output CSV
header = ['Tile', 'Cloud_CoverPercentage', 'Cloud_Cover_Class']

# Checks if NI-Cloud_Search
if not os.path.exists(cloudsearch_pd):
    os.mkdir(cloudsearch_pd)

# Years to Check
years = [2022, 2021] #TODO: Currently Hardcode, Update with sys.argv at some point.
# Loops through all Year, Month, and Days. Finds S2 Meta labeled TM65 (NI) and copies them to the Cloudsearch dir
for year in years:
    for month in range(1, 13):
        for day in range(1, 32):
            file_path = "{}/{}/{:02d}/{:02d}".format(ceda, year, month, day)
            dir_check = os.path.isdir(file_path)
            if dir_check is True:
                for f in os.listdir(file_path):
                    if f.endswith('.xml'):
                        if 'TM65' in f:
                            shutil.copyfile("{}/{}".format(file_path, f), "{}/{}".format(cloudsearch_pd, f))
            elif dir_check is False:
                print("No Directory Found: {}".format(file_path))

# Creats a CSV to outout the list
with open('NI_CloudCover.csv', 'w', encoding='UTF8') as f:
    writer = csv.writer(f)

    # write the header
    writer.writerow(header)

    # write the data

    for file in os.listdir(cloudsearch_pd):
        xml_path = "{}/{}".format(cloudsearch_pd, file)
        fn = file.split('_vmsk_')[0]

        # Uses beatiful Soup to go thru and pull out the 'ARCSI_CLOUD_COVER' value
        btree = BeautifulSoup(open(xml_path), "lxml-xml")
        texttags = btree.find_all("gco:CharacterString")
        for text in texttags:
            if 'ARCSI_CLOUD_COVER' in text.string:
                cloud_cover = float(str(text.string).split('ARCSI_CLOUD_COVER:')[1].split('ARCSI_AOT_RANGE_MAX: ')[0])
                print(cloud_cover)
                # Classify results below 10% Cloud Cover outputs results to CSV
                if cloud_cover == 0:
                    writer.writerow([fn, cloud_cover, 'No Cloud'])
                    print('{} - No Cloud'.format(fn))
                elif 0.05 > cloud_cover > 0:
                    print('{} - Less than 5% Cloud'.format(fn))
                    writer.writerow([fn, cloud_cover, 'Less than 5% Cloud'])
                elif 0.1 > cloud_cover > 0.05:
                    print('{} - Less than 10% Cloud'.format(fn))
                    writer.writerow([fn, cloud_cover, 'Less than 10% Cloud'])

# Clear XML from Cloudsearch
for item in os.listdir(cloudsearch_pd):
    if item.endswith(".xml"):
        os.remove(os.path.join(cloudsearch_pd, item))