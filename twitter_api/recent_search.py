from functools import singledispatch
import os
import csv
import json
import requests
import dateutil.parser
import pandas as pd
from dotenv import load_dotenv


# To set your environment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'
# bearer_token = os.getenv("BEARER_TOKEN")

def recent_search_url()-> str:
    return "https://api.twitter.com/2/tweets/search/recent"

def _bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """
    load_dotenv()
    bearer_token = os.getenv("BEARER_TOKEN")
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r

# Optional params: start_time,end_time,since_id,until_id,max_results,next_token,
# expansions,tweet.fields,media.fields,poll.fields,place.fields,user.fields
query_params = {'query': '(from:twitterdev -is:retweet) OR #twitterdev','tweet.fields': 'author_id'}


def create_query_params(query: str, max_results: int=10)-> dict:
    """
    Create the query parameters for the recent search endpoint.
    """
    # change params based on the endpoint you are using
    query_params = {'query': query,
                    # 'start_time': start_date,
                    # 'end_time': end_date,
                    'max_results': max_results,
                    'expansions': 'author_id,in_reply_to_user_id,geo.place_id',
                    'tweet.fields': 'id,text,author_id,in_reply_to_user_id,geo,conversation_id,created_at,lang,public_metrics,referenced_tweets,reply_settings,source',
                    'user.fields': 'id,name,username,created_at,description,public_metrics,verified',
                    'place.fields': 'full_name,id,country,country_code,geo,name,place_type',
                    'next_token': {}}
    return query_params

def connect_to_endpoint(url: str, params: dict, next_token: str = None)-> dict:
    """
    Connect to the endpoint and return the response.
    """
    params['next_token'] = next_token   # params object received from create_url function
    response = requests.get(url, auth=_bearer_oauth, params=params)
    print("Endpoint Response Code: " + str(response.status_code))
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

# %%%%%%%%%%%%%%%
# Data processing
# ===============

def csv_headers():
    """
    Create the headers for the CSV file.
    """
    headers = ['author id', 'created_at', 'geo', 'id','lang', 'like_count',
               'quote_count', 'reply_count', 'retweet_count', 'source', 'tweet']
    return headers

def unpack_row(row: dict)-> tuple:
    """
    Unpack the values from a row in the response data,
    Return a list of values.
    """
    # We will create a variable for each since some of the keys might not exist for some tweets
    # So we will account for that

    # 1. Author ID
    author_id = row['author_id']

    # 2. Time created
    created_at = dateutil.parser.parse(row['created_at'])

    # 3. Geolocation
    if ('geo' in row):   
        geo = row['geo']['place_id']
    else:
        geo = " "

    # 4. Tweet ID
    tweet_id = row['id']

    # 5. Language
    lang = row['lang']

    # 6. Tweet metrics
    retweet_count = row['public_metrics']['retweet_count']
    reply_count = row['public_metrics']['reply_count']
    like_count = row['public_metrics']['like_count']
    quote_count = row['public_metrics']['quote_count']

    # 7. source
    source = row['source']

    # 8. Tweet text
    text = repr( row['text'] )
    
    # Assemble all data in a list
    out = (author_id, created_at, geo, tweet_id, lang, like_count, \
           quote_count, reply_count, retweet_count, source, text)
    
    print(out)
    
    return out

def collect_rows(response: dict)-> list:
    """
    Collect the rows from the response.
    """
    return list(map(unpack_row, response['data']))

def create_csv_file(filename: str)-> str:
    """
    Create a CSV file from the data.
    """
    # Create file
    with open("data.csv", "a", newline="", encoding='utf-8') as csvFile:
        csvWriter = csv.writer(csvFile)

        # Create headers for the data you want to save, in this example,
        # we only want save these columns in our dataset
        headers = csv_headers()
        csvWriter.writerow(headers)
    return filename

def append_to_csv(response: dict, filename: str)-> None:
    """
    Append the data to the CSV file.
    """
    # Open OR create the target CSV file
    with open(filename, "a", newline="", encoding='utf-8') as csvFile:
        csvWriter = csv.writer(csvFile)

        # Loop through each tweet, and append the data to the CSV file
        rows = list(map(unpack_row, response['data']))

        csvWriter.writerows(rows)
    
    # Print the number of tweets for this iteration
    print("# of Tweets added from this response: ", len(rows))

@singledispatch
def get_dataframe():
    """
    Create a pandas dataframe from the response.
    """
    return
@get_dataframe.register
def _(response: dict)-> pd.DataFrame:
    return pd.DataFrame(response['data'], columns=csv_headers())
    # Create a pandas dataframe from the response
    return pd.DataFrame(response['data'], columns=csv_headers())
@get_dataframe.register
def _(filename: str)-> pd.DataFrame:
    """
    Create a pandas dataframe from the CSV file.
    """
    # Create a pandas dataframe from the CSV file
    return pd.read_csv(filename, encoding='utf-8')


def get_metadata(response: dict)-> pd.Series:
    """
    Get the metadata from the response.
    """
    return pd.Series(response['meta'])    

def collect_tweet_data(search_url: str, search_query: dict, store: bool=True):
    flag = True
    filename = create_csv_file(filename)
    rows = []
    while flag:
        # Connect to the endpoint
        response = connect_to_endpoint(search_url, search_query, next_token)
        # Collect the data
        rows.extend(collect_rows(response))
        if store:
            # Append the data to the CSV file
            append_to_csv(response, filename)
        # Check if there is another page of data
        if 'next_token' in response['meta']:
            next_token = response['meta']['next_token']
        else:
            flag = False

    return pd.DataFrame(rows, columns=csv_headers())

def store_in_file(response: dict, filename: str)-> None:
    """
    Store the data in a file.
    """
    create_csv_file(filename)
    append_to_csv(response, filename)

# %%%%
# Demo
# ====

def main():
    search_url = recent_search_url()
    query = '(Aemond -is:retweet)'
    search_query = create_query_params(query, max_results=10)
    json_response = connect_to_endpoint(search_url, search_query)
    df = get_dataframe(json_response)
    metadata = get_metadata(json_response)
    

    print(metadata)
    print()
    print(df)
    print()
    print(json.dumps(json_response['data'], indent=4, sort_keys=True))
    
    store_in_file(json_response, 'data.csv')

if __name__ == "__main__":
    print()
    main()
    print()