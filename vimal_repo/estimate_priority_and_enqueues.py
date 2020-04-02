# this program helps to find the priority of the urls which contain keywords like ('job','jobs','gig','gigs','career','careers','https')
# by using the glove algorithm

#import essential libraries
import os
from wordsegment import load, segment, clean
import mysql.connector
import scipy.spatial.distance as dist
import re
import numpy as np
import pandas as pd
import time
import multiprocessing
import concurrent.futures
start=time.perf_counter()



mydb = mysql.connector.connect(host=os.environ['DBHOST'], 
                                user=os.environ['DBUSER'], 
                                password=os.environ['DBPASS'],
                                database=os.environ['DBNAME'])

load()
scur = mydb.cursor()

embeddings_dict = {}
job_keywords=['job','jobs','gig','gigs','career','careers','https']

with open("glove.6B.50d.txt", 'r') as f:  
    for line in f:
        dimension= line.split()       			#split keys and values of the "glove.6B.50d.txt" and storing in dimension
        embedding_word = dimension[0]            			# taking embedding_word==> key present at 0th index    
        embedding_vector = np.asarray(dimension[1:2], "float32")     #taking 1st to 10th dimension of the same  and converted in array 
        embeddings_dict[embedding_word] = embedding_vector 

def fetch_url_from_db():
  '''this function help to get the url from the sitemap table and store into a list.Because we have to show url which has higher priority'''
  listofurls=[]
  scur.execute("select url from sitemap")
  myscur=scur.fetchall()
  count=0
  for tuple_url in (myscur):            # these lines  are  written for testing purpose  
    print(count)                        #
    count=count+1                       #
    if count<10000:                       #
      listofurls.append(tuple_url[0])   #
    else:                               #
      break                             #
  return(listofurls)                    #

listofurls=fetch_url_from_db()


def isjobvector(job_keywords):
  '''this function helps to convert the job related keyword ('job','jobs','gig','gigs','career','careers','https')
  into the vectors and return the vector_job_is_list'''
  vector_job_is_list=[]
  for keyword in range(len(job_keywords)):
    if job_keywords[keyword] not in embeddings_dict:
      continue
    else:
      for value_words in embeddings_dict[job_keywords[keyword]]: 
        vector_job_is_list.append(value_words)
  return(vector_job_is_list)

vector_job_is_list=isjobvector(job_keywords)


def finding_euclidean_distance(vector,vector_job_is_list):
  ''' this function is used to find the euclidean distance between the vector of urls and job keywords'''
  euclidean_difference=0.0
  for word_index in vector_job_is_list:
      for url_index in vector:
        distances=dist.euclidean(word_index,url_index)
        euclidean_difference=euclidean_difference+distances
  return(euclidean_difference)

euclidean_difference_list=[]
eucleadean_dista=[]


def segmentation(urls):
  url=re.sub(r'[^("a-zA-Z")]',' ',urls)
  segment_url=segment(url)
  return(segment_url)
  
def urlvector(urls):
  ''' this function takes the url and convert the words of url into vector and append into vector_url_list and return it'''
  vector_url_list=[]
  for u_rl in range(len(urls)):
    if urls[u_rl] not in embeddings_dict:
      continue
    else:
      for value_word in embeddings_dict[urls[u_rl]]:
        vector_url_list.append(value_word)
  return(vector_url_list)



segment_urls=[]
vector_of_urls=[]


with multiprocessing.Pool() as executer:

    results= executer.map(segmentation,listofurls)

    for result in results:
      segment_urls.append(result)

    
    results_vector= executer.map(urlvector,segment_urls)
    
    for vector_segment_url in results_vector:
      vector_of_urls.append(vector_segment_url)



eucleadean_dista=[]        #this list will contain the resultant distance of each url(vector of url and vector of job releated keyword)
no_of_url=len(vector_of_urls)

def get_computed_distance(no_of_url):
  ''' this function takes the length  i.e no of urls and call the function finding_euclidean_distance and return list of 
    euclidean distance vector in the list called  eucleadean_dista'''
  for url in range(no_of_url):
    euclidean_distance_vector=finding_euclidean_distance(vector_of_urls[url],vector_job_is_list)
    eucleadean_dista.append(euclidean_distance_vector)
  return(eucleadean_dista)

get_distance=get_computed_distance(no_of_url)


 # converting list of urls into dataframe
url_df=pd.DataFrame({'list of url':listofurls}) 
euclidean_distance_df=pd.DataFrame({'euclidean distance':get_distance}) 
concatinating_df = pd.concat([ url_df,euclidean_distance_df ], axis=1) 
df=concatinating_df.sort_values(by='euclidean distance')


# making priority queue by according to percentile

percentile_greater_90=np.percentile(df['euclidean distance'],10)           # to calculate 90 percentile that is best match we have to 
                                             #calculate 10 percentile because its a distance between keywords  and urls (df of url and distance is alredy sorted )  
                                                 
priority1=df[df['euclidean distance']<percentile_greater_90] 
priority1=priority1.rename(columns={'list of url':'priority1 url'})                                           
print('priority queue contain >90 percentile match \n',priority1)

percentile_between_80_90=np.percentile(df['euclidean distance'],20)


priority2=df[(df['euclidean distance']>percentile_greater_90) & (df['euclidean distance']<percentile_between_80_90) ]
priority2=priority2.rename(columns={'list of url':'priority2 url'})
print('\n priority queue contain between 80-90 percentile match \n',priority2)

priority3=df[df['euclidean distance']>percentile_between_80_90]
priority3=priority3.rename(columns={'list of url':'priority3 url'})
print('\n priority queue contain <80 percentile match \n',priority3) 



finish=time.perf_counter()




