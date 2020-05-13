#!/usr/bin/env python

"""
This script goes through your exported tweet archive and finds users that you
follow that you have never interacted with before (a retweet, reply or like).
It then prompts you to see if you want to unfollow them.
"""

import os
import re
import sys
import json
import tweepy

from pathlib import Path
from termcolor import colored
from collections import Counter

def prompt_boolean(s, default=True, boolean=False):
    result = prompt(s + " [Y,n]: ").lower()
    if result == "y":
        return True
    elif result == "n":
        return False
    elif result == "":
        return default
    else:
        return prompt_boolean(s, boolean)

def prompt(s):
    return input(colored(s + ": ", "green", attrs=["bold"]))

def error(s):
    sys.exit(colored(s, "red", attrs=["bold"]))

def parsejs(path):
    text = open(path).read()
    text = re.sub('^.+?= *', '', text)
    return json.loads(text)

archive = Path(prompt("Enter the path to your twitter archive"))
if not archive.is_dir():
    error("{} is not a directory!".format(archive))

tweets_file = archive / "tweet.js"
if not tweets_file.is_file():
    error("{} is missing tweets.js file".format(archive))

retweeted = Counter()
replied = Counter()
faved = Counter()

for tweet in parsejs(tweets_file):
    if re.match('^RT:? ', tweet["full_text"]) and len(tweet["entities"]["user_mentions"]) > 0:
        retweeted[tweet["entities"]["user_mentions"][0]["screen_name"]] += 1
    elif tweet.get("in_reply_to_screen_name"):
        replied[tweet["in_reply_to_screen_name"]] += 1

print(colored("\nTop Retweeted:", attrs=["bold"]))
for user, count in retweeted.most_common(10):
    print('{:20s} {:5n}'.format(user, count))

print(colored("\nTop Replied:", attrs=["bold"]))
for user, count in replied.most_common(10):
    print('{:20s} {:5n}'.format(user, count))

        
