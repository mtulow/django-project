import os
import tweepy
import sqlite3
from contextlib import contextmanager


@contextmanager
def db_connection(dbpath: str='./database/tweets.db'):
    if not os.path.exists(dbpath):
        print('DataBase created!')
    with sqlite3.connect(dbpath) as conn:
        yield conn
        conn.commit()
    

def create_table(dbpath: str='./database/tweets.db'):
    # extract query from sql file
    with open('database/create_table.sql') as f:
        query = f.read()
    # execute `create table` query
    with db_connection(dbpath) as conn:
        conn.execute(query)
        print('Table created!')

def insert_tweet(tweet: dict, dbpath: str='./database/tweets.db'):
    # extract query from sql file
    with open('database/insert_tweet.sql') as f:
        query = f.read()
    # execute `insert` query
    with db_connection(dbpath) as conn:
        conn.execute(query, tweet)
        print('Tweet inserted!')


class TweetStreamV2(tweepy.StreamingClient):
    new_tweet = {}

    def on_connect(self):
        print("You are now connected to the streaming API.")
    
    def on_includes(self, includes):
        self.new_tweet['username'] = includes['users'][0].username
        print(self.new_tweet)

        insert_tweet(self.new_tweet['username'], self.new_tweet['tweet'])
        
        print(self.new_tweet)
        print('tweet added to database!')
        print(''.center(30, '-'))

    def on_tweet(self, data):
        print()
        print(data)
        print()
        # if data.referenced_tweets is None:
        #     self.new_tweet['tweet'] = data.text
        #     print(self.new_tweet)
        # print(data.text)
        # time.sleep(0.3)