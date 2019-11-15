import logging
import warnings

import numpy as np
import pandas as pd

'''
Sharpe Ratio

(Portfollio Expected Return - Risk Free Rate) / Portfolio Risk
Expected Return a.k.a Mean
Risk a.k.a Standard Deviation

The Sharpe ratio, also known as the reward-to-variability ratio, is perhaps the most common portfolio management metric. 

The excess return of the portfolio over the risk-free rate is standardized by the risk of the excess of the portfolio return. 

Hypothetically, investors should always be able to invest in government bonds and obtain the risk-free rate of return. 

The Sharpe ratio determines the expected realized return over that minimum. 

Within the risk-reward framework of portfolio theory, higher risk investments should produce high returns. 

As a result, a high Sharpe ratio indicates superior risk-adjusted performance.

'''
class RISK :
      @staticmethod
      def shave(data, size) :
          ret = data.sort_values(['risk']).head(size)
          logging.info(ret.sort_values(['risk']).head(5))
          return ret
      @staticmethod
      def trim(data) :
          desc = data.describe()
          risk =  desc['risk']['75%']
          ret = data[data['risk'] <= risk]
          logging.info(ret.sort_values(['risk']).head(5))
          return ret
      @staticmethod
      def cut(data) :
          desc = data.describe()
          risk =  desc['risk']['25%']
          ret = data[data['risk'] <= risk]
          logging.info(ret.sort_values(['risk']).head(5))
          return ret
class SHARPE :
      @staticmethod
      def shave(data, size) :
          ret = data.sort_values(['sharpe']).tail(size)
          logging.info(ret.sort_values(['sharpe']).head(5))
          return ret
      @staticmethod
      def trim(data) :
          desc = data.describe()
          sharpe =  desc['sharpe']['25%']
          ret = data[data['sharpe'] >= sharpe]
          logging.info(ret.sort_values(['sharpe']).tail(5))
          return ret
      @staticmethod
      def cut(data) :
          desc = data.describe()
          sharpe =  desc['sharpe']['75%']
          ret = data[data['sharpe'] >= sharpe]
          logging.info(ret.sort_values(['sharpe']).tail(5))
          return ret
class RETURNS :
      @staticmethod
      def shave(data, size) :
          ret = data.sort_values(['returns']).tail(size)
          logging.info(ret.sort_values(['returns']).tail(5))
          return ret
      @staticmethod
      def trim(data) :
          desc = data.describe()
          returns =  desc['returns']['25%']
          ret = data[data['returns'] >= returns]
          logging.info(ret.sort_values(['returns']).tail(5))
          return ret
      @staticmethod
      def cut(data) :
          desc = data.describe()
          returns =  desc['returns']['75%']
          ret = data[data['returns'] >= returns]
          logging.info(ret.sort_values(['returns']).tail(5))
          return ret
class BIN :
      @staticmethod
      def descending(data,target) :
          desc = data.describe()
          logging.debug(desc)
          _bin1 =  desc[target]['75%']
          _bin2 =  desc[target]['50%']
          _bin3 =  desc[target]['25%']
          logging.debug((_bin1,_bin2,_bin3))
          bin1 = data[data[target] > _bin1]
          bin2 = data[(data[target] <= _bin1) & (data[target] > _bin2)]
          bin3 = data[(data[target] <= _bin2) & (data[target] > _bin3)]
          bin4 = data[data[target] <= _bin3]
          ret = [ bin1, bin2, bin3, bin4 ]
          ret = filter(lambda x : len(x) > 0, ret)
          return ret

      @staticmethod
      def ascending(data,target) :
          desc = data.describe()
          logging.debug(desc)
          _bin1 =  desc[target]['75%']
          _bin2 =  desc[target]['50%']
          _bin3 =  desc[target]['25%']
          logging.debug((_bin1,_bin2,_bin3))
          bin4 = data[data[target] < _bin3]
          bin3 = data[(data[target] >= _bin3) & (data[target] < _bin2)] 
          bin2 = data[(data[target] >= _bin2) & (data[target] < _bin1)] 
          bin1 = data[data[target] >= _bin1]
          ret = [ bin4, bin3, bin2, bin1 ]
          ret = filter(lambda x : len(x) > 0, ret)
          return ret

class HELPER :
      key_list = ['returns', 'risk','sharpe','len']
      @staticmethod
      def find(data, **kwargs) :
          #logging.debug(kwargs)
          if not isinstance(data,pd.DataFrame) :
             warnings.warn("prices are not in a dataframe {}".format(type(data)), RuntimeWarning)
             data = pd.DataFrame(data)
          target = "period"
          period = kwargs.get(target,0)
          target = "risk_free_rate"
          risk_free_rate = kwargs.get(target,0.02)
          target = "span"
          span = kwargs.get(target,500)
          if period < 0 :
             warnings.warn("period must be positive", RuntimeWarning)
          if span < 0 :
             warnings.warn("span must be positive", RuntimeWarning)
             span = 0
          return HELPER._find(data, risk_free_rate, period, span)

      @staticmethod
      def _find(data, risk_free_rate, period, span) :
          ret = data.pct_change().dropna(how="all")
          _len = len(ret)
          if _len < period :
             return dict(zip(HELPER.key_list, [0, 0, 0,_len]))

          if span == 0 :
             returns, risk = HELPER._findRiskAndReturn(ret)
          else :
             returns, risk = HELPER._findRiskAndReturnSpan(ret,span)
          if isinstance(returns,pd.Series) : returns = returns[0]
          if isinstance(risk,pd.Series) : risk = risk[0]
          if period > 0 :
             returns *= period
             risk *= np.sqrt(period)
          sharpe = 0
          if risk != 0 :
             sharpe = ( returns - risk_free_rate ) / risk
          return dict(zip(HELPER.key_list, [returns, risk, sharpe,_len]))

      @staticmethod
      def _findRiskAndReturn(data) :
          returns = data.mean()
          risk = data.std()
          return returns, risk

      @staticmethod
      def _findRiskAndReturnSpan(data,span) :
          #weigth recent history more heavily that older history
          returns = data.ewm(span=span).mean().iloc[-1]
          risk = data.ewm(span=span).std().iloc[-1]
          return returns, risk

class PORTFOLIO :
      key_list = ['returns', 'risk','sharpe','len']
      @staticmethod
      def find(data, **kwargs) :
          logging.debug(kwargs)
          if not isinstance(data,pd.DataFrame) :
             warnings.warn("prices are not in a dataframe", RuntimeWarning)
             data = pd.DataFrame(data)
          target = "stocks"
          stock_list = kwargs.get(target,['AAPL','GOOG'])
          target = "portfolios"
          portfolios = kwargs.get(target,25000)
          target = "period"
          period = kwargs.get(target,252)
          target = "portfolios"
          portfolios = kwargs.get(target,25000)
          target = "risk_free_rate"
          risk_free_rate = kwargs.get(target,0.02)
          target = "span"
          span = kwargs.get(target,500)
          if portfolios < 0 :
             warnings.warn("portfolios must be positive", RuntimeWarning)
             portfolios = 0
          if period < 0 :
             warnings.warn("period must be positive", RuntimeWarning)
             period = 0
          if span < 0 :
             warnings.warn("span must be positive", RuntimeWarning)
             span = 0
          return PORTFOLIO._find(data, stock_list, portfolios, risk_free_rate, period)


      @staticmethod
      def _find(data, stock_list, num_portfolios, risk_free_rate, period) :
          stocks = filter(lambda x : x in data, stock_list)
          if len(stocks) == 0 :
              return pd.DataFrame(), pd.DataFrame()
          data = data[stocks]
          portfolio_list = PORTFOLIO._process(data, len(stocks), num_portfolios, risk_free_rate, period)

          #convert results array to Pandas DataFrame
          columns = ['returns','risk','sharpe']
          columns += stocks
          results_frame = pd.DataFrame(portfolio_list.T,columns=columns)

          #locate position of portfolio with highest Sharpe Ratio
          max_sharpe = results_frame['sharpe'].idxmax()
          max_sharpe_port = results_frame.iloc[max_sharpe]

          #locate positon of portfolio with minimum risk
          min_vol = results_frame['risk'].idxmin()
          min_vol_port = results_frame.iloc[min_vol]
          return max_sharpe_port, min_vol_port

      @staticmethod
      def _weights(size, num_portfolios) :
          low = 0.1
          high = low + low + (1/size) 
          for i in xrange(num_portfolios):
              #select random weights for portfolio holdings
              #weights = np.array(np.random.random(size))
              weights = np.random.uniform(low=low, high=high, size=size)
              weights = np.array(weights)
              #rebalance weights to sum to 1
              weights /= np.sum(weights)
              #logging.debug(weights)
              yield weights, i

      @staticmethod
      def _sharpe(cov_matrix, mean, period, risk_free_rate, weights) :
          logging.debug((mean, period, risk_free_rate))
          #logging.debug(cov_matrix)
          logging.debug(weights)
          magic = np.dot(cov_matrix, weights)
          magic_number = np.dot(weights.T,magic)

          #calculate return and volatility
          returns = np.sum(mean * weights) * period
          risk = np.sqrt(magic_number) * np.sqrt(period)

          #calculate Sharpe Ratio (return - risk free rate / volatility)
          sharpe = 0
          if risk != 0 : 
             sharpe = ( returns - risk_free_rate ) / risk
          return returns, risk, sharpe

      @staticmethod
      def _process(data, size, num_portfolios, risk_free_rate, period) :
          data.sort_index(inplace=True)
          #convert daily stock prices into daily returns
          returns = data.pct_change()

          #set up array to hold results
          #We have increased the size of the array to hold the weight values for each stock
          ret = np.zeros((3+size,num_portfolios))

          #calculate mean daily return and covariance of daily returns
          mean = returns.mean()
          cov_matrix = returns.cov()
          for weights, i in PORTFOLIO._weights(size, num_portfolios) :
              returns, risk, sharpe = PORTFOLIO._sharpe(cov_matrix, mean, period, risk_free_rate, weights)
              #store results in results array
              ret[0,i] = returns
              ret[1,i] = risk
              ret[2,i] = sharpe
              for j in range(len(weights)):
                  ret[j+3,i] = weights[j]
          return ret

      @staticmethod
      def findWeightedSharpe(data, weights, risk_free_rate=0.02, period=252) :
          if not isinstance(data,pd.DataFrame) :
             warnings.warn("prices are not in a dataframe {}".format(type(data)), RuntimeWarning)
             data = pd.DataFrame(data)

          #calculate mean daily return and covariance of daily returns
          mean = data.mean()
          cov_matrix = data.cov()
          logging.info((weights, mean,cov_matrix))
          logging.info(data.head(2))
          returns, risk, sharpe = PORTFOLIO._sharpe(cov_matrix, mean, period, risk_free_rate, weights)
          ret = dict(zip(['returns', 'risk', 'sharpe'],[returns,risk,sharpe]))
          logging.info(ret)
          return ret

if __name__ == "__main__" :

   import sys
   import logging

   from libCommon import ENVIRONMENT, INI
   from libFinance import STOCK_TIMESERIES

   env = ENVIRONMENT()
   file_list = env.list_filenames('local/historical_prices/*pkl')
   ini_list = env.list_filenames('local/*.ini')

   def prep(*ini_list) :
       ini_list = filter(lambda x : "benchmark" in x , ini_list)
       print ini_list
       for path, section, key, stock_list in INI.loadList(*ini_list) :
           if section == 'Index' : pass
           else : continue
           yield key, stock_list

   log_msg = '%(module)s.%(funcName)s(%(lineno)s) %(levelname)s - %(message)s'
   logging.basicConfig(stream=sys.stdout, format=log_msg, level=logging.DEBUG)

   reader = STOCK_TIMESERIES.init()
   for name, stock_list in prep(*ini_list) :
       for stock in stock_list :
           print (stock,name)
           data = reader.extract_from_yahoo(stock)
           if data is None : continue
           ret = data[['Adj Close']]
           print ret.head(2)
           print ret.tail(2)
           print ret.mean()
           print ret.std()
           print ret.mean()[0]
           print ret.std()[0]
           print HELPER.find(ret,period=252,span=0)
           print HELPER.find(ret,period=252)
           print (stock,name)
