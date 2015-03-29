import os, re, sys
import MySQLdb, getpass
from metadata_parser import *

# parse the parent directory where all the subchats-N directories are stored
# using gmvault, this is usually /gmvault-db/db/chats/
if sys.argv[-1] == '/':
	work_dir = sys.argv[1][:-1]
else:
	work_dir = sys.argv[1] 
subchats_folder = [work_dir + '/' + dir for dir in os.listdir(work_dir) if 'subchats' in dir]

# list of metadata files in the subchats folders
files = []
for folder in subchats_folder:
	listdir = os.listdir(folder)
	listdir = [folder + '/' + f for f in listdir if 'meta' in f]
	files += listdir
print "%d metadata files located" %(len(files))

# determine the output file location and name
try:
	output_file = sys.argv[2]
except:
	output_file = '/private/tmp/gchat_metadata_store.csv'

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

pwd = getpass.getpass('MySQL server root password:')
db = MySQLdb.connect(host='localhost',
					user='root',
					passwd=pwd,
					db='gmail')
cur = db.cursor()

query = "LOAD DATA LOCAL INFILE \
        \'%s\' \
        REPLACE \
        INTO TABLE chats_metadata_shellyjang \
        FIELDS TERMINATED BY ','\
        OPTIONALLY ENCLOSED BY '\"';" 
query = query % (output_file)

cur.execute(query)
db.commit()	

