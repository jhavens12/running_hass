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


database=open_file()



# for n,x in enumerate(sorted(reversed(database))):
#     # if n == 13:
#     print(x)
#     if 'strava_specific' in database[x]:
#         print("PR:")
#         #if database[x]['strava_specific']['pr_count'] != 0:
#             #print("PR:",database[x]['strava_specific']['pr_count'])
#         for y in database[x]['strava_specific']['best_efforts']: #for each best effort entry
#                 #if y['achievements'] != []: #if the achievements are not empty
#                     #print(x['achievements'])
#             print(y['pr_rank'],"--",y['name'],"--",data.convert_seconds_to_minutes(y['elapsed_time']))
#
#         print()
#         print("ACH:")
#         #if database[x]['strava_specific']['achievement_count'] != 0:
#             #print("ACH:",database[x]['strava_specific']['achievement_count'])
#         for z in database[x]['strava_specific']['segment_efforts']:
#                 #if z['achievements'] != []:
#             for w in z['achievements']: #list inside dictionary for some reason
#                         #if w['type'] != 'segment_effort_count_leader':
#                 print( w['rank'], "--", w['type'], "--", z['name'], "--", data.convert_seconds_to_minutes(z['elapsed_time']))
#     else:
#         print("Missing Stava Specific Data!")
#
#     print()
#     print("Date:",database[x]['weekday_full_date'])
#     print()
#     print("Notables:")
#     if 'notables' in database[x]['smash']:
#         if database[x]['smash']['notables'] != 'N/A':
#             for x in database[x]['smash']['notables']:
#                 print(x['description'])
#         else:
#             print("Notables is N/A")
#     else:
#         print("Missing Notables!")


next_key = next(iter(reversed(sorted(database))))

pprint.pprint(database[next_key])

# print(next_key)
# print("Date:",database[next_key]['weekday_full_date'])
# print()
# print("Notables:")
# if 'notables' in database[next_key]['smash']:
#     if database[next_key]['smash']['notables'] != 'N/A':
#         for x in database[next_key]['smash']['notables']:
#             print(x['description'])
#     else:
#         print("Notables is N/A")
# else:
#     print("Missing Notables!")
# print()
# print("PR Count:",database[next_key]['strava_specific']['pr_count'])
# print()
