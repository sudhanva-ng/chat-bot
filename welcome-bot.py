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
port = int(os.environ.get("PORT", 80))


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


@app.route('/', methods=['POST'])
def index():
	global   Persons
	json_content = request.json

	if json_content['data']['personEmail'] == 'sudng-quiz-bot@webex.bot':
		print ('My own msg; go to sleep')
	else:
		print ('real msg')
		msg = getMsg(json_content['data']['id'])
		email = json_content['data']['personEmail']
		person = getPerson(Persons, email)
		
		print ('Create a container!')
		sendMsg(person.email,  'Hello! Do you want to play a game? Remeber I am just a yes/no bot but you can say "start" to startover or "quit" to end anytime')



	return "OK"



if __name__ == '__main__':

	# url = runNgrok()
	# print (url)
	#createWebhook(sys.argv[1])

	app.run(host="0.0.0.0",port=port)







