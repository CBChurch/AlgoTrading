import ConfigParser
import time
import random
import datetime
import telepot
from telepot.loop import MessageLoop

config = ConfigParser.ConfigParser()
config.read("../config/cred.config")

token = config.get("configuration","GoogleVMBot")

def handle(msg):
    chat_id = msg['chat']['id']
    command = msg['text']

    print 'Got command: %s' % command

    if command == '/roll':
        bot.sendMessage(chat_id, random.randint(1,6))
    elif command == '/time':
        bot.sendMessage(chat_id, str(datetime.datetime.now()))

bot = telepot.Bot(token)

MessageLoop(bot, handle).run_as_thread()
print 'I am listening ...'

while 1:
    time.sleep(10)