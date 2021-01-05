import twitter
import tweepy
import json
import time
import pandas as pd
# Import personal API login & initiate the connection to Twitter Rest API
# !!! This requires to have in the same folder of this script a Tri_API_key.py file

from .Twitter_API_key import my_API
#oauth = OAuth(my_API[0], my_API[1], my_API[2], my_API[3])
#twitter = Twitter(auth=oauth, retry=True)

def connect_tweepy_api(consumer_key=my_API[2], consumer_secret=my_API[3], 
                       access_token=my_API[0], access_token_secret=my_API[1]):
    
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)
    
    return api

def connect_twitter_py_api(consumer_key=my_API[2], consumer_secret=my_API[3], 
                       access_token=my_API[0], access_token_secret=my_API[1]):
    api = twitter.Api(consumer_key=consumer_key,
                              consumer_secret=consumer_secret,
                              access_token_key=access_token,
                              access_token_secret=access_token_secret)
    return api

def get_replies(user_name, tweet_id):
    
    replies=[]
    for tweet in tweepy.Cursor(api.search,q='to:'+user_name, result_type='mixed', count=50, timeout=999999).items(1000):
        if hasattr(tweet, 'in_reply_to_status_id_str'):
            if (tweet.in_reply_to_status_id_str==tweet_id):
                reply_id = tweet.id_str
                user = tweet.user.screen_name
                text = tweet.text.encode('utf')
                hashtags = [h['text'] for h in tweet.entities['hashtags']]
                urls = [u['expanded_url'] for u in tweet.entities['urls']]
                replies.append([tweet_id, reply_id, user, text, hashtags, urls])
    
    return replies

# returns twitter user obj after searching for str name
def get_user_from_name(name, api):
    user_list = api.search_users(name)
    if user_list:
        user = user_list[0]
        if user.verified:
            return user
    return None

def make_user_list(queries,api):
    V = []
    for query in queries:
        user = get_user_from_name(query, api)
        if user:
            row = [repr(user.id), user.name, user.screen_name]
            V.append(row)
    return V

def build_df(queries,api):
    V = []
    for query in queries:
        user = get_user_from_name(query, api)
        if user:
            row = [repr(user.id), user.name, user.screen_name]
            V.append(row)
    
    header = ['user_id','user_name','handle']
    df = pd.DataFrame(V,columns=header)
    return df

class StreamListener(tweepy.StreamListener):
    '''
    Class definition for a stream listener.
    Inherits from the standard tweepy stream listener and overloads functions.
    
    Example usage:
    stream_listener = StreamListener(time_limit=60*15,tweet_limit=50000) # stream for 15 minutes, or until 50k tweets
    stream = tweepy.Stream(auth=api.auth, listener=stream_listener) # connect stream
    stream.filter(lang=['en','es'],track=['Python','C++']) # filter based on languages and tracked terms
    
    '''
    
    def __init__(self, time_limit=60,tweet_limit=50000):
        self.start_time = time.time()
        self.limit = time_limit
        self.t_limit = tweet_limit
        self.tweets = 0
        self.db = dataset.connect(settings.CONNECTION_STRING)
        super(StreamListener, self).__init__()


    def on_status(self, status):

        if ((time.time() - self.start_time) < self.limit) & (self.tweets < self.t_limit):
    
            description = status.user.description
            loc = status.user.location
            text = status.text
            coords = status.coordinates
            geo = status.geo
            name = status.user.screen_name
            uid = status.user.id_str
            user_created = status.user.created_at
            followers = status.user.followers_count
            id_str = status.id_str
            created = status.created_at
            retweets = status.retweet_count
            bg_color = status.user.profile_background_color
            
    
            if geo is not None:
                geo = json.dumps(geo)
    
            if coords is not None:
                coords = json.dumps(coords)
            
            '''
            INSERT CODE HERE            
            '''
    
            self.tweets += 1
            return True
        else:
            print(f"Run for {time.time() - self.start_time} seconds and archived {self.tweets} tweets")
            return False

    def on_error(self, status_code):
        if status_code == 420: # 420 error is rate-limited error
            print(f'Error Status code {status_code}')
            return False #returning False in on_data disconnects the stream
