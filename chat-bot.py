from flask import Flask, request
import json
import requests
import csv
from webex_person import webex_person
import random
import os
import subprocess, sys, time
from pyngrok import ngrok

app = Flask(__name__)
app.debug = False
port = int(os.environ.get("PORT", 5000))


access_token = "M2FmNGNlZDItNDM3Yi00NGM2LTkxNjMtZjAwZGM2NzQ5NzczZjU2YWI5Y2MtNmYz_P0A1_16d45015-863d-4604-9bc8-b783b72ace5b"

httpHeaders = {"Content-type" : "application/json", "Authorization" : "Bearer " + access_token}

msg = 'Do you want to play a game?'
msg_thankYou = 'Thank you; your response has been recorded'


Persons = []

def getPerson(Persons, email):
	for items in Persons:
		if items.email == email:
			return(items)

	return None

def createWebhook(url):
	apiUrl = 'https://webexapis.com/v1/webhooks'
	queryParams = {'name':'test', 'targetUrl':url, 'resource':'messages', 'event':'created'}
	response = requests.post(url=apiUrl, json=queryParams, headers=httpHeaders)
	print('Success!')
	print (response.status_code)
	print(response.text)

def runNgrok():
# 	p = subprocess.Popen('ngrok http 5000', shell=True, stderr=subprocess.PIPE)
# 	print ('hi')
 
# ## But do not wait till netstat finish, start displaying output immediately ##
# 	while True:
# 		out = p.stderr.read(1)
# 		if out == '' and p.poll() != None:
# 			break
# 		if out != '':
# 			#sys.stdout.write(out)
# 			print('!'+out)
# 			#sys.stdout.flush()

# 		if 'Forwarding' in out:
# 			url = re.search('Forwarding\s*(http.*)\s->')
# 			print (url)
# 			break

	public_url = ngrok.connect(5000,'http')
	return (public_url)

def sendMsg(to, msg):
	global access_token, httpHeaders
	apiUrl = "https://webexapis.com/v1/messages"
	queryParams = {"toPersonEmail" : to, "text" : msg}

	response = requests.post(url=apiUrl, json=queryParams, headers=httpHeaders)

	print (response.status_code)
	#print (response.text)


def getMsg(msgId):
	global access_token, httpHeaders
	apiUrl = "https://webexapis.com/v1/messages/"+msgId

	response = requests.get(url=apiUrl, headers=httpHeaders)
	#print(response.text)

	if response.status_code==200:
		out = json.loads(response.text)
		#print (type(out))
		return(out['text'])

def getQuestions():

	Questions = []
	url = 'https://opentdb.com/api.php'
	param = {'amount': '1', 'type':'multiple', 'category':'17'}

	response = requests.get(url=url, params=param)
	out = json.loads(response.text)
	if response.status_code == 200:

		for questions  in out['results']:
			ques = questions['question']
			opt = questions['incorrect_answers']
			opt.append(questions['correct_answer'])
			random.shuffle(opt)

			opt = '\n'.join(opt)

			ans = questions['correct_answer']

			Questions.append([ques, opt, ans])

		return (Questions)


@app.route('/', methods=['GET'])
def test():
	print ('Hello!!!!')
	return "OK"

@app.route('/', methods=['POST'])
def index():
	global   Persons
	json_content = request.json

	if json_content['data']['personEmail'] == 'sudng-test@webex.bot':
		print ('My own msg; go to sleep')
	else:
		print ('real msg')
		msg = getMsg(json_content['data']['id'])
		email = json_content['data']['personEmail']

		person = getPerson(Persons, email)

		if person == None:
			person = webex_person(email)
			Persons.append(person)
			sendMsg(person.email,  'Hello! Do you want to play a game? Remeber I am just a yes/no bot but you can say "start" to startover or "quit" to end anytime')
			return "OK"


		if len(person.Questions) == 0 and 'yes' in msg:
			person.Questions = getQuestions()
			person.AskQues = 1

		elif len (person.Questions) == 0 and 'no' in msg:
			sendMsg(person.email, 'Bye!' )
			return "OK"

		elif (len(person.Questions)>0 and 'no' in msg) or ('Quit' in msg or 'quit' in msg):
			sendMsg(person.email, 'Bye!' )
			return "OK"

		elif 'start' in msg or 'Start' in msg:
			print ('here!!')

			person.Questions = getQuestions()
			person.AskQues = 1


		while len(person.Questions)>0:
			print ('inside while')

			if person.AskQues == 1 :
				print ('am here!')
				sendMsg(person.email, person.Questions[0][0] )
				sendMsg(person.email, person.Questions[0][1])
				person.AskQues = 0
				break

			elif  person.AskQues == 0:
				print ('elif?')
				if msg == person.Questions[0][2]:
					sendMsg(person.email, 'That is right!' )
					del(person.Questions[0])
					person.AskQues = 1

				else:
					person.AskQues = 1
					sendMsg(person.email, 'Sorry! Right answer is '+person.Questions[0][2] )
					del(person.Questions[0])



		if len (person.Questions) == 0 and 'yes' not in msg:
			sendMsg(person.email, 'Do you want to start again?')



	return "OK"



if __name__ == '__main__':

	# url = runNgrok()
	# print (url)
	createWebhook(sys.argv[1])

	app.run(host="0.0.0.0",port=port)







