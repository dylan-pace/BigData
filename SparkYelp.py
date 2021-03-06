# -*- coding: utf-8 -*-
"""SparkCoursework.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1R_oYFb9NnhLy6fs1UQ8wDNIF9WpO9egp

# High Perfromance Computing and Big Data - Spark Task (50%)

## Introduction

Apache Spark is a cluster-computing framework used for the purposes of dealing with large sets of data. The data being explored throughout this task is the Yelp challenge dataset, which is split into multiple JSON files. The goal would be to investigate these files in order to answer relevant questions and then carry on this exploration to learn more about the data. Some of these datasets include, business information, reviews and user profiles. Take, for example, the business file. It would have data relating to the name of the business, the city in which it may be found and the rating, all save in a JSON object as key/value pairs.
Using the Apache Spark core API, it should be easy to explore these datasets using the actions and functions made available. This means that when investigating the JSON objects, they can counted, sorted and filtered to ensure that the specific data needed can be found using Spark pipelines.The JSON RDDs may also be joined if needed so that all the relevant data may be present in a single RDD.
"""

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
# %matplotlib inline
import seaborn as sns
import json
sns.set()
#Import all the necessary libraries that may be required for this task.

import findspark
findspark.init()
#Allowed for the environment to find the Spark files.

from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession
#Import the spark libraries so that big data can be managed.
spark_conf = SparkConf().setMaster('local').setAppName('MyApp')
sc = SparkContext(conf=spark_conf)
#Set up a Spark context so actions may be run as they would in the terminal.
spark = SparkSession(sc)

"""## Which reviews have been rated as useful by more than 30 users and funny by more than 20 users?"""

yelp_review_rdd = sc.textFile('Spark/datasets/yelp_dataset/review.json').map(lambda x: json.loads(x))
#Instantiating the JSON file and converting it into an RDD (resilient distributed dataset).

yelp_review_rdd.count()
#The count action counts how many objects are saved in the RDD.

yelp_review_rdd.take(3)
#The take action will take a specified number of objected from the RDD and display them, in this case it will take 3.

yelp_review_rdd.filter(lambda x: x['useful'] > 30).filter(lambda x: x['funny'] > 20).count()
#The filter function can perform operations on RDDs in order to display certain sets of data.

yelp_review_rdd.filter(lambda x: x['useful'] > 30).filter(lambda x: x['funny'] > 20).take(5)
#The lambda function will count and take data where useful has been marked over 30 and funny has been rated over 20.

"""## Which businesses based in Las Vegas that are identified as Nightlife have been rated 4.5 stars or higher?"""

yelp_business_rdd = sc.textFile('Spark/datasets/yelp_dataset/business.json').map(lambda x: json.loads(x))
#Instantiating the business file.

yelp_business_rdd.count()

yelp_business_rdd.take(3)

yelp_business_rdd.filter(lambda x: x['city'] == 'Las Vegas')\
.filter(lambda x: 'Nightlife' in x['categories'])\
.filter(lambda x: x['stars'] >= 4.5).count()
#Filtering the data with lambda functions can be done multiple times using a pipeline.

yelp_business_rdd.filter(lambda x: x['city'] == 'Las Vegas')\
.filter(lambda x: 'Nightlife' in x['categories'])\
.filter(lambda x: x['stars'] >= 4.5).take(5)
#Different operations can be done to filter the data such as relational operations or searching through an array.

"""## What are the top-10 reviewers, in terms of the absolute number of reviews marked as useful by other users, of Nightlife businesses in Urbana-Champaign?"""

yelp_user_rdd = sc.textFile('Spark/datasets/yelp_dataset/user.json').map(lambda x: json.loads(x))
#Instantiating the user file.

yelp_user_rdd.take(3)

def slice_dict(my_dict, keys): 
    return { k: v for k, v in my_dict.items() if k in keys }
#Method that can be used to slice dictionaries and reassemeble them based on key/value pairs.

