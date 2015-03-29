import re, json,time
from datetime import datetime

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
