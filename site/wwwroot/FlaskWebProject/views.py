"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template
from FlaskWebProject import app
import facebook
import requests
import HTMLParser
htmlparser = HTMLParser.HTMLParser()

# Removes pagination from Facebook API responses

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index2.html',
        title='Home Page',
        year=datetime.now().year
    )

ACCESS_TOKEN = "CAACEdEose0cBAELBDPWnmPXWu9Ioh6BAfJcv2ggWPgMtJZAeIZCXXdOnBhSWc6gxiw4nf9GBEZArYpaqvWV9oen6uZAz29ZCDkTWudzcggrAqI1Q1Vybh8ydti5V4GklGSTslVva6T0fEIdnhGMJLUUgo5UMsURNgvQysNgUAxCtr9dmEFezoZBE8xq7d8unghzBZAiGqLLF82jTWLoWkuC"
graph = facebook.GraphAPI(ACCESS_TOKEN)

MAX_PICS = 2

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
@app.route('/getsent')
def getsentiment():
    results = post_requests('analyzesentiment', data={'text': posts})
    at = "Sentiment: %s" % results['aggregate']['sentiment']
    bt = "Score: %s" % results['aggregate']['score']
    print "Sentiment: %s" % results['aggregate']['sentiment']
    print "Score: %s" % results['aggregate']['score']
    return at+", "+bt
    
@app.route('/userentity')
def userentity():
    print 'hello a'
    fd = ""
    info = '\n'.join(get_recursively(info, "name"))
    data = {'entity_type': 'pii', 'text': info}
    info_entities = post_requests('extractentities', data=data)
    for entity in info_entities['entities']:
        a=''
    return fd

@app.route('/entity')
def entity():
    data = {'entity_type': 'pii', 'text': posts}
    post_entities = post_requests('extractentities', data=data)
    fd =''
    for entity in post_entities['entities']:
        pa= entity['original_text']
        pb= entity['type']
        print pa+" "+pb
        fd = fd+"<tr><td>"+pa+"</td><td> "+pb+"</td></tr>"
        print
    return fd
    
@app.route('/pic')
def getPic():
    fd = ''
    for index, picture in enumerate(pictures):
        print "Getting text from image..."
        fd = fd+"<tr><td><img src = "+picture+" class = 'imgclass'> </td><td>"
        print picture
    #    #<tr><td>
    #  <img src = "" class = 'imgclass'>
    #  </td><td>fdsafds</td></tr>
        try:
            text = post_requests('ocrdocument', data={'url': picture})
            text = text["text_block"][0]["text"]
            text = " ".join(htmlparser.unescape(text).replace("\n", " ").split())
        except KeyError:
            pass
        
        print "Getting entities from text..."
        data = {'entity_type': 'pii', 'text': text}
        entities = post_requests('extractentities', data=data)
        for entity in entities['entities']:
            fd = fd+entity['type']+"</td><td>"+entity['original_text']+"</td></tr>"
            print entity
        print
        if (index >= MAX_PICS):
            break
    return fd
    
# Create graph API object
@app.route('/getposts')
def get_posts():
    # Get self and all friends using app
    users = ["me"] #+ [friend["id"] for friend in depaginate(graph.get_connections("me", "friends"))]
    
    # Get data for all users
    data = [get_user_data(user) for user in users]
    
    raw_data = ""
    
    for post in data[0][1]:
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
    sentences = ''
    for sentence in summarizer(parser.document, 10):
        sentences = sentences+'<tr><td>'+str(sentence)+'</td></tr>'
    print sentences
    return sentences
    
#sent = get_posts()

@app.route('/profile')
def profile():
    """Renders the profile page."""
    return render_template(
        'profile.html',        
        title='Profile',
        year=datetime.now().year,
        message = "<tr><td>hi world</td></tr>",
        
#        title='P',
#        year=datetime.now().year,
#        message='Your contact page.'
    )


@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )
