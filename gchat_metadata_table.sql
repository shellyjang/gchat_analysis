CREATE TABLE IF NOT EXISTS chats_metadata (
	time_stamp datetime,
	gm_id VARCHAR(100), 
	subject VARCHAR(100), 
	msg_id VARCHAR(100) primary key, 
	thread_ids VARCHAR(300), 
	x_gmail_received VARCHAR(300)
);


CREATE TABLE IF NOT EXISTS chats_variables (
	msg_id VARCHAR(100) primary key, 
	gm_id VARCHAR(100), 
	num_msgs_me INT, 
	num_msgs_other INT, 
	num_msgs_both INT,
	num_words_tot INT, 
	min_num_words_per_msg INT,
	max_num_words_per_msg INT, 
	avg_num_words FLOAT, 
	chat_duration INT, 
	avg_frequency FLOAT, 
	initiator VARCHAR(100), 
	max_cont_num_msgs_me INT, 
	max_cont_num_msgs_other INT, 
	max_delay_me INT, 
	max_delay_other INT
);

-- LOAD DATA LOCAL INFILE 
-- '/private/tmp/gchat_variables.csv'
-- REPLACE 
-- INTO TABLE chats_variables
-- FIELDS TERMINATED BY ','
-- IGNORE 1 LINES; 