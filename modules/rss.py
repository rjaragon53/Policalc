import feedparser
from modules import modify_data as md
import sqlite3
from datetime import datetime as dt
import os
from modules import dbase


class gather_rss:

    def __init__(self, week):
        dbs = dbase.access_db()
        news_urls = {
            'gmanews1': 'https://data.gmanews.tv/gno/rss/news/nation/feed.xml',
            'gmanews2': 'https://data.gmanews.tv/gno/rss/news/regions/feed.xml',
            'gmanews3': 'https://data.gmanews.tv/gno/rss/news/ulatfilipino/feed.xml',
            'gmanews4': 'https://data.gmanews.tv/gno/rss/news/specialreports/feed.xml',
            'philstar1': 'https://www.philstar.com/rss/headlines',
            'philstar2': 'https://www.philstar.com/rss/nation',
            'philstar3': 'https://www.philstar.com/rss/agriculture',
            'inquirer': 'https://www.inquirer.net/fullfeed',
            'manilatimes': 'https://www.manilatimes.net/feed/',
            'businessworld': 'http://www.bworldonline.com/feed/',
            'eaglenews': 'https://www.eaglenews.ph/feed/',
            'sunstarDav': 'https://www.sunstar.com.ph/rssFeed/67/29',
            'sunstarDav2': 'https://www.sunstar.com.ph/rssFeed/67',
            'sunstarMnl': 'https://www.sunstar.com.ph/rssFeed/70',
            'sunstarMnl2': 'https://www.sunstar.com.ph/rssFeed/70/50',
            'sunstarZam': 'https://www.sunstar.com.ph/rssFeed/76',
            'sunstarZam2': 'https://www.sunstar.com.ph/rssFeed/76/78',
            'sunstarCeb': 'https://www.sunstar.com.ph/rssFeed/63/1',
            'sunstarCeb2': 'https://www.sunstar.com.ph/rssFeed/63',
            'sunstar1': 'https://www.sunstar.com.ph/rssFeed/81',
            'sunstar2': 'https://www.sunstar.com.ph/rssFeed/81/97',
            'sunstar3': 'https://www.sunstar.com.ph/rssFeed/selected',
            'businessmirror': 'https://businessmirror.com.ph/feed/',
            'PhilNewAgency': 'https://www.feedspot.com/infiniterss.php?q=site:http%3A%2F%2Fwww.pna.gov.ph%2Flatest.rss',
            'interaksyon': 'https://www.feedspot.com/infiniterss.php?q=site:http%3A%2F%2Fwww.interaksyon.com%2Ffeed'
        }

        print('Gathering rss feed on news sources...')
        mod = md.modify_data()
        raw_rss = []

        if week == 'same_week':
            try:
                dbs.get_file('raw_rss', 'raw/raw_rss.txt')
                dbs.get_file('clean_rss', 'clean/clean_rss.txt')
                with open('raw/raw_rss.txt', 'r') as raw_file:
                    for raw in raw_file:
                        raw = raw.split('\n')[0]
                        raw_rss.append(raw)
            except FileNotFoundError:
                pass

        for key, url in news_urls.items():
            feed = feedparser.parse(url)

            for newsitem in feed['items']:
                news = newsitem.title.encode('ascii', 'ignore').decode('utf-8')

                if news not in raw_rss:
                    raw_rss.append(news)

                    with open('raw/raw_rss.txt', 'a') as raw_file:
                        raw = news + '\n'
                        raw_file.write(raw)

                    news2 = mod.translate(news)
                    news2 = mod.remove_stopwords(news2)

                    with open('clean/clean_rss.txt', 'a') as clean_file:
                        clean = news2 + '\n'
                        clean_file.write(clean)

        print('Saved raw rss data on \"raw_rss.txt\"...')
        print('Saved clean rss data on \"clean_rss.txt\"...')
        print('Finished gathering rss data...')

        conn = sqlite3.connect('policalc.db')
        db_con = conn.cursor()

        with open('raw/raw_rss.txt', 'rb') as file:
            blob_file = file.read()
            db_con.execute("INSERT INTO {} VALUES (:id, :date, :file)".format('raw_rss'), {'id': None, 'date': dt.now(), 'file': blob_file})
            conn.commit()

        with open('clean/clean_rss.txt', 'rb') as file:
            blob_file2 = file.read()
            db_con.execute("INSERT INTO {} VALUES (:id, :date, :file)".format('clean_rss'), {'id': None, 'date': dt.now(), 'file': blob_file2})
            conn.commit()

        conn.close()

        os.remove('raw/raw_rss.txt')
        os.remove('clean/clean_rss.txt')
