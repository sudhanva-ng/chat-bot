from flask import Flask, request
import json
import requests
from webex_person import webex_person
from mdb import mdb
import random
import os
import subprocess, sys, time
from bs4 import BeautifulSoup

app = Flask(__name__)
app.debug = False


port = os.getenv("CONT_PORT")

print('port! + {}'.format(port))


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

def sendMsg(to, msg):
	global access_token, httpHeaders
	apiUrl = "https://webexapis.com/v1/messages"
	queryParams = {"toPersonEmail" : to, "text" : msg}

	response = requests.post(url=apiUrl, json=queryParams, headers=httpHeaders)

	# print (response.status_code)
	# print (response.text)

	if response.status_code == 400:
		print(msg)



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
	param = {'amount': '10', 'type':'multiple', 'category':'17'}

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
			ques = BeautifulSoup(ques).get_text(ques)
			opt = BeautifulSoup(opt).get_text(opt)
			ans = BeautifulSoup(ans).get_text(ans)
			Questions.append([ques, opt, ans])

		return (Questions)



@app.route('/', methods=['POST'])
def index():
	global   Persons
	json_content = request.json

	print ('real msg')
	msg = getMsg(json_content['data']['id'])
	email = json_content['data']['personEmail']

	db_name = email.replace('.com','')
	db_name = db_name.replace('.','')
	db_name = db_name.replace('@','')

	person_handler = mdb(db_name)

	out = person_handler.read()

	if not out:
			ques = getQuestions()
			data = {'person':email, 'questions':ques,'state':'new','score':0 }
			person_handler.write(data)
			sendMsg(email,  'Hello! Do you want to play a game? Remeber I am just a yes/no bot but you can say "start" to startover or "quit" to end anytime')
	else:
		if msg == 'stop' or msg == 'Stop' or msg == 'quit' or msg == 'Stop':
			sendMsg(email,  'Thank you for playing, bye!')
			person_handler.deleteCollection()
			return "OK"

		if out['state'] == 'new':
			print('new', flush=True)
			question = out['questions']
			curr = question.pop()
			sendMsg(email, curr[0])
			sendMsg(email, curr[1])
			data = {'questions':question, 'state':'asked', 'ans':curr[2]}
			person_handler.update(data)

		elif out['state'] == 'asked':
			print('asked', flush=True)
			score = out['score']
			if msg == out['ans']:
				score+=1
				sendMsg(email,  'That is right! Your current score is {}'.format(score))
			else:
				sendMsg(email,  'Sorry, the right answer is {}. Your current score is {}'.format(out['ans'],score))

			question = out['questions']
			if len(question) != 0:
				curr = question.pop()
				sendMsg(email, curr[0])
				sendMsg(email, curr[1])
				data = {'questions':question, 'state':'asked', 'ans':curr[2], 'score':score}
				person_handler.update(data)
			else:
				sendMsg(email, 'Good job! You scored {}. Do you want to go again? Remeber I am just a yes/no bot but you can say "start" to startover or "quit" to end anytime'.format(score))
				ques = getQuestions()
				data = {'person':email, 'questions':ques,'state':'new','score':0 }
				person_handler.update(data)
				


		
		# person = getPerson(Persons, email)
		# person_handler.updatePerson(email)







	# person = getPerson(Persons, email)

	# if person == None:
	# 	person = webex_person(email)
	# 	Persons.append(person)
	# 	person.Questions = getQuestions()
	# 	sendMsg(person.email,  'Hello! Do you want to play a game? Remeber I am just a yes/no bot but you can say "start" to startover or "quit" to end anytime')
	# 	return "OK"
		


	# while len(person.Questions)>0:
	# 	print ('inside while')

	# 	if person.AskQues == 1 :
	# 		print ('am here!')
	# 		sendMsg(person.email, person.Questions[0][0] )
	# 		sendMsg(person.email, person.Questions[0][1])
	# 		person.AskQues = 0
	# 		break

	# 	elif  person.AskQues == 0:
	# 		print ('elif?')
	# 		if msg == person.Questions[0][2]:
	# 			person.score+=1
	# 			sendMsg(person.email, 'That is the right Answer! Your score is {}'.format(person.score) )
	# 			del(person.Questions[0])
	# 			person.AskQues = 1

	# 		else:
	# 			person.AskQues = 1
	# 			sendMsg(person.email, 'Sorry! Right answer is {}. Your score is {}'.format(person.Questions[0][2], person.score) )
	# 			del(person.Questions[0])

	# 		if len(person.Questions) == 0 :
	# 			person.Questions = getQuestions()
	# 			sendMsg(person.email, 'Well done! Your final score is {}!'.format(person.score))
	# 			person.score = 0
	# 			sendMsg(person.email, "Reply 'start' to start again, 'stop' to end")
	# 			break 


	return "OK"



if __name__ == '__main__':

	# url = runNgrok()
    # print (url)
    #createWebhook(sys.argv[1])
    app.run(host="0.0.0.0",port=port)







