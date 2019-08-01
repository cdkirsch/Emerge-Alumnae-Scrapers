#this code scrapes bill data for Maryland alumnae using Python, Selenium, and BeautifulSoup
#then imports it to Google Sheets using Pygsheets
#last updated 07/17/2019 by Camille Kirsch, communications intern

from selenium import webdriver
from bs4 import BeautifulSoup
import re
import os
import time
import pandas as pd
import numpy as np
import pygsheets
import lxml
from updatesheet import update_sheet, next_available_row

def scrape_info(legislator):
 driver.get(legislator)
 soup = BeautifulSoup(driver.page_source, 'lxml')
 all_info = soup.find("table", {'class': 'table table-dark table-borderless table-striped'})
 df = pd.read_html(str(all_info))[0]
 df = df.drop(df.columns[0], axis = 1)
 #billnumbers = df[1].tolist()
 #urls = ["https://malegislature.gov/Bills/191/" + (elem - ".") for elem in billnumbers]
 urls = [elem.get('href') for elem in all_info.find_all("a", href=True)]
 urls = list(dict.fromkeys(urls))
 urls = ["https://malegislature.gov" + elem for elem in urls]
 df['Links'] = urls
 print(sheet.title + " successfully scraped")
 
 update_sheet(sheet, df)
 print("sheet updated")
 
#executable code starts here
path = os.path.abspath("Chromedriver")
driver = webdriver.Chrome(executable_path = path)

#authorize python to access the google spreadsheet using pygsheets
credspath = os.path.abspath("nevada-creds.json")
gc = pygsheets.authorize(service_file=credspath)

#open the google spreadsheet 'Massachusetts'
sh = gc.open('Massachusetts')

#fetch a list of all tabs in the spreadsheet
allsheets = sh.worksheets()

#this loops through each legislator one by one, scraping her data and importing it to her tab of the google sheet
for sheet in allsheets:
 #fetch the link to the legislator's homepage from cell E1 of her sheet
 legislator = sheet.get_value('E1')
 #if cell E1 has text in it, run the webscraping function
 if legislator:
  scrape_info(legislator)

print("all done!")
driver.close()