from os import environ

from praw import Reddit

reddit = Reddit(
    client_id=environ["ID"],
    client_secret=environ["SECRET"],
    user_agent="tork:1.0.0:u/czenty",
)

for submission in reddit.subreddit("AskReddit").hot(limit=10):
    print(submission.title)
