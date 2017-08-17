# -*- coding: utf-8 -*-

import os
import shutil
import unicodedata
import webbrowser
from datetime import datetime

import requests
from wox import Wox,WoxAPI
from bs4 import BeautifulSoup

URL = 'https://services2.hdb.gov.sg/webapp/BB24APPT1/WelcomeDate.jsp'
link = 'https://services2.hdb.gov.sg/webapp/SX05AWSPCP/SX05PSPCPLogin.jsp'

def full2half(uc):
    """Convert full-width characters to half-width characters.
    """
    return unicodedata.normalize('NFKC', uc)


class Main(Wox):
  
    def request(self,url,form):
	#get system proxy if exists
        if self.proxy and self.proxy.get("enabled") and self.proxy.get("server"):
	    proxies = {
		"http":"http://{}:{}".format(self.proxy.get("server"),self.proxy.get("port")),
		"https":"http://{}:{}".format(self.proxy.get("server"),self.proxy.get("port"))
	    }
	    return requests.get(url,proxies = proxies)
	return requests.post(url, form)
			
    def query(self, param):
        p = param.strip()
        now = datetime.now()
        date = now.strftime('%Y%m')
        
        if p == 'n':
            if now.month < 12:
                date = now.replace(month=now.month+1).strftime('%Y%m')
            else:
                date = now.replace(year=now.year+1, month=1).strftime('%Y%m')
        elif p == 'nn':
            if now.month < 11:
                date = now.replace(month=now.month+2).strftime('%Y%m')
            else:
                date = now.replace(year=now.year+1, month=1).strftime('%Y%m')

	r = self.request(URL, {'date':date})
	bs = BeautifulSoup(r.content, 'html.parser')
	tds = bs.select("table td[style]")

	result = []
	for td in tds:
            sty = td['style']

            if "009e73" in sty:
                title = td.find('span').text
            
                item = {
                    'Title': "There are slots in %s%s" % (date,full2half(title)),
                    'IcoPath': os.path.join('img', 'hdb2app.png'),
                    'JsonRPCAction': {
                        'method': 'open_url',
                        'parameters': [link]
                    }
                }
                result.append(item)
        if not result:
            result.append({
                    'Title': 'No Slot in month: %s' % date
                })
            
	return result
    
    def open_url(self, url):
	webbrowser.get("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s").open(url)

if __name__ == '__main__':
    Main()
