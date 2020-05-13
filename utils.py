import sys
import dotenv

import tweepy
from os import environ as e

dotenv.load_dotenv()

if not e["CONSUMER_KEY"]:
    sys.exit("Please add your Twitter API keys to a .env file.")

auth = tweepy.OAuthHandler(e["CONSUMER_KEY"], e["CONSUMER_SECRET"])
auth.set_access_token(e["ACCESS_TOKEN"], e["ACCESS_TOKEN_SECRET"])
twitter = tweepy.API(auth, wait_on_rate_limit=True)


