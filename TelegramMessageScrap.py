import asyncio
from telethon.sync import TelegramClient
from telethon.sync import TelegramClient
from telethon import events
from twilio.rest import Client
import requests
import json
from flask import Flask, jsonify, request
import threading
import os

#Its better to Make this an different file like .env

#We store images in 3rd party cloud and API ID is stored in mgur_client_secert
imgur_client_id="0ceXXXXXX13c6"

#We store images in 3rd party cloud and API key is stored in mgur_client_secert
imgur_client_secert="6f729fXXXXXXXXXXXXXX0972fdbc1"

#Api ID for Telegram account
api_id=28334974

#Api hash for Telegram account
api_hash='a3e0133XXXXXXXXXXXX823'

#Telegram groups to be filtered
groupNames=['F1_Visa_Slots_Only']

#Filtering based on keywords
listOfChennaiKeyWord=["chennai","che","open","hyderabad","hyd","present","available"]

notConditions=[]

# Numbers to be notified with the bot
numbers=["+919XXXXXXX69","+919XXXXXXX75"]

app=Flask(__name__)

@app.route('/telegrambot/filters', methods=['GET'])
def get_telegrambot_filters():
    conditions={"or":listOfChennaiKeyWord,"not":notConditions}
    return jsonify(conditions)

@app.route('/telegrambot/filters', methods=['POST'])
def post_telegrambot_filters():
    global listOfChennaiKeyWord,notConditions
    conditions=json.loads(request.data)
    if "or" in conditions.keys():
        listOfChennaiKeyWord=conditions["or"]
    if "not" in conditions.keys():
        notConditions=conditions["not"]
    return jsonify({"Result":"Updated"})

@app.route('/telegrambot/contactnumbers', methods=['GET'])
def get_telegrambot_contact():
    conditions={"numbers":numbers}
    return jsonify(conditions)

@app.route('/telegrambot/contactnumbers', methods=['POST'])
def post_telegrambot_contact():
    global numbers
    conditions=json.loads(request.data)
    if "numbers" in conditions.keys():
        numbers=conditions["numbers"]
    return jsonify({"Result":"Updated"})


def upload_image_to_imgur(image_path, client_id):
    url = "https://api.imgur.com/3/image"
    headers = {'Authorization': 'Client-ID ' + client_id}

    with open(image_path, 'rb') as file:
        files = {'image': file}
        response = requests.post(url, headers=headers, files=files)

        if response.status_code == 200:
            data = response.json()
            print("image",data)
            image_url = data['data']['link']
            return image_url
        else:
            print("Error uploading image:", response.text)
            return None

def sendWhatsapp(ph_no,text,media_url=None):
    print(media_url)
    #Whatsapp account API key and token
    account_sid = 'AC3a4d9dXXXXXXXXXXXXXXXX957d824e'
    auth_token = '1a1253XXXXXXXXXXXXXXXXXXXdc40'
    client = Client(account_sid, auth_token)
    message_params = {
        'from_': 'whatsapp:+141XXXXXX86',
        'body': "Text  : "+text + "\nImage : "+str(media_url),
        'to': 'whatsapp:' + ph_no
    }
    #if media_url:
    #    message_params['media_url'] = [media_url]
    message = client.messages.create( **message_params)
    return "Sent"
    

def conditionsMatch(str):
    for i in notConditions:
        if i.lower() in str.lower():
            return False
    for i in listOfChennaiKeyWord:
        if i.lower() in str.lower():
            return True
    return False

def deleteUploadedImageInLocal(media):
    if os.path.exists(media):
        os.remove(media)

def startAlert():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    for group in groupNames:
        print("Service started")
        with TelegramClient("StaticSession1",api_id=api_id,api_hash=api_hash) as client:
            @client.on(events.NewMessage(chats=group))
            async def handle_new_message(event):
                print(event.message.text)
                if event.message.media:
                    media = await event.message.download_media()
                    print("Received media:", media)
                    url=upload_image_to_imgur(media,imgur_client_id)

                    print(url)
                    temp= [ sendWhatsapp(n, str(event.message.text),url) for n in numbers]
                elif conditionsMatch(event.message.text) and len(event.message.text) < 50:
                    print("Notify:", event.message.text)
                    temp= [ sendWhatsapp(n, str(event.message.text)) for n in numbers]
            client.run_until_disconnected()

def flask_service():
    app.run(host='0.0.0.0',port=5000)
def bot_service():
    startAlert()


flask_thread = threading.Thread(target=flask_service)
telegram_thread = threading.Thread(target=bot_service)

flask_thread.start()
telegram_thread.start()

flask_thread.join()
telegram_thread.join()


