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
            posts += [post['message']]
        except KeyError:
            pass
    
    # Return data as a tuple
    return info, likes, posts


# Create graph API object
ACCESS_TOKEN = "CAACEdEose0cBAAFGA9tAvZBZB4bTa5AQsyWZBzO1yXQSwWHt5m4ZCyL1KxHxoGYkaMhKgzi8lwle94T9wfIylEZAFqqEJNGDZCRTs0rRsY96rZBI4Ee8WtmH0UtHhrAvXqQKpq5dLzTvGlNKO4sWscEOolQpka0iKvxNpvNuEidlXKZAjIkOvOgXJkjRkrFEOTBj8J3d2H5nj9cQw50QQRRR"
graph = facebook.GraphAPI(ACCESS_TOKEN)

# Get self and all friends using app
users = ["me"] + [friend["id"] for friend in depaginate(graph.get_connections("me", "friends"))]

# Get data for all users
data = [get_user_data(user) for user in users]
