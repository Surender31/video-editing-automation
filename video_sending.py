from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time

# Set up ChromeOptions
options = Options()
options.add_argument("profile-directory=Profile 1")
options.add_argument("--user-data-dir=C:/Users/xyz Foundation/Documents/database rm/abc/chrome-data")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(executable_path="chromedriver.exe", options=options)
driver.get("http://web.whatsapp.com")
time.sleep(10)  # wait time to scan the code in second
input("code red")

def send_video(phone_number, video_path):
    # Open chat window
    driver.get("https://web.whatsapp.com/send?phone={}".format(phone_number))

    try:
        # Wait for document button to load
        document_button = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//div[@title='Attach']")))
        document_button.click()

        # Select document option
        document_option = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//input[@accept='*']")))
        document_option.send_keys(video_path)

        # Wait for video to upload
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//span[@data-icon='send']")))

        # Click send button
        send_button = driver.find_element(By.XPATH, "//span[@data-icon='send']")
        send_button.click()
        input('Video sent successfully!')



    except Exception as e:
        print("Error:", str(e))

# Example usage
phone_number = "9999999997"  # Replace with the recipient's phone number
video_path = "C:/Users/xyz/Documents/database rm/abc/Happy Birthday Avaneesh Reddy.mp4"  # Replace with the path to your video file

send_video(phone_number, video_path)

# Close the driver
driver.quit()
