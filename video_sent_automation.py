import os
import pandas as pd
from tkinter import filedialog
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
import tkinter as tk
from tkinter import filedialog

# Set up ChromeOptions
options = Options()
options.add_argument("profile-directory=Profile 1")
options.add_argument("--user-data-dir=C:/Users/XYZ/Documents/database rm/ABC/chrome-data")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
driver = webdriver.Chrome( options=options)
driver.get("http://web.whatsapp.com")
time.sleep(30)  # wait time to scan the code in seconds
input("code red")


def send_video(phone_number, video_path):
    # Open chat window
    driver.get("https://web.whatsapp.com/send?phone={}".format(phone_number))

    try:
        # Wait for document button to load
        document_button = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//div[@title='Attach']")))
        document_button.click()

        # Select document option
        document_option = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//input[@accept='*']")))
        document_option.send_keys(video_path)

        # Wait for video to upload
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, "//span[@data-icon='send']")))

        # Click send button
        send_button = driver.find_element(By.XPATH, "//span[@data-icon='send']")
        send_button.click()
        time.sleep(15)

    except Exception as e:
        print("Error:", str(e))


# Prompt user to select the Excel file
excel_file = filedialog.askopenfilename(initialdir="/", title="Select A File", filetypes=(("Excel File", "*.xlsx"),
                                                                                          ("All Files", "*.*")))

# Read Excel file with names, numbers, and video paths
df = pd.read_excel(excel_file)

# Create a tkinter window
root = tk.Tk()

# Hide the main window
root.withdraw()

# Ask the user to select the video directory
video_directory = filedialog.askdirectory(title="Select Video Directory")

# Check if a directory was selected
if video_directory:
    # Get the list of video files in the directory in alphabetical order
    video_files = sorted([file for file in os.listdir(video_directory) if file.endswith(".mp4")])

    # Iterate over rows and send videos to recipients
    for index, row in df.iterrows():
        name = row['NAME']
        phone_number = str(row['NUM'])

        if len(phone_number) == 10:
            phone_number = "91" + phone_number

        # Check if video is available for the name in the excel file
        if str(name) + ".mp4" in video_files:
            video_path = os.path.join(video_directory, name + ".mp4")
            video_folder_name = os.path.basename(video_directory)
            send_video(phone_number, video_path)
            print(f"Video for {name} sent to {phone_number}")
        else:
            print(f"No video available for {name} - {phone_number}")

    # Close the driver
    driver.quit()

