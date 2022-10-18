import os
import tweepy
from dotenv import load_dotenv



def twitter_oauth():
    """
    Method required by bearer token authentication.
    """
    load_dotenv()
    consumer_key = os.getenv("API_KEY")
    consumer_secret = os.getenv("API_KEY_SECRET")
    access_token = os.getenv("ACCESS_TOKEN")
    access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    return auth

def connect_to_api(auth: tweepy.OAuthHandler = None)-> tweepy.API:
    """
    Connect to the endpoint and return the response.
    """
    auth = auth or twitter_oauth()
    api = tweepy.API(auth)
    return api

def search_tweets(query: str, max_results: int=10, api: tweepy.API = None)-> dict:
    """
    Create the query parameters for the recent search endpoint.
    """
    # change params based on the endpoint you are using
    api = api or connect_to_api()
    tweets = api.search_tweets(query, count=max_results)
    return tweets



#override tweepy.StreamListener to add logic to on_status
class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        print(status.text)


# api = API()
api = connect_to_api()
# tweets = search_tweets("Aegon")

myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener())

print()
myStream.filter(track=['Aegon'])

print()