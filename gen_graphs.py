import matplotlib
matplotlib.use('Agg')

import get_time
import data
import calc
import matplotlib.pyplot as plt
import pylab
import matplotlib.dates as mdates
from pprint import pprint
import numpy as np
import datetime
import pandas as pd
from random import randint
from sklearn.linear_model import LinearRegression
from time import mktime
import yagmail
import io
import credentials
#####

global mass_figsize
mass_figsize=(13,10)
png_location = credentials.png_location

#####
gmail_user = credentials.gmail_user
gmail_password = credentials.gmail_password
yag = yagmail.SMTP( gmail_user, gmail_password)
temp_folder = credentials.temp_folder

global graph_list
graph_list = []

master_dict = data.run()

def append_image(graph_name,plt):
    name = temp_folder+graph_name+'.png' #this needs to change if run by cron
    plt.savefig(name)
    graph_list.append(name)


def format_number(number):
    return str("{0:.2f}".format(number))

def trend_line(x_list,y_list):
    df = pd.DataFrame()
    df['dates'] = x_list
    df['miles'] = y_list
    df['seconds'] = df.dates.apply(lambda x: mktime(x.timetuple()))
    model = LinearRegression().fit(df.seconds.values.reshape(-1,1), df.miles)
    df['y_trend'] = model.predict(df.seconds.values.reshape(-1,1))

    return df

