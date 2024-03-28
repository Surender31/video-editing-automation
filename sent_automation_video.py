import subprocess
import time
from datetime import datetime
from io import BytesIO
from time import sleep
from tkinter import Tk
from tkinter import filedialog 

import moviepy.editor as mp
import numpy as np
import pandas as pd
from PIL import Image, ImageOps
from gtts import gTTS
from pydub import AudioSegment
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def resize_with_padding(image_input, output_size):
    """
    Resizes an image with padding to the given output size.
    Returns a PIL Image object.
    """
    img = image_input.copy()
    w, h = img.size
    aspect_ratio = w / h
    target_ratio = output_size[0] / output_size[1]

    if aspect_ratio >= target_ratio:
        # Fit to width
        new_w = output_size[0]
        new_h = int(output_size[0] / aspect_ratio)
    else:
        # Fit to height
        new_w = int(output_size[1] * aspect_ratio)
        new_h = output_size[1]

    img = img.resize((new_w, new_h))

    # Add padding to fill the output size
    pad_w = output_size[0] - new_w
    pad_h = output_size[1] - new_h
    left = pad_w // 2
    right = pad_w - left
    top = pad_h // 2
    bottom = pad_h - top
    padding = (left, top, right, bottom)
    img = ImageOps.expand(img, padding, fill=(255, 255, 255))

    return img


def add_logo_to_video(video_path, image_path, x, y):
    """
    Adds an image to a video at the given x, y position.
    Saves the new video to the same path as the original.
    """
    # Load the video clip
    clip = VideoFileClip(video_path)

    # Load the image and resize if necessary
    image = Image.open(image_path)

    if image.size != (clip.w, clip.h):
        image = image.resize((clip.w, clip.h))

    # Convert the image to a clip
    image_clip = ImageClip(np.array(image)).set_duration(clip.duration)

    # Set the position of the image clip
    image_clip = image_clip.set_position((x, y))

    # Add the image clip to the video clip
    final_clip = CompositeVideoClip([clip, image_clip])

    # Save the new video to the same path as the original
    final_clip.write_videofile(video_path, fps=clip.fps)


def duck_audio(vo_path, bg_path, output_path):
    # Load audio files
    vo = AudioSegment.from_file(vo_path)
    bg = AudioSegment.from_file(bg_path)

    # Define ducking parameters
    duck_dB = -20  # Amount of ducking in decibels
    fade_in_ms = 50  # Duration of fade in for ducking
    fade_out_ms = 1500  # Duration of fade out for ducking
    overlap_ms = 30  # Amount of overlap between ducking and non-ducking segments

    # Calculate ducking and non-ducking segments
    vo_duration = vo.duration_seconds * 1000
    duck_segment = bg[vo_duration + overlap_ms:].fade_in(fade_in_ms).fade_out(fade_out_ms).dBFS
    duck_segment = duck_segment(duck_dB)
    non_duck_segment = bg[:vo_duration + overlap_ms]

    # Apply ducking to non-voiceover segments
    output = non_duck_segment.overlay(duck_segment)

    # Add voiceover track
    output = vo.overlay(output)
    # Export final mix
    output.export(output_path, format="mp3")


def generate_tts_audio(text_list: object, delay: object = 0) -> object:
    # Initialize empty audio clip
    audio_clip = AudioSegment.silent(duration=0)

    # Loop through each text and generate TTS audio clip
    for text in text_list:
        # Generate TTS audio clip
        tts = gTTS(text=text, lang='en-us')

        # Convert TTS audio to bytes

        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)

        # Load TTS audio clip and add to the main audio clip
        tts_audio_clip = AudioSegment.from_file(fp, format="mp3")
        audio_clip += tts_audio_clip

        # Add delay between each text
        time.sleep(delay)

    audio_clip.export('output_audio.mp3', format='mp3')
    return audio_clip


