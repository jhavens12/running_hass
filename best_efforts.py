import data
import pprint
import copy

database = data.run()

print("*****")
print()
last_key = next(iter(reversed(sorted(database))))

for run in reversed(sorted(database)):

    if 'strava_specific' in database[run]:

        pr = []
        for y in database[run]['strava_specific']['best_efforts']: #for each best effort entry
            if y['pr_rank'] != None:
                if str(y['name']) == '10k':
                    print(run)
                    print(y)
                    print()