def weekly_compare():
    print("Weekly...")

    diff = datetime.datetime.now() - datetime.datetime(2019, 1, 1) #when to start the graph

    weeks_back = 96 #int(diff.days/7)
    weeks_to_calculate = list(range(0,weeks_back)) #calculate 0 to 17

    week_dict = {}
    for week in weeks_to_calculate:
        week_dict[week] = master_dict.copy() #make a master dict for each week to calculate

    for week in week_dict:
        for key in list(week_dict[week]): #for each key in each master dictionary
            if key < get_time.LM(week): #if older than last monday (0 is 1, 1 is 2,2 mondays ago)
                del week_dict[week][key]
        for key in list(week_dict[week]):
           if key > get_time.LS(week-1): #if newer than last sunday (0 is 1)
               del week_dict[week][key]

    #Mileage
    miles_dict = {}
    pace_dict = {}
    hr_dict = {}
    ele_dict = {}
    tred_dict = {}
    count_dict = {}
    partner_dict = {}

    for week in week_dict: #this creates the lists of y values for the below graphs
        if week_dict[week]: #check to see if any activites exist in the given week
            mile_list = []
            pace_list = []
            hr_list = []
            ele_list = []
            tred_list = []
            count_list = []
            partner_list = []
            for activity in week_dict[week]:
                count_list.append(1)
                mile_list.append(float(week_dict[week][activity]['distance_miles']))
                pace_list.append(float(week_dict[week][activity]['pace_dec']))
                if float(week_dict[week][activity]['average_heartrate']) != 0: #don't cound the 0's in runs i manually enter
                    hr_list.append(float(week_dict[week][activity]['average_heartrate']))
                #print(week_dict[week][activity]['average_heartrate'])
                if 'total_elevation_feet' in week_dict[week][activity]:
                    ele_list.append(float(week_dict[week][activity]['total_elevation_feet']))
                    ele_dict[get_time.LM(week)] = sum(ele_list)#/len(ele_list)
                # else:
                #     ele_dict[get_time.LM(week)] = 0
                if 'treadmill_flagged' in week_dict[week][activity]:
                    if week_dict[week][activity]['treadmill_flagged'] == 'yes':
                        tred_list.append(1)
                if 'athlete_count' in week_dict[week][activity]:
                    if week_dict[week][activity]['athlete_count'] > 1:
                        partner_list.append(1)
                # else:
                #     tred_list.append(0)
            hr_dict[get_time.LM(week)] = sum(hr_list)/len(hr_list)
            miles_dict[get_time.LM(week)] = sum(mile_list)
            pace_dict[get_time.LM(week)] = sum(pace_list)/len(pace_list)
            tred_dict[get_time.LM(week)] = sum(tred_list)
            count_dict[get_time.LM(week)] = sum(count_list)
        # else:
        #     miles_dict[get_time.LM(week)] = 0
        #     pace_dict[get_time.LM(week)] = 0
        #     hr_dict[get_time.LM(week)] = 0
        #     count_dict[get_time.LM(week)] = 0

    x_list = []
    y_list = []
    for month in miles_dict:
        x_list.append(month)
        y_list.append(miles_dict[month])

    x2_list = []
    y2_list = []
    for month in pace_dict:
        x2_list.append(month)
        y2_list.append(pace_dict[month])

    x3_list = []
    y3_list = []
    for month in hr_dict:
        x3_list.append(month)
        y3_list.append(hr_dict[month])

    x4_list = []
    y4_list = []
    for month in ele_dict:
        x4_list.append(month)
        y4_list.append(ele_dict[month])

    x5_list = []
    y5_list = []
    for month in tred_dict:
        x5_list.append(month)
        y5_list.append(tred_dict[month])

    x6_list = []
    y6_list = []
    for month in count_dict:
        x6_list.append(month)
        y6_list.append(count_dict[month])

    x7_list = []
    y7_list = []
    for month in partner_dict:
        x7_list.append(month)
        y7_list.append(partner_dict[month])

    ########
    fig, (ax1,ax2,ax4,ax5) = plt.subplots(nrows=4, figsize=mass_figsize) #figsize sets window

    myFmt = mdates.DateFormatter('%m')
    months = mdates.MonthLocator()  # every month

    # Miles Ran
    ax1df = trend_line(x_list, y_list)
    ax1.bar(x_list, y_list, align='center', width=6, label="Total: "+format_number(sum(y_list)))
    ax1slope = format_number(float(ax1df['y_trend'].iloc[0]) - float(ax1df['y_trend'].iloc[-1]))
    ax1.plot_date(ax1df.dates, ax1df.y_trend, 'red', ls='--', marker='None',label=ax1slope)
    ax1.set_ylabel('Miles Ran', color='b')
    ax1.set_yticks(range(0,int(max(y_list))+1,5))
    #ax1.set_xticks(x_list)
    ax1.xaxis.set_major_locator(months)
    ax1.xaxis.set_major_formatter(myFmt)
    #ax.set_yticks([]) # values
    #fig.autofmt_xdate()
    ax1.tick_params('y', colors='b')

    ax1.yaxis.grid(True)
    ax1.legend()

    #labels = ax1.set_xticklabels(x_list)
    # for i, label in enumerate(labels):
    #     label.set_y(label.get_position()[1] - (i % 3) * 0.9) #this offsets every other (or 3rd) label by .9 vertically, essentially removing


    # Pace vs HR
    ax2.plot(x2_list,y2_list, color='g', linewidth=2, label='Pace: '+format_number(sum(y2_list)/len(y2_list)))
    ax2.set_ylabel('Pace (Decimal)', color='g')
    ax2.tick_params('y', colors='g')

    #labels = ax2.set_xticklabels(x2_list)
    # for i, label in enumerate(labels):
    #     label.set_y(label.get_position()[1] - (i % 2) * 0.09)
    ax2.xaxis.set_major_locator(months)
    ax2.xaxis.set_major_formatter(myFmt)

    ax2.yaxis.grid(True)
    ax2.legend()

    ax3 = ax2.twinx()
    ax3.plot(x3_list,y3_list, color='r', label='Avg HR')
    ax3.set_ylabel('Avg of Avg HR', color='r')
    ax3.tick_params('y', colors='r')

    ax3.xaxis.set_major_locator(months)
    ax3.xaxis.set_major_formatter(myFmt)

    #Outside/partner/treadmill
    ax4.bar(x6_list,y6_list, align='center', width=6, color='b', label='Outdoor') #total runs
    ax4.bar(x5_list,y5_list, align='center', width=6, color='#fc5e02', label=('Treadmill: '+str(sum(y5_list)))) #treadmill runs
    ax4.bar(x7_list,y7_list, align='center', width=6, color='#f442e2', label=('Partner: '+str(sum(y7_list)))) #treadmill runs
    ax4.set_ylabel('Runs Per Week', color='b')
    ax4.set_yticks(range(max(y6_list)+1))
    # ax4.set_xticks(x5_list)
    # #labels = ax4.set_xticklabels(x5_list)
    # for i, label in enumerate(labels):
    #     label.set_y(label.get_position()[1] - (i % 3) * 0.09)
    ax4.xaxis.set_major_locator(months)
    ax4.xaxis.set_major_formatter(myFmt)
    ax4.tick_params('y', colors='b')
    ax4.yaxis.grid(True)
    #ax4.legend() #COMMENT THIS LINE OUT this causes issues on linux system

    #elevation
    ax5.plot(x4_list,y4_list, label='Total: '+format_number(sum(y4_list)))
    ax5.set_ylabel('Total Elevation (Feet)')
    #ax5.set_yticks(range(int(max(y4_list)+1)),20)
    #ax5.set_xticks(x4_list)
    # labels = ax5.set_xticklabels(x4_list)
    # for i, label in enumerate(labels):
    #     label.set_y(label.get_position()[1] - (i % 3) * 0.09)
    ax5.xaxis.set_major_locator(months)
    ax5.xaxis.set_major_formatter(myFmt)
    ax5.yaxis.grid(True)
    ax5.legend()

    plt.setp(ax1.get_xticklabels(), rotation=10, horizontalalignment='center')
    plt.setp(ax2.get_xticklabels(), rotation=10, horizontalalignment='center')
    plt.setp(ax4.get_xticklabels(), rotation=10, horizontalalignment='center')
    plt.setp(ax5.get_xticklabels(), rotation=10, horizontalalignment='center')


    fig.tight_layout()
    fig.subplots_adjust(hspace=0.2)
    #plt.show()

    append_image("Weekly_Compare",plt)
    plt.savefig(png_location+"1_Weekly_Compare.png")

    ####

