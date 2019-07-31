#this code scrapes bill data for Connecticut alumnae using Python, Selenium, and BeautifulSoup
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
import time
from updatesheet import update_sheet, next_available_row

#this function finds the legislator's bill page starting from a stable directory page
def find_legislator(legislator, chamber):
 if chamber == "House":
  driver.get("https://www.cga.ct.gov/asp/menu/hlist.asp");
 elif chamber == "Senate":
  driver.get("https://www.cga.ct.gov/asp/menu/slist.asp");
 driver.implicitly_wait(10)
 time.sleep(2)
 driver.find_element_by_xpath('//a[contains(@href, "name=' + legislator + '")]').click()
 print ("found " + legislator)

#this is the web scraping function; it imports to google docs
def scrape_info(legislator):
 
 find_legislator(legislator,chamber)
 time.sleep(1)
 #Selenium hands the page source to BeautifulSoup
 soup = BeautifulSoup(driver.page_source, 'lxml')
 
 #BeautifulSoup scrapes the bill info 
 all_info = soup.find('table')
 url_links = all_info.find_all('a')
 urls = ["https://www.cga.ct.gov/asp/CGABillStatus/" + link.get('href') for link in url_links]
 all_info = str(all_info).title()
 
 #Give the HTML table to pandas to put in a dataframe object
 df = pd.read_html(all_info)[0]
 df['Link to Bill'] = urls
 df = df.drop(df.columns[2], axis=1)

 update_sheet(sheet, df)


#executable code starts here
path = os.path.abspath("Chromedriver")
driver = webdriver.Chrome(executable_path = path)

#authorize python to access the google spreadsheet using pygsheets
credspath = os.path.abspath("nevada-creds.json")
gc = pygsheets.authorize(service_file=credspath)

#open the google spreadsheet 'Connecticut'
sh = gc.open('Connecticut')

#fetch a list of all tabs in the spreadsheet
allsheets = sh.worksheets()
sheetnames = [sheet.title.strip() for sheet in allsheets]
x = 0

#this loops through each legislator one by one, scraping her data and importing it to her tab of the google sheet
for sheet in allsheets:
 #get the name of the tab, assign that as the legislator's name
 legislator = sheetnames[x]
 chamber = sheet.get_value('E1')
 if chamber:
  scrape_info(legislator)
  print(legislator + " successfully scraped")
 x += 1
  
print("all done!")
driver.close()
