# Google chat analysis
Were you too busy this year? Lacking the discipline to keep a self-log? Curious about what you & your friends chatted about in 2009?? Go digging around your own chat log!

## Pre-req

You will need to download [gmvault] and download your chat logs by running the following command
```
$ gmvault sync --chats-only <your_email>@gmail.com
```
This will create a gmvault-db folder in your home directory. The chats are stored in gmvault-db/db/chats -- depending on the number of chats, it will create sub-directory called subchats-1, ...

## Parsing the corpus from chat logs

 * corpus_builder.py 
 
The script takes two arguments, the subchats directory and the directory to store the flat files (the files are divided into (corresponder, year) pair). Running the following command will create files in the /output/location/ named by the email addresses of your correspondents. For each email address, there will be two corresponding files -- one with no suffix, and another with suffix '_mywords'. Simply the first contains their words, and the second contains your words. (Be sure that /output/location/ folder already exists)

```bash
python corpus_builder.py ~/gmvault-db/db/chats /output/location/
```

 * gchat_variables.py

The script parses out a pre-defined set of temporal variables - num_msgs_me, num_msgs_other, num_msgs_both, num_words_tot, min_num_words_per_msg, max_num_words_per_msg, avg_num_words, chat_duration, avg_frequency, initiator, max_cont_num_msgs_me, max_cont_num_msgs_other, max_delay_me, max_delay_other. The script takes two arguments, the subchats directory and the file name for storing the variables.

```bash
python gchat_variables.py ~/gmvault-db/db/chats /output/location2/metadata.csv
```

 * gchat_metadata_store.py
 
The script parses out the .meta files generated alongside the eml files. It holds the timestamp, gm_id, subject, msg_id, thread_ids, x_gmail_received.

```bash
python gchat_metadata_store.py ~/gmvault-db/db/chats /output/location2/metadata2.csv
```

 * ngram_builder.py

The script builds 1-, 2- and 3-gram frequency dictionary from the chat logs for each corresponder and year. It takes two arguments, the location of corpus files from 'corpus_builder.py' and the name of the output pickle file. Depending on the size of your chat log, this may take a few minutes. 

```bash
python ngram_builder.py /private/tmp/corpus/ /output/location3/ngrams.pkl
```

 * words_that_divide.py

The script uses the method featured in '[Dataclysm]'. It ranks the common words between two lists of corpora, ranks their relevant frequency in each corpus, then picks out the words that are used much more in one corpus than the other. The arguments are the location of the ngrams file from 'ngram_builder.py' and two lists of corpus you want to compare. For example, if you want to compare the words that *you* used with two different friends (friend1, friend2) in years 2009 through 2011, then 

```bash
python words_that_divide.py /output/location3/ngrams.pkl "['friend1@gmail.com_2009_mywords','friend1@gmail.com_2010_mywords', 'friend1@gmail.com_2011_mywords']" "['friend2@gmail.com_2009_mywords','friend2@gmail.com_2010_mywords', 'friend2@gmail.com_2011_mywords']" 
```
this will give you the top 5 'words that divide', if you wish to see 2-grams or 3-grams, you have to provide optional argument 'bg' or 'tg'. Depending on the size of your chat log, this may take a few minutes. Additionally, if you want to see more words or n-grams, provide an additional integer. 
```bash 
python words_that_divide.py /output/location3/ngrams.pkl "['friend1@gmail.com_2009_mywords','friend1@gmail.com_2010_mywords', 'friend1@gmail.com_2011_mywords']" "['friend2@gmail.com_2009_mywords','friend2@gmail.com_2010_mywords', 'friend2@gmail.com_2011_mywords']" 'bg' 10
```

 * words_that_divide_tfidf.py

This script uses tf-idf scores to find the most frequently used, but not necessarily globally frquently used, words in each corpus. Currently, the default is to give top 5 words for each corpus, but you can specify 2- or 3-grams by providing an optional argument as so.

```bash
python words_that_divide_tfidf.py /private/tmp/corpus/ /output/location2/result "(2,2)" 
```
This will go thorugh all of the files in the corpus directory. To look for the corresponder and the year you're interested in, try:

```bash
egrep 'friend1.*2009' -A5 /output/location2/result
```

Right now, when the range is expanded, this will most likely give you overlapping results (e.g. sign, actually sign, actually sign gchat).


[gmvault]:http://gmvault.org/download.html
[dataclysm]:http://www.amazon.com/Dataclysm-When-Think-Ones-Looking/dp/0385347375
