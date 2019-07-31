#this code scrapes bill data for Vermont alumnae using Python, Selenium, and BeautifulSoup
#then imports it to Google Sheets using Pygsheets
#last updated 07/17/2019 by Camille Kirsch, communications intern

from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import pygsheets
import os
import datetime
import lxml
import re 
import time

#this function finds the next available row of a given sheet
def next_available_row(sheet):
    col_b = sheet.get_col(2, include_tailing_empty=False)
    return len(col_b)+2

#this is the web scraping function; it imports to google docs
def scrape_info(legislator):
 #open list of all legislators
 driver.get("https://legislature.vermont.gov/people/all/")
 driver.implicitly_wait(5)
 
 #choose to view all names instead of just first 50
 driver.find_element_by_xpath('//*[@id="people_length"]/label/select/option[text()="All"]').click()
 driver.implicitly_wait(5)
 
 #open the legislator's homepage
 driver.find_element_by_partial_link_text(legislator).click()
 
 #choose to view all legislation instead of just first 50
 driver.find_element_by_xpath('//*[@id="bill-table_length"]/label/select/option[text()="All"]').click()
 driver.implicitly_wait(5)
 
 driver.find_element_by_partial_link_text('Sponsored').click()
 driver.implicitly_wait(5)
 time.sleep(1)
 
 #Selenium hands the page source to BeautifulSoup
 soup = BeautifulSoup(driver.page_source, 'html.parser')
 
 #BeautifulSoup scrapes the bill info 
 all_info = soup.find('table', {'id': 'bill-table'})
 url_links = all_info.find_all('a', {'href': re.compile('/bill.status')})
 urls = ["https://legislature.vermont.gov" + link.text.strip() for link in url_links]
 print(len(urls))
 all_info = str(all_info)
 
 #Give the HTML table to pandas to put in a dataframe object
 df = pd.read_html(all_info)[0]
 print(len(df))
 df['Link'] = urls

 #update the Google sheet with df, starting at first row of latest session (existing session)
 #or at the first empty cell (new session). 
 row = next_available_row(sheet)
 allsessions = sheet.get_values('A1','A'+str(row), returnas='cell', include_tailing_empty_rows = False)
 latestsession = allsessions[-1]
 cutat = str(latestsession[0]).find(" '")
 firstbill = str(latestsession[0])[7:cutat]
 firstbill_loc = 'B'+str(int(firstbill)+1)
 firstbilltxt = sheet.get_value(firstbill_loc)

 if df.iat[0,1] == firstbilltxt:
  sheet.set_dataframe(df,firstbill_loc,copy_head=False)
 elif firstbilltxt == "":
  sheet.set_dataframe(df,firstbill_loc,copy_head=False)
 else:
  today = datetime.datetime.now()
  sheet.update_value('A' + str(row), str(today.year) + ' Session')
  sheet.set_dataframe(df,'B' + str(row+1),copy_head=False)


#executable code starts here
path = os.path.abspath("Chromedriver")
driver = webdriver.Chrome(executable_path = path)

#authorize python to access the google spreadsheet using pygsheets
credspath = os.path.abspath("nevada-creds.json")
gc = pygsheets.authorize(service_file=credspath)

#open the google spreadsheet 'New Mexico'
sh = gc.open('Vermont')

#fetch a list of all tabs in the spreadsheet
allsheets = sh.worksheets()
sheetnames = [sheet.title.strip() for sheet in allsheets]
x = 0

#this loops through each legislator one by one, scraping her data and importing it to her tab of the google sheet
for sheet in allsheets:
 #get the name of the tab, assign that as the legislator's name
 legislator = sheetnames[x]
 if sheet.get_value('E1'):
  scrape_info(legislator)
 x += 1
driver.close()
