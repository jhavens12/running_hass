import data
import pprint
import get_time
import datetime
import math
import calendar
import numpy as np
import json
import credentials
import requests
import matplotlib.pyplot as plt

runs_per_week = 5
goal_mileage = 800
png_location = credentials.png_location


def post_sensor(sensor,data):
    headers = {"Authorization": "Bearer "+credentials.api_token,
               'content-type': 'application/json'}

    url = credentials.api_url+"/api/states/"+sensor
    #data = '{"state": "1", "attributes": {"unit_of_measurement": "Miles"}}'
    response = requests.post(url, headers=headers, data=data)
    print("Posting Sensor: ",sensor)
    #print(response.text)

def get_sensor(sensor):
    url = credentials.api_url+"/api/states/"+sensor
    headers = {"Authorization": "Bearer "+credentials.api_token,
               'content-type': 'application/json'}

    response = requests.get(url, headers=headers)
    return response.json()


def format_text(x):
    return str("{0:.2f}".format(x))


def full_running_totals(dictionary1,days,unit):
    #creadted for use with database
    #newest and working
    #limit days after this calculation for range
    #Creates running totals for each day - not just activity day
    calculation_range_time = []
    final_list = []
    dictionary = dictionary1.copy()
    x = days
    #time functions
    now = datetime.datetime.now()
    start_of_today = datetime.datetime(now.year, now.month, now.day, hour=0, minute=0, second=0)
    end_of_today = datetime.datetime(now.year, now.month, now.day, hour=23, minute=59, second=59)

    difference = start_of_today - get_time.forever() #fix start peroid

    calculation_range = list(range(0,(difference.days +1))) #creates list from past date(given) to current date
    calculation_range_rev = list(reversed(calculation_range))
    calculation_range_time = [end_of_today - datetime.timedelta(days=x) for x in range(0,(difference.days +1))]

    for i,f in zip(calculation_range_time,calculation_range): #for every calculation day ex 1,2,3,4,5 back
        dictionary_1 = dictionary.copy() #create a new dictionary
        oldest_time = end_of_today - (datetime.timedelta(days=(x+f)))
        for key in list(dictionary_1):
            if key > i:
                del dictionary_1[key] #delete keys newer than calculation day
        for key in list(dictionary_1):
            if key < oldest_time: #delete keys older than oldest time
                 del dictionary_1[key]
        value_list = []
        for key in dictionary_1:
            value_list.append(float(dictionary_1[key][unit])) #adds variables to list
        list_sum = sum(value_list)
        final_list.append(list_sum)
    new_date_list = []
    for i in calculation_range: #create list of days going backwards from today
        new_day = get_time.day(i)
        new_date_list.append(new_day)
    new_dict = dict(zip(new_date_list, final_list))
    return new_dict

def monthly_daily_totals(dictionary,time_input,unit_input):
    #for use with masterdict (data.my_filtered_activities())
    #01.29.18
    #takes in number for how many months ago. Ex 0 is current, 1 is last month
    x_list = []
    y_list = []



    #filters out only dates needed
    for key in list(dictionary):
        if key < get_time.FOM(time_input): #if older than first of month
            del dictionary[key]
    for key in list(dictionary):
       if key > get_time.LOM(time_input): #if newer than first of month
           del dictionary[key]

    calculation_day_count = (get_time.LOM(time_input) - get_time.FOM(time_input)).days #how many days in the month
    calculation_day_range = list(range(1,calculation_day_count+2)) #range of 1 to the days in the month - calculation days

    mile_count = 0
    mile_count_list = [] #list of miles
    day_count_list = [] #list of days miles occurred
    for day in calculation_day_range:  #ex 1-31
        for activity in dictionary:
            if activity.day == day: #if the day of the activity matches the day in the list
                mile_count = mile_count + float(dictionary[activity][unit_input])
                mile_count_list.append(mile_count) #add mile count
                day_count_list.append(activity.day) #add day that count occurs

    return dict(zip(day_count_list,mile_count_list))

def monthly_stats(dictionary):
    #used to return dictionary of stats for each month - key is just a string
    #currently only distance_miles is being used
    #can certainly be expanded upon in the future
    count_dict = {}
    for date in dictionary:
        count_dict[str(date.year)+"-"+str(date.month)] = [] #create dict of lists
        #count_dict[datetime.datetime(date.year,date.month,1)] = [] #use datetime as key

    for date in dictionary:
        count_dict[str(date.year)+"-"+str(date.month)].append(float(dictionary[date]['distance_miles'])) #creates list of distance_miles
        #count_dict[datetime.datetime(date.year,date.month,1)].append(dictionary[date]['distance_miles']) #use datetime as key

    final_dict = {}
    for month in count_dict:
        final_dict[month] = {}
        final_dict[month]['run_count'] = len(count_dict[month])
        final_dict[month]['miles_ran'] = sum(count_dict[month])
        month_name = month.split('-')
        final_dict[month]['year'] = str(month_name[0])
        final_dict[month]['month'] = str(month_name[1])
        final_dict[month]['date_human'] = str(calendar.month_name[int(month_name[1])]+" "+month_name[0])

    return final_dict

