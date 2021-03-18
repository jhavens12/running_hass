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
import os
#check to see if it needs a full update
#combine strava data and smash, make multiple smash calls for more details

dictionary_file = Path('./running_data.dict')

def open_file():
    if dictionary_file.is_file():
        pickle_in = open(dictionary_file,"rb")
        try:
            sav_dict = pickle.load(pickle_in)
            print("Found saved dictionary")
        except Exception:
            print("Dictionary File Bad")
            os.remove(dictionary_file)
            open_file()
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


def get_strava_specific(activity_id):

    try:
        with open('./access_token.txt') as f:
            access_token = f.read().splitlines()[0] #only grab first line, remove /n from string
            print("Access Token: "+access_token)
    except Exception:
        print("No Access Token found in file! Renewing")
        access_token = renew.main()

    url = "https://www.strava.com/api/v3/activities/"+str(activity_id)+"?include_all_efforts="
    header = {'Authorization': 'Bearer '+access_token}
    print("Getting Strava Run Specific Data...")
    try:
        dataset = requests.get(url, headers=header).json()
    except Exception as e:
        print("Error getting Strava data, sleeping")
        print(e)
        print("current Time:",str(datetime.datetime.now()))
        time.sleep(3600)
    print("API Sleep...")
    time.sleep(1.5)
    return dataset

def get_strava_data(): #combines my_activities and filter functions
    try:
        with open('./access_token.txt') as f:
            access_token = f.read().splitlines()[0] #only grab first line, remove /n from string
            print("Access Token: "+access_token)
    except Exception:
        print("No Access Token found in file! Renewing")
        access_token = renew.main()


    def get_count():
        url = 'https://www.strava.com/api/v3/athlete/activities'
        header = {'Authorization': 'Bearer '+access_token}
        param = {'per_page':200, 'page':1}
        print("Running get_count to test")
        dataset = requests.get(url, headers=header, params=param).json()
        count = len(dataset)
        return count

    url = 'https://www.strava.com/api/v3/athlete/activities'
    header = {'Authorization': 'Bearer '+access_token}
    param = {'per_page':200, 'page':1}
    print("Page: 1")
    dataset = requests.get(url, headers=header, params=param).json()
    count = len(dataset)

    #stop here to check data
    if count == 2: #if there is an error
        print(dataset)
        #this runs if there is a key found in the text file, but it is expired
        print("Access Token is bad, requesting new one with Refresh Token and restarting script")
        print("------------")
        try:
            with open('./refresh_token.txt') as f:
                refresh_token = f.read().splitlines()[0] #only grab first line, remove /n from string
        except Exception:
            print("refresh_token.txt does not exist - exiting!")
            exit()

        access_token = renew.reauth(refresh_token)
        print("Starting Over...")
        get_strava_data() #start over


    #now continue getting data
    if count == 200: #if 200 results come back
        loop_count = 1 #we've already done one loop
        while count == 200: #while it keeps returning 200 results
            loop_count = loop_count + 1 #increase loop_count or page number
            print("Page: "+str(loop_count))
            param = {'per_page':200, 'page':loop_count} #reset params
            sub_dataset = requests.get(url, headers=header, params=param).json() #pull new data with sub_dataset name
            dataset = dataset + sub_dataset #combine (Json files, not dictionaries thank jesus)
            count = len(sub_dataset) #count results to see if we need to loop again
    print(str(len(dataset))+" Total Activities")
    #done getting data at this point
    return dataset

def update(database,smash):
    strava = get_strava_data()
    return_dict = {}
    for i in strava:
        if wanted_event(i):
            return_dict[event_timestamp(i)] = clean_event(i)

    strava = return_dict #dictionary of dictionaries

    for i in strava:
        if i not in database:
            print("Activity not in database!",i)
            #add to database
            database[i] = strava[i]
            database[i]['strava_specific'] = get_strava_specific(database[i]['id']) #add strava specific data to database
            for x in smash: #iterate to find the correct smash record
                if strava[i]['external_id'] == 'garmin_push_'+str(x['externalId']):
                    database[i]['smash'] = smash_spec(x['activityId']) #add smash to dictionary
                    database[i]['smash']['notables'] = smash_notables(x['activityId']) #add notables to dictionary
    return database

def prepare():
    strava = get_strava_data()
    return_dict = {}
    for i in strava:
        if wanted_event(i):

            return_dict[event_timestamp(i)] = clean_event(i)

    smash_data = get_smash_data() #list of dicitonaries

    spec = []
    sub_count = 1 #create list of dictionaries just as smash API hands off
    for act in smash_data: #first 3 items
        print(act)
        print("Count: ",sub_count)
        id = act['activityId'] #works
        spec.append(smash_spec(id)) #add to list
        sub_count = sub_count+1
    smash = spec #rename list

    strava = return_dict #dictionary of dictionaries

    match_list = []
    for i in strava:
        for x in smash:
            if strava[i]['external_id'] == 'garmin_push_'+str(x['externalId']):
                strava[i]['smash'] = x #grab smash entry and add it to dict
            else:
                pass

    for i in strava:
        if 'smash' in strava[i]:
            print("Match")
        else:
            strava[i]['smash'] = "N/A"

    return strava

def wanted_event(i):
    try:
        return i['type'] == 'Run' and i['distance'] != 0.0 and i['private'] != True
    except Exception:
        print("Exception!")
        pprint.pprint(i)

def event_timestamp(i):
    return convert_timestamp_strava(i['start_date_local'])

def convert_timestamp_strava(i):
    return datetime.datetime.strptime(i, "%Y-%m-%dT%H:%M:%SZ")

def convert_timestamp_smash(i):
    #'2021-03-14T10:25:00-04:00'
    i = i.split('-',3) #split by dash
    i = '-'.join(i[:3]) #join with dash, first 3 entries of list
    return datetime.datetime.strptime(i, "%Y-%m-%dT%H:%M:%S")

def convert_weekday(i):
    return str(calendar.day_name[i.weekday()])+" "+str(i.day)

def convert_weekday_full(i):
    return str(calendar.day_name[i.weekday()])+" "+str(calendar.month_name[i.month])+" "+str(i.day)

def convert_weekday_short(i):
    return str(calendar.day_abbr[i.weekday()])+" "+str(calendar.month_abbr[i.month])+" "+str(i.day)

def convert_seconds_to_minutes(i):
    return datetime.timedelta(seconds=i)

def convert_pace(distance,elapsed):
    minutes = elapsed/60
    miles = distance * 0.00062137
    pace = minutes/miles
    return pace

def convert_dec_time(dec):
    #converts decimal time to readable time format
    Minutes = dec
    Seconds = 60 * (Minutes % 1)
    result = ("%d:%02d" % (Minutes, Seconds))
    return result

def convert_meters_to_miles(meters):
    return ("{0:.2f}".format(int(meters) * 0.000621371))

def convert_elevation(i):
    return float(("{0:.2f}".format(i*3.28)))

def clean_event(i):
    if not i['has_heartrate']:
        i['average_heartrate'] = i['max_heartrate'] = 0
    i['elapsed'] = convert_seconds_to_minutes(i['elapsed_time'])
    i['pace_dec'] = convert_pace(i['distance'],i['moving_time'])
    i['pace'] = convert_dec_time(convert_pace(i['distance'],i['moving_time']))
    i['distance_miles'] = convert_meters_to_miles(i['distance'])
    i['total_elevation_feet'] = convert_elevation(i['total_elevation_gain'])
    i['start_date_datetime'] = event_timestamp(i)
    i['weekday_date'] = convert_weekday(i['start_date_datetime'])
    i['weekday_full_date'] = convert_weekday_full(i['start_date_datetime'])
    i['weekday_short_date'] = convert_weekday_short(i['start_date_datetime'])
    if "Treadmill" not in i['name']:
        i['treadmill_flagged'] = "no"
    if "Treadmill" in i['name']:
        i['treadmill_flagged'] = "yes"

    return i

def get_smash_data():
    token= credentials.smash_token
    print("Getting Smash run data...")
    url = "https://api.smashrun.com/v1/my/activities"
    header = {'Authorization': 'Bearer '+token}
    dataset = requests.get(url, headers=header).json()

    return dataset

def smash_spec(activity_id):
    token= credentials.smash_token
    print("Getting Smash run specific data...")
    url = 'https://api.smashrun.com/v1/my/activities/'+str(activity_id)
    header = {'Authorization': 'Bearer '+token}
    try:
        dataset = requests.get(url, headers=header).json()
    except Exception as e:
        print("Error getting Smash data, sleeping")
        print(e)
        print("Sleeping 1 hour")
        print("Current time: ",str(datetime.datetime.now()))
        time.sleep(3600)
    print("API Sleep...")
    time.sleep(15)

    return dataset

def smash_notables(activity_id):
    token= credentials.smash_token
    print("Getting Notables...")
    url = "https://api.smashrun.com/v1/my/activities/"+str(activity_id)+"/notables"
    header = {'Authorization': 'Bearer '+token}
    try:
        dataset = requests.get(url, headers=header).json()
    except Exception as e:
        print("Error getting Smash data, sleeping")
        print(e)
        print("Sleeping 1 hour")
        print("Current time: ",str(datetime.datetime.now()))
        time.sleep(3600)
    print("API Sleep...")
    time.sleep(15)

    return dataset

def run():
    database = open_file()
    #current_timestamp = datetime.datetime.now()
    # if database['timestamp'] < current_timestamp-datetime.timedelta(hours=1900):
    #     print("Last data gathered at: "+str(database['timestamp']))
    #     print("Gathering update information")
    #     print("Please Wait...")
    #     print()
    #
    #     database = update()
    #
    #     #save and close the file
    #     close_file(database)
    # else:
        #print("Found existing dictionary in time period")
        #del database['timestamp']

    smash = get_smash_data()
    new_key = smash[0]['externalId']
    print("KEY: ",smash[0]['activityId'])
    force_update = 1
    for x in reversed(sorted(database)):
        if database[x]['external_id'] == 'garmin_push_'+new_key:
            force_update = 0
            print('found matching run to latest smashrun... run')
            print("Found: ",x)
            print("no need to update at this time")

    if force_update == 1:
        print("Did not find latest activity")
        database = update(database,smash) #update and pass smash dic used to check
        #perform update to dictionary
        #save and close the file
        close_file(database)
        return database

    else:
        return database
