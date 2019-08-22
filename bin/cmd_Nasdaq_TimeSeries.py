#!/usr/bin/python

import logging

from libCommon import STOCK_TIMESERIES, NASDAQ

'''
   Web Scraper
   Use RESTful interface to download stock and fund stock market prices for the past 10 years
   Store as pkl files
'''
def main(local) :
    try :
        _main(local)
    except Exception as e :
        logging.error(e, exc_info=True)

def _main(local) :
    reader = STOCK_TIMESERIES.init()
    nasdaq = NASDAQ.init()

    for stock in nasdaq() :
        filename = '{}/historical_prices/{}.pkl'.format(local,stock)
        ret = reader.extract_from_yahoo(stock)
        STOCK_TIMESERIES.save(filename, stock, ret)

if __name__ == "__main__" :
   import os,sys
   from libCommon import TIMER

   pwd = os.getcwd()

   dir = pwd.replace('bin','log')
   name = sys.argv[0].split('.')[0]
   log_filename = '{}/{}.log'.format(dir,name)
   log_msg = '%(module)s.%(funcName)s(%(lineno)s) %(levelname)s - %(message)s'
   logging.basicConfig(filename=log_filename, filemode='w', format=log_msg, level=logging.INFO)

   local = pwd.replace('bin','local')

   logging.info("started {}".format(name))
   elapsed = TIMER.init()
   main(local)
   logging.info("finished {} elapsed time : {} ".format(name,elapsed()))

