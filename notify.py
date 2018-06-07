import logging
import telegram

key     = 'PAST_API_KEY_HERE'
chatid  = 372188992

def notify_log(msg):
    logging.basicConfig(filename='SRSI_bot.log',format='%(asctime)s: %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')
    bot = telegram.Bot(token=key)
    bot.send_message(chat_id=chatid, text=msg)
    logging.warning(msg)