def mix_audio_files(file1, file2, gain1=0, gain2=0):
    # Load audio files
    sound1 = AudioSegment.from_file(file1)
    sound2 = AudioSegment.from_file(file2)

    # Normalize audio levels
    normalized_sound1 = sound1.normalize()
    normalized_sound2 = sound2.normalize()

    # Apply gain to audio files
    adjusted_sound1 = normalized_sound1 + gain1
    adjusted_sound2 = normalized_sound2 + gain2

    # Mix audio files
    mixed_sound = adjusted_sound1.overlay(adjusted_sound2)

    # Export mixed audio to a file
    mixed_sound.export("mixed.mp3", format="mp3")
    os.remove(file2)


def cut_and_fade_audio(input_file, output_file, cut_sec):
    # Load the audio file
    audio = AudioSegment.from_file(input_file)

    # Cut the audio at the given second
    print("cut_sec:", cut_sec)
    cut_millisec = int(cut_sec * 1000)
    audio_cut = audio[:cut_millisec]

    # Add a 3-second fade out
    fade_duration = 3000
    audio_fade = audio[cut_millisec:]
    audio_fade = audio_fade.fade_out(fade_duration)

    # Concatenate the cut audio and the fade audio
    audio_output = audio_cut + audio_fade

    # Export the output audio file
    audio_output.export(output_file, format='mp3')
    audio_output.export("Testout.mp3", format='mp3')


def add_audio_to_video(video_file, audio_file, output_file):
    # Load video and audio files
    video_clip = VideoFileClip(video_file)
    audio_clip = AudioFileClip(audio_file)

    # Create composite audio clip with both clips
    final_audio_clip = CompositeAudioClip([audio_clip])

    # Set audio clip duration to video clip duration
    final_audio_clip = final_audio_clip.set_duration(video_clip.duration)

    # Add composite audio clip to video clip
    final_video_clip = video_clip.set_audio(final_audio_clip)

    # Write video clip with added audio to output file
    final_video_clip.write_videofile(output_file, audio_codec='aac')


def concat_videos(video1_path, video2_path, video3_path, output_path):
    # Load the three video clips
    video1 = mp.VideoFileClip(video1_path).resize((1080, 1980))
    video2 = mp.VideoFileClip(video2_path).resize((1080, 1980))
    video3 = mp.VideoFileClip(video3_path).resize((1080, 1980))

    # Concatenate the three clips
    final_video = concatenate_videoclips([video1, video2, video3])

    # Write the concatenated clip to a new file
    final_video.write_videofile(output_path, threads=4)


from moviepy.editor import *


def add_logo_and_concat_videos(video1_path, video2_path, video3_path, image_path, x, y, output_path, audio_path):
    """
    Adds an image to each of the three videos at the given x, y position.
    Concatenates the three videos into a single output video.
    Saves the new video to the specified output path.
    """
    # Load the three video clips
    video1 = VideoFileClip(video1_path).resize((1080, 1980))
    video2 = VideoFileClip(video2_path).resize((1080, 1980))
    video3 = VideoFileClip(video3_path).resize((1080, 1980))

    # Load the image and resize if necessary
    image = Image.open(image_path)

    # Convert the image to a clip
    image_clip = ImageClip(np.array(image)).set_duration(video1.duration)

    # Set the position of the image clip
    image_clip = image_clip.set_position((x, y))

    # Add the image clip to each of the three video clips
    video1 = CompositeVideoClip([video1, image_clip])

    image_clip = ImageClip(np.array(image)).set_duration(video2.duration)
    video2 = CompositeVideoClip([video2, image_clip])

    image_clip = ImageClip(np.array(image)).set_duration(video3.duration)
    video3 = CompositeVideoClip([video3, image_clip])

    # Concatenate the three clips
    final_video = concatenate_videoclips([video1, video2, video3])

    # add music/audio
    cut_and_fade_audio(audio_path, audio_path, final_video.duration)
    sleep(1)
    # Load the audio clip
    audio_clip = AudioFileClip(audio_path)

    # Set the duration of the audio clip to match the duration of the final video
    audio_clip = audio_clip.set_duration(final_video.duration)

    # Add the audio to the final video
    final_video = final_video.set_audio(audio_clip)

    # Write the final video to the output path
    final_video.write_videofile(output_path, threads=4, bitrate="5000k", audio_codec="aac", audio_bitrate="256k",
                                preset="medium",
                                ffmpeg_params=["-map", "0:v:0", "-map", "1:a:0", "-c:v", "libx264", "-c:a", "aac",
                                               "-b:a", "256k"])


