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

database=open_file()

reference = database.copy()
# del reference['timestamp']
# del database['timestamp']

next_key = next(iter(reversed(sorted(reference))))
print("Removing: ",next_key)
del database[next_key]
del reference[next_key]
remaining_key = next(iter(reversed(sorted(reference))))
print("Remaining Key: ",remaining_key)

close_file(database)
