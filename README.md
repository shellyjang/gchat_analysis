# Google chat analysis

## Pre-req

You will need to download [gmvault] and download your chat logs by running the following command
```
$ gmvault sync --chats-only <your_email>@gmail.com
```
This will create a gmvault-db folder in your home directory. The chats are stored in gmvault-db/db/chats -- depending on the number of chats, it will create sub-directory called subchats-1, ...

## Parsing the corpus from chat logs

 * corpus_builder.py 
 
The script takes two arguments, the subchats directory and the directory to store the flat files. Running the following command will create files in the /output/location/ named by the email addresses of your correspondents. For each email address, there will be two corresponding files -- one with no suffix, and another with suffix '_mywords'. Simply the first contains their words, and the second contains your words.

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

 * 

[gmvault]:http://gmvault.org/download.html