def monthly_compare():
    print("Monthly...")

    weeks_to_calculate = list(range(0,24))

    week_dict = {}

    for week in weeks_to_calculate:
        week_dict[week] = master_dict.copy() #make a master dict for each week to calculate

    for week in week_dict:

        for key in list(week_dict[week]): #for each key in each master dictionary
            if key < get_time.FOM(week): # this is causing a lot of issues
                del week_dict[week][key]
        for key in list(week_dict[week]):
           if key > get_time.LOM(week):
               del week_dict[week][key]

    #Mileage
    miles_dict = {}
    pace_dict = {}
    hr_dict = {}
    ele_dict = {}
    tred_dict = {}
    count_dict = {}

    for week in week_dict:
        if week_dict[week]: #check to see if any activites exist in the given week
            mile_list = []
            pace_list = []
            hr_list = []
            ele_list = []
            tred_list = []
            count_list = []
            for activity in week_dict[week]:
                count_list.append(1)
                mile_list.append(float(week_dict[week][activity]['distance_miles']))
                pace_list.append(float(week_dict[week][activity]['pace_dec']))
                if float(week_dict[week][activity]['average_heartrate']) != 0: #don't cound the 0's in runs i manually enter
                    hr_list.append(float(week_dict[week][activity]['average_heartrate']))
                #print(week_dict[week][activity]['average_heartrate'])
                if 'total_elevation_feet' in week_dict[week][activity]:
                    ele_list.append(float(week_dict[week][activity]['total_elevation_feet']))
                    ele_dict[get_time.FOM(week)] = sum(ele_list)#/len(ele_list)
                # else:
                #     ele_dict[get_time.FOM(week)] = 0
                if 'treadmill_flagged' in week_dict[week][activity]:
                    if week_dict[week][activity]['treadmill_flagged'] == 'yes':
                        tred_list.append(1)
                # else:
                #     tred_list.append(0)
            hr_dict[get_time.FOM(week)] = sum(hr_list)/len(hr_list)
            miles_dict[get_time.FOM(week)] = sum(mile_list)
            pace_dict[get_time.FOM(week)] = sum(pace_list)/len(pace_list)
            tred_dict[get_time.FOM(week)] = sum(tred_list)
            count_dict[get_time.FOM(week)] = sum(count_list)
        # else:
        #     miles_dict[get_time.FOM(week)] = 0
        #     pace_dict[get_time.FOM(week)] = 0
        #     hr_dict[get_time.FOM(week)] = 0
        #     count_dict[get_time.FOM(week)] = 0

    x_list = []
    y_list = []
    for month in miles_dict:
        x_list.append(month)
        y_list.append(miles_dict[month])

    x2_list = []
    y2_list = []
    for month in pace_dict:
        x2_list.append(month)
        y2_list.append(pace_dict[month])

    x3_list = []
    y3_list = []
    for month in hr_dict:
        x3_list.append(month)
        y3_list.append(hr_dict[month])

    x4_list = []
    y4_list = []
    for month in ele_dict:
        x4_list.append(month)
        y4_list.append(ele_dict[month])

    x5_list = []
    y5_list = []
    for month in tred_dict:
        x5_list.append(month)
        y5_list.append(tred_dict[month])

    x6_list = []
    y6_list = []
    for month in count_dict:
        x6_list.append(month)
        y6_list.append(count_dict[month])

    ########
    fig, (ax1,ax2,ax4,ax5) = plt.subplots(nrows=4, figsize=mass_figsize) #figsize sets window

    myFmt = mdates.DateFormatter('%m')
    months = mdates.MonthLocator()  # every month

    ax1df = trend_line(x_list, y_list)
    ax1.bar(x_list, y_list, align='center', width=25)
    ax1slope = format_number(float(ax1df['y_trend'].iloc[0]) - float(ax1df['y_trend'].iloc[-1]))
    ax1.plot_date(ax1df.dates, ax1df.y_trend, 'red', ls='--', marker='None',label=ax1slope)
    ax1.set_ylabel('Miles Ran', color='b')
    #ax1.set_yticks(range(int(max(y_list))+1),3)
    ax1.tick_params('y', colors='b')
    ax1.yaxis.grid(True)
    ax1.legend()
    # ax1.set_xticks(x_list)
    # labels = ax1.set_xticklabels(x_list)
    # for i, label in enumerate(labels):
    #     label.set_y(label.get_position()[1] - (i % 2) * 0.09)
    ax1.xaxis.set_major_locator(months)
    ax1.xaxis.set_major_formatter(myFmt)

    ax2.plot(x2_list,y2_list, color='g', label='Pace', linewidth=2)
    ax2.set_ylabel('Pace (Decimal)', color='g')
    ax2.tick_params('y', colors='g')
    ax2.yaxis.grid(True)
    ax2.xaxis.set_major_locator(months)
    ax2.xaxis.set_major_formatter(myFmt)

    ax3 = ax2.twinx()
    ax3.plot(x3_list,y3_list, color='r', label='Avg HR')
    ax3.set_ylabel('Avg of Avg HR', color='r')
    ax3.tick_params('y', colors='r')
    # ax2.set_xticks(x2_list)
    # labels = ax2.set_xticklabels(x2_list)
    # for i, label in enumerate(labels):
    #     label.set_y(label.get_position()[1] - (i % 2) * 0.09)
    ax3.xaxis.set_major_locator(months)
    ax3.xaxis.set_major_formatter(myFmt)




    ax4.bar(x6_list,y6_list, align='center', width=25, color='b', label='Outdoor') #total runs
    ax4.bar(x5_list,y5_list, align='center', width=25, color='#fc5e02', label='Treadmill') #treadmill runs
    ax4.set_ylabel('Runs Per Month', color='b')
    ax4.set_yticks(range(0,max(y6_list)+1,5))
    ax4.tick_params('y', colors='b')
    ax4.yaxis.grid(True)
    ax4.legend()
    # ax4.set_xticks(x5_list)
    # labels = ax4.set_xticklabels(x6_list)
    # for i, label in enumerate(labels):
    #     label.set_y(label.get_position()[1] - (i % 2) * 0.09)
    ax4.xaxis.set_major_locator(months)
    ax4.xaxis.set_major_formatter(myFmt)

    ax5.plot(x4_list,y4_list, label='Total')
    ax5.set_ylabel('Total Elevation (Feet)')
    #ax5.set_yticks(range(int(max(y4_list)+1)),20)
    ax5.yaxis.grid(True)
    ax5.legend()
    # ax5.set_xticks(x4_list)
    # labels = ax5.set_xticklabels(x4_list)
    # for i, label in enumerate(labels):
    #     label.set_y(label.get_position()[1] - (i % 2) * 0.09)
    ax5.xaxis.set_major_locator(months)
    ax5.xaxis.set_major_formatter(myFmt)

    plt.setp(ax1.get_xticklabels(), rotation=10, horizontalalignment='center')
    plt.setp(ax2.get_xticklabels(), rotation=10, horizontalalignment='center')
    plt.setp(ax4.get_xticklabels(), rotation=10, horizontalalignment='center')
    plt.setp(ax5.get_xticklabels(), rotation=10, horizontalalignment='center')

    fig.tight_layout()
    fig.subplots_adjust(hspace=0.2)
    plt.savefig(png_location+"2_Monthly_Compare.png")

    append_image("Monthly_Compare",plt)