def resample_video(input_path, output_path):
    # Convert the input video to an uncompressed format
    temp_path = 'temp.avi'
    ffmpeg_command = f'ffmpeg -i "{input_path}" -c:v rawvideo -c:a copy "{temp_path}"'
    os.system(ffmpeg_command)

    # Load the converted video
    video = mp.VideoFileClip(temp_path)

    # Set the new frame rate and resolution
    new_fps = 30
    new_resolution = (1080, 1980)

    # Resample the video
    resampled_video = video.set_fps(new_fps).resize(new_resolution)

    # Write the resampled video to the output path
    resampled_video.write_videofile(output_path, codec='libx264')
    sleep(1)
    os.remove(temp_path)


def img_to_video(input_folder, output_file):
    # Define output video size and frame rate
    video_size = (1080, 1980)
    frame_rate = 1

    # Load all images from the input folder
    image_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if
                   f.endswith('.jpeg') or f.endswith('.png') or f.endswith('.jpg') or f.endswith('.JPEG')]

    # Sort the image files in ascending order by file name
    image_files = sorted(image_files)[:30]

    # Load the images and resize them to the output video size
    resized_images = []

    for image_file in image_files:
        image = Image.open(image_file)
        image = resize_with_padding(image, video_size)  # Assuming you have a function called 'resize_with_padding'
        image_array = np.asarray(image)
        resized_images.append(image_array)

    # Create a clip from the resized images with cross-fade transition
    clip = mp.ImageSequenceClip(resized_images, fps=frame_rate)

    # Write the clip to the output file
    clip.write_videofile(output_file, fps=30, threads=4)


def add_audio_to_video_ffmpeg(video_path, audio_path, output_path):
    """
    Uses FFmpeg to add audio to a video.
    """
    # Run FFmpeg command to merge audio and video
    cmd = ['ffmpeg', '-i', video_path, '-i', audio_path, '-c', 'copy', '-map', '0:v:0', '-map', '1:a:0', '-shortest',
           output_path]
    subprocess.run(cmd)


output_file = os.path.join("output_video.mp4")

try:
    resample_video("src/ev.mp4", "src/ev.mp4")
    os.remove("src/ev.mp4")
    resample_video("src/dv.mp4", "src/dv.mp4")
    os.remove("src/dv.mp4")
except Exception as e:
    print(e)
    pass
# Open file dialog to select Excel file
Tk().withdraw()
excel = filedialog.askopenfilename(initialdir="/", title="Select A File",
                                   filetypes=(("Excel File", "*.xlsx"), ("all files", "*.*")))

# Open folder dialog to select parent folder
parent_folder = filedialog.askdirectory(title="Parent folder")

# Read the Excel file into a DataFrame
df = pd.read_excel(excel)
# Set up ChromeOptions
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("profile-directory=Profile 1")
options.add_argument("--user-data-dir=C:/Users/XYZ/Desktop/_video_sent_bot/chrome-data")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
driver = webdriver.Chrome(options=options)
driver.get("http://web.whatsapp.com")
wait = WebDriverWait(driver, 30)
input('code red')

# Initialize counters for video statistics
total_videos_assigned = 0
total_videos_created = 0
total_videos_sent = 0
total_videos_remaining = 0

sent_video_details = []


# Function to send a video and update statistics
def send_video(phone_number, video_path, name_on_food_parcel):
    global total_videos_sent
    total_videos_sent += 1

    # Open chat window
    webpage = "https://web.whatsapp.com/send?phone={}&source=&data=#".format(phone_number)
    driver.get(webpage)

    try:
        # Wait for document button to load
        document_button = WebDriverWait(driver, 45).until(
            EC.presence_of_element_located((By.XPATH, "//div[@title='Attach']")))
        document_button.click()

        # Select document option
        document_option = WebDriverWait(driver, 45).until(
            EC.presence_of_element_located((By.XPATH, "//input[@accept='*']")))
        document_option.send_keys(video_path)

        # Wait for video to upload
        WebDriverWait(driver, 45).until(EC.presence_of_element_located((By.XPATH, "//span[@data-icon='send']")))

        # Click send button
        send_button = driver.find_element(By.XPATH, "//span[@data-icon='send']")
        send_button.click()

        # Record the time of sending
        sent_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        sent_video_details.append([name_on_food_parcel, phone_number, sent_time])

        # Sleep to avoid sending too quickly
        time.sleep(45)
    except Exception as e:
        print("Error:", str(e))


for i in range(len(df)):
    Donor_Name = df.loc[i, "NAME"]
    Donor_Name = str(Donor_Name)
    number_food_parcels = df.loc[i, "COUNT"]
    name_on_food_parcel = df.loc[i, "NAME_ON_PARCEL"]
    name_on_food_parcel = str(name_on_food_parcel)
    phone_number = df.loc[i, "PHONE_NUMBER"]

    food_parcel_folder = os.path.join(parent_folder, name_on_food_parcel)
    final_video_filename = name_on_food_parcel + ".mp4"
    final_video_folder = os.path.join(parent_folder, "Distribution Video")
    os.makedirs(final_video_folder, exist_ok=True)
    final_video_path = os.path.join(final_video_folder, final_video_filename)

    image_folder = os.path.join(parent_folder, name_on_food_parcel.strip())
    if not os.path.isdir(food_parcel_folder):
        print(f"Folder not found: {food_parcel_folder}")
        continue

    img_to_video(image_folder, output_file)
    resample_video(output_file, output_file)
    generate_tts_audio([
        f"Hello {Donor_Name}, we at XYZ would like to extend our heartfelt gratitude for your generous "
        f"contribution. Your donation of {number_food_parcels} food parcels, On behalf of {name_on_food_parcel}, "
        f"has made a significant impact in the lives of many homeless people in India. Thanks to your support, "
        f"we continue to nourish and uplift those in need, creating a better tomorrow for all. Together, "
        f"we are making a difference, one meal at a time. Thank you! "],
        3)
    mix_audio_files("Music_folder/arrrrrrrrrr.mp3", "output_audio.mp3", -5, 1)
    add_logo_and_concat_videos("src/dvc.mp4", output_file, "src/evc.mp4", "LogoP.png", 0, 0, final_video_path,
                               "mixed.mp3")
    send_video(phone_number, final_video_path, name_on_food_parcel)

    # ... (rest of your code)

    # ...

    # Write video statistics to a separate Excel file
    report_data = {
        "Total videos assigned": [total_videos_assigned],
        "Total Videos Created": [total_videos_created],
        "Total Videos Sent": [total_videos_sent],
        "Total Videos Remaining": [total_videos_remaining]
    }

    report_df = pd.DataFrame(report_data)
    report_excel_file = "video_report.xlsx"
    report_df.to_excel(report_excel_file, index=False)
    print(f"Report generated at: {report_excel_file}")

    # Write sent video details to a separate Excel file
    sent_video_df = pd.DataFrame(sent_video_details, columns=["name_on_food_parcel", "Phone Number", "Sent Time"])
    sent_video_excel_file = "sent_video_details.xlsx"
    sent_video_df.to_excel(sent_video_excel_file, index=False)
    print(f"Sent video details generated at: {sent_video_excel_file}")
    current_directory = os.getcwd()
    print("Current Working Directory:", current_directory)

    print("Process totally completed")
