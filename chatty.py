#!/usr/bin/env python3

"""
Looks at your home timeline and tells you who tweets the most on it
"""

import csv
import sys
import time
import tweepy
import datetime

from utils import twitter
from collections import Counter

tweets = Counter()
users = Counter()
retweets = Counter()
seen = set()

def count(status):
    if status.id in seen:
        return

    seen.add(status.id)
    user = status.user.screen_name
    users[user] += 1

    if hasattr(status, "retweeted_status"):
        retweets[user] += 1
        sys.stdout.write("🔁 ")
    else:
        tweets[user] += 1
        sys.stdout.write("🐦 ")

    sys.stdout.flush()

def check():
    for status in twitter.home_timeline(count=200):
        count(status)

print("")
print("Following your home timeline tweet (🐦) retweet (🔁)")
print("Press CTRL-C to stop and output summary.\n")

start = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

for status in tweepy.Cursor(twitter.home_timeline, count=200).items(800):
    count(status)

while True:
    try:
        time.sleep(120)
        check()
    except tweepy.error.RateLimitError as e:
        print("sleeping", e)
        time.sleep(15 * 60)
    except tweepy.error.TweepError as e:
        print("caught Twitter API error sleeping")
        time.sleep(60)
    except KeyboardInterrupt:
        break

end = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
filename = "chatty-{}-{}.csv".format(start, end)
cols = ["User", "Tweets", "Retweets", "Total"]

print("\n\n")
print("| {:20s} | {:6s} | {:6s} | {:6s} |".format(*cols))
print("| -------------------- | ------ | ------ | ------ |")

with open(filename, "w") as fh:
    out = csv.writer(fh)
    out.writerow(["user", "retweets", "tweets", "total"])
    for user, total in users.most_common():
        row = [
            user,
            retweets.get(user, 0),
            tweets.get(user, 0),
            total
        ]
        print("| {:20s} | {:6n} | {:6n} | {:6n} |".format(*row))
        out.writerow(row)

print("\n")
print("full results written to {}".format(filename))
