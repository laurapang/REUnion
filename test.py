# Import necessary libraries
import facebook
import requests
import HTMLParser

# For removing escape characters
htmlparser = HTMLParser.HTMLParser()

# Takes a dict with nested dicts and searches for all values of key
def get_recursively(search_dict, field):
    fields_found = []
    for key, value in search_dict.iteritems():
        if key == field:
            fields_found.append(value)
        elif isinstance(value, dict):
            results = get_recursively(value, field)
            for result in results:
                fields_found.append(result)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    more_results = get_recursively(item, field)
                    for another_result in more_results:
                        fields_found.append(another_result)
    return fields_found

# Removes paging from Facebook API responses
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
    
    # Get your posts and pictures
    posts = ""
    for post in depaginate(graph.get_connections(user, "posts")):
        try:
            posts += post['message'] + "\n" # Should this be a space?
        except KeyError:
            pass
        
    # Get your pictures
    pictures = []
    for picture in depaginate(graph.get_connections(user, "photos/uploaded")):
        pictures += [picture["images"][0]["source"]]
    
    # Return data as a tuple
    return info, posts, pictures


# Create graph API object
FB_ACCESS_TOKEN = "CAACEdEose0cBALvzckSbHOUO5LlBsJOyySZB9cwYF3YoxRfyg1zEZBlquz2zv0KZBRfnVSKvuLEM0aAqZCtjZCVuDRbUSFywl5wDymMxmNTvDJZAyX6HNZBtwtm1LlGAmpK2ZCjdiyXGy5iMUd0M0NKXIxtC8VKCZBaJn0GurzzLJfsjZBDy9IgzdD1G5YdoPSDUUSHWRcnTotupsgdEPba2rq"
graph = facebook.GraphAPI(FB_ACCESS_TOKEN)

# Get your data
print "Getting user data..."
info, posts, pictures = get_user_data("me")

# Strip down info
info_keys = ("hometown", "education", "location", "birthday")
info = {x: info[x] for x in info_keys if x in info}


# Haven API key and endpoint
HAVEN_APIKEY = "ae21f0f2-29f4-43c6-8fc5-cdfc55010c01"
URL = "https://api.havenondemand.com/1/api/sync/{}/v1"

# Make a post request to the Haven API
def post_requests(function, data={}, files={}):
   data["apikey"] = HAVEN_APIKEY
   callurl = URL.format(function)
   r = requests.post(callurl, data=data, files=files)
   return r.json()

# Get user overall sentiment
results = post_requests('analyzesentiment', data={'text': posts})
print "Sentiment: %s" % results['aggregate']['sentiment']
print "Score: %s" % results['aggregate']['score']
print

# Get user info and entities
print info
info = '\n'.join(get_recursively(info, "name"))
data = {'entity_type': 'pii', 'text': info}
info_entities = post_requests('extractentities', data=data)
for entity in info_entities['entities']:
    print entity
    print

# Get user post and entities
print posts
data = {'entity_type': 'pii', 'text': posts}
post_entities = post_requests('extractentities', data=data)
for entity in post_entities['entities']:
    print entity
    print
    
# Print picture and text
for picture in pictures:
    print "Getting text from image..."
    print picture
    try:
        text = post_requests('ocrdocument', data={'url': picture})
        text = text["text_block"][0]["text"]
        text = " ".join(htmlparser.unescape(text).replace("\n", " ").split())
        print text
    except KeyError:
        pass
    
    print "Getting entities from text..."
    entities = post_requests('extractentities', data = {'entity_type': 'pii', 'text': text})
    for entity in entities['entities']:
        print entity
    print
    
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import *

LANGUAGE = "english"

parser = PlaintextParser.from_string(posts, Tokenizer(LANGUAGE))
 
stemmer = Stemmer(LANGUAGE)

summarizer = Summarizer(stemmer)
summarizer.stop_words = get_stop_words(LANGUAGE)

for sentence in summarizer(parser.document, 10):
    print(sentence)