
from tkinter import *
from tkinter import filedialog, messagebox
import tkinter as tk
from selenium import webdriver
from selenium.common.exceptions import (NoSuchElementException,
                                        StaleElementReferenceException,ElementClickInterceptedException,TimeoutException)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from time import sleep
import random
import pandas
from tkinter import simpledialog
from tkinter.messagebox import askyesno
#pip install webdriver-manager

global debug
debug = True

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
    lambda x: driver.find_element(By.XPATH, '//*[@id="side"]/div[1]/div/div/div[2]/div/div[2]'))

####################### GET SQL #############################
import mysql.connector
from datetime import date, timedelta
mydb = mysql.connector.connect(
    host="166.62.27.182",
    user="Testing1",
    password="xyz@123",
    database="xyzWhatsapp"
)

mycursor = mydb.cursor()
today = date.today()
fifteen_days_back = today - timedelta(days = 15)

get_sql = f"SELECT w_number FROM 15_days WHERE date_created >= '{fifteen_days_back}' AND date_created <= '{today}'".format(fifteen_days_back=fifteen_days_back,today=today)
mycursor.execute(get_sql)
myresult = mycursor.fetchall()

global skipped
skipped = 0

block_sql = "SELECT w_number FROM blocklist "
mycursor.execute(block_sql)
block_list = mycursor.fetchall()

if mycursor:
  mycursor = None

###############

def update_15days(name, no):
  mydb = mysql.connector.connect(
    host="166.62.27.182",
    user="Testing1",
    password="xyz@123",
    database="xyzWhatsapp"
  )
  mycursor = mydb.cursor()
  sql = "INSERT INTO `15_days`(`name`, `w_number`,`date_created`) VALUES ('{name}','{no}','{date}')".format(name=name, no=no, date=today)
  mycursor.execute(sql)
  mydb.commit()
  print(mycursor.rowcount, "record(s) updated")

def dbcheck(no):
  global skipped
  for result in myresult:
    if no in result:
      print("MESSAGE SENT WITHIN 15 days THEREFORE SKIPPED")
      skipped = skipped + 1
      return True

  for block in block_list:
    if no in block:
      print("BLOCKLISTED THEREFORE SKIPPED")
      skipped = skipped + 1
      return True

  else:
    return False

def element_presence(by, xpath, time):
  element_present = EC.presence_of_element_located((By.XPATH, xpath))
  WebDriverWait(driver, time).until(element_present)

def send_photo(phone_no, img_dir, phototext):

  try:
    webpage = "https://web.whatsapp.com/send?phone={}&source=&data=#".format(phone_no)
    if debug == True: print(webpage)
    driver.get(webpage)

    element = WebDriverWait(driver, 10).until(
      lambda x: driver.find_element(By.CSS_SELECTOR,"span[data-icon='clip']"))

    clip = driver.find_element(By.CSS_SELECTOR,"span[data-icon='clip']")
    clip.click()

    photobut = driver.find_element(By.CSS_SELECTOR,"input[type='file']")
    photobut.send_keys(img_dir)

    #TextBox = 'role="textbox"'
    element = WebDriverWait(driver, 10).until(
      lambda x: driver.find_element(By.XPATH,'//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]/p'))
                                            #there
    ptext = driver.find_element(By.XPATH,'//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]/p')
    ptext.send_keys(phototext)


    #picture send button = data-icon="send"
    send = element = WebDriverWait(driver, 10).until(
      lambda x: driver.find_element(By.XPATH,
        '//*[@id="app"]/div/div/div[2]/div[2]/span/div/span/div/div/div[2]/div/div[2]/div[2]/div/div/span'))
    send = driver.find_element(By.XPATH,
      '//*[@id="app"]/div/div/div[2]/div[2]/span/div/span/div/div/div[2]/div/div[2]/div[2]/div/div/span')
    send.click()

  except TypeError:
    pass

def send_whatsapp_msg(phone_no, text):
  driver.get("https://web.whatsapp.com/send?phone={}".format(phone_no))
  try:
    driver.switch_to.alert().accept()
  except Exception as e:
    pass



  try:
    element_presence(By.XPATH, '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]/p', 40)
    txt_box = driver.find_element(By.XPATH,'//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]/p'
                                  )
    txt_box.click()
    txt_box.send_keys(text)
    txt_box.send_keys("\n")

  except Exception as e:
    print(e)

  sleep(random.randint(10,40))

excel = filedialog.askopenfilename(initialdir="/", title="Select A File", filetypes=(("Excel File", "*.xlsx"),
                                                                                       ("all files", ".")))

text = answer = simpledialog.askstring("Input", "Input Whatsapp Message")

photoyn = askyesno("Sending Photo", "Do you want to add Photo?")
if photoyn == True:
  img_dir = filedialog.askopenfilename(
        title="Select Video File",
        filetypes=(("Video Files", ".mp4 *.avi"), ("All Files", ".*"))
    )

df = pandas.read_excel(excel)


for i in range(len(df)):
  name = (df.loc[i, "NAME"])
  no = (df.loc[i, "NUM"])
  textcus = text.replace("{DONOR}", name)

  no = str(no)
  if len(no) == 10:
      no = ("91" + no)

  if dbcheck(no) == True:
    skipped = skipped + 1
    continue

  if photoyn == True:
    send_photo(no, img_dir,
               textcus)
    sleep(random.randint(3, 7))
  else:
    send_whatsapp_msg(no,textcus)
  try:
    update_15days(name,no)
  except mysql.connector.errors.OperationalError as me:
    print(me)
    print("TRYING AGAIN TO UPDATE MYSQL")
    sleep(3)
    update_15days(name, no)

  print("TOTAL SKIPPED:", skipped)
  sleep(10)

#messagebox.showinfo("TOTAL SKIPPED:", skipped)
exit()
