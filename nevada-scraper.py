#this code scrapes bill data for Nevada alumnae using Python, Selenium, and BeautifulSoup
#then imports it to Google Sheets using Pygsheets
#last updated 07/15/2019 by Camille Kirsch, communications intern
 
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import pygsheets
import os

path = os.path.abspath("Chromedriver")
driver = webdriver.Chrome(executable_path = path)

#this is the web scraping function; it imports to google docs
def scrape_info(legislator):
 driver.get(legislator)
 driver.find_element_by_id('billsTabLI').click()
 driver.implicitly_wait(15)
 
 #scrape the bill numbers and store them in a list
 bill_links = driver.find_elements_by_css_selector('#billsTab.tab-pane.active a')
 bill = [link.text.strip() for link in bill_links if len(link.text.strip())>0]
 
 #scrape the bill titles and store them in a list
 summary_links = driver.find_elements_by_css_selector('#billsTab.tab-pane.active span')
 summary = [link.text.strip() for link in summary_links if len(link.text.strip())>0]
 
 #scrape the links to the bills and store them in a list
 url_links = driver.find_elements_by_xpath('//*[@title="Classic Bill Website"]')
 url = [link.get_attribute('href') for link in url_links]

 # Create empty dataframe
 df = pd.DataFrame()

 # Create a column
 df['Bill Number'] = bill
 df['Summary'] = summary
 df['Link to Bill Info'] = url

 #update the appropriate sheet with df, starting at cell B3. 
 sheet.set_dataframe(df,'B3')

#authorize python to access the google spreadsheet using pygsheets
credspath = os.path.abspath("nevada-creds.json")
gc = pygsheets.authorize(service_file=credspath)

#open the google spreadsheet (where 'Maryland' is the name of my sheet)
sh = gc.open('Nevada')

#fetch a list of all tabs in the spreadsheet
allsheets = sh.worksheets()

#this loops through each legislator one by one, scraping her data and importing it to her tab of the google sheet
for sheet in allsheets:
 legislator = sheet.get_value('E1')
 if legislator:
  scrape_info(legislator)
 
driver.close()

