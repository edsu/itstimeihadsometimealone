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

from tqdm import tqdm
from pathlib import Path
from utils import twitter
from termcolor import colored
from collections import Counter

def prompt_boolean(s, default=True, boolean=False):
    result = prompt(s + " [Y,n]").lower()
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

def bold(s):
    return colored(s, attrs=["bold"])

def parsejs(path):
    text = open(path).read()
    text = re.sub('^.+?= *', '', text)
    return json.loads(text)

def get_users(user_ids):
    users = {}
    bucket = []
    for user_id in tqdm(user_ids):
        if len(bucket) == 100:
            for user in twitter.lookup_users(bucket):
                users[user.id] = user._json
            bucket = []
        else:
            bucket.append(user_id)
    if len(bucket) > 0:
        for user in twitter.lookup_users(bucket):
            users[user.id] = user._json
    return users

def save_json(obj, path):
    if not path.parent.is_dir():
        path.parent.mkdir(parents=True)
    json.dump(obj, path.open("w"), indent=2)

archive = Path(prompt("Enter the path to your twitter archive"))
if not archive.is_dir():
    error("{} is not a directory!".format(archive))

tweets_file = archive / "data" / "tweet.js"
if not tweets_file.is_file():
    error("{} is missing tweets.js file".format(archive))

retweeted = Counter()
replied = Counter()
faved = Counter()

for obj in parsejs(tweets_file):
    tweet = obj['tweet']
    try:
        if re.match('^RT:? ', tweet["full_text"]) and len(tweet["entities"]["user_mentions"]) > 0:
            retweeted[tweet["entities"]["user_mentions"][0]["screen_name"]] += 1
        elif tweet.get("in_reply_to_screen_name"):
            replied[tweet["in_reply_to_screen_name"]] += 1
    except:
        sys.exit(json.dumps(tweet, indent=2))

print(bold("\nHere are the 10 users you retweeted the most:\n"))
for user, count in retweeted.most_common(10):
    print('{:20s} {:5n}'.format(user, count))

print(bold("\nAnd here are the top 10 users you replied to the most:\n"))
for user, count in replied.most_common(10):
    print('{:20s} {:5n}'.format(user, count))

# the archive owners account information
account = parsejs(archive / "data" / "account.js")[0]["account"]

# the users who follow the archive owner
followers = parsejs(archive / "data" / "follower.js")
followers = list(map(lambda f: f["follower"]["accountId"], followers))

# the users that the archive owner follows
following = parsejs(archive / "data" / "following.js")
following = list(map(lambda f: f["following"]["accountId"], following))

print("\n")
print(bold("According to your archive you follow {} accounts and are followed by {} accounts".format(len(following), len(followers))))

# combine all the user ids
user_ids = set(following).union(set(followers))

# look up all the users unless we have a copy already
users_path = archive / "extras" / "users.json"
use_cached = users_path.is_file()
if users_path.is_file():
    print("\n")
    use_cached = prompt_boolean("I found an old copy of user information at {} shall I use it?".format(users_path))
if not use_cached:
    users = get_users(user_ids)
    print("\n")
    print(bold("Ok, I'm going to fetch the information for {} users from Twitter...".format(len(users))))

else:
    users = json.load(users_path.open())
save_json(users, archive / "extras" / "users.json")

for user_id in followers:
    if user_id not in users:
        continue
    user = users[user_id]
    print("\n{} {}".format(user['name'], bold("@" + user['screen_name'])))
    print("https://twitter.com/{}".format(user['screen_name']))
    print("")
    print(user["description"])
    print("")
    prompt_boolean("Unfollow?", default=False)

