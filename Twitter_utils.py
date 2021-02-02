import twitter
import tweepy
import json
import time
import pandas as pd
from wordcloud import WordCloud, STOPWORDS , ImageColorGenerator
import matplotlib.pyplot as plt
# Import personal API login & initiate the connection to Twitter Rest API
# !!! This requires to have in the same folder of this script a Tri_API_key.py file

from .Tri_API_key import my_API
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

def get_timeline(user_name='minusplnp',max_statuses = 100):
    
    all_statuses = []
    
    for tweet in tweepy.Cursor(api.user_timeline, screen_name=user_name, 
                                exclude_replies=True, include_rts=False,
                                tweet_mode="extended").items(max_statuses):
        t_id = tweet.id_str
        created_at = tweet.created_at
        text = tweet.full_text
        hashtags = [h['text'] for h in tweet.entities['hashtags']]
        users_mention = [u['screen_name'] for u in tweet.entities['user_mentions']] 
        urls = [u['expanded_url'] for u in tweet.entities['urls']]
        retweet_count = tweet.retweet_count


        if (hasattr(tweet, 'retweeted_status')):

            rt_bool = True
            rt_user = tweet.retweeted_status.user.screen_name
            rt_text = tweet.retweeted_status.full_text
            rt_hashtags = [h['text'] for h in tweet.retweeted_status.entities['hashtags']]
            rt_urls = [u['expanded_url'] for u in tweet.retweeted_status.entities['urls']]
            if 'media' in tweet.retweeted_status.entities:
                rt_media_url = [m['media_url'] for m in tweet.retweeted_status.entities['media']]
                rt_media_type = [m['type'] for m in tweet.retweeted_status.entities['media']]
            else:
                rt_media_url = rt_media_type = None

        else:
            rt_bool = False 
            rt_user = rt_text = rt_hashtags = rt_urls = rt_media_url = rt_media_type = None

        # if media not present in status, check if present in retweeted status 
        # I am assuiming that if you retweet a media content you don't post additional media content
        if 'media' in tweet.entities:
            media_url = [m['media_url'] for m in tweet.entities['media']]
            media_type = [m['type'] for m in tweet.entities['media']]
        else:
            media_url = media_type = None

        row = [t_id, created_at, text, hashtags, retweet_count, users_mention, urls, media_url, media_type,
               rt_bool, rt_user, rt_text, rt_hashtags, rt_urls, rt_media_url, rt_media_type]
        all_statuses.append(row)
        user_bio = tweet.user.description
        #print(created_at)


    header = ['tweet_id', 'created_at', 'text', 'hashtags', 'retweet_count', 'users_mention', 'urls',
              'media_url', 'media_type', 'rt_bool', 'rt_user', 'rt_text', 'rt_hashtags', 
              'rt_urls', 'rt_media_url', 'rt_media_type']

    df = pd.DataFrame(all_statuses,columns=header)
    
    return df

def text_clean(x):
    # all lower case
    x = str(x).lower()
    # remove URLS
    x = re.sub(r'https?://\w+\.\w+((\/\S+)+)?',r'',x)
    # remove emojis
    x = re.sub(r'\\x[a-z0-9]{2}',r'',x)
    # remove slashes and underscores
    #x = re.sub(r'[\\\_\/]',r'',x)
    # remove >3x repeated characters i.e. loooooook -> look
    x = re.sub(r'([a-z])\1{3,}', r'\1\1', x)
    
    
    return x

def make_wordcloud(user_name='minusplnp',max_statuses=200):

    df = get_timeline(user_name=user_name,max_statuses=max_statuses)

    tweet_speech = df['text'].apply(lambda x: text_clean(x)).str.cat()

    wordcloud_ALL = WordCloud(max_font_size=100, 
                              max_words=50, 
                              background_color="black",
                              collocations=False,
                              normalize_plurals=False).generate(tweet_speech)

    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111)
    ax.imshow(wordcloud_ALL,interpolation="bilinear")
    ax.axis('off')
    
    return ax


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
