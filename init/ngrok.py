#!/usr/bin/python3

import json
import requests
from pyngrok import ngrok


access_token = "M2FmNGNlZDItNDM3Yi00NGM2LTkxNjMtZjAwZGM2NzQ5NzczZjU2YWI5Y2MtNmYz_P0A1_16d45015-863d-4604-9bc8-b783b72ace5b"

httpHeaders = {"Content-type" : "application/json", "Authorization" : "Bearer " + access_token}

def createWebhook(url):
	apiUrl = 'https://webexapis.com/v1/webhooks'
	queryParams = {'name':'test', 'targetUrl':url, 'resource':'messages', 'event':'created'}
	response = requests.post(url=apiUrl, json=queryParams, headers=httpHeaders)
	print('Success!')
	print (response.status_code)
	print(response.text)


def sendMsg(to, msg):
	global access_token, httpHeaders
	apiUrl = "https://webexapis.com/v1/messages"
	queryParams = {"toPersonEmail" : to, "text" : msg}

	response = requests.post(url=apiUrl, json=queryParams, headers=httpHeaders)

	print (response.status_code)
	print (response.text)

	if response.status_code == 400:
		print(msg)


def runNgrok(ip,port):
	ngrok.set_auth_token("2BT4t3kNCKW7jyOMT2IKhUaJpB6_7bXXsT4teob5FzifpnaSN")
	#http_tunnel = ngrok.connect(addr=port)
	print('running command ')

	http_tunnel = ngrok.connect(ip+':'+port)
	print('Opened')
	print(http_tunnel)
	print(http_tunnel.public_url)
	return http_tunnel.public_url

def getHooks():
	global access_token, httpHeaders
	apiUrl = "https://webexapis.com/v1/webhooks"
	response = requests.get(url=apiUrl, headers=httpHeaders)
	hooks = []

	if response.status_code == 200:
		out = json.loads(response.text)
		for items in out['items']:
			hooks.append(items['id'])

	return hooks

def deleteHooks(hooks):
	global access_token, httpHeaders
	apiUrl = "https://webexapis.com/v1/webhooks"

	for ids in hooks:
		queryParams = {"webhookId" : ids}
		apiUrl = "https://webexapis.com/v1/webhooks/{}".format(ids)
		#response = requests.delete(url=apiUrl, json=queryParams, headers=httpHeaders)
		response = requests.delete(url=apiUrl, headers=httpHeaders)
		print(response.status_code)




if __name__ == '__main__':


    hooks = getHooks()
    deleteHooks(hooks)

    #url = runNgrok(5000)
    #url = runNgrok('172.17.0.2', '5000')
    url = runNgrok('10.10.10.5', '5000')
    print(url)
    createWebhook(url)
    while(1):
    	pass
