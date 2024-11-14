import os

import praw

reddit = praw.Reddit(
    client_id=os.environ["ID"],
    client_secret=os.environ["SECRET"],
    user_agent="tork:1.0.0:u/czenty",
)

for submission in reddit.subreddit("AskReddit").hot(limit=10):
    print(submission.title)
