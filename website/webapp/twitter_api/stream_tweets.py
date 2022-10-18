import os
import tweepy
from dotenv import load_dotenv

load_dotenv()

bearer_token = os.environ["BEARER_TOKEN"]

class MyStreamer(tweepy.StreamingClient):
    def on_tweet(self, tweet):
        tweet.id
        row = [tweet.id, repr(tweet.text), (tweet.created_at), tweet.lang, #tweet.author.id, tweet.source,
            #    tweet.source, tweet.geo.place.id,
            #    tweet.favorite_count, tweet.quote_count, tweet.reply_count, tweet.retweet_count
            ]
        print(' | '.join(map(str, row)))
        print("======")

streamer = MyStreamer(bearer_token)
rules = streamer.get_rules()
# streamer.delete_rules()
streamer.add_rules(tweepy.StreamRule("(Aegon lang:en -is:retweet)"))

streamer.filter()