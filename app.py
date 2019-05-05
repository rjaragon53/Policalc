from flask import Flask, render_template, request, make_response
from modules import rss
from modules import dbase
import datetime as dt
from modules import search_twitter as st
from modules import get_fc_inf as gfi
from modules import triangulation as tr
from modules import sentiment_analysis as sa
from functools import wraps
from datetime import timedelta
app = Flask(__name__)

app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

dbs = dbase.access_db()


def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        auth = request.authorization
        if auth and auth.username == 'user' and auth.password == 'pass':
            return f(*args, **kwargs)

        return make_response(render_template('index.html'), 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

    return decorated


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/index')
def blank():
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/decagon')
@auth_required
def decagon():
    run = dbs.latest_date('gathered_tweets')
    run = dt.datetime.strptime(run, '%Y-%m-%d %H:%M:%S.%f')
    next_run = run + dt.timedelta(7)
    next_run = next_run.strftime('%B %d, %Y %I:%M %p')

    rsss = dbs.latest_date('clean_rss')
    rsss = dt.datetime.strptime(rsss, '%Y-%m-%d %H:%M:%S.%f')
    next_rss = rsss + dt.timedelta(1)
    next_rss = next_rss.strftime('%B %d, %Y %I:%M %p')

    if (dt.datetime.now()-run) > dt.timedelta(7):
        return render_template('decagon.html', next_process='concerns', process='Analyzing Top National Concerns in Twitter...', disable_rss='disable_rss', next_rss=next_rss)
    else:
        if (dt.datetime.now()-rsss) > dt.timedelta(1):
            return render_template('decagon.html', disable_run='disable_run', process='Gathering RSS...', next_run=next_run)
        else:
            return render_template('decagon.html', disable_run='disable_run', disable_rss='disable_rss', next_run=next_run, next_rss=next_rss)


@app.route('/decagon_rss')
@auth_required
def decagon_rss():
    run = dbs.latest_date('gathered_tweets')
    run = dt.datetime.strptime(run, '%Y-%m-%d %H:%M:%S.%f')

    rsss = dbs.latest_date('clean_rss')
    rsss = dt.datetime.strptime(rsss, '%Y-%m-%d %H:%M:%S.%f')

    if (dt.datetime.now()-rsss) > dt.timedelta(1):
        if (dt.datetime.now()-run) < dt.timedelta(1):
            rss.gather_rss('new_week')
            return render_template('decagon.html', disable_run='disable_run', disable_rss='disable_rss', end_process='Finished Gathering RSS...', redirect='decagon')
        else:
            rss.gather_rss('same_week')
            return render_template('decagon.html', disable_run='disable_run', disable_rss='disable_rss', end_process='Finished Gathering RSS...', redirect='decagon')
    else:
        return render_template('decagon.html', disable_run='disable_run', disable_rss='disable_rss', redirect='decagon')


@app.route('/decagon_concerns')
@auth_required
def decagon_concerns():
    st.gather_concerns()
    gfi.get_final_concerns()
    return render_template('decagon.html', disable_rss='disable_rss', end_process='Gathered the Final Concerns...', next_process='tweets',
                           process='Gathering tweets from Twitter...', change_ip='change_ip')


@app.route('/decagon_tweets')
@auth_required
def decagon_tweets():
    st.gather_tweets()
    dbs.get_file('raw_rss', 'raw/raw_rss.txt')
    dbs.get_file('clean_rss', 'clean/clean_rss.txt')
    return render_template('decagon.html', disable_rss='disable_rss', end_process='Gathered Tweets for the past 7 days...', next_process='analyze',
                           process='Performing Triangulation and Sentiment Analysis...', change_ip='change_ip')


@app.route('/decagon_analyze')
@auth_required
def decagon_analyze():
    tr.compare_tweet_rss()
    sa.analyze_tweets()
    dbs.insert_all_file()
    dbs.delete_local_files()
    return render_template('decagon.html', disable_rss='disable_rss', end_process='Tweets have been filtered and polarity was analyzed...',
                           disable_run='disable_run', redirect='decagon')


if __name__ == '__main__':
    app.run(debug=True)
