#this code scrapes bill data for Washington alumnae using Python, Selenium, and BeautifulSoup
#then imports it to Google Sheets using Pygsheets
#last updated 07/17/2019 by Camille Kirsch, communications intern

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import pygsheets
import os
import lxml
import re 
import time
from updatesheet import update_sheet, next_available_row

#this function finds the legislator's bill report page for this session
#starting from a stable link that won't change year-to-year
def find_legislator(legislator):
 driver.get("https://app.leg.wa.gov/bi/billsbysponsor")
 driver.maximize_window()
 driver.implicitly_wait(10)
 #time.sleep(2)
 if chamber == "House":
    driver.find_element_by_xpath('//input[@id = "sponsorTypeHouse"]/following-sibling::*[1]').click()
    #time.sleep(2)
    select = Select(driver.find_element_by_id("houseSponsorId"))
    select.select_by_visible_text(legislator)
 elif chamber == "Senate":
    driver.find_element_by_xpath('//input[@id = "sponsorTypeSenate"]/following-sibling::*[1]').click()
    #time.sleep(2)
    select = Select(driver.find_element_by_id("senateSponsorId"))
    select.select_by_visible_text(legislator)  
 driver.find_element_by_xpath('//input[@id = "optReportTypeAllBills"]/following-sibling::*[1]').click()
 driver.find_element_by_id("submit").click()
 time.sleep(5)
 print ("found " + legislator)

#this is the web scraping function; it imports to google docs
def scrape_info(legislator):
 #open the legislator's homepage
 find_legislator(legislator)
 
 #choose to view all bills instead of just first 50
 elem = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "tblBills_length")))
 time.sleep(1)
 driver.find_element_by_xpath('//*[@id="tblBills_length"]/label/select/option[text()="All"]').click()
 
 print("all bills visible")
 
 #Selenium hands the page source to BeautifulSoup
 soup = BeautifulSoup(driver.page_source, 'lxml')
 
 #BeautifulSoup scrapes the bill info 
 all_info = soup.find_all('table', {'id': 'tblBills'})
 all_info = str(all_info)
 
 print ("scraped info")
 
 #Give the HTML table to pandas to put in a dataframe object
 df = pd.read_html(all_info)[0]
 cols = [0,2,3,6]
 df = df.drop(df.columns[cols], axis=1)

 update_sheet(sheet, df) 
 print ("data entered to sheet")


#executable code starts here
path = os.path.abspath("Chromedriver")
driver = webdriver.Chrome(executable_path = path)

#authorize python to access the google spreadsheet using pygsheets
credspath = os.path.abspath("nevada-creds.json")
gc = pygsheets.authorize(service_file=credspath)

#open the google spreadsheet 'Washington'
sh = gc.open('Washington')

#fetch a list of all tabs in the spreadsheet
allsheets = sh.worksheets()
sheetnames = [sheet.title.strip() for sheet in allsheets]
x = 0

#this loops through each legislator one by one, scraping her data and importing it to her tab of the google sheet
for sheet in allsheets:
 #get the name of the tab, assign that as the legislator's name
 legislator = sheetnames[x]
 chamber = sheet.get_value('E1')
 if sheet.get_value('E1'):
  scrape_info(legislator)
 x += 1

print("all done!")
driver.close()
