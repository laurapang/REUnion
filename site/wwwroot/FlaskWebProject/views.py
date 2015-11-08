"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template
from FlaskWebProject import app
import facebook
import requests

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

ACCESS_TOKEN = "CAACEdEose0cBAOZCIZAFJzYMb4B9JSc7urVz8WIBS0kzXMr8ocgUdUQbiEscIIReImHTIW7tqVDc31cDgzCLZANYSEQFP9ag6bIGf8dUp8e0zWfdLiVX0kEbPf6tWbnk4cy0JcAkKssymee4kKvY0bHncLiZBjAayEQv4Liu5MGXRjF5ZArqPrqFXxRVlXbAOb93S0djiXILBQutIn30r"
graph = facebook.GraphAPI(ACCESS_TOKEN)
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
def get_posts():
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
    sentences = ''
    for sentence in summarizer(parser.document, 10):
        sentences = sentences+'<tr><td>'+str(sentence)+'</td></tr>'
    print sentences
    return sentences
    
sent = get_posts()

@app.route('/profile')
def profile():
    """Renders the profile page."""
    return render_template(
        'profile.html',        
        title='Profile',
        year=datetime.now().year,
        message = sent
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
