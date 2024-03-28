"""last message - without group condition"""

from tkinter import *
from tkinter import filedialog
import tkinter as tk
from selenium import webdriver
from selenium.common.exceptions import (NoSuchElementException,
                                        StaleElementReferenceException,ElementClickInterceptedException,TimeoutException)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from time import sleep, time
import random
import pandas
from tkinter import simpledialog
from tkinter.messagebox import askyesno
#pip install webdriver-manager


options = Options()
options.add_argument("profile-directory=Profile 1")
options.add_argument("--user-data-dir=C:/Users/xyz/Documents/database rm/abc/chrome-data")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(executable_path="chromedriver.exe", options=options)
driver.get("http://web.whatsapp.com")
sleep(10)  # wait time to scan the code in second
input("code red")



element = WebDriverWait(driver, 10).until(
    lambda x: driver.find_element(By.XPATH,'//*[@id="side"]/div[1]/div/div/div[2]/div/div[2]'))



def element_presence(by, xpath, time):
  element_present = EC.presence_of_element_located((By.XPATH, xpath))
  WebDriverWait(driver, time).until(element_present)


def send_photo(phone_no, img_dir, phototext):

  try:
    driver.get("https://web.whatsapp.com/send?phone={}&source=&data=#".format(phone_no))

    element = WebDriverWait(driver, 10).until(
      lambda x: driver.find_element_by_css_selector("span[data-icon='clip']"))

    clip = driver.find_element_by_css_selector("span[data-icon='clip']")
    clip.click()

    photobut = driver.find_element_by_css_selector("input[type='file']")
    photobut.send_keys(img_dir)

    #TextBox = 'role="textbox"'
    element = WebDriverWait(driver, 10).until(
      lambda x: driver.find_element_by_xpath('//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]/p'))

    ptext = driver.find_element_by_xpath('//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]/p')

    ptext.send_keys(phototext)





    #picture send button = data-icon="send"
    send = element = WebDriverWait(driver, 10).until(lambda x: driver.find_element_by_xpath(
        '//*[@id="app"]/div/div/div[2]/div[2]/span/div/span/div/div/div[2]/div/div[2]/div[2]/div/div/span'))
    send = driver.find_element_by_xpath( '//*[@id="app"]/div/div/div[2]/div[2]/span/div/span/div/div/div[2]/div/div[2]/div[2]/div/div/span')
    send.click()

  except TypeError:
    pass

def send_whatsapp_msg(phone_no, text):
  driver.get("https://web.whatsapp.com/send?phone={}".format(phone_no))
  try:
    driver.switch_to.alert().accept()
  except Exception as e:
    pass

excel = filedialog.askopenfilename(initialdir="/", title="Select A File", filetypes=(("Excel File", "*.xlsx"),
                                                                                       ("all files", "*.*")))
application_window = tk.Tk()
text = answer = simpledialog.askstring("Input", "Input Whatsapp Message",
                                parent=application_window)

photoyn = askyesno("Sending Photo", "Do you want to add Photo?")
if photoyn == True:
  img_dir = filedialog.askopenfilename(initialdir="/", title="Select A File", filetypes=(("all File", "*.*"),
                                                                                       ("all files", "*.*")))

df = pandas.read_excel(excel)
print(df)

for i in range(len(df)):
  name = (df.loc[i, "NAME"])
  no = (df.loc[i, "NUM"])

  textcus = text.replace("{DONOR}",name)

  no = str(no)
  if len(no) == 10:
      no = ("91" + no)


  if photoyn == True:
    send_photo(no, img_dir,textcus)
  else:
    send_whatsapp_msg(no,textcus)


sleep(60)
exit()


