import requests
import time
import datetime
from datetime import date
import json
import calendar
import credentials
import pprint
import renew
from pathlib import Path
import pickle
import data


dictionary_file = Path('./running_data.dict')

def open_file():
    if dictionary_file.is_file():
        pickle_in = open(dictionary_file,"rb")
        sav_dict = pickle.load(pickle_in)
        print("Found saved dictionary")
    else:
        f=open(dictionary_file,"w+") #create file
        f.close()
        print("Creating new dictionary file")
        sav_dict = {}
        #sav_dict['timestamp'] = datetime.datetime(1900, 1, 1)
    return sav_dict

def close_file(sav_dict):
    #sav_dict['timestamp'] = datetime.datetime.now()
    outfile = open(dictionary_file,"wb")
    pickle.dump(sav_dict, outfile)
    outfile.close()

run = 1

database=open_file()
for x in reversed(sorted(database)):
    print(x)
    print("Run: ",str(run))
    run = run + 1
    if database[x]['smash'] != "N/A":
        if 'notables' in database[x]['smash']: # pass if entry exists
            print("Already have notables for this run")
            pass
        else:
            print(database[x]['smash']['activityId'])
            notables = data.smash_notables(database[x]['smash']['activityId'])
            print(notables)
            if notables:
                database[x]['smash']['notables'] = notables
                close_file(database)
            else:
                print("No notables for this time period")
                database[x]['smash']['notables'] = 'N/A'
    print('***')


# next_key = next(iter(database))
#
# pprint.pprint(database[next_key])
# print(next_key)
# print(database[next_key]['weekday_full_date'])
