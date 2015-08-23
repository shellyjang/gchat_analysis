import os, gzip, sys, re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re, json,time
from nltk.tokenize import regexp_tokenize, word_tokenize
from nltk import pos_tag

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
		# msg = {}
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
		try:
			ts = divs[0].contents[0].text.encode('ascii','ignore')
			for (ii, entry) in enumerate(divs):			
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
		except:
			print('%s is corrupted' % file_name)
			pass

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
		# ts = self.start_timestamp.split(', ')[1]
		# if not ts[:2].isdigit():
		# 	ts = '0' + ts
		# a = re.search('[0-9]{2}:[0-9]{2}:[0-9]{2}', ts)
		# ts = ts[:a.end()]
		# start_date = datetime.strptime(ts, '%d %b %Y %H:%M:%S')
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
		# sender_seq = list(self.logs.sender)
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
		# self.delay()
		self.logs['delay'] = self.delay()
		my_logs = self.logs[self.logs.sender == 'me']
		their_logs = self.logs[self.logs.sender != 'me']
		if my_logs.delay.max() > their_logs.delay.max():
			return ('me', my_logs.delay.max().seconds)
		else:
			return (their_logs.sender.iloc[0], their_logs.delay.max().seconds)

	def corpus_writer(self, file_name, mode='a'):
		print 1
		f1 = open(file_name, 'a')
		f2 = open(file_name + '_mywords','a')
		start_datetime = ' '.join(self.start_timestamp.split()[1:4])
		t = datetime.strptime(start_datetime, '%d %b %Y')

		for r in self.logs.iterrows():
			r_ = r[1]
			if r_.sender == 'me':
				f2.write('%d-%d-%02d|%s|%s|%s\n' % (t.year, t.month, t.day, r_.timestamp, r_.sender, r_.message))
			else:
				f1.write('%d-%d-%02d|%s|%s|%s\n' % (t.year, t.month, t.day, r_.timestamp, r_.sender, r_.message))
		f1.close()
		f2.close()

	def corpus_writer_yearly(self, file_name, mode='a'):
		start_datetime = ' '.join(self.start_timestamp.split()[1:4])
		t = datetime.strptime(start_datetime, '%d %b %Y')

		f1 = open('%s_%d' %(file_name, t.year), 'a')
		f2 = open('%s_mywords_%d' %(file_name, t.year), 'a')
		for r in self.logs.iterrows():
			r_ = r[1]
			if r_.sender == 'me':
				f2.write('%d-%d-%02d|%s|%s|%s\n' % (t.year, t.month, t.day, r_.timestamp, r_.sender, r_.message))
			else:
				f1.write('%d-%d-%02d|%s|%s|%s\n' % (t.year, t.month, t.day, r_.timestamp, r_.sender, r_.message))
		f1.close()
		f2.close()

	def pos_tag(self, alphanum_only=True):
		if alphanum_only:
			self.logs['tags'] = self.logs['message'].apply(lambda x: pos_tag(regexp_tokenize(x, r'\w+')))
		else:
			self.logs['tags'] = self.logs['message'].apply(lambda x: pos_tag(word_tokenize(x)))

		return self.logs['tags']

	def formality_score(self):
		if 'tags' not in self.logs.columns:
			self.pos_tag()
		self.logs['formality'] = self.logs['tags'].apply(formality_score)
		return self.logs['formality']

class Metadata:
	def __init__(self, line):
		try:
			d = json.loads(line)
			self.gm_id = d['gm_id']

			t = d['internal_date']
			t = time.gmtime(int(t))
			td = datetime(year=t.tm_year, month=t.tm_mon, day=t.tm_mday, hour=t.tm_hour, minute=t.tm_min, second=t.tm_sec)
			self.timestamp = td.strftime("%Y-%m-%d %H:%M:%S")

			self.msg_id = d['msg_id']
			self.subject = d['subject'].replace('Chat with ', '')
			self.subject = self.subject.replace(',',' ')
			self.thread_ids = d['thread_ids']
			self.x_gmail_received = d['x_gmail_received']

			self.flags = d['flags']
			self.flags = ' '.join(self.flags)
			
			self.labels = d['labels']
			self.labels = ' '.join(self.labels)
			self.status = 'Success'
		except: 
			self.status = 'Corrupted'

	def write(self):
		print ','.join(map(str, [self.timestamp, self.gm_id, self.subject, self.msg_id, self.thread_ids, self.x_gmail_received]))

	def write_file(self, filename):
		if not self.status == 'Corrupted':
			f = open(filename, 'a')
			new_line = ','.join(map(str, [self.timestamp, self.gm_id, self.subject, self.msg_id, self.thread_ids, self.x_gmail_received]))
			f.write(new_line + '\n')
		else: 
			print 'file was corrupted...'
			return 0

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

def locate_eml(work_dir, ext='eml.gz'):
	'''
	locate the *.eml.gz files from gmvault-db/db/chats/subchats-* directory
	'''
	if work_dir[-1] != '/':
		work_dir += '/'

	subchats_dir = [d for d in os.listdir(work_dir) if 'subchats' in d]
	files = []
	for d in subchats_dir:
		files += [work_dir + d + '/' + f for f in os.listdir(work_dir + d) if ext in f]
	return files

def formality_score(tagged):
    '''
    the formula is from https://trinker.github.io/qdap/vignettes/qdap_vignette.html#formality
    tagged is a list of tupples (word, pos_tag)

    '''
    f_tags = r'(NN.*)|(JJ.*)|(\bTO)|(\bIN)|(\bDT)' # noun, adjective, preposition, article
    c_tags = r'(PRP.*)|(VB.*)|(RB.*)|(\bWRB)|(\bUH)' # pronoun, verb, adverb, interjection

    n_f = map(lambda x: re.match(f_tags, x[1]), tagged)
    n_f = sum([1 for a in n_f if a])
    n_c = map(lambda x: re.match(c_tags, x[1]), tagged)
    n_c = sum([1 for a in n_c if a])

    n_o = len(tagged) - (n_f + n_c)
    try:
        F = 50 * ((n_f - n_c) / float(len(tagged)) + 1)
    except ZeroDivisionError:
        F = None

    return F


if __name__ == '__main__':
	gc = Gchat('1304479349618348157.eml.gz')
	print gc.max_delayer()
	# gc.build_chat_log()
	# gc.count_num_words()
	# print gc.logs[['sender', 'message', 'num_words']]
	# print gc.convo_duration()
	# print gc.initiator()
	# gc.delay()
	# print gc.chat_duration()
	# print gc.frequency_analysis()