def yearly_compare():
    print("Yearly...")
    year_linewidth = 4
    goal_linewidth = 2
    linewidth = year_linewidth
    single_dict = {}

    # 2017 - green
    # 2018 - blue
    # 2019 - red
    # goal - white

    # for event in master_dict:
    #     if master_dict[event]['athlete_count'] == 1:
    #         if master_dict[event]['treadmill_flagged'] == 'no':
    #             single_dict[event] = master_dict[event]
    #
    # single_yearly_dict = calc.yearly_totals(single_dict.copy(),0) #this year
    # single_yearly_dict_2 = calc.yearly_totals(single_dict.copy(),1) #last year

    label1=int(datetime.datetime.now().year)
    label2=label1-1
    label3=label1-2
    label4=label1-3 #3 years ago
    label5=label1-4 #4 years ago

    yearly_dict = calc.yearly_totals(master_dict.copy(),0) #current year
    yearly_dict2 = calc.yearly_totals(master_dict.copy(),1) #last year
    yearly_dict3 = calc.yearly_totals(master_dict.copy(),2) #two years ago
    yearly_dict4 = calc.yearly_totals(master_dict.copy(),3) #3 years
    yearly_dict5 = calc.yearly_totals(master_dict.copy(),4) #4 years

    fig, (ax1,ax2) = plt.subplots(nrows=2, figsize=mass_figsize)

    ax1.plot(list(yearly_dict5.keys()),list(yearly_dict5.values()), 'black', linewidth = year_linewidth, label=label5)
    ax1.plot(list(yearly_dict4.keys()),list(yearly_dict4.values()), 'orange', linewidth = year_linewidth, label=label4)
    ax1.plot(list(yearly_dict3.keys()),list(yearly_dict3.values()),label=label3, color='green', linewidth = year_linewidth)
    ax1.plot(list(yearly_dict2.keys()),list(yearly_dict2.values()),label=label2, color='blue', linewidth = year_linewidth)
    ax1.plot(list(yearly_dict.keys()),list(yearly_dict.values()), label=label1, color='red', linewidth = year_linewidth)

    def graph(formula, x_range,title,plot_number,color):
        x = np.array(x_range)
        y = eval(formula)
        plot_number.plot(x, y, color, label=title, linestyle=':', linewidth = goal_linewidth)

    def format_number(number):
        return str("{0:.2f}".format(number))

    graph('x*(800/365)', range(0,366),"800",ax1,'y')
    graph('x*(1000/365)', range(0,366),"1000",ax1,'k')
    ax1.set_title('Yearly Totals')
    ax1.legend()

    ########################################################
    #ax2 setup
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
        extended_range = list(range(x_list[0],end_day))
        model = np.polyfit(x_list, y_list, 1)
        predicted = np.polyval(model, extended_range)
        return extended_range, predicted

    extended_range, predicted = extended_prediction(x_list, y_list, 365)
    extended_range_30, predicted_30 = extended_prediction(x2_list, y2_list, 365)

    label1 = "30 Days: "+format_number(predicted_30[-1])
    label2 = "This Year: "+format_number(predicted[-1])

    graph('x*(800/365)', range(0,366),"800",ax2,'y')
    graph('x*(1000/365)', range(0,366),"1000",ax2,'k')

    ax2.plot(extended_range, predicted, label=label2, linestyle='--', color='blue', linewidth = goal_linewidth)
    ax2.plot(extended_range_30, predicted_30, label=label1, linestyle='--', color='orange', linewidth = goal_linewidth)
    ax2.plot(list(yearly_dict.keys()),list(yearly_dict.values()),label=('This Year'), color='red', linewidth = year_linewidth)
    ax2.set_title('Predictions')
    ax2.legend()

    fig.tight_layout()
    fig.subplots_adjust(hspace=0.3)
    #plt.show()
    plt.savefig(png_location+"3_Yearly_Compare.png")
    append_image("Yearly_Compare",plt)

def running_totals():
    print("Running Totals...")
    input1 = 365 #Blue
    input2 = 90 #Red
    input3 = 30 #
    input4 = 8 #
    input5 = 7
    input6 = 1

    months_back = 24

    graph_dict_1 = {}
    graph_dict_1 = calc.full_running_totals(master_dict.copy(),input1,'distance_miles')

    for key in list(graph_dict_1.keys()):
        if key < get_time.FOM(months_back):
            del graph_dict_1[key]

    #
    graph_dict_2 = {}
    graph_dict_2 = calc.full_running_totals(master_dict.copy(),input2,'distance_miles')

    for key in list(graph_dict_2.keys()):
        if key < get_time.FOM(months_back):
            del graph_dict_2[key]

    #
    graph_dict_3 = {}
    graph_dict_3 = calc.full_running_totals(master_dict.copy(),input3,'distance_miles')

    for key in list(graph_dict_3.keys()):
        if key < get_time.FOM(months_back):
            del graph_dict_3[key]

    #
    graph_dict_4 = {}
    graph_dict_4 = calc.full_running_totals(master_dict.copy(),input4,'distance_miles')

    for key in list(graph_dict_4.keys()):
        if key < get_time.FOM(months_back):
            del graph_dict_4[key]

    #
    graph_dict_5 = {}
    graph_dict_5 = calc.full_running_totals(master_dict.copy(),input5,'distance_miles')

    for key in list(graph_dict_5.keys()):
        if key < get_time.FOM(months_back):
            del graph_dict_5[key]

    #
    graph_dict_6 = {}
    graph_dict_6 = calc.full_running_totals(master_dict.copy(),input6,'distance_miles')

    for key in list(graph_dict_6.keys()):
        if key < get_time.FOM(months_back):
            del graph_dict_6[key]

    myFmt = mdates.DateFormatter('%m')
    months = mdates.MonthLocator()  # every month

    fig, (ax1,ax2,ax3,ax4,ax5,ax6) = plt.subplots(nrows=6, figsize=mass_figsize) #figsize sets window

    ax1.plot(list(graph_dict_1.keys()),list(graph_dict_1.values()),'red')
    ax1.set_title(str(input1)+" Running Days Total")
    ax1.grid(True)
    ax1.xaxis.set_major_locator(months)
    ax1.xaxis.set_major_formatter(myFmt)

    ax2.plot(list(graph_dict_2.keys()),list(graph_dict_2.values()),'blue') #set up third
    ax2.set_title(str(input2)+" Running Days Total")
    ax2.grid(True)
    ax2.xaxis.set_major_locator(months)
    ax2.xaxis.set_major_formatter(myFmt)

    ax3.plot(list(graph_dict_3.keys()),list(graph_dict_3.values()),'green') #set up fourth graph
    ax3.set_title(str(input3)+" Running Days Total")
    ax3.grid(True)
    ax3.xaxis.set_major_locator(months)
    ax3.xaxis.set_major_formatter(myFmt)

    ax4.plot(list(graph_dict_4.keys()),list(graph_dict_4.values()),'red') #set up fourth graph
    ax4.set_title(str(input4)+" Running Days Total")
    ax4.grid(True)
    ax4.xaxis.set_major_locator(months)
    ax4.xaxis.set_major_formatter(myFmt)

    ax5.plot(list(graph_dict_5.keys()),list(graph_dict_5.values()),'blue') #set up fourth graph
    ax5.set_title(str(input5)+" Running Days Total")
    ax5.grid(True)
    ax5.xaxis.set_major_locator(months)
    ax5.xaxis.set_major_formatter(myFmt)

    ax6.plot(list(graph_dict_6.keys()),list(graph_dict_6.values()),'green') #set up fourth graph
    ax6.set_title(str(input6)+" Running Days Total")
    ax6.grid(True)
    ax6.xaxis.set_major_locator(months)
    ax6.xaxis.set_major_formatter(myFmt)


    plt.setp(ax1.get_xticklabels(), rotation=10, horizontalalignment='center')
    plt.setp(ax2.get_xticklabels(), rotation=10, horizontalalignment='center')
    plt.setp(ax4.get_xticklabels(), rotation=10, horizontalalignment='center')
    plt.setp(ax5.get_xticklabels(), rotation=10, horizontalalignment='center')
    plt.setp(ax6.get_xticklabels(), rotation=10, horizontalalignment='center')


    fig.subplots_adjust(hspace=0.2)
    fig.tight_layout()
    append_image("Running_Totals",plt)
    plt.savefig(png_location+"4_Running_Totals.png")


####
weekly_compare()
monthly_compare()
yearly_compare()
running_totals()
