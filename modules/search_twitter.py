import TwitterSearch as ts
import json
from modules import get_data as gd
from modules import modify_data as md
import time


class gather_tweets:

    def avoid_rate_limit(self, ts):  # accepts ONE argument: an instance of TwitterSearch

        queries, tweets_seen = ts.get_statistics()
        if queries > 0 and (queries % 5) == 0:  # trigger delay every 5th query
            time.sleep(30)  # sleep for 60 seconds

    def save_tweet(self, json_data):

        with open('raw/gathered_tweets.json', 'w') as json_file:
            json.dump(json_data, json_file, indent=4, sort_keys=True)

    def save_cleaned_tweet(self, res_dict):

        for k, v in res_dict.items():
            k = k + '\n'
            if v == 1:
                with open('clean/clean_tweet.txt', 'a') as ct:
                    ct.write(k)
            else:
                with open('clean/clean_retweet.txt', 'a') as crt:
                    crt.write(k)

    def initialize_triangulation(self, res, tweet):

        if tweet not in res:
            res[tweet] = 1
        else:
            res[tweet] += 1

        return res

    def __init__(self):

        print('Gathering tweets with political context...')
        get = gd.get_data()
        mod = md.modify_data()
        api = get.api()
        tso = ts.TwitterSearchOrder()
        tso.arguments.update({'tweet_mode': 'extended'})
        res_list = []
        res_dict = {}
        json_data = {}
        senators = get.senators()
        concerns = get.concerns()
        coordinates = get.coordinates()

        for senator in senators:
            json_data[senator] = {}
            print('Gathering tweets mentioning ' + senator + '...')

            for concern in concerns:
                json_data[senator][concern] = []
                con_en = concern.split(',')[0]
                try:
                    con_tl = concern.split(', ')[1]
                    con_cb = concern.split(', ')[2]
                    con_list = [con_en, con_tl, con_cb]
                except IndexError:
                    con_tl = concern.split(', ')[1]
                    con_cb = None
                    con_list = [con_en, con_tl]
                print('\t' + concern + '...')

                for con_item in con_list:
                    tso.set_keywords([senator, con_item])

                    for coordinate in coordinates:
                        tso.set_geocode(coordinate['lat'], coordinate['long'], 5, False)

                        for tweet in api.search_tweets_iterable(tso, callback=self.avoid_rate_limit):
                            try:
                                tweet_text = tweet['retweeted_status']['full_text']
                                is_retweet = True
                            except KeyError:
                                tweet_text = tweet['full_text']
                                is_retweet = False

                            res_text = tweet['id_str'] + ': ' + tweet_text
                            if res_text not in res_list:
                                res_list.append(res_text)

                                if tweet['is_quote_status']:
                                    if is_retweet:
                                        quote_text = tweet['retweeted_status']['quoted_status']['full_text']
                                    else:
                                        quote_text = tweet['quoted_status']['full_text']
                                else:
                                    quote_text = None

                                tweet_text2 = mod.clean_tweet(tweet_text)
                                tweet_text2 = mod.translate(tweet_text2)

                                if tweet_text2 is None:
                                    continue

                                if quote_text is not None:
                                    quote_text2 = mod.clean_tweet(quote_text)
                                    quote_text2 = mod.translate(quote_text2)
                                else:
                                    quote_text2 = None

                                json_data[senator][concern].append({
                                    'tweet_text': tweet_text,
                                    'tweet_text2': tweet_text2,
                                    'is_retweet': is_retweet,
                                    'quote_text': quote_text,
                                    'quote_text2': quote_text2,
                                    'tweet_id': tweet['id'],
                                    'rt_count': tweet['retweet_count'],
                                    'tweet_created': tweet['created_at'],
                                    'tweet_loc': coordinate['city'],
                                    'user_id': tweet['user']['id'],
                                    'user_created': tweet['user']['created_at'],
                                    'user_verified': tweet['user']['verified'],
                                    'user_follower': tweet['user']['followers_count'],
                                    'user_total_tweet': tweet['user']['statuses_count'],
                                    'user_loc': tweet['user']['location']
                                })

                                res_tweet = mod.remove_stopwords(tweet_text2)
                                if quote_text2 is not None:
                                    res_dict = self.initialize_triangulation(
                                        res_dict, res_tweet + ' ' + quote_text2 + ' ' + coordinate['city'])
                                else:
                                    res_dict = self.initialize_triangulation(
                                        res_dict, res_tweet + ' ' + coordinate['city'])

        print('Saving collected tweets into \"gathered_tweets.json\" file...')
        self.save_tweet(json_data)
        self.save_cleaned_tweet(res_dict)
        print('Finished gathering tweets with political context...')


class gather_concerns:

    def avoid_rate_limit(self, ts):  # accepts ONE argument: an instance of TwitterSearch

        queries, tweets_seen = ts.get_statistics()
        if queries > 0 and (queries % 5) == 0:  # trigger delay every 5th query
            time.sleep(30)  # sleep for 60 seconds

    def __init__(self):

        print('Gathering National Concerns in Twitter...')
        con_total = {}
        final_concerns = []

        with open('raw/survey_concerns.txt', 'r') as concerns:

            limit = 0
            for con in concerns:

                print('Gathering tweets for ' + con.split('\n')[0] + '...')
                if limit < 3:
                    final_concerns.append(con.split('\n')[0])
                    limit += 1

                con_en = con.split(',')[0]
                try:
                    con_tl = con.split(', ')[1]
                    con_cb = con.split(', ')[2].split('\n')[0]
                    con_list = [con_en, con_tl, con_cb]
                    con_label = con_en + ', ' + con_tl + ', ' + con_cb
                except IndexError:
                    con_tl = con.split(', ')[1].split('\n')[0]
                    con_cb = None
                    con_list = [con_en, con_tl]
                    con_label = con_en + ', ' + con_tl

                con_total[con_label] = self.count_response(con_list)

            print('Sorting result to get the top 3 most talked national concern in Twitter...')
            top_list = sorted(con_total.items(), key=lambda kv: kv[1], reverse=True)

            with open('raw/twitter_concerns.json', 'w') as top_file:
                top_data = {}
                print('Saving the result to \"twitter_concerns.json\" ...')
                limit = 0
                for i in range(len(top_list)):
                    if limit < 3:
                        if top_list[i][0] not in final_concerns:
                            final_concerns.append(top_list[i][0])
                        limit += 1
                    top_data[top_list[i][0]] = top_list[i][1]
                json.dump(top_data, top_file, indent=4, sort_keys=True)

        with open('clean/final_concerns.txt', 'a') as final:
            print('Saving the top 6 final concerns to \"final_concerns.txt\" ...')
            for final_con in final_concerns:
                final.write(final_con + '\n')

        print('Finished gathering National Concerns in Twitter...')

    def count_response(self, con_list):

        get = gd.get_data()
        mod = md.modify_data()
        tso = ts.TwitterSearchOrder()
        tso.arguments.update({'tweet_mode': 'extended'})
        api = get.api()
        coordinates = get.coordinates()
        con_count = 0
        respo_list = []
        respo_loc = []

        for con in con_list:
            print('\tCounting ' + con + '...')
            tso.set_keywords([con])

            for coordinate in coordinates:
                tso.set_geocode(coordinate['lat'], coordinate['long'], 5, False)

                for tweet in api.search_tweets_iterable(tso, callback=self.avoid_rate_limit):
                    try:
                        tweet_text = tweet['retweeted_status']['full_text']
                    except KeyError:
                        tweet_text = tweet['full_text']

                    cleaned_tweet = mod.clean_tweet(tweet_text)
                    temp_res = cleaned_tweet + ' --- ' + tweet['id_str']
                    if temp_res not in respo_list:
                        respo_list.append(temp_res)
                        respo_loc.append(coordinate['city'])
                        con_count += 1

        with open('raw/response.txt', 'a') as res:
            print('Total: ' + str(con_count))
            res.write(con_list[0] + ': ' + str(con_count) + '\n')
            for i in range(con_count):
                response = respo_list[i] + ' (' + respo_loc[i] + ')'
                res.write(response + '\n')
            res.write('\n')

        return con_count
