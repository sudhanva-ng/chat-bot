from flask import Flask, request
import json
import requests
import csv
from webex_person import webex_person
import random
import os
import subprocess, sys, time
from subprocess import check_output
from pyngrok import ngrok
import time

app = Flask(__name__)
app.debug = False

if '-d' in sys.argv:
	port = int(os.environ.get("PORT", 5000))
else:
	port = int(os.environ.get("PORT", 80))

print('port! + {}'.format(port))


access_token = "M2FmNGNlZDItNDM3Yi00NGM2LTkxNjMtZjAwZGM2NzQ5NzczZjU2YWI5Y2MtNmYz_P0A1_16d45015-863d-4604-9bc8-b783b72ace5b"

httpHeaders = {"Content-type" : "application/json", "Authorization" : "Bearer " + access_token}

msg = 'Do you want to play a game?'
msg_thankYou = 'Thank you; your response has been recorded'


Persons = []
ports = list(range(3000,3100))

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

def forwardApi(ip, json_content, port):
	apiUrl = "http://{}:{}".format(ip,port)
	response = requests.post(url=apiUrl, json=json_content)

def createContainer(name, port):
	# p = subprocess.Popen('sudo docker run -d -p {}:{} -e CONT_PORT={} chat-bot'.format(port, port, port), shell=True, stderr=subprocess.PIPE)
	
	# cmd = 'sudo docker run -d -p {}:{} -e CONT_PORT={} --name {} chat-bot'.format(port, port, port, name)
	# p = subprocess.Popen('ssh -i /root/chat-bot.pem ubuntu@172.17.0.1 '+ cmd, shell=True, stderr=subprocess.PIPE)

	# print('Container {} is created!'.format(name))

	# time.sleep(10)

	# cmd = "sudo docker inspect -f \'{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}\' {}".format(name)
	# p = subprocess.Popen('ssh -i /root/chat-bot.pem ubuntu@172.17.0.1 '+ cmd, shell=True, stderr=subprocess.PIPE)
	# out = p.stderr.read().decode("utf-8")
	# print('IP!!'+out)
	# return (out)

	base = 'ssh -i /root/chat-bot.pem ubuntu@172.17.0.1 '
	cmd = 'sudo docker run -d -p {}:{} -e CONT_PORT={} --name {} chat-bot'.format(port, port, port, name)
	out = check_output((base + cmd).split())

	print('Container created with name {}'.format(name))

	time.sleep(2)

	cmd = "sudo docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' {}".format(name)
	out = check_output((base + cmd).split())
	out = out.decode('utf-8')
	print('!!' + out)
	return out



@app.route('/', methods=['POST'])
def index():
	global   containers, ports
	json_content = request.json

	if json_content['data']['personEmail'] == 'sudng-quiz-bot@webex.bot':
		print ('My own msg; go to sleep')
	else:
		print ('real msg')
		msg = getMsg(json_content['data']['id'])
		email = json_content['data']['personEmail']

		person = getPerson(Persons, email)
		if person == None:
			person = webex_person(email)
			person.port = ports.pop()
			Persons.append(person)

			sendMsg(person.email,  'Hello! Do you want to play a game? Remeber I am just a yes/no bot but you can say "start" to startover or "quit" to end anytime')

			person.ip = createContainer(person.container, person.port)
			print('New person! Creating contianer with IP!'.format(person.ip))
			
		else:

			print('Found person, Forwarding api')
			forwardApi(person.ip, json_content, person.port)

	

		#sendMsg(person.email,  'Hello! Do you want to play a game? Remeber I am just a yes/no bot but you can say "start" to startover or "quit" to end anytime')



	return "OK"



if __name__ == '__main__':

	# url = runNgrok()
	# print (url)
	#createWebhook(sys.argv[-1])

	app.run(host="0.0.0.0",port=port)







