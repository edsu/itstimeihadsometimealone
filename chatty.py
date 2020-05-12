#!/usr/bin/env python3

"""
Looks at your home timeline and tells you who tweets the most on it
"""

import sys
import time
import dotenv
import tweepy
import datetime

from os import environ as e
from collections import Counter

dotenv.load_dotenv()

auth = tweepy.OAuthHandler(e['CONSUMER_KEY'], e['CONSUMER_SECRET'])
auth.set_access_token(e['ACCESS_TOKEN'], e['ACCESS_TOKEN_SECRET'])
twitter = tweepy.API(auth)

tweets = Counter()
users = Counter()
retweets = Counter()
seen = set()

def check():
    for status in twitter.home_timeline(count=200):
        if status.id in seen:
            continue

        seen.add(status.id)
        user = status.user.screen_name
        users[user] += 1

        if hasattr(status, 'retweeted_status'):
            retweets[user] += 1
            sys.stdout.write('+')
        else:
            tweets[user] += 1
            sys.stdout.write('.')

        sys.stdout.flush()

print("")
print("Following your home timeline (tweet (.) retweet (+)")
print("Press CTRL-C to stop and output summary.\n")

while True:
    try:
        check()
        time.sleep(120)
    except tweepy.error.RateLimitError as e:
        print('sleeping', e)
        time.sleep(15 * 60)
    except KeyboardInterrupt:
        break

print("\nOriginal Tweets")
for user, count in tweets.most_common():
    print('{:30s} {:3n}'.format(user, count))

print("\nRetweets")
for user, count in retweets.most_common():
    print('{:30s} {:3n}'.format(user, count))

print("\nTotal")
for user, count in users.most_common():
    print('{:30s} {:3n}'.format(user, count))

