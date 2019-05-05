import json
from modules import dbase
from modules import get_data as gd
import os


class get_final_concerns():

    def __init__(self):
        get = gd.get_data()
        concerns = get.concerns()
        final_concerns = []

        limit = 0
        for con in concerns:
            if limit < 3:
                final_concerns.append(con)
                limit += 1

        dbs = dbase.access_db()
        dbs.get_file('twitter_concerns_inf', 'DB/twitter_concerns_inf.json')
        with open('DB/twitter_concerns_inf.json', 'r') as db_file:
            db_data = json.load(db_file)

            with open('raw/twitter_concerns.json', 'r') as tc_file:
                tc_data = json.load(tc_file)

                with open('raw/twitter_concerns_inf.json', 'w') as js_file:
                    js_data = {}

                    for i in db_data:
                        js_data[i] = db_data[i] + tc_data[i]

                    top_list = sorted(js_data.items(), key=lambda kv: kv[1], reverse=True)

                    limit = 0
                    for i in range(len(top_list)):
                        if limit < 3:
                            print(top_list[i][0], final_concerns)
                            if top_list[i][0] not in final_concerns:
                                final_concerns.append(top_list[i][0])
                            limit += 1

                    json.dump(js_data, js_file, indent=4, sort_keys=True)

        with open('clean/final_concerns_inf.txt', 'a') as final:
            for final_con in final_concerns:
                final.write(final_con + '\n')

        os.remove('DB/twitter_concerns_inf.json')
