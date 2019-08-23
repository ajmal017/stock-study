try:
    from functools import lru_cache
except ImportError:
    from backports.functools_lru_cache import lru_cache

try:
    import urlparse
    from urllib import urlencode
except: # For Python 3
    import urllib.parse as urlparse
    from urllib.parse import urlencode

import logging
import requests
import re
from bs4 import BeautifulSoup
from json import load

'''
https://financialmodelingprep.com/developer/docs/
'''
class WEB_UTIL(object) :
      @staticmethod
      def invoke_url(url,headers=None, raw=False) :
          ret = None
          try :
              ret = WEB_UTIL._invoke_url(url,headers,raw)
          except Exception as e : logging.error(e, exc_info=True)
          return ret
      @staticmethod
      def json(url,headers=None) :
          ret = None
          try :
              ret = WEB_UTIL._base_invoke(url,headers)
          except Exception as e : logging.error(e, exc_info=True)
          return ret.json()
      @staticmethod
      def _invoke_url(url,headers=None, raw=False) :
        ret = WEB_UTIL._base_invoke(url,headers)
        if not raw : ret = ret.text
        else : ret = ret.content
        return ret
      @staticmethod
      def _base_invoke(url,headers=None) :
        if headers is not None :
          ret = requests.get(url, headers=headers)        
        else :
          ret = requests.get(url)
        if ret.status_code != 200 :
           msg = "{} {}".format(ret.status_code,url)
           logging.error(msg)
        return ret
      @staticmethod
      def format_as_soup(url_response, raw=False) :
        ret = BeautifulSoup(url_response,'lxml')
        if not raw : 
          for script in ret(["script", "style"]):
                script.extract() # Remove these two elements from the BS4 object
        return ret

class YAHOO_PROFILE() :
      url = "https://finance.yahoo.com/quote/{0}/profile?p={0}"
      def __call__(self, stock) :
          ret = YAHOO_PROFILE.get(stock)
          logging.debug(ret)
          return ret

      @staticmethod
      def get(stock) :
          url = YAHOO_PROFILE.url.format(stock)
          response = WEB_UTIL.invoke_url(url)
          soup = WEB_UTIL.format_as_soup(response)
          ret = PROFILE_PARSE.parse(soup)
          ret['Stock'] = stock
          logging.info(ret)
          return ret

class FINANCEMODELLING_STOCK_LIST() :
      url = "https://financialmodelingprep.com/api/v3/company/stock/list"
      def __call__(self, stock) :
          ret = FINANCEMODELLING_STOCK_LIST.get(stock)
          logging.debug(ret)
          return ret

      @staticmethod
      def get() :
          url = FINANCEMODELLING_STOCK_LIST.url
          response = WEB_UTIL.json(url)
          target = "symbolsList"
          ret = response.get(target,{})
          logging.info(ret)
          return ret

class FINANCEMODELLING_INDEX() :
      url = "https://financialmodelingprep.com/api/v3/majors-indexes"
      def __call__(self, stock) :
          ret = FINANCEMODELLING_INDEX.get()
          logging.debug(ret)
          return ret

      @staticmethod
      def get() :
          url = FINANCEMODELLING_INDEX.url
          response = WEB_UTIL.json(url)
          target = "majorIndexesList"
          ret = response.get(target,{})
          logging.info(ret)
          return ret

class FINANCEMODELLING_PROFILE() :
      url = "https://financialmodelingprep.com/api/v3/company/profile/{0}"
      def __call__(self, stock) :
          ret = FINANCEMODELLING_PROFILE.get(stock)
          logging.debug(ret)
          return ret

      @staticmethod
      def get(stock) :
          url = FINANCEMODELLING_PROFILE.url.format(stock)
          response = WEB_UTIL.json(url)
          target = "profile"
          ret = response.get(target,{})
          ret['Stock'] = stock
          logging.info(ret)
          return ret

class PROFILE_PARSE() :
      def __call__(self, soup) :
          return PROFILE_PARSE.parse(soup)
      @staticmethod
      def parse(soup) :
          if soup is None : return {}
          if soup.body is None : return {}
          span_list = soup.body.findAll('span')
          data = []
          for span in span_list :
              data.append(span.text)
          if len(data) == 0 :
             return {}
          while True :
                if data[0] == 'Sector' :
                   break
                if data[0] == 'Category' :
                   break
                data = data[1:]
                if len(data) == 0 :
                   return {}
          logging.debug(data)
          key_list = data[0:10:2]
          value_list = data[1:10:2]
          ret = dict(zip(key_list,value_list))
          logging.debug(ret)
          return ret

if __name__ == "__main__" :
   from multiprocessing import Pool
   def sync(stock):
       return YAHOO_PROFILE.get(stock)

   def worker(pool_size, *stock_list):
       pool = Pool(pool_size)
       logging.debug(stock_list)
       ret = pool.map(sync,stock_list)
       return ret

   reader = YAHOO_PROFILE()
   reader = FINANCEMODELLING_PROFILE()

   ret_list = FINANCEMODELLING_STOCK_LIST.get()
   for ret in ret_list :
       print ret
   stock_list = ['AAPL','GOOG','SPY', 'SRCpA','SRC-A', 'SRC$A', 'SRCA']
   print worker(5,*stock_list)
   for stock in stock_list :
       print stock
       ret = reader(stock)
       print ret
   for index in FINANCEMODELLING_INDEX.get() :
       print index