def weekly_stats(dictionary):
    #Monday is first day of week
    #This is done poorly and needs to be rewritten
    count_dict = {} #create keys (weeks)
    weekly_runs = {} #dictionary to hold the actual runs
    for date in dictionary:
        week_number = date.isocalendar()[1]
        #print(str(date)+" - "+str(week_number)) #this seems to be accurate
        count_dict[str(date.year)+"-"+str(week_number)] = [] #create list
        weekly_runs[str(date.year)+"-"+str(week_number)] = {} #create dict
    for date in dictionary:
        week_number = date.isocalendar()[1]
        count_dict[str(date.year)+"-"+str(week_number)].append(float(dictionary[date]['distance_miles'])) #list of distances for each week
        weekly_runs[str(date.year)+"-"+str(week_number)][date] = dictionary[date]

    final_dict = {}
    for week in count_dict:

        final_dict[week] = {}
        final_dict[week]['run_dict'] = weekly_runs[week] #add the actual runs to the final dictionary
        final_dict[week]['run_count'] = len(count_dict[week])
        final_dict[week]['miles_ran'] = sum(count_dict[week])
        week_name = week.split('-')
        final_dict[week]['year'] = str(week_name[0])
        final_dict[week]['week'] = str(week_name[1])
        week_datetime = datetime.datetime.strptime(week + '-1', "%Y-%W-%w")
        #week_datetime = datetime.datetime.strptime(week, "%Y-%W-%w") #this does not fix issue
        final_dict[week]['datetime'] = week_datetime #added 7/7/19 for calculations in "weekly" in fsubview
        final_dict[week]['date_human'] = str(week_datetime.year)+"-"+str(week_datetime.month)+"-"+str(week_datetime.day)

    return final_dict

def yearly_totals(dictionary,years_ago):
    #0 = this year
    #1 = last year
    #returns days of year as keys (1-365)
    now = datetime.datetime.now()
    start_of_year = datetime.datetime((now.year - years_ago), 1, 1)
    end_of_year = datetime.datetime((now.year - years_ago), 12, 31)

    for key in list(dictionary):
        if key < start_of_year: #if older than first of month
            del dictionary[key]
    for key in list(dictionary):
       if key > end_of_year: #if newer than first of month
           del dictionary[key]

    calculation_day_count = (end_of_year - start_of_year).days #how many days in the month
    calculation_day_range = list(range(1,calculation_day_count+2)) #range of 1 to the days in the month - calculation days

    mile_count = 0
    mile_count_list = [] #list of miles
    day_count_list = [] #list of days miles occurred
    for day in calculation_day_range:  #ex 1-31
        for activity in dictionary:
            if activity.timetuple().tm_yday == day: #if the day of the activity matches the day in the list
                mile_count = mile_count + float(dictionary[activity]['distance_miles'])
                mile_count_list.append(mile_count) #add mile count
                day_count_list.append(activity.timetuple().tm_yday) #add day that count occurs

    return dict(zip(day_count_list,mile_count_list))

def activity_count(dictionary):
    #counts amount of keys in dictionary
    amount = len(dictionary.keys())
    amount_str = str(amount)
    return amount_str

