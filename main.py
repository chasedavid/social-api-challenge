
# coding: utf-8

# In[1]:


#dependencies
import tweepy
import numpy as np
import pandas as pd
from datetime import datetime
#for graphing
import matplotlib.pyplot as plt
from pprint import pprint
from random import randint 
from datetime import datetime

#VADER for sentiment analysis
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
analyzer = SentimentIntensityAnalyzer()


# In[2]:


#retrieve keys for Twitter API
from config import (consumer_key, 
                    consumer_secret, 
                    access_token, 
                    access_token_secret)

#set up keys
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())


# In[3]:


#functions to pull from call to anazlye twitter handle
def extract_target(string):
    lngth = len(string)
    i = lngth - 1
    while string[i] != '@':
        i -= 1
    return (string[i:lngth])


# In[4]:


#function to pull text from target twitter handle/ returns DataFrame of sentiment analysis and text
def tweet_sentiment(account_id):
    target = account_id
    
    #store list of text from tweets (for testing purposes)
    texts = []
    #create list of scores
    compound = []
    positive = []
    negative = []
    neutral = []
    created_at = []
    
    #create counter and list of index corresponing with how many text ago
    counter = -1
    ctrs = []
    
    #reference for oldest tweet
    oldest_tweet = None
    
    #iterate through 5 pages of 100: range(5), count=100
    for x in range(5):
        public_tweets = api.user_timeline(target, 
                                          max_id = oldest_tweet, 
                                          count=100,
                                         page=x)
        
        #iterate through public tweets
        for tweet in public_tweets:
            #store text in variable
            texts.append(tweet['text'])
            created_at.append(tweet['created_at'])
            
            #analyze text for sentiment => store values accoringingly
            scores = analyzer.polarity_scores(tweet['text'])
            compound.append(scores['compound'])
            positive.append(scores['pos'])
            negative.append(scores['neg'])
            neutral.append(scores['neu'])
            
            #decriment counter and append list into counter, 
            ctrs.append(counter)
            counter -= 1
            oldest_tweet = tweet['id'] - 1
    
    #build result data frame 
    result_df = pd.DataFrame({
        'tweet_index':ctrs,
        'comp':compound,
        'positive':positive,
        'negative':negative,
        'neutral':neutral,
        'text': texts,
        'created_at':created_at
    })
    #save data frame as csv
    result_df.to_csv('./data/target.csv')
    
    return (result_df)


# In[5]:


def graph_df(df, target):
    cur_date = datetime.now().strftime('%x %X')

    plt.plot(df.tweet_index, 
             df.comp, 
             marker='o',
             alpha=0.75,
            linewidth=0.4)

    #labels on graph
    plt.title(f"New Tweet Analysis: {target} ({cur_date})")
    plt.xlabel("Tweets Ago")
    plt.ylabel("Tweet Polarity")

    #save fig
    plt.savefig('./figs/figure.png')

    #plt.hlines(y=0, xmin=-25, xmax=0)
    plt.show()
    


# In[6]:


##end of funcitons - beginning of main

#create variables to store past analyzed accounts, 
past_accounts = []
target = ''
#reference to a test posting to test if code works as desired
last_checked='1048732048163106816'


while(True):
    #make an api call to check twitter page
    check = api.search('@chasethedavid', since_id=last_checked)


# In[ ]:


#check if there is a text, and confirm not @chasethedavid (handle of bot)
if check['statuses'][0]['text'] and extract_target(check['statuses'][0]['text']).strip(' ') != '@chasethedavid':
    target = extract_target(check['statuses'][0]['text']).strip(' ')
else:
    api.update_status("I'm sorry, the desired account has not found.")

#check to see if analyzed in past
if target not in past_accounts:
    df = tweet_sentiment(target)
    graph_df(df, target)
    api.update_with_media('./figs/figure.png')
    past_accounts.append(target)
else:
    api.update_status("That account has been anazlyzed")
 


# In[ ]:


#update reference to last text analyzed
if int(check['statuses'][0]['id']) > int(last_checked):
    last_checked = check['statuses'][0]['id']


# In[ ]:


#wait 5 minutes between scanning for mentions
time.sleep(300)

