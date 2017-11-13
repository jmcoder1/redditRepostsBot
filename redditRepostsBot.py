"""
This script is responsible for the reddit reposts bot.

Rquirements:
	
	Initially the bot should be opt in. 

			(This is open to change once I am sure the bot is working completely as intended)

	The bot should be authorised in the subreddits that it operates in. Message the mods beforehand!

Functionality:
	
	Loops through any new posts and sees if they are reposts - images, same title, same contents.
	Lists all the posts in the subreddit that are reposts.

Created by /u/slaynShadow

Licence:


"""

from requests import get

import datetime
import itertools

import praw
import os
import time
import re

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
COMMENTED_FILE_PATH = os.path.join(SCRIPT_PATH, "commented.txt")

header = "##Reposted Bot"
footer = "*Bot created by /u/slaynShadow*"

def parseSubmissionURLInfo(data):
	"""
	This function parses the data passed to it about the reposts and 
	string appropriate for the main part of the comment.

	Parameters: 
		data: infomration to be parsed.

	Return:	
		String appropriate for reading.
	"""
	parsed_data = "**Matches By URL**"

	for datum in data:
		dat_url = datum.url
		dat_title = datum.title
		dat_author = getSubmissionAuthor(datum)
		dat_time_date = datetime.datetime.fromtimestamp(datum.created)
		parsed_data += ("\n\n[" + dat_title + "]("  + dat_url + ")\n\n by " + dat_author + " [" + str(dat_time_date) +  "]\n\n")
		
	if len(data) == 0:
		parsed_data += "\n\nNo Matches Found\n\n"

	return parsed_data

def getSubmissionURLInfo(main_submission, subreddit, reddit):
	"""
	Parameters: 
		main_submission: the submission parent object of the comment that calls the reddit bot.
		subreddit: (string) subreddit name.
		reddit: authorised version of reddit.

	Return:
		Unparsed match data of the submission body.
	"""

	matches_by_url = []
	lmt = 1000
	sub = reddit.subreddit(subreddit)

	submissions = itertools.chain(
	sub.top(limit = lmt),
	sub.rising(limit = lmt),
	sub.controversial(limit = lmt),
	sub.new(limit = lmt),
	sub.hot(limit = lmt)#,
	#sub.gilded(limit = lmt)
)
	for submission in submissions:

		"""
		if type(submission) != type(comment_submission): #for gilded posts
			submission = getCommentPost(submission)#consider renaming this function for more clarity
		"""
		if submission.url == main_submission.url and submission not in matches_by_url and submission != main_submission:
			matches_by_url.append(submission)


		#assumes that the only types you can get from the stream are submissions and comments
	
	return matches_by_url

def parseSubmissionBodyInfo(data):
	"""
	This function parses the data passed to it about the reposts and 
	string appropriate for the main part of the comment.

	Parameters: 
		data: infomration to be parsed.

	Return:	
		String appropriate for reading.
	"""
	parsed_data = "**Matches By Body**"

	for datum in data:
		dat_url = datum.url
		dat_body = datum.selftext
		dat_author = getSubmissionAuthor(datum)
		dat_time_date = datetime.datetime.fromtimestamp(datum.created)
		parsed_data += ("\n\n[" + dat_body + "]("  + dat_url + ")\n\n by " + dat_author + " [" + str(dat_time_date) +  "]\n\n")
		
	if len(data) == 0:
		parsed_data += "\n\nNo Matches Found\n\n"

	return parsed_data

def getSubmissionBodyInfo(main_submission, subreddit, reddit):
	"""
	Parameters:
		main_submission: the submission parent object of the comment that calls the reddit bot. 
		subreddit: (string) subreddit name.
		reddit: authorised version of reddit

	Return:
		Unparsed match data of the submission body.
	"""
	matches_by_body = []
	lmt = 1000
	sub = reddit.subreddit(subreddit)

	submissions = itertools.chain(
	sub.top(limit = lmt),
	sub.rising(limit = lmt),
	sub.controversial(limit = lmt),
	sub.new(limit = lmt),
	sub.hot(limit = lmt)#,
	#sub.gilded(limit = lmt)
)
	for submission in submissions:

		"""
		if type(submission) != type(comment_submission): #for gilded posts
			submission = getCommentPost(submission)#consider renaming this function for more clarity
		"""
		if submission.selftext == main_submission.selftext and submission not in matches_by_body and submission != main_submission:
			matches_by_body.append(submission)


		#assumes that the only types you can get from the stream are submissions and comments
	
	return matches_by_body

def getMoreSubmissionInfo(comment, subreddit, reddit):
	"""
	Parameters:
		comment: the reddit commment that called the bot with the signall string.
		reddit: authorised instance of reddit.
		subreddit: (string) subreddit name.

	Return:
		Bonus information about the post.

	This function returns bonus information (in addition to the title information) about the reddit post.
	"""
	submission = getCommentPost(comment)
	if submission.is_self:
		bonus_info = getSubmissionBodyInfo(submission, subreddit, reddit)
		parsed_bonus_info = parseSubmissionBodyInfo(bonus_info)
		return parsed_bonus_info
	else:
		bonus_info = getSubmissionURLInfo(submission, subreddit, reddit)
		parsed_bonus_info = parseSubmissionURLInfo(bonus_info)	
		return parsed_bonus_info

def getSubmissionAuthor(submission):
	"""
	This function returns the author of a reddit submission.
	
	Parameters:
		submission: the submission.

	Return: (string) text of the submission
	"""
	if submission.author is None:
		return "Deleted"
	else:
		return ("/u/" + str(submission.author))

def getCommentPost(comment):
	"""
	This function gets the submission/post of a comment, i.e. if a comment's .parent is another parent it will
	return the submission.

	Parameter:
		comment: the comment from which we find the ultimate parent class.

	Return:
		The parent variable (post)
	"""
	
	#clean this up after you check if these are passed by reference

	original_comment = comment 

	while type(comment) == type(original_comment):
		comment = comment.parent()

	return comment

def fileWriter(file_path, data):
	"""
	This method writes text to a file located at a file path.

	Parameters:
		file_path: the file path for a specific file
		data: the text intended to be written to the file.
	"""
	try:
		with open(file_path, "a+") as f:
			f.write(data + "\n")
	except IOError:
		raise IOError("Error: can\'t find file or read data")


def getSubmissionTitleInfo(comment, subreddit, reddit):
	"""
	
	This function is called when a reddit user calls the script using the approved keyowrd. 

	It gets the comment and checks from the comment if the post is a repost based on the title.

	The data is not completely parsed into a neat string.

	Parameters
		comment: the reddit comment the the user uses to invoke the script.
		subreddit: (string) the subreddit the funtion checks for reposts.
		reddit: the authorised respective subreddit.

	Return:
		Information about the (re)post information of the script.

	*This function compares the titles of the posts.

	"""

	matches_by_title = []
	comment_submission = getCommentPost(comment)#change to main_submission

	lmt = 1000
	sub = reddit.subreddit(subreddit)

	submissions = itertools.chain(
	sub.top(limit = lmt),
	sub.rising(limit = lmt),
	sub.controversial(limit = lmt),
	sub.new(limit = lmt),
	sub.hot(limit = lmt)#,
	#sub.gilded(limit = lmt)
)
	for submission in submissions:

		"""
		if type(submission) != type(comment_submission): #for gilded posts
			submission = getCommentPost(submission)#consider renaming this function for more clarity
		"""
		if submission.title == comment_submission.title and submission not in matches_by_title and submission != comment_submission:
			matches_by_title.append(submission)


		#assumes that the only types you can get from the stream are submissions and comments
	
	return matches_by_title

def parseTitleInfo(data):
	"""
	This function parses the data passed to it about the reposts and 
	string appropriate for the main part of the comment.

	Parameters: 
		data: infomration to be parsed.

	Return:	
		String appropriate for reading.
	"""

	parsed_data = "**Matches By Title**"

	for datum in data:
		dat_url = datum.url
		dat_title = datum.title
		dat_author = getSubmissionAuthor(datum)
		dat_time_date = datetime.datetime.fromtimestamp(datum.created)
		parsed_data += ("\n\n[" + dat_title + "]("  + dat_url + ") by " + dat_author + " [" + str(dat_time_date) +  "]\n\n")
		
	if len(data) == 0:
		parsed_data += "\n\nNo Matches Found\n\n"

	return parsed_data

def getApprovedSubs():
	"""
	This functions gets a tuple of approved subs (str) from the .txt file.

	Return:
		(tuple) Strings of the named approved subs.
	"""

	approved_subs_path = os.path.join(SCRIPT_PATH, "approvedSubreddits.txt")

	lines = []
	try:
		with open(approved_subs_path) as f:
			for line in f:
				line = line.strip()
				lines.append(line)
	except IOError:
		raise IOError("Error: can\'t find file or read data.")
		print("File Path:", path)
	return lines

def runRepostedBot(reddit):
	"""
	This function is the main function responsible for the operations of the reposts bot.

	Parameters:
		reddit: an authenticated instance of the reddit class.
	"""

	signall_str = "RedditRepostBot"
	#secs_to_wait = 60
	subs = getApprovedSubs()
	print("Getting comments\n")

	for sub in subs:
		for comment in reddit.subreddit(sub).comments(limit = 1000): 
			
			match = re.findall(signall_str, comment.body)

			if match:
				try:
					print("Finding Data\n")
					file_obj_r = open(COMMENTED_FILE_PATH, 'r')
				except IOError: #handle this better 
					print("Exception Found\n")
				else:
					if comment.id not in file_obj_r.read().splitlines():
						print("Unique Comment Found\n\n...posting response\n")

						title_info = getSubmissionTitleInfo(comment, sub, reddit)
						
						parsed_title_info = parseTitleInfo(title_info)
						bonus_info = getMoreSubmissionInfo(comment, sub, reddit)
						main_content = parsed_title_info + bonus_info
				
						final_comment = header + "\n\n" + main_content + "\n\n" + footer

						try:
							comment.reply(final_comment)
						except praw.exceptions.APIException:
							comment_too_long_msg = "too many reposts found"
							print(comment_too_long_msg)
							comment.reply(header + "\n\n" + comment_too_long_msg + "\n\n" + footer)

						file_obj_r.close()

						fileWriter(COMMENTED_FILE_PATH, comment.id)

					else:
						print("Already checked this comment... no reply needed.\n")


				#time.sleep(secs_to_wait)
	print("Running...\n")

def authenticateReddit():
	"""
	This function returns and authenticated instance of the reddit object.
	"""

	print("Authenticating...\n")
	reddit = praw.Reddit("repostedBot")
	print("Authenticated as {}\n".format(reddit.user.me()))

	return reddit 

def main():

	reddit = authenticateReddit()

	while True:

		runRepostedBot(reddit)

if __name__ == "__main__":

	main()