def current_period(database):
    main_dict = {}
    dict_2 = database.copy()

    #filter out old runs (older than monday)
    for key in database:
        if key < get_time.LM(0):
            del dict_2[key]

    current_week_count = activity_count(dict_2)
    main_dict['current_week_count'] = current_week_count #USED FOR CALCULATIONS

    mile_list = []
    for i in dict_2:
        mile_list.append(float(dict_2[i]['distance_miles']))
    current_miles = "{0:.2f}".format(sum(mile_list))
    main_dict['current_miles'] = current_miles #USED FOR CALCULATIONS
    current_run_title_label = []
    for i in list(sorted(dict_2)):
        current_run_title_label.append(dict_2[i]['weekday_short_date'])
    current_run_mile_label = []
    for i in list(sorted(dict_2)):
        current_run_mile_label.append(dict_2[i]['distance_miles'])
    current_run_pace_label = []
    for i in list(sorted(dict_2)):
        current_run_pace_label.append(dict_2[i]['pace'])
    current_run_elapsed_label = []
    for i in list(sorted(dict_2)):
        current_run_elapsed_label.append(str(dict_2[i]['elapsed']))
    current_run_treadmill_label = []
    for i in list(sorted(dict_2)):
        current_run_treadmill_label.append(str("{0:.2f}".format(dict_2[i]['total_elevation_feet'])))

    #bottom values
    dec_pace_list = []
    for i in list(sorted(dict_2)):
        dec_pace_list.append(dict_2[i]['pace_dec'])
    if len(dec_pace_list) != 0:
        current_pace_average = data.convert_dec_time(sum(dec_pace_list)/len(dec_pace_list))
    else:
        current_pace_average = 0

    seconds_elapsed_list = []
    for i in list(sorted(dict_2)):
        seconds_elapsed_list.append(dict_2[i]['elapsed_time'])
    total_elapsed_seconds = sum(seconds_elapsed_list)
    current_duration_total = data.convert_seconds_to_minutes(total_elapsed_seconds)

    current_elevation_list = []
    for i in list(sorted(dict_2)):
        current_elevation_list.append(float(dict_2[i]['total_elevation_feet']))
    current_elevation_total = "{0:.2f}".format(sum(current_elevation_list))

    #main_dict['title'] = (get_time.weekday(get_time.LM(0)) + " " + str(get_time.LM(0).day) + " - " + get_time.weekday(get_time.now()) + " " + str(get_time.now().day))
    #main_dict['subtitle1_title'] = "Remaining:"
    main_dict['subtitle1_title'] = "UP:"
    main_dict['subtitle2_title'] = "Match:"
    main_dict['subtitle3_title'] = "DOWN:"
    #main_dict['subtitle2_title'] = "Per Run:"
    main_dict['subtitle1_value'] = "0"
    main_dict['subtitle2_value'] = "0"
    main_dict['subtitle3_value'] = "0"

    main_dict['box_titles'] = ['Date','Distance','Duration','Pace','Elevation']
    main_dict['box_values'] = []
    main_dict['box_values'].append("\n".join(current_run_title_label))
    main_dict['box_values'].append("\n".join(current_run_mile_label))
    main_dict['box_values'].append("\n".join(current_run_elapsed_label))
    main_dict['box_values'].append("\n".join(current_run_pace_label))
    main_dict['box_values'].append("\n".join(current_run_treadmill_label))


    sensor = {}
    sensor['state'] = get_time.convert_weekday_short(get_time.LM(0)) + " - " + get_time.convert_weekday_short(datetime.datetime.now())
    sensor['attributes'] = {}
    sensor['attributes']['Total Distance'] = str(current_miles)
    sensor['attributes']['Total Duration'] = str(current_duration_total)
    sensor['attributes']['AVG Pace'] = str(current_pace_average)
    sensor['attributes']['Total Elevation'] = current_elevation_total

    post_sensor("sensor.run_current_weekly_stats",json.dumps(sensor))

    return main_dict

def period(database,Sunday,Monday,current_info): #given master dict copy, and then 0 and 1 for last week

    main_dict = {} #main dictionary to add values to and then return
    dict_1 = database.copy() #create dictionary to manipulate

    #Filter out entries
    for key in database:
        if key > get_time.LS(Sunday):
            del dict_1[key]
    for key in database:
        if key < get_time.LM(Monday):
            del dict_1[key]

    past_dict_rev = {k: dict_1[k] for k in list(reversed(sorted(dict_1.keys())))}
    past_dict = {k: past_dict_rev[k] for k in list(sorted(past_dict_rev.keys()))}
    past_run_count = activity_count(past_dict)
    past_mile_list = []
    for i in past_dict:
        past_mile_list.append(float(past_dict[i]['distance_miles']))
    past_miles = ("{0:.2f}".format(sum(past_mile_list)))
    past_ten_percent = ("{0:.2f}".format(float(past_miles) * .1))


    #calculate rolling 10 percent over the past 4 weeks
    def rolling_ten_percent(Sunday,Monday):
        def period_ten_percent(sun,mon):
            dict_1 = database.copy()
            for key in database:
                if key > get_time.LS(sun):
                    del dict_1[key]
            for key in database:
                if key < get_time.LM(mon):
                    del dict_1[key]
            past_dict_rev = {k: dict_1[k] for k in list(reversed(sorted(dict_1.keys())))}
            past_dict = {k: past_dict_rev[k] for k in list(sorted(past_dict_rev.keys()))}
            past_run_count = activity_count(past_dict)
            past_mile_list = []
            for i in past_dict:
                past_mile_list.append(float(past_dict[i]['distance_miles']))
            past_miles = ("{0:.2f}".format(sum(past_mile_list)))
            past_ten_percent = float(("{0:.2f}".format(float(past_miles) * .1)))

            return past_ten_percent
        past_list = []
        past_list.append(period_ten_percent(Sunday,Monday))
        past_list.append(period_ten_percent(Sunday+1,Monday+1))
        past_list.append(period_ten_percent(Sunday+2,Monday+2))
        past_list.append(period_ten_percent(Sunday+3,Monday+3))

        past_four = sum(past_list)
        past_avg = past_four/4
        return past_avg

    past_avg = rolling_ten_percent(Sunday,Monday)

    #create lists of items to display
    past_run_title_label = []
    for i in list(sorted(past_dict)):
        past_run_title_label.append(past_dict[i]['weekday_short_date'])
    past_run_mile_label = []
    for i in list(sorted(past_dict)):
        past_run_mile_label.append(past_dict[i]['distance_miles'])
    past_run_pace_label = []
    for i in list(sorted(past_dict)):
        past_run_pace_label.append(past_dict[i]['pace'])
    past_run_elapsed_label = []
    for i in list(sorted(past_dict)):
        past_run_elapsed_label.append(str(past_dict[i]['elapsed']))
    past_run_treadmill_label = []
    for i in list(sorted(past_dict)):
        past_run_treadmill_label.append(str(past_dict[i]['total_elevation_feet']))

    #bottom values
    dec_pace_list = []
    for i in list(sorted(past_dict)):
        dec_pace_list.append(past_dict[i]['pace_dec'])
    current_pace_average = data.convert_dec_time(sum(dec_pace_list)/len(dec_pace_list))

    seconds_elapsed_list = []
    for i in list(sorted(past_dict)):
        seconds_elapsed_list.append(past_dict[i]['elapsed_time'])
    total_elapsed_seconds = sum(seconds_elapsed_list)
    current_duration_total = data.convert_seconds_to_minutes(total_elapsed_seconds)

    current_elevation_list = []
    for i in list(sorted(past_dict)):
        current_elevation_list.append(float(past_dict[i]['total_elevation_feet']))
    current_elevation_total = "{0:.2f}".format(sum(current_elevation_list))

    #calculate remaining
    current_miles = current_info['current_miles']
    current_week_count = current_info['current_week_count']

    #THIS IS WHERE CSUBVIEW SUBTITLES HAPPEN
    #remaining_miles = str("{0:.2f}".format((float(past_ten_percent) + float(past_miles)) - float(current_miles))) #this uses just 1 week
    remaining_miles = str("{0:.2f}".format((float(past_avg) + float(past_miles)) - float(current_miles))) #this uses past rolling 4 weeks
    main_dict['remaining_miles'] = remaining_miles
    main_dict['remaining_miles_match'] = str("{0:.2f}".format(float(past_miles) - float(current_miles)))
    if float(runs_per_week)-float(current_week_count) != 0:
        miles_per_run_remaining = float(remaining_miles)/(runs_per_week-float(current_week_count))
        main_dict['remaining_per_run'] = format_text(miles_per_run_remaining)
    else:
        main_dict['remaining_per_run'] = "0"
    remaining_miles_down = str("{0:.2f}".format(float(past_miles) - float(current_miles) - float(past_avg))) #this uses past rolling 4 weeks
    main_dict['remaining_miles_down'] = remaining_miles_down

    #
    sensor = {}
    sensor['state'] = get_time.convert_weekday_short(get_time.LM(Monday)) + " - " + get_time.convert_weekday_short(get_time.LS(Sunday))
    sensor['attributes'] = {}
    sensor['attributes']['Ten Percent'] = str(past_ten_percent)
    sensor['attributes']['4 Weeks Roll'] = format_text(past_avg)
    sensor['attributes']['Date'] = "\n".join(past_run_title_label)
    sensor['attributes']['Distance'] = "\n".join(past_run_mile_label)
    sensor['attributes']['Duration'] = "\n".join(past_run_elapsed_label)
    sensor['attributes']['Pace'] = "\n".join(past_run_pace_label)
    sensor['attributes']['Elevation'] = "\n".join(past_run_treadmill_label)
    sensor['attributes']['Total Distance'] = str(past_miles)
    sensor['attributes']['Total Duration'] = str(current_duration_total)
    sensor['attributes']['AVG Pace'] = str(current_pace_average)
    sensor['attributes']['Total Elevation'] = current_elevation_total

    sensor_name = "sensor.run_"+str(Monday)+"_Weeks_Ago_Stats"
    post_sensor(sensor_name,json.dumps(sensor))

    return main_dict

def weekly(current_info):

    def how_most_running_period(days): #Used for "Days" as running consecutive days
        output_dict = {}
        input_day = days
        result_dict = full_running_totals(database.copy(),input_day,'distance_miles')
        current_total_date = sorted(result_dict.keys())[-1]
        current_total = result_dict[current_total_date]
        highest_total = 0
        for run in result_dict:
            if result_dict[run] > highest_total:
                highest_total = result_dict[run]
                highest_total_date = run
        #result_dict has date as key, 7 day total as value
        output_dict['highest_total'] = highest_total
        output_dict['highest_total_date'] = highest_total_date
        output_dict['current_total'] = current_total
        output_dict['current_total_date'] = current_total_date
        output_dict['difference_distance'] = output_dict['current_total'] - output_dict['highest_total']
        output_dict['difference_time'] =  output_dict['current_total_date'] - output_dict['highest_total_date']

        return output_dict

    run_period_7 = how_most_running_period(7)
    run_period_30 = how_most_running_period(30)

    current_miles = current_info['current_miles']
    current_week_count = current_info['current_week_count']

    #taken from top peroid
    weekly_dict = weekly_stats(database.copy())

    #find how well this week is going
    top_week_in_weeks = 0 #this may need to be changed
    for week in weekly_dict: #list iterates from current week backwards
        #find how well this week is going
        if float(weekly_dict[week]['miles_ran']) > float(current_miles): #this weeks miles
            print("historic week is greater than current")
            break
        else:
            top_week_in_weeks = top_week_in_weeks + 1

    #find how many days since top week
    max_weekly_miles = 0
    for week in weekly_dict: #list iterates from current week backwards
        #find top week
        if weekly_dict[week]['miles_ran'] > max_weekly_miles:
            max_weekly_miles = float(weekly_dict[week]['miles_ran'])
            most_miles_week = week
            #added
            mmw_dt = weekly_dict[most_miles_week]['datetime']
            mmw_ds = datetime.datetime.now() - mmw_dt
            if mmw_ds.days < 0: #fix negative days if done within 24 hours
                mmw_ds = 0
            else:
                mmw_ds = mmw_ds.days

    sensor = {}
    sensor['state'] = str(current_miles)
    post_sensor("sensor.running_this_week",json.dumps(sensor))

    sensor['state'] = format_text(run_period_7['current_total'])
    post_sensor("sensor.running_7_day_total",json.dumps(sensor))

    sensor = {}
    sensor['state'] = 'Weekly'
    sensor['attributes'] = {}
    sensor['attributes']['This Week'] = str(current_miles)
    sensor['attributes']['Best Week'] = format_text(max_weekly_miles)
    sensor['attributes']['Best Difference'] = format_text(float(max_weekly_miles)-float(current_miles))
    sensor['attributes']['Days Since'] = str(mmw_ds)
    sensor['attributes']['Weeks Top'] = str(top_week_in_weeks)
    sensor['attributes']['7 Day'] = format_text(run_period_7['current_total'])
    sensor['attributes']['Best 7 Day'] = format_text(run_period_7['highest_total'])
    sensor['attributes']['7 Day Difference'] = format_text(run_period_7['difference_distance'])
    sensor['attributes']['7 Day Days Since'] = str(run_period_7['difference_time'].days)
    sensor['attributes']['30 Day'] = format_text(run_period_30['current_total'])
    sensor['attributes']['Best 30 Day'] = format_text(run_period_30['highest_total'])
    sensor['attributes']['Best 30 Difference'] = format_text(run_period_30['difference_distance'])
    sensor['attributes']['Best 30 Days Since'] = str(run_period_30['difference_time'].days)

    post_sensor("sensor.run_weekly_stats",json.dumps(sensor))

def monthly():

    def MTD(dictionary,months_ago): #month to date
        month_total_dict = monthly_daily_totals(dictionary,months_ago,'distance_miles')
        if month_total_dict.keys():
            return month_total_dict[max(month_total_dict.keys())] #finds highest date, uses that date to find value
        else:
            return 0

    this_month_full = monthly_daily_totals(database.copy(),0,'distance_miles')
    last_month_full = monthly_daily_totals(database.copy(),1,'distance_miles')
    this_month = MTD(database.copy(),0)
    last_month = MTD(database.copy(),1)
    month_difference = this_month - last_month
    now = datetime.datetime.now()
    if now.month == 12:
      past = datetime.datetime(now.year,12,31)
    else:
      past = datetime.datetime(now.year, now.month - (0-1), 1) - (datetime.timedelta(days=1))
    LOM = datetime.datetime(past.year, past.month, past.day, hour=23, minute=59, second=59)
    days_remaining = LOM.day - now.day
    #runs_per_week = 3
    runs_remain = math.ceil(days_remaining*(runs_per_week/7))
    if runs_remain == 0:
      runs_remain = 1
    monthly_dict = monthly_stats(database.copy())
    max_miles = 0
    for month in monthly_dict:
        if monthly_dict[month]['miles_ran'] > max_miles:
            max_miles = int(monthly_dict[month]['miles_ran'])
            most_miles_month = month

    sensor = {}
    sensor['state'] = format_text(this_month)
    post_sensor("sensor.running_this_month",json.dumps(sensor))

    sensor['state'] = format_text(len(this_month_full))
    post_sensor("sensor.running_this_month_count",json.dumps(sensor))

    sensor['state'] = get_time.convert_month_name(datetime.datetime.now())
    sensor['attributes'] = {}
    sensor['attributes']['This Month'] = format_text(this_month)
    sensor['attributes']['This Run Count'] = format_text(len(this_month_full))
    sensor['attributes']['Last Month'] = format_text(last_month)
    sensor['attributes']['Last Run Count'] = format_text(len(last_month_full))
    sensor['attributes']['Difference'] = format_text(month_difference)
    sensor['attributes']['Runs Remain'] = format_text(runs_remain)
    sensor['attributes']['MPR Last Month'] = format_text(abs(month_difference/runs_remain))
    sensor['attributes']['50 Miles Goal'] = format_text(this_month-50)
    sensor['attributes']['MPR to 50M'] = format_text((50-this_month)/runs_remain)
    sensor['attributes']['Month Record'] = str(max_miles)
    sensor['attributes']['MPR to Record'] = format_text((max_miles-this_month)/runs_remain)

    post_sensor("sensor.Run_Monthly_Stats",json.dumps(sensor))

def yearly():
    #this year
    now = datetime.datetime.now()
    if now.month == 12:
      past = datetime.datetime(now.year,12,31)
    else:
      past = datetime.datetime(now.year, now.month - (0-1), 1) - (datetime.timedelta(days=1))
    LOM = datetime.datetime(past.year, past.month, past.day, hour=23, minute=59, second=59)
    end_of_year = datetime.datetime(now.year, 12, 31)
    days_remaining = LOM.day - now.day

    ytd_dict = database.copy()
    for key in list(ytd_dict):
        if key < get_time.FOY():
            del ytd_dict[key]
    ytd_miles = []
    for run in ytd_dict:
        ytd_miles.append(float(ytd_dict[run]['distance_miles']))
    miles_this_year = sum(ytd_miles)

    #last year
    timestamp = datetime.datetime.now()
    past_ytd_dict = database.copy()
    for key in list(past_ytd_dict):
        if key < get_time.PFOY():
            del past_ytd_dict[key]
        if key > datetime.datetime(timestamp.year - 1, timestamp.month, timestamp.day): #get date this time last year
            del past_ytd_dict[key]
    pytd_miles = []
    for run in past_ytd_dict:
        pytd_miles.append(float(past_ytd_dict[run]['distance_miles']))
    miles_last_year_this_time = sum(pytd_miles)

    MPD = goal_mileage/365 #miels per day starting 1/1
    day_of_year = now.timetuple().tm_yday #numerical value of day in the year
    #day_of_year = LOM.timetuple().tm_yday #found the day of the last of month for some reason, changed to above
    target_miles = MPD*day_of_year #what my current target_miles should be - NOT year long goal
    remaining_ytd_miles = miles_this_year - target_miles #why is this named like this?
    days_remaining_in_year = (end_of_year - now).days
    weeks_remaining_in_year = days_remaining_in_year/7

    #new 3.6.18
    goal_miles_left_in_year = goal_mileage - miles_this_year #reverse of remaining_ytd_miles for some reason
    goal_miles_per_day_now = goal_miles_left_in_year/days_remaining_in_year

    #goal_miles_per_week_now = goal_miles_per_day_now*7
    goal_miles_per_week_now = goal_miles_left_in_year/weeks_remaining_in_year
    goal_miles_per_run_now = goal_miles_per_week_now/runs_per_week

    #new 5.16.18 - Goal predictions
    def goal_hit_date(filter_day):
        yearly_dict = yearly_totals(database.copy(),0) #current year
        x_list = []
        y_list = []
        for event in yearly_dict:
            if event > filter_day:
                x_list.append(event)
                y_list.append(yearly_dict[event])

        def extended_prediction(x_list,y_list,end_day):
            if not y_list:
                y_list = [0]
            if not x_list:
                x_list = [0]
            extended_range = list(range(x_list[0],end_day))
            model = np.polyfit(x_list, y_list, 1)
            predicted = np.polyval(model, extended_range)
            return extended_range, predicted

        extended_range_30, predicted_30 = extended_prediction(x_list, y_list, 720)
        the_list = []
        for x,y in zip(extended_range_30,predicted_30):
            if y > goal_mileage:
                the_list.append(x)
        if not the_list:
            goal_day = 365 #changed from 0 as it showed last year when it could not predict
        else:
            goal_day = the_list[0]
        timestamp = datetime.datetime.now()
        goal_day_nice = datetime.datetime(timestamp.year, 1, 1) + datetime.timedelta(goal_day - 1)
        return str(goal_day_nice.month)+"."+str(goal_day_nice.day)+"."+str(goal_day_nice.year)[-2:]

    todays_number = datetime.datetime.now().timetuple().tm_yday #finds number of year
    days_ago_30 = todays_number - 30 #number to filter entires out from since not datetime objects
    days_ago_90 = todays_number - 90

    goal_30 = goal_hit_date(days_ago_30) #30 days ago
    goal_90 = goal_hit_date(days_ago_90)
    goal_year = goal_hit_date(0) #0 is beginning of year

    sensor = {}
    sensor['state'] = format_text(miles_this_year)
    post_sensor("sensor.running_ytd_miles",json.dumps(sensor))

    sensor['state'] = format_text(miles_last_year_this_time)
    post_sensor("sensor.running_last_ytd_miles",json.dumps(sensor))

    sensor['state'] = format_text(miles_this_year-miles_last_year_this_time)
    post_sensor("sensor.running_ytd_difference",json.dumps(sensor))

    sensor['state'] = get_time.convert_year_name(datetime.datetime.now())+" Goal: "+str(goal_mileage)+" Miles"
    sensor['attributes'] = {}
    sensor['attributes']['YTD Miles'] = format_text(miles_this_year)
    sensor['attributes']['Last YTD by now'] = format_text(miles_last_year_this_time)
    sensor['attributes']['YTD Difference'] = format_text(miles_this_year-miles_last_year_this_time)
    sensor['attributes']['Days Remain'] = str(days_remaining_in_year)
    sensor['attributes']['Weeks Remain'] = format_text(weeks_remaining_in_year)
    sensor['attributes']['Goal (30)'] = goal_30
    sensor['attributes']['Goal (90)'] = goal_90
    sensor['attributes']['Goal (Year)'] = goal_year
    sensor['attributes']['Yearly Goal'] = format_text(target_miles)
    sensor['attributes']['Goal Difference'] = format_text(remaining_ytd_miles)
    sensor['attributes']['Miles Per Day'] = format_text(goal_miles_per_day_now)
    sensor['attributes']['Miles Per Week'] = format_text(goal_miles_per_week_now)
    sensor['attributes']['Miles Per Run'] = format_text(goal_miles_per_run_now)

    post_sensor("sensor.Run_Yearly_Stats",json.dumps(sensor))

def yearly_graph():
    #modified from running_graphs to show YTD mileage
    yearly_dict = yearly_totals(database.copy(),0) #current year
    #print(yearly_dict)
    yearly_dict2 = yearly_totals(database.copy(),1) #last year
    yearly_dict3 = yearly_totals(database.copy(),2) #2 years
    yearly_dict4 = yearly_totals(database.copy(),3) #3 years
    yearly_dict5 = yearly_totals(database.copy(),4) #4 years

    def graph(formula):
        x = np.array(range(0,366))
        y = eval(formula)
        plt.plot(x, y, 'w', linestyle=':', linewidth=4,label=goal_mileage)

    label1=int(datetime.datetime.now().year)
    label2=label1-1
    label3=label1-2
    label4=label1-3 #3 years ago
    label5=label1-4 #4 years ago

    graph('x*('+str(goal_mileage)+'/365)')
    #in order of appearance
    plt.plot(list(yearly_dict5.keys()),list(yearly_dict5.values()), 'white', linewidth=4, label=label5)
    plt.plot(list(yearly_dict4.keys()),list(yearly_dict4.values()), 'orange', linewidth=4, label=label4)
    plt.plot(list(yearly_dict3.keys()),list(yearly_dict3.values()), 'green', linewidth=4,label=label3)
    plt.plot(list(yearly_dict2.keys()),list(yearly_dict2.values()), 'blue', linewidth=4,label=label2)
    plt.plot(list(yearly_dict.keys()),list(yearly_dict.values()), 'red', linewidth=4, label=label1)


    plt.style.use('dark_background')
    plt.axis('off')
    plt.legend(loc=0,fontsize=18) #20
    plt.subplots_adjust(left=0, bottom=0, right=1, top=1,
                wspace=None, hspace=None)

    plt.savefig(png_location+"Yearly_Compare.png", transparent='True')
    #plt.show()
    #b = BytesIO()
    #plt.savefig(b, transparent='True')
    plt.close('all')
    #return b

def yearly_prediction_graph(): #This is currently used
    #modified from running_graphs to show YTD mileage

    def graph(formula):
        x = np.array(range(0,366))
        y = eval(formula)
        plt.plot(x, y, 'w', linestyle=':', linewidth=4,label=goal_mileage)

    yearly_dict = yearly_totals(database.copy(),0) #current year
    yearly_dict2 = yearly_totals(database.copy(),1) #last year

    x_list = []
    y_list = []
    x2_list = []
    y2_list = []

    todays_number = datetime.datetime.now().timetuple().tm_yday #finds number of year
    month_ago_number = todays_number - 30 #number to filter entires out from since not datetime objects

    for event in yearly_dict:
        x_list.append(event)
        y_list.append(yearly_dict[event])
        if event > month_ago_number:
            x2_list.append(event)
            y2_list.append(yearly_dict[event])

    def extended_prediction(x_list,y_list,end_day):
        if not y_list:
            y_list = [0]
        if not x_list:
            x_list = [0]
        extended_range = list(range(x_list[0],end_day))
        model = np.polyfit(x_list, y_list, 1)
        predicted = np.polyval(model, extended_range)
        return extended_range, predicted

    extended_range, predicted = extended_prediction(x_list, y_list, 365)
    extended_range_30, predicted_30 = extended_prediction(x2_list, y2_list, 365)

    graph('x*('+str(goal_mileage)+'/365)')
    plt.plot(extended_range, predicted, linestyle='--',color='green',linewidth=4,label='Year: '+format_text(predicted[-1]))
    plt.plot(extended_range_30, predicted_30, linestyle='--',color='blue',linewidth=4,label='30 Days: '+format_text(predicted_30[-1]))
    plt.plot(list(yearly_dict.keys()),list(yearly_dict.values()),label=('This Year'),color='red',lw='4')

    plt.style.use('dark_background')
    plt.axis('off')
    plt.legend(loc=0,fontsize=18)#20
    plt.subplots_adjust(left=0, bottom=0, right=1, top=1,
                wspace=None, hspace=None)

    plt.savefig(png_location+"Yearly_Predictions.png", transparent='True')
    # b = BytesIO()
    # plt.savefig(b, transparent='True')
    plt.close('all')
    # return b
def run_and_graph(latitude,longitude):
    print("Graphing...")

    fig,ax=plt.subplots()
    ax.plot(longitude,latitude,color="#fc4c02",linewidth=4)
    ax.set_axis_off()
    ax.set_aspect(aspect=1.5) #not sure how to fix this, adjusting this changes the width of the graph
    plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=None, hspace=None)

    print("Saving...")
    plt.savefig(png_location+"Last_Run.png", transparent='True')
    plt.close('all')

def last_run():

    last_key = next(iter(reversed(sorted(database))))

    #Graph polyline
    run_and_graph(database[last_key]['smash']['recordingValues'][1],database[last_key]['smash']['recordingValues'][2])

    sensor = {}
    sensor['state'] = database[last_key]['name']
    sensor['attributes'] = {}
    sensor['attributes']['Date'] = database[last_key]['weekday_short_date']
    sensor['attributes']['Distance'] = database[last_key]['distance_miles']
    sensor['attributes']['Pace'] = database[last_key]['pace']
    sensor['attributes']['Speed Variability'] = database[last_key]['smash']['speedVariability']
    post_sensor("sensor.running_last_run",json.dumps(sensor))

    sensor = {}
    sensor['state'] = len(database[last_key]['smash']['notables'])
    sensor['attributes'] = {}

    for n,x in enumerate(database[last_key]['smash']['notables']):
        n = n + 1
        print(x)
        sensor['attributes'][x['description']] = n
    post_sensor("sensor.running_last_run_notables",json.dumps(sensor))



database = data.run()

last_run()
yearly_graph()
yearly_prediction_graph()

current_info = current_period(database)

yearly()
monthly()
weekly(current_info)
period(database,0,1,current_info)
