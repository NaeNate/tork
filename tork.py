from os import environ

from elevenlabs import ElevenLabs
from moviepy.editor import CompositeVideoClip, TextClip, VideoFileClip
from praw import Reddit

reddit = Reddit(
    client_id=environ["REDDIT_ID"],
    client_secret=environ["REDDIT_SECRET"],
    user_agent="tork:0.1.0:u/czenty",
)

submission = reddit.submission("1gpmw0i")
submission.comment_sort = "confidence"
submission.comments.replace_more(limit=0)

print(submission.title)

for comment in submission.comments[:10]:
    print(comment.body)

client = ElevenLabs(api_key=environ["ELEVEN_KEY"])

audio = client.generate(
    text="Hello! 你好! Hola! नमस्ते! Bonjour! こんにちは! مرحبا! 안녕하세요! Ciao! Cześć! Привіт! வணக்கம்!",
    voice="Will",
    model="eleven_multilingual_v2",
)

clip = VideoFileClip("input.webm").subclip(30, 90)

text = TextClip("Hey There", fontsize=70, color="white")
text = text.set_position("center").set_duration(10)

video = CompositeVideoClip([clip, text])
video.write_videofile("out.mp4")
