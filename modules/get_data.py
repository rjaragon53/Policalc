import TwitterSearch as ts
import json


class get_data:

    def senators(self):

        sen_list = []
        with open('raw/senators.txt', 'r') as senators:
            for sen in senators:
                sen = sen.split('\n')[0]
                sen_list.append(sen)
        return sen_list

    def concerns(self):

        con_list = []
        with open('clean/final_concerns.txt', 'r') as concerns:
            for con in concerns:
                con = con.split('\n')[0]
                con_list.append(con)
        return con_list

    def coordinates(self):

        coordinates = []
        with open('raw/city_coordinates.json') as loc_json:

            loc = json.load(loc_json)
            for i in range(len(loc['location'])):
                coordinates.append({
                    "city": loc['location'][i]['city'],
                    "lat": loc['location'][i]['lat'],
                    "long": loc['location'][i]['long']
                })

        return coordinates

    def api(self):

        api = ts.TwitterSearch(
            consumer_key="JwUkEgxaHGamnY8vw6o9HFTlI",
            consumer_secret="JVlWOsbj1uDTWwCZ6g1ThT95kVGFjLDCgQBoRdHTOEZfCfJxMl",
            access_token="719916492331098112-2iviJfFYNs49Ur4c5Joo7SG6yfbgUDr",
            access_token_secret="ljKVR1aq2jYvQMjoa0iTUz0alE4evpVEqgooMWd8G2kNk"
        )
        return api

    def file_data(self):

        file_names = ['gathered_tweets', 'response', 'twitter_concerns', 'twitter_concerns_inf', 'clean_retweet',
                      'clean_tweet', 'final_concerns', 'final_concerns_inf', 'final_tweets', 'tweet_scores', 'tweet_scores_inf']

        file_paths = ['raw/gathered_tweets.json', 'raw/response.txt', 'raw/twitter_concerns.json', 'raw/twitter_concerns_inf.json',
                      'clean/clean_retweet.txt', 'clean/clean_tweet.txt', 'clean/final_concerns.txt',
                      'clean/final_concerns_inf.txt', 'clean/final_tweets.json', 'clean/tweet_scores.json', 'clean/tweet_scores_inf.json']

        return file_names, file_paths
