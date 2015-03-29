import os, gzip, sys, re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

class Gchat:
	def __init__(self, file_name):
		raw = gzip.open(file_name,'rb').read()
		raw = raw.replace('\r','').replace('=\n','')
		pieces = raw.split('\n')

		self.start_timestamp = pieces[0].replace('Date: ','')

		msg_from = pieces[1].replace('From: ','')
		a = re.search('\<.*\>', msg_from)
		self.msg_from_address = msg_from[a.start()+1:a.end()-1]
		self.msg_from_display = msg_from[1:a.start()-2]

		self.msg_to = pieces[2].replace('To: ','')

		a = re.search('\<.*\>', pieces[3])
		self.msg_id = pieces[3][a.start()+1:a.end()-1]

		search = 0
		self.msg = {}
		for item in pieces[4:]:
			if 'Content-Type' in item and 'html' in item and search == 0:
				search = 1 - search
				content_type = 'html'
			try: 
				if '<' == item[0] and search == 1:
					self.msg[content_type] = item
			except: 
				pass
		
		soup = BeautifulSoup(self.msg['html'])

		divs = soup.findAll('div')
		self.logs = pd.DataFrame(columns=['timestamp','sender','message'])

		s1, s2, sender = '', '', ''
		entry = divs[0]
		try:
			ts = entry.contents[0].text.encode('ascii','ignore')
		except:
			ts = 'NULL'

		for (ii, entry) in enumerate(divs):	
			if len(entry.contents) == 2:
				
				tmp = entry.contents[0].text.encode('ascii','ignore')

				if tmp != "":
					ts = tmp
				foo = entry.contents[1]
				try:
					sender, msg = foo.span.span.text, foo.span.text
					a = re.search('%s: ' % sender, msg)
					msg = msg[a.end():]	
					if s1 == '':
						s1 = sender
					elif s2 == '':
						s2 = sender
				except AttributeError:
					msg = foo.span.text
				self.logs.loc[ii] = [ts, sender, msg]

	def num_messages(self):
		num_me = len(self.logs[self.logs.sender=='me'])
		num_other = len(self.logs[self.logs.sender!='me'])
		return (('num_me', num_me), ('num_other', num_other), ('num_both', num_me + num_other))

	def count_num_words(self):
		self.logs['num_words'] = self.logs.message.apply(lambda x: len(x.split()))
		return self.logs.num_words

	def min_num_words(self):
		my_logs = self.logs[self.logs.sender == 'me']
		other_logs = self.logs[self.logs.sender != 'me']
		return (('me', my_logs.num_words.min()), ('other', other_logs.num_words.min()))

	def max_num_words(self):
		my_logs = self.logs[self.logs.sender == 'me']
		other_logs = self.logs[self.logs.sender != 'me']
		return (('me', my_logs.num_words.max()), ('other', other_logs.num_words.max()))

	def avg_num_words(self):
		avg_num_me = np.mean(self.logs[self.logs.sender=='me'].num_words)
		avg_num_other = np.mean(self.logs[self.logs.sender!='me'].num_words)
		avg_num = np.mean(self.logs.num_words)
		return (('me', avg_num_me), ('other', avg_num_other), ('both', avg_num))

	def chat_duration(self):
		gstart = self.start_timestamp
		gstart = gstart.split(', ')[1]
		gstart = gtime_to_datetime(gstart)

		ts = self.logs.timestamp.ix[0,0]
		te = self.logs.timestamp.ix[len(self.logs)-1,0]
		ts, te = msgtime_to_datetime(ts), msgtime_to_datetime(te)
		ts = ts.replace(year=gstart.year, month=gstart.month, day=gstart.day)
		te = te.replace(year=gstart.year, month=gstart.month, day=gstart.day)
		# ts, te = gtime_to_datetime(ts), gtime_to_datetime(te)
		self.ts, self.te = ts, te
		return (te - ts).total_seconds()

	def frequency_analysis(self):
		try: 
			avg_f = (len(self.logs) / (self.te - self.ts).total_seconds())
		except ZeroDivisionError:
			avg_f = 0
		return avg_f

	def initiator(self):
		return self.logs.sender.ix[0]

	def longest_sequence(self):
		try:
			s1, s2 = self.logs.sender.unique()
		except:
			s1, s2 = self.logs.sender[0], ''

		curr_len = 1
		max_len_s1, max_len_s2 = 0, 0
		if self.logs.sender[0] == s1:
			curr_sender = s1
		else:
			curr_sender = s2
		for s in self.logs.sender[1:]:
			if s == curr_sender:
				curr_len += 1
			if s != curr_sender:
				if curr_sender == s1:
					max_len_s1 = max(max_len_s1, curr_len)
				else:
					max_len_s2 = max(max_len_s2, curr_len)
				curr_len = 1
				curr_sender = s
		return (('%s' %s1, max_len_s1), ('%s' %s2, max_len_s2))

	def delay(self):
		self.logs.datetime = self.logs.timestamp.apply(msgtime_to_datetime)
		self.logs['delay'] = self.logs.datetime.diff()
		return self.logs.delay

	def max_delayer(self):
		self.delay()
		my_logs = self.logs[self.logs.sender == 'me']
		their_logs = self.logs[self.logs.sender != 'me']
		if my_logs.delay.max() > their_logs.delay.max():
			return ('me', my_logs.delay.max())
		else:
			return (their_logs.sender[0], their_logs.delay.max())

	def corpus_writer(self, file_name, mode='a'):
		my_logs = self.logs[self.logs.sender == 'me']
		their_logs = self.logs[self.logs.sender != 'me']

		g = open(file_name, 'a')
		g.write('msg_id: %s \n' % self.msg_id)
		g.write('timestamp: %s \n' % self.start_timestamp)
		g.write('account: %s \n' % self.msg_to)
		g.write('sender: %s \n' % self.msg_from_address)
		g.write('message: ' + ' '.join(list(their_logs.message)) + '\n')
		g.write('\n')
		g.close()

		g = open(file_name + '_mywords', 'a')
		g.write('msg_id: %s \n' % self.msg_id)
		g.write('timestamp: %s \n' % self.start_timestamp)
		g.write('account: %s \n' % self.msg_to)
		g.write('sender: %s \n' % self.msg_from_address)
		g.write('message: ' + ' '.join(list(my_logs.message)) + '\n')
		g.write('\n')
		g.close()

def gtime_to_datetime(time_str):
	if not time_str[:2].isdigit():
		time_str = '0' + time_str
	a = re.search('[0-9]{2}:[0-9]{2}:[0-9]{2}', time_str)
	time_str = time_str[:a.end()]
	return datetime.strptime(time_str, '%d %b %Y %H:%M:%S')

def msgtime_to_datetime(time_str):
	if not time_str[:2].isdigit():
		time_str = '0' + time_str
	return datetime.strptime(time_str, '%I:%M %p')

if __name__ == '__main__':
	print 1