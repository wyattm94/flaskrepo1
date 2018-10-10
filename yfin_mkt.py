# -*- coding: utf-8 -*-
"""
Yahoo Finance Web Scraping Module (Part of Master Module Development)
Current Module Includes:
	- Fetch OHLC + Volume + Adjusted Close Equity/ETF Prices/Index Values (Time Period + d/w/m freq)
	- Fetch Dividend Data + Split Data (*Splits NOT implemented here currently)
	- Wrapper: 
		> Return full dictionary of all data (dict of lists/np arrays)
		> Plot Constructor
		> Comparision Plot constructed (normalized --> growth from base 0 (ideally at same t, can handle differences)
		> More to be added...
		> Additional Scripts for other data sourcing/app functionalities are also in development...
		> Also, these functions are part of a proprietary Fund Development project and as such are not to be copied, reproduced or modified in any way without explict permission by root dev Wyatt Marciniak (jackrabbit). They are being utilized here to test their effectiveness as the remaining development is completed and converted across multiple source languages for Sentient Asset Management. Contact the Author/Maintainer for any concerns, questions are feedback. Thank you.

@Author: Wyatt Marciniak (jackrabbit)
@Maintainer: Wyatt Marciniak <wyattm94@gmail.com> .. <jackrabbit@...>

"""

import time
import io
import base64
import datetime as dt
import requests as req
import numpy as np
import pandas as pd
import scipy.stats as ss
import matplotlib.pyplot as plt
#from bs4 import BeautifulSoup as bs

# Calculate UNIX dates to parse Yahoo fetch URL
def yahoo_calc_date(d):
	if type(d) is str:
		convd   = [int(x) for x in d.split('-')]
		current = dt.datetime(convd[0],convd[1],(convd[2]))
		d_unix  = [str(x) for x in str(time.mktime(current.timetuple())).split('.')][0]
		return d_unix
	else:
		d_unix  = [str(x) for x in str(time.mktime(d.timetuple())).split('.')][0]
		return d_unix

# Format data response dates (from timestamp)
def yahoo_format_date(d):
	dates = []
	for x in d:
		dates.append(dt.datetime.fromtimestamp(x).strftime('%y-%m-%d %H:%M:%S'))
	return dates

# Get Market Data (OHLC + Volume + Adjusted Close, Dividends, Splits)
def yahoo_get_data(t,d='all',f='d',start='1970-1-1',end=dt.date.today()):
	base = 'https://query1.finance.yahoo.com/v8/finance/chart/%s' % (t)

	# Error Handling on data/freq parameters
	if not d in ['all','price','div','split']:
		print('Bad data selection...'); return None
	if not f in ['d','w','m']:
		print('Bad freq...'); return None

	# Calculate url-parsed params
	def f_switch(f):
		switch = {'d':'1d','w':'1wk','m':'1mo'}
		return switch.get(f)
	freq = f_switch(f)
	t0   = yahoo_calc_date(start)
	t1   = yahoo_calc_date(end)

	# Parse fetching URL and GET data response (return as .json)
	url = ("""{}?&lang=en-US&region=US&period1={}&period2={}&interval={}
		&events=div%7Csplit&corsDomain=finance.yahoo.com""")
	url = url.format(base,t0,t1,freq)

	res = req.get(url).json()
	return(res)

# Extract OHLC + Volume + Adjusted Close data
def extract_price_data(r):
	dateu = r['chart']['result'][0]['timestamp']
	datec = yahoo_format_date(dateu)

	raw = r['chart']['result'][0]['indicators']
	adj = raw['adjclose'][0]['adjclose']
	prc = raw['quote'][0]

	keys = ['dateu','datec','open','high','low','close','volume','adjusted']
	vals = [dateu,datec,np.array(prc['open']),np.array(prc['high']),
		 np.array(prc['low']),np.array(prc['close']),np.array(prc['volume']),
		 np.array(adj)]

	return dict(zip(keys,vals))

	'''
	return {'dateu':dateu,
		 'datec':datec,
		 'open':np.array(prc['open']),
		 'high':np.array(prc['high']),
		 'low':np.array(prc['low']),
		 'close':np.array(prc['close']),
		 'volume':np.array(prc['volume']),
		 'adjusted':np.array(adj)
		 }
	'''

# Extract Dividend Data (with dates)
def extract_div_data(r):
	try:
		raw = r['chart']['result'][0]['events']['dividends'] #['splits']
	except:
		return False
	amount = list()
	dateu = list()
	for x in sorted(raw):
		amount.append(raw[x]['amount'])
		dateu.append(raw[x]['date'])
	datec = yahoo_format_date(dateu)
	return {'dateu':np.array(dateu),'datec':datec,'amount':np.array(amount)}

#Main wrapper for stock pulling
def yget_stock(t,f='d',start='1970-1-1',end=dt.date.today()):
	# Adjust ticker to upper case + start date for pandas plotting
	t.upper()
	ad = start.split('-')
	ad = ad[1]+'/'+ad[2]+'/'+ad[0]
	# Fetch data + return data set (with input details)
	fetch = yahoo_get_data(t=t,f=f,start=start,end=end)
	price = extract_price_data(fetch)
	divs  = extract_div_data(fetch)
	return {'price':price,'dividend':divs,'ticker':t,'start':ad,'freq':f}

#	Plotting wrapper (outputs a graph image for parsing into templates)
def yf_plot(sd,what='adjusted',how='mkt'): #mkt,period,growth
	def h_switch(h):
		switch = {'mkt':what+' market data',
			'period':what+' periodic returns (%)',
			'growth':what+' relative growth (% from time 0)'}
		return switch.get(h)
	def f_switch(f):
		switch = {'d':'daily','w':'weekly','m':'monthly'}
		return switch.get(f)
	def y_alter(s):
		if how == 'mkt':
			return s
		elif how == 'period':
			temp = []
			for i in range(1,len(s),1):
				temp.append((s[i]-s[(i-1)])/s[(i-1)])
			return temp
		else:
			temp = []
			for i in range(0,len(s),1):
				if i == 0:
					temp.append(0)
				else:
					temp.append((s[i]-s[0])/s[0])
			return temp

	tick = sd['ticker']
	freq = f_switch(sd['freq'])
	yraw = sd['price'][what]
	xraw = pd.date_range(sd['start'],periods=len(yraw)); xadj = 0
	yadj = y_alter(yraw)
	if len(yadj) < len(yraw):
		xadj = xraw[1:]
	else:
		xadj = xraw
	hadj = h_switch(how)

	ts = pd.Series(yadj,index=xadj)
	fig = plt.figure(); ts.plot()
	plt.title(str(tick+' '+freq+' time series: '+hadj))
	return fig;

	
	
# # Tests for minor fetching functions:
# tempd 	= yahoo_get_data('DHI',start='2018-1-1')
# prc1    		= extract_price_data(tempd)
# div1     	= extract_div_data(tempd)

# # Tests for main wrapper fetching function
# test1 		= yget_stock('AAPL')
# test2 		= yget_stock('DHI',f='w')
# test3 		= yget_stock('F',start='1995-1-1')

# # Tests for intro index graphs (SP500, DJIA + NASDAQ)
# sp 			= yget_stock('^GSPC',start='2018-1-1')
# dj 			= yget_stock('^DJI',start='2018-1-1')
# nd 			= yget_stock('^IXIC',start='2018-1-1')

# p1 			= yf_plot(sp)
# p2 			= yf_plot(dj,what='volume')
# p3 			= yf_plot(nd,what='close',how='period')
# p4 			= yf_plot(sp,how='growth')







