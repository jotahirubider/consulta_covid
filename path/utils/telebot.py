# -*- coding: utf-8 -*-
import telebot
import os

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_ID"]
bot = telebot.TeleBot(TOKEN)

def send_msg(body):
    bot.send_message(CHAT_ID, body)
