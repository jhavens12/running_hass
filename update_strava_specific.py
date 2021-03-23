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
    if 'strava_specific' not in database[x]:
            print(database[x]['id'])
            strava_specific = data.get_strava_specific(database[x]['id'])
            #print(strava_specific)
            if strava_specific["achievement_count"] != 0:
                pprint.pprint(strava_specific["segment_efforts"] )
            else:
                print ("Achieve: ",strava_specific["achievement_count"])
            print("PR: ",strava_specific['pr_count'])
            database[x]['strava_specific'] = strava_specific
            close_file(database)
    else:
        print("we already have strava specific data for this run")
    print('***')

#pprint.pprint(data.get_strava_specific('4803968858'))
