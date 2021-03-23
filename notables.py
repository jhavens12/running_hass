import data
import pprint
import copy

database = data.run()

print("*****")
print()
last_key = next(iter(reversed(sorted(database))))

mon = {99:'Ever',1:"1 Month",3:"3 Months",6:"6 Months"}

cur_notes = []
for x in database[last_key]['smash']['notables']:
    cur_notes.append(x['reasonCode'])
    #print("****")

last_run = last_key #start things
for cnote in cur_notes:
    note_dict = {}
    print(cnote)
    for run in sorted(reversed(database)):
        if 'notables' in database[run]['smash']: #if the run was matched and smashrun pulled
            if database[run]['smash']['notables'] != 'N/A': #if there were notables
                for note in database[run]['smash']['notables']: #for each notable
                    if note['reasonCode'] == cnote: #if the note description matches
                        note_dict[run] = note

                        #diff = last_run - run
                        #print(run,mon[note['periodMonths']],"Now:",note['value'],"Old:",note['periodValue'],"Days Ago:",str(diff.days))
                        #last_run = run
                    #print(note['description'])


    for myrun in reversed(sorted(note_dict)):
        #print(run)
        cur_value = note_dict[myrun]['value']
        old_value = note_dict[myrun]['periodValue']
        the_dict = copy.deepcopy(note_dict)
        for therun in reversed(sorted(the_dict)):
            del the_dict[therun]['periodValue']
            if old_value in the_dict[therun].values(): #this finds old value and cur value for past runs
                if therun != myrun:
                    if therun < myrun:
                        old_run = therun
                        break
        diff = old_run - myrun
        print(myrun,mon[note_dict[myrun]['periodMonths']],"Now:",note_dict[myrun]['value'],"Old:",note_dict[myrun]['periodValue'],str(old_run),"Days:",diff.days)
