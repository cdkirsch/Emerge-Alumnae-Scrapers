#this code scrapes bill data for Colorado alumnae using Python, Selenium, and BeautifulSoup
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

#this function finds the next available row of a given sheet
def next_available_row(sheet):
    col_b = sheet.get_col(2, include_tailing_empty=False)
    return len(col_b)+2

#this is the web scraping function; it imports to google docs
def scrape_info(legislator):
 #open the legislator's homepage
 driver.get(legislator)
 
 #Selenium hands the page source to BeautifulSoup
 soup = BeautifulSoup(driver.page_source, 'lxml')
 
 #BeautifulSoup scrapes the bill info on page 1
 bill_numbers = soup.find_all("div",{'class': re.compile("bill-number")})
 bills = [link.find_next("div").text.strip() for link in bill_numbers]
 url_links = soup.find_all('h4',{'class': 'node__title node-title'})
 urls = [link.find_next("a") for link in url_links]
 titles = [link.text.strip() for link in urls]
 urls = ["https://leg.colorado.gov" + url.get('href') for url in urls]
 summaries = soup.find_all(string=re.compile("Concerning"))
 sponsors = soup.find_all(string=re.compile("Sponsors:"))
 sponsors = [link.find_next().text.strip() for link in sponsors]
 status = soup.find_all(string=re.compile("Last Action:"))
 status = [link.find_next().text.strip() for link in status]
 
 #Give the HTML table to pandas to put in a dataframe object
 df = pd.DataFrame()
 df['Bill Number'] = bills
 df['Title'] = titles
 df['Sponsor Type'] = "Prime Sponsor"
 df['Summary'] = summaries
 df['Link'] = urls
 df['Status'] = status
 df['Sponsors'] = sponsors

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

#open the google spreadsheet 'Colorado'
sh = gc.open('Colorado')

#fetch a list of all tabs in the spreadsheet
allsheets = sh.worksheets()

#this loops through each legislator one by one, scraping her data and importing it to her tab of the google sheet
for sheet in allsheets:
 #fetch the link to the legislator's homepage from cell E1 of her sheet
 legislator = sheet.get_value('E1')
 #if cell E1 has text in it, run the webscraping function
 if legislator:
  scrape_info(legislator)
  print(sheet.title.strip() + " successfully scraped")

print("all done!")

driver.close()
