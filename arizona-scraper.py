#this code scrapes bill data for Arizona alumnae using Python, Selenium, and BeautifulSoup
#then imports it to Google Sheets using Pygsheets
#last updated 07/30/2019 by Camille Kirsch, communications intern

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

def find_legislator(legislator):
 driver.get("https://www.azleg.gov/MemberRoster/")
 driver.implicitly_wait(10)
 driver.find_element_by_partial_link_text(legislator).click()
 print ("found " + legislator)

#this is the web scraping function; it imports to google docs
def scrape_info(legislator):
 find_legislator(legislator)
 time.sleep(2)
 
 #Selenium hands the page source to BeautifulSoup
 soup = BeautifulSoup(driver.page_source, 'lxml')
 
 #BeautifulSoup scrapes the bill info 
 all_info = soup.find('table', {'id': 'bills-table'})
 if all_info == None:
    all_info = soup.find('table', {'id': 'search-results-table'})
 url_links = all_info.find_all('a')
 urls = [link.get('href') for link in url_links]
 all_info = str(all_info)
 
 #Give the HTML table to pandas to put in a dataframe object
 df = pd.read_html(all_info)[0]
 spontype = df['Sponsor Type']
 clearspontype = []
 for elem in spontype: 
  if elem == "C": newelem = "Cosponsor"; 
  elif elem == "P*": newelem = "Prime Prime"; 
  elif elem == "P": newelem = "Prime";
  clearspontype = clearspontype + [newelem]
 df['Sponsor Type'] = clearspontype
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

#open the google spreadsheet 'Arizona'
sh = gc.open('Arizona')

#fetch a list of all tabs in the spreadsheet
allsheets = sh.worksheets()
sheetnames = [sheet.title.strip() for sheet in allsheets]
x = 0

#this loops through each legislator one by one, scraping her data and importing it to her tab of the google sheet
for sheet in allsheets:
 #get the name of the tab, assign that as the legislator's name
 legislator = sheetnames[x]
 chamber = sheet.get_value('E2')
 if sheet.get_value('E2'):
  scrape_info(legislator)
  print(legislator + " successfully scraped")
 x += 1

print("all done!")
driver.close()
