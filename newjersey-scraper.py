#this code scrapes bill data for New Jersey alumnae using Python, Selenium, and BeautifulSoup
#then imports it to Google Sheets using Pygsheets
#last updated 07/17/2019 by Camille Kirsch, communications intern

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
 #open the legislator's homepage
 driver.get(legislator)
 
 #click on "List of Bills Sponsored by Assemblywoman"
 driver.find_element_by_xpath('/html/body/div/table/tbody/tr[2]/td[2]/table/tbody/tr[8]/td[4]/font/a').click()
 driver.implicitly_wait(5)
 
 summaries = []
 bills = []
 
 #BS scrapes info from the page, then clicks on each subsequent page
 #loop stops when there are no more pages to click on 
 while driver.find_elements_by_xpath('//a[@href="javascript:NextRecords()"]'): 
  #Selenium hands the page source to BeautifulSoup
  soup = BeautifulSoup(driver.page_source, 'lxml')
  #BeautifulSoup finds bill numbers and urls 
  bill_links = soup.find_all(title="View Detail Bill Information")
  bills = bills + [link.text.strip() for link in bill_links]
  #BS finds bill summaries
  summary_links = soup.find_all("font",color="maroon",size="2")
  summaries = summaries + [link.text.strip() for link in summary_links]
  #go to next page of results
  driver.find_element_by_xpath('//a[@href="javascript:NextRecords()"]').click()
 
 #Do it all one last time to get data on the last page  
 soup = BeautifulSoup(driver.page_source, 'lxml')
 bill_links = soup.find_all(title="View Detail Bill Information")
 bills = bills + [link.text.strip() for link in bill_links]
 summary_links = soup.find_all("font",color="maroon",size="2")
 summaries = summaries + [link.text.strip() for link in summary_links]
  
 
 #Create a pandas data frame and put the bill numbers and summaries in it
 df = pd.DataFrame()
 df["Bill Number"]=bills
 df["Summary"]=summaries
 
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

#opens the 'New Jersey' google spreadsheet
sh = gc.open('New Jersey')

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
