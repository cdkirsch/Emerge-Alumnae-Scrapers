#this code scrapes bill data for Kentucky alumnae using Python, Selenium, and BeautifulSoup
#then imports it to Google Sheets using Pygsheets
#last updated 07/17/2019 by Camille Kirsch, communications intern

from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import pygsheets
import os
import lxml
import re 
from updatesheet import update_sheet, next_available_row

#this is the web scraping function; it imports to google docs
def scrape_info(legislator):
 #open the legislator's homepage
 driver.get(legislator)
 
 #Selenium hands the page source to BeautifulSoup
 soup = BeautifulSoup(driver.page_source, 'lxml')
 
 #BeautifulSoup scrapes the bill info 
 all_info = soup.find('table')
 url_links = all_info.find_all('a')
 urls = [link.get('href') for link in url_links]
 urls = ["https://www.nmlegis.gov/Legislation" + url for url in urls]
 all_info = str(all_info)
 
 #Give the HTML table to pandas to put in a dataframe object
 df = pd.read_html(all_info)[0]
 df['Link to Bill'] = urls

 update_sheet(sheet, df)


#executable code starts here
path = os.path.abspath("Chromedriver")
driver = webdriver.Chrome(executable_path = path)

#authorize python to access the google spreadsheet using pygsheets
credspath = os.path.abspath("nevada-creds.json")
gc = pygsheets.authorize(service_file=credspath)

#open the google spreadsheet 'Kentucky'
sh = gc.open('Kentucky')

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
