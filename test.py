# Import necessary libraries
import facebook
import requests

# Removes pagination from Facebook API responses
def depaginate(data):
    outdata = []
    while(data["data"]):
        outdata += data["data"]
        try:
            data = requests.get(data["paging"]["next"]).json()
        except KeyError:
            break
    return outdata

# Return the info, likes, posts of a user with given id
def get_user_data(user):
    # Get your info
    info = graph.get_object(user)
    
    # Get your likes
    likes = depaginate(graph.get_connections(user, "likes"))
    
    # Get your posts
    posts = []
    for post in depaginate(graph.get_connections(user, "posts")):
        try:    
            data = post['message']
            #try:
            #    data += post['link']
            #except KeyError:
            #    pass
            posts += [data]
        except KeyError:
            pass
    
    # Return data as a tuple
    return info, likes, posts


# Create graph API object
ACCESS_TOKEN = "CAACEdEose0cBAE6YQQVWGeUNhh5QUWbzECzVzawEML5haoJBfsOvZANW1y5pLuJ1GECZCC2V6BWrvhnZB1W73sqKlnZADVhcBUDqk85ZBNK65iJF9ZBuhvv8M263il27igIhMZARMDhzDbNLBajBKEbgzK6HsNlRS6jeA4T2Jf0Fl3BZBQ0ZBtyPuZBCYbVKaYS6jCPoHDqe3p7AZDZD"
graph = facebook.GraphAPI(ACCESS_TOKEN)

# Get self and all friends using app
users = ["me"] #+ [friend["id"] for friend in depaginate(graph.get_connections("me", "friends"))]

# Get data for all users
data = [get_user_data(user) for user in users]

raw_data = ""

for post in data[0][2]:
    raw_data += post

#print raw_data

#from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer

#from sumy.summarizers.lex_rank import LexRankSummarizer as Summarizer
#from sumy.summarizers.text_rank import TextRankSummarizer as Summarizer
#from sumy.summarizers.random import RandomSummarizer as Summarizer
from sumy.nlp.stemmers import *
from sumy.utils import get_stop_words

LANGUAGE = "english"

parser = PlaintextParser.from_string(raw_data, Tokenizer(LANGUAGE))
 
stemmer = Stemmer(LANGUAGE)

summarizer = Summarizer(stemmer)
#summarizer.stop_words = get_stop_words(LANGUAGE)

for sentence in summarizer(parser.document, 10):
    print(sentence)