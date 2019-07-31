#this code scrapes bill data for Pennsylvania alumnae using Python, Selenium, and BeautifulSoup
#then imports it to Google Sheets using Pygsheets
#last updated 07/18/2019 by Camille Kirsch, communications intern

from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import pygsheets
import os
import datetime
import lxml
import re 
import time 
import requests

headers = {
  'User-Agent' : 'Bill Scraper for Emerge America (kirsch@emergeamerica.org)'
  }

def add_bill_summary_tooltip(s, session_year, session_ind, bill_body, bill_type, bill_no):
    url = 'https://www.legis.state.pa.us/cfdocs/cfc/GenAsm.cfc?returnformat=plain'
    data = { 'method' : 'GetBillSummaryTooltip',
            'SessionYear' : session_year,
            'SessionInd' : session_ind,
            'BillBody' : bill_body,
            'BillType' : bill_type,
            'BillNo' : bill_no,
            'IsAjaxRequest' : '1'
            }

    r = s.get(url, params = data)
    soup = BeautifulSoup(r.content, 'lxml')
    tooltip = soup.select_one('.ToolTip-BillSummary-ShortTitle')
    if tooltip is not None:
        tooltip = tooltip.text.strip()
    return tooltip

#this is the web scraping function; it imports to google docs
def scrape_info(legislator):
 #open the legislator's homepage
 driver.get(legislator)
 
 #open the legislator's sponsored bills page
 driver.find_element_by_partial_link_text("sponsored").click()
 
 #Selenium hands the page source to BeautifulSoup
 soup = BeautifulSoup(driver.page_source, 'lxml')
 
 #BeautifulSoup scrapes the bill info 
 bill_links = soup.find_all('a', {'id': re.compile('Bill')})
 summaries = []
 bill_numbers = [link.text.strip() for link in bill_links]
 bill_urls = ["https://www.legis.state.pa.us" + link.get('href') for link in bill_links]

 #add_bill_summary_tooltip('#Bill_1',2019,0,'S','B','0012')
 with requests.Session() as s:
    r = s.get(legislator)
    tooltips = {item.select_one('a').text:item.select_one('script').text[:-1] for item in soup.select('.DataTable td:has(a)')}
    p = re.compile(r"'(.*?)',(.*),(.*),'(.*)','(.*)','(.*)'")
    for bill in tooltips:
        arg1,arg2,arg3,arg4,arg5,arg6 = p.findall(tooltips[bill])[0]
        tooltips[bill] = add_bill_summary_tooltip(s, arg2, arg3,arg4,arg5,arg6)
        summaries = summaries + [tooltips[bill]]
 
 df = pd.DataFrame()
 df['Bill Number'] = bill_numbers
 df['Summary'] = summaries 
 df['Link'] = bill_urls
 
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
  
 #pause for 5 seconds to comply with PA rules as stated in robots.txt
 time.sleep(5)

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

#open the google spreadsheet (where 'Pennsylvania' is the name of my sheet)
sh = gc.open('Pennsylvania')

#fetch a list of all tabs in the spreadsheet
allsheets = sh.worksheets()

#this loops through each legislator one by one, scraping her data and importing it to her tab of the google sheet
for sheet in allsheets:
 #fetch the link to the legislator's homepage from cell E1 of her sheet
 legislator = sheet.get_value('F1')
 #if cell E1 has text in it, run the webscraping function
 if legislator:
  scrape_info(legislator)

driver.close()
