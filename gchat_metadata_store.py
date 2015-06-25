import os, re, sys
import MySQLdb, getpass
from metadata_parser import Metadata
from gchat_eml import locate_eml

# parse the parent directory where all the subchats-N directories are stored
# using gmvault, this is usually /gmvault-db/db/chats/
work_dir = sys.argv[1]
files = locate_eml(work_dir, 'meta')
print "%d metadata files located" %(len(files))

# specify the output file location and name
try:
	output_file = sys.argv[2]
except:
	output_file = '/private/tmp/gchat_metadata_store.csv'

f = open(output_file,'w')
f.write('%s\n' %'timestamp, gm_id, subject, msg_id, thread_ids, x_gmail_received')
f.close()

l = len(files)/5
corrupted = 0

for (ii, metadata_file) in enumerate(files):
	# line = open(work_dir + metadata_file, 'r').next()
	line = open(metadata_file, 'r').next()
	m = Metadata(line)
	a = m.write_file(output_file)
	if a:
		print 'file was corrupted'
		corrupted += 1
	if ii % l == 0 and ii != 0:
		print '%d percent finished...' % (ii / l * 20)
print '%d of %d files were successfully stored.' %(len(files)-corrupted, len(files))

if __name__ == '__main__':
	pass