review_cut_rdd = yelp_review_rdd.map(lambda x: (x['business_id'], slice_dict (x, ['review_id', 'user_id'])))
#Slicing the review RDD in order to make the foreign key, 'business_id' the primary key.
#Slicing also allows for some of the useless key/value pairs to be dropped from the RDD.

review_cut_rdd.take(3)

business_cut_rdd = yelp_business_rdd.map(lambda x: (x['business_id'], slice_dict (x, ['name', 'city', 'categories'])))
#Slicing the business RDD in order to make the 'business_id' the primary key of the object.

business_cut_rdd.take(3)

review_cut_rdd.join(business_cut_rdd).take(5)
#When two RDDs have the same key, a join function can be perfromed in order to put the two sets of data together as one.

def merge_dicts(d1, d2):
    return { **d1, **d2 }
#Method that will merge dictionaries into one object.

review_business_rdd = review_cut_rdd.join(business_cut_rdd).map(lambda x: merge_dicts(x[1][0], x[1][1]))
#The joined object will be split into two dictionaries and must therefore but merged back together before actions may be taken.

review_business_rdd.take(3)

user_review_rdd = review_business_rdd.map(lambda x: (x['user_id'], slice_dict(x, ['review_id', 'name', 'city', 'categories'])))
#Slicing the user RDD, putting 'user_id' as the primary key of the object.

user_review_rdd.take(3)

user_cut_rdd = yelp_user_rdd.map(lambda x: (x['user_id'], slice_dict (x, ['name', 'review_count', 'useful'])))
#Slicing the joined RDD between business and review in order to make the foreign key 'user_id' primary.

user_cut_rdd.take(3)

final_rdd = user_cut_rdd.join(user_review_rdd).map(lambda x: merge_dicts(x[1][0], x[1][1]))
#The three RDDs are joined here, being merged together means they can be explored as a single object.

final_rdd.take(3)

final_rdd.filter(lambda x: x['useful']).sortBy(lambda x: x['useful'], ascending=False).take(10)
#Sorting the RDD by the highest number of useful comments.

final_rdd.filter(lambda x: x['useful'])\
.sortBy(lambda x: x['useful'], ascending=False)\
.filter(lambda x: (x['city'] == 'Champaign') | (x['city'] =='Urbana'))\
.filter(lambda x: 'Nightlife' in x['categories'])\
.take(10)
#This pipeline sorts the data by useful comments and filters the data by the city the businesses were based in 
#and by the type of business it is.

"""## Data Science Exploratory Analaysis - Investigation

### What is the most common category attribute to describe a business?
"""

categories = yelp_business_rdd.flatMap(lambda x: x['categories']).map(lambda x: (x,1)).reduceByKey(lambda x,y: x+y)
#Mapping the business RDD and reducing the size in order to get the data into a relative format.

categories.sortBy(lambda x: x[1], ascending=False).take(10)
#Sorting the RDD in ascending order to see which category appears the most.

"""### Which business has the most number of reviews with the highest rating?"""

yelp_business_rdd.filter(lambda x: x['review_count'])\
.sortBy(lambda x: x['review_count'], ascending=False)\
.sortBy(lambda x: x['stars'], ascending=False).take(5)
#Sorting data by review count and stars to show which businesses has the most reviews and the highest number of stars.
#This should be the best business in the dataset.

"""### Which business has the most number of reviews with the lowest rating?"""

yelp_business_rdd.filter(lambda x: x['review_count'])\
.sortBy(lambda x: x['review_count'], ascending=False)\
.sortBy(lambda x: x['stars'], ascending=True).take(5)
#Sorting data by review count and stars to show which businesses has the most reviews and the lowest number of stars.
#This should be the worst business in the dataset.

"""## Conclusion

In conclusion, the Apache Spark API allows for a more efficient way of exploring large data files and manipulating the data in order to show relevant information needed to answer data science questions. The Spark framework is one of the most reliable and effective big data manipulation tools available and its simple list of commands means that the data can be selected, sorted and joined with a few commands in a pipeline. The questions presented for the yelp dataset would've been much harder to answer if not for the Spark API, an efficeient framework for dealing with big data.
"""
