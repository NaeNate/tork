import os

import praw
from gtts import gTTS
from moviepy.editor import (
    AudioFileClip,
    CompositeVideoClip,
    TextClip,
    VideoFileClip,
    concatenate_videoclips,
)
from yt_dlp import YoutubeDL

# Initialize Reddit client with environment variables
reddit = praw.Reddit(
    client_id=os.environ["REDDIT_ID"],
    client_secret=os.environ["REDDIT_SECRET"],
    user_agent="tork:0.1.0:u/czenty",
)

# Fetch a submission from AskReddit
# subreddit = reddit.subreddit("AskReddit")
# submission = next(subreddit.hot(limit=1))
submission = reddit.submission("1grik2y")

# Fetch the submission title
title = submission.title

# Fetch comments with less than 30 words
submission.comments.replace_more(limit=0)
comments = []
for comment in submission.comments:
    if len(comments) >= 8:
        break
    if comment.body and not comment.stickied:
        word_count = len(comment.body.split())
        if word_count < 30:
            comments.append(comment.body)

# Check if background video exists, if not, download it using yt_dlp
video_filename = "background_video.mp4"
if not os.path.exists(video_filename):
    video_url = "https://www.youtube.com/watch?v=_-2ZUciZgls"
    ydl_opts = {
        "format": "bestvideo[ext=mp4][height<=1080]",
        "outtmpl": "background.mp4",
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

# Generate TTS for the title
tts_title = gTTS(text=title, lang="en")
tts_title.save("title.mp3")
audio_title = AudioFileClip("title.mp3")

# Generate TTS audio for each comment with index
audio_clips = []
for i, comment in enumerate(comments):
    # Include the index before the comment
    comment_text = f"{i + 1}. {comment}"
    tts = gTTS(text=comment_text, lang="en")
    audio_filename = f"comment_{i}.mp3"
    tts.save(audio_filename)
    audio_clip = AudioFileClip(audio_filename)
    audio_clips.append(audio_clip)

# Load the background video
video_clip = VideoFileClip(video_filename)

# Crop the video to 9:16 aspect ratio
width, height = video_clip.size
target_aspect = 9 / 16
current_aspect = width / height

if current_aspect > target_aspect:
    # Crop width
    new_width = int(height * target_aspect)
    x1 = (width - new_width) // 2
    x2 = x1 + new_width
    cropped_video = video_clip.crop(x1=x1, y1=0, x2=x2, y2=height)
else:
    # Crop height
    new_height = int(width / target_aspect)
    y1 = (height - new_height) // 2
    y2 = y1 + new_height
    cropped_video = video_clip.crop(x1=0, y1=y1, x2=width, y2=y2)

# Use a subclip of the background video (e.g., start at 10 seconds)
background_duration = cropped_video.duration
subclip_start = 10  # Start at 10 seconds

# Calculate total duration needed
total_audio_duration = audio_title.duration + sum(ac.duration for ac in audio_clips)
subclip_end = min(background_duration, subclip_start + total_audio_duration)

# Create video clips with text overlay and sync with audio
final_clips = []
current_time = subclip_start

# Process the title
# Create subclip for the title
clip_duration = audio_title.duration
clip = cropped_video.subclip(current_time, current_time + clip_duration)
current_time += clip_duration  # Update current time for the next clip

# Create text clip for the title
txt_clip_title = (
    TextClip(
        title,
        fontsize=80,
        font="Arial-Bold",
        color="white",
        stroke_color="black",
        stroke_width=3,
        method="caption",
        size=(clip.w * 0.8, None),
        align="center",
    )
    .set_duration(clip_duration)
    .set_position("center")
)

# Composite text over video
composite_title = CompositeVideoClip([clip, txt_clip_title]).set_audio(audio_title)
final_clips.append(composite_title)

# Process each comment
for i, audio_clip in enumerate(audio_clips):
    # Set clip duration to match audio
    clip_duration = audio_clip.duration
    # Create subclip from the background video
    clip = cropped_video.subclip(current_time, current_time + clip_duration)
    current_time += clip_duration  # Update current time for the next clip
    # Create text clip with index
    comment_text = f"{i + 1}. {comments[i]}"
    txt_clip = (
        TextClip(
            comment_text,
            fontsize=50,
            font="Arial-Bold",
            color="white",
            stroke_color="black",
            stroke_width=2,
            method="caption",
            size=(clip.w * 0.8, None),
            align="center",
        )
        .set_duration(clip_duration)
        .set_position("center")
    )
    # Composite text over video
    composite = CompositeVideoClip([clip, txt_clip]).set_audio(audio_clip)
    final_clips.append(composite)

# Concatenate all clips
final_video = concatenate_videoclips(final_clips, method="compose")

# Write the output video
final_video.write_videofile("output_video.mp4", fps=30)

# Clean up temporary files
video_clip.close()
cropped_video.close()
audio_title.close()
os.remove("title.mp3")
for audio_clip in audio_clips:
    audio_clip.close()
for i in range(len(comments)):
    os.remove(f"comment_{i}.mp3")
# Do not delete 'background_video.mp4' so it can be reused
