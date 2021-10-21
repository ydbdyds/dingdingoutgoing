# -*- coding: utf-8 -*-
import requests
import json
import time
import hmac
import hashlib
import base64
import socket
import os,sys
from multiprocessing import Process

def handle_client(client_socket):
	request_data=client_socket.recv(20000)
	res=getPost(request_data)
	try:
		if res==0:
			client_socket.sendall(b'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<h1>Hello World</h1>')
		else:
			initKey(res['post_userid'],res['post_sign'],res['post_timestamp'],res['post_mes'])
	except Exception as e:
		print(e)
	finally:
		client_socket.close()
def getPost(request_data):
	request_data=str(request_data,encoding="utf8").split('\r\n')
	items=[]
	for item in request_data[1:-2]:
		items.append(item.split(':'))
	post_useful={}
	for i in items:
		post_useful.update({i[0]:i[1]})
	if post_useful.get('sign')==None:
		print('other connect')
		return 0
	else:
		post_sign=post_useful.get('sign').strip()
		post_timestamp=post_useful.get('timestamp').strip()
		
		post_mes=json.loads(request_data[-1])
		post_userid=post_mes.get('senderId').strip()
		post_mes=post_mes.get('text').get('content').strip()

		return {'post_userid':post_userid,'post_sign':post_sign,'post_timestamp':post_timestamp,'post_mes':post_mes}

	
def initKey(post_userid,post_sign,post_timestamp,post_mes):
	#配置token
	whtoken="e3ecf15be053813ee1c14aaba90f1e827645c0249883b349600249c972bcb928"
	#得到当前时间戳
	timestamp = str(round(time.time() * 1000))
	#计算签名
	app_secret = '4YYMR8m1KbVjmngdDBsq7jdIkUIQceFFhcjx1boKdCQ4-lIxbs3EiKZAoprYvk1b'
	app_secret_enc = app_secret.encode('utf-8')
	string_to_sign = '{}\n{}'.format(post_timestamp, app_secret)
	string_to_sign_enc = string_to_sign.encode('utf-8')
	hmac_code = hmac.new(app_secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
	sign = base64.b64encode(hmac_code).decode('utf-8')
	print(post_sign)
	print(sign)
	#验证是否来自钉钉的合法请求
	if (abs(int(post_timestamp)-int(timestamp))<3600000 and post_sign==sign):
		webhook = "https://oapi.dingtalk.com/robot/send?access_token="+whtoken+"&timestamp="+timestamp+"&sign="+sign
		header = {
			"Content-Type": "application/json",
			"Charset": "UTF-8"
		}
		#发送消息
		message_json = json.dumps(selectMes(post_userid,post_mes))
		#返回发送状态
		info = requests.post(url=webhook,data=message_json,headers=header)
		print(info.text)
	else:
		print("Warning:Not DingDing's post")

def selectMes(post_userid,post_mes):
	#判断指令选择对应回复
	if(post_mes=='1'):
		send_mes='This is 1'
		return sendText(post_userid,send_mes)
	elif (post_mes=='天气'):
		send_mes=getWeather()
		return sendMarkdown('天气预报',send_mes)
	elif (post_mes=='学习'):
		send_mes=startxuexi()
		return sendMarkdown('猪宝学习',send_mes)
	else:
		return sendText(post_userid,'Not understand')
		
def sendText(post_userid,send_mes):
	#发送文本形式
	message={
		"msgtype": "text",
		"text": {
			"content": send_mes
		},
		"at": {
			"atDingtalkIds": [post_userid], 
		   "isAtAll": False
		}
	}
	return message

def sendMarkdown(title,send_mes):
	#发送Markdown形式
	message={
			"msgtype": "markdown",
			"markdown": {
				"title":title,
				"text": send_mes
			},
			"at": {
			"atDingtalkIds": [],
			"isAtAll": False
			}
		}
	return message
	
def getWeather():
	#爬取天气数据返回的方法，这里就不多编写了
	send_mes='#### 今日天气 \n' \
		'> 9度，西北风1级，空气良89，相对温度73%\n' \
		'> ![screenshot](https://img.alicdn.com/tfs/TB1NwmBEL9TBuNjy1zbXXXpepXa-2400-1218.png)\n' \
		'> ###### 10点20分发布 [天气](https://www.dingalk.com) \n'
	return send_mes
	
def startxuexi():
	send_mes='#### 学习即将开始'
	os.system('sh do.sh')
	return send_mes

if __name__ == "__main__":
	#启动服务,端口9000
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    server_socket.bind(("", 9000))
    server_socket.listen(120)
    while True:
        client_socket, client_address = server_socket.accept()
        print("[%s, %s]用户连接上了" % client_address)
        handle_client_process = Process(target=handle_client, args=(client_socket,))
        handle_client_process.start()
        client_socket.close()


