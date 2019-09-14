import json 
import requests
import time
import urllib

from dbhelper import DBHelper

db = DBHelper()


TOKEN = "842323588:AAE-nLEtZaLpw_id5F2lR4UTq8Szfgmcs_g"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js

def get_updates(offset=None):
    url = URL + "getUpdates?timeout=100"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js


def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)

def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

def send_message(text, chat_id, reply_markup=None):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)


def build_keyboard(items):
    keyboard = [[item] for item in items]
    reply_markup = {"keyboard":keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)    

def curr_exchange(curTo):
    base = 'USD'
    to = curTo
    amount = 1
    #print(base,to,amount)

    url = "https://api.exchangeratesapi.io/latest?base=" + base

    response = requests.get(url) 
    data = response.text 
    parsed = json.loads(data) 
    rates = parsed["rates"]
    conversion = None
    for currency, rate in rates.items():
        if currency == to:
            conversion = rate * amount
            #print("1", base, "=", currency, rate)
            #print(amount, base, "=", currency, conversion)
                
    #print(conversion)
    return conversion

def handle_updates(updates):
    for update in updates["result"]:
        text = update["message"]["text"]
        chat = update["message"]["chat"]["id"]
        items = db.get_items(chat)  ##
        #print(items)

#Showing Items
    #send_message("Select Currancy:", chat, None)  #Display the contents here
    keyboard = build_keyboard(items)

    if text in items:
        #print(items)
        newRate = curr_exchange(text.upper())
        send_message(str(newRate), chat, keyboard)
        keyboard = build_keyboard(items)
    else:
        items = db.get_items(chat)
        db.add_item(text, chat)
        send_message("This is a new currency, Successfully added in Database!", chat, keyboard)
        keyboard = build_keyboard(items)


def main():
    db.setup()
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            handle_updates(updates)
        time.sleep(0.5)

if __name__ == '__main__':
    main()