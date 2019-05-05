from similarity.cosine import Cosine
import json
from modules import get_data as gd
from modules import modify_data as md


class compare_tweet_rss:

    def triangulate(self, tweet, loc):

        print('Triangulating: ' + tweet)
        cosine = Cosine(2)
        cos_tweet = cosine.get_profile(tweet)

        with open("clean/clean_rss.txt", "r") as clean_rss:

            for rss in clean_rss:
                rss = rss.split('\n')[0]
                cos_rss = cosine.get_profile(rss)
                cos_result = cosine.similarity_profiles(cos_tweet, cos_rss)

                if cos_result > 0.7:
                    print('\t[PASS: ' + str(cos_result) + '] ' + rss)
                    return True
                else:
                    print('\t[FAIL: ' + str(cos_result) + '] ' + rss)

        with open("clean/clean_retweet.txt", "r") as clean_rt:

            for rtweet in clean_rt:
                rt = rtweet.rsplit(' ', 1)[0]
                rt_loc = rtweet.split('\n')[0].rsplit(' ', 1)[1]
                cos_rt = cosine.get_profile(rt)

                if loc == rt_loc:
                    cos_result = cosine.similarity_profiles(cos_tweet, cos_rt)
                    if cos_result > 0.7:
                        print('\t[PASS: ' + str(cos_result) + '] ' + rt)
                        return True
                    else:
                        print('\t[FAIL: ' + str(cos_result) + '] ' + rt)

        with open('clean/clean_tweet.txt', 'r') as clean_tweet:

            for ctweet in clean_tweet:
                ct = ctweet.rsplit(' ', 1)[0]
                ct_loc = ctweet.split('\n')[0].rsplit(' ', 1)[1]
                cos_ct = cosine.get_profile(ct)

                if loc == ct_loc:
                    cos_result = cosine.similarity_profiles(cos_tweet, cos_ct)
                    if cos_result > 0.7 and cos_result != 1.0:
                        print('\t[PASS: ' + str(cos_result) + '] ' + ct)
                        return True
                    else:
                        print('\t[FAIL: ' + str(cos_result) + '] ' + ct)

        print('\tNo matching results found...')
        return False

    def __init__(self):

        json_data = {}
        get = gd.get_data()
        mod = md.modify_data()
        print('Triangulating tweets...')
        senators = get.senators()
        concerns = get.concerns()

        with open('raw/gathered_tweets.json', 'r') as json_file:
            data = json.load(json_file)

            for sen in senators:
                json_data[sen] = {}

                for con in concerns:
                    json_data[sen][con] = []

                    for i in range(len(data[sen][con])):
                        tweet = data[sen][con][i]['tweet_text2']
                        tweet = mod.remove_stopwords(tweet)

                        if self.triangulate(tweet, data[sen][con][i]['tweet_loc']):
                            json_data[sen][con].append(data[sen][con][i])

        with open('clean/final_tweets.json', 'w') as json_file:
            json.dump(json_data, json_file, indent=4, sort_keys=True)
