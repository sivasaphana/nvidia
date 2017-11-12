# Imports
import csv
import re
import string
import tweepy
from tweepy import OAuthHandler
from textblob import TextBlob
from alpha_vantage.timeseries import TimeSeries
import matplotlib.pyplot as plt
import sys
import pandas as pd
from dateutil import parser


# Twitter Client Class
class TwitterClient(object):
    def __init__(self):
        # keys and tokens from the Twitter Dev Console
        consumer_key = 'eJlIQgcMf05crn7PWhT0qQpQu'
        consumer_secret = '5ZY4HTo84VZs4FuorDK8GRKLD0jxEFgQq9tECuY5OYsh4wRfLx'
        access_token = '823577912255385600-Tknji32sUZ17uy5i1YjqCJf9uAbJjEq'
        access_token_secret = '5Gujkwm4s3x6h9o72TPptnMH4CFpKrFRW387tRKl3nS0c'

        # attempt authentication
        try:
            # create OAuthHandler object
            self.auth = OAuthHandler(consumer_key, consumer_secret)
            # set access token and secret
            self.auth.set_access_token(access_token, access_token_secret)
            # create tweepy API object to fetch tweets
            self.api = tweepy.API(self.auth)
        except:
            print("Error: Authentication Failed")

    def clean_tweet(self, tweet):
        return ' '.join(
            re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ",
                   tweet).split())

    def get_tweet_sentiment(self, tweet):
        # create TextBlob object of passed tweet text
        analysis = TextBlob(self.clean_tweet(tweet))
        # set sentiment
        if analysis.sentiment.polarity > 0:
            return 'positive'
        elif analysis.sentiment.polarity == 0:
            return 'neutral'
        else:
            return 'negative'

    def get_tweets(self, query, count=10):
        '''
        Main function to fetch tweets and parse them.
        '''
        # empty list to store parsed tweets
        tweets = []

        try:
            # call twitter api to fetch tweets
            fetched_tweets = self.api.search(q=query, count=count)

            # parsing tweets one by one
            for tweet in fetched_tweets:
                # empty dictionary to store required params of a tweet
                parsed_tweet = {}

                # saving text of tweet
                parsed_tweet['text'] = tweet.text
                # saving sentiment of tweet
                parsed_tweet['sentiment'] = self.get_tweet_sentiment(
                    tweet.text)
                # saving time of tweet
                parsed_tweet['created_at'] = tweet.created_at

                # Location of user
                parsed_tweet['user_location'] = tweet.user.location

                # appending parsed tweet to tweets list
                if tweet.retweet_count > 0:
                    # if tweet has retweets, ensure that it is appended only once
                    if parsed_tweet not in tweets:
                        tweets.append(parsed_tweet)
                else:
                    tweets.append(parsed_tweet)

            # return parsed tweets
            return tweets

        except tweepy.TweepError as e:
            # print error (if any)
            print("Error : " + str(e))
api = TwitterClient()

def tweet_fetcher(count, country, disease_list ):
    tweet_list = []
    for disease in disease_list :
        print (disease)
        # creating object of TwitterClient Class
        print ("fetching tweets")
        tweets = api.get_tweets(query=disease, count=count)

        for tweet in tweets:
            tweet_data = {}
            if country in tweet['user_location'].lower().split() :
                print (tweet['user_location'])
                print (tweet['created_at'])
                print (tweet['sentiment'])
                if tweet['sentiment'] =='positive':
                    tweet_data['sentiment'] = 1
                elif tweet['sentiment'] =='neutral':
                    tweet_data['sentiment'] = 0
                elif tweet['sentiment'] =='negative':
                    tweet_data['sentiment'] = -1

                tweet_data['user_location']=tweet['user_location']
                exclude = set(string.punctuation)
                tweet_data['user_location'] = ''.join(ch for ch in tweet_data['user_location'] if ch not in exclude)
                tweet_data['timestamp']= tweet['created_at'].strftime(
                    "%Y-%m-%d")
                tweet_data['disease_type'] = disease
                tweet_list.append(tweet_data)
    return tweet_list
# dlist = ["flu",'dengue', 'dengue', 'malaria' , 'Swine Flu', 'Bird Flu',
#          'typhoid ', 'jaundice', 'chicken pox', 'bronchitis']
dlist = ["dengue"]
tweet_list = tweet_fetcher (count = 500,country ='india',disease_list=dlist)
print (tweet_list)

# keys = tweet_list[0].keys()
# with open('analysis_disease_data.csv', 'wb') as output_file:
#     dict_writer = csv.DictWriter(output_file, keys)
#     dict_writer.writeheader()
#     dict_writer.writerows(toCSV)

# # pd_data=pd.DataFrame(tweet_list.items(), columns=['timestamp',
#                                      'sentiment', 'user_location'])

pd_data=pd.DataFrame(tweet_list)
print(pd_data.head())
pd_data.to_csv('analysis_disease_data.csv')

