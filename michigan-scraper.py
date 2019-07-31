#this code scrapes bill data for Michigan alumnae using Python, Selenium, and BeautifulSoup
#then imports it to Google Sheets using Pygsheets
#last updated 07/17/2019 by Camille Kirsch, communications intern

#If you're a real software developer reading this, my apologies
#This was my first time coding and my guess is it's pretty messy
#Although I've tried to thoroughly explain my logic via comments

#import the necessary packages
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import pygsheets
import os
import datetime
import lxml

#this is the web scraping function; it imports to google docs
def scrape_info(legislator):
 #open the legislator's sponsored bills page
 driver.get(legislator)
 
 #Selenium hands the page source to BeautifulSoup
 soup = BeautifulSoup(driver.page_source, 'lxml')
 
 #BeautifulSoup scrapes the bill info 
 all_info = soup.find_all('table', {'id': 'frg_executesearch_SearchResults_Results'})
 
 #Give the HTML table to pandas to put in a dataframe object
 df_spon = pd.read_html(str(all_info),header=0)[0]
 
 legislator_cos = sheet.get_value('G1')
 
 #open the legislator's cosponsored bills page
 driver.get(legislator_cos)
 
 #Selenium hands the page source to BeautifulSoup
 soup = BeautifulSoup(driver.page_source, 'lxml')
 
 #BeautifulSoup scrapes the bill info 
 all_info = soup.find_all('table', {'id': 'frg_executesearch_SearchResults_Results'})
 
 #Give the HTML table to pandas to put in a dataframe object
 df_cos = pd.read_html(str(all_info),header=0)[0]

 #concatenate the two dataframes
 df = pd.concat([df_spon, df_cos])
 
 #update the Google sheet with df, starting at first row of latest session (existing session)
 #or at the first empty cell (new session). 
 row = next_available_row(sheet)
 allsessions = sheet.get_values('A1','A'+str(row), returnas='cell', include_tailing_empty_rows = False)
 latestsession = allsessions[-1]
 cutat = str(latestsession[0]).find(" '")
 firstbill = str(latestsession[0])[7:cutat]
 firstbill_loc = 'B'+str(int(firstbill)+1)
 firstbilltxt = sheet.get_value(firstbill_loc)

 if df.iat[0,0] == firstbilltxt:
  sheet.set_dataframe(df,firstbill_loc,copy_head=False)
 elif firstbilltxt == "":
  sheet.set_dataframe(df,firstbill_loc,copy_head=False)
 else:
  today = datetime.datetime.now()
  sheet.update_value('A' + str(row), str(today.year) + ' Session')
  sheet.set_dataframe(df,'B' + str(row+1),copy_head=False)

#this function finds the next available row of a given sheet
def next_available_row(sheet):
    col_b = sheet.get_col(2, include_tailing_empty=False)
    return len(col_b)+2


#executable code starts here
path = os.path.abspath("Chromedriver")
driver = webdriver.Chrome(executable_path = path)

#authorize python to access the google spreadsheet using pygsheets
credspath = os.path.abspath("nevada-creds.json")
gc = pygsheets.authorize(service_file=credspath)

#open the google spreadsheet (where 'Maryland' is the name of my sheet)
sh = gc.open('Michigan')

#fetch a list of all tabs in the spreadsheet
allsheets = sh.worksheets()

#this loops through each legislator one by one, scraping her data and importing it to her tab of the google sheet
for sheet in allsheets:
 #fetch the link to the legislator's homepage from cell E1 of her sheet
 legislator = sheet.get_value('E1')
 #if cell E1 has text in it, run the webscraping function
 if legislator:
  scrape_info(legislator)

driver.close()
