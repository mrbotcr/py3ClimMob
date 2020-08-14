#!/usr/bin/python
# -*- coding: utf-8 -*-
# pip install mysqlclient
# pip install pyTelegramBotAPI
import telebot
import MySQLdb
import datetime
import json
from configparser import ConfigParser


config = ConfigParser()
config.read("development.ini")

dConfig = config.__dict__["_sections"].copy()

TOKEN = dConfig["app:climmob"]["telegram.token"]
HOST = dConfig["app:climmob"]["odktools.mysql.host"]
USER = dConfig["app:climmob"]["odktools.mysql.user"]
PASSWORD = dConfig["app:climmob"]["odktools.mysql.password"]
DATABASE = dConfig["app:climmob"]["odktools.mysql.db"]

bot = telebot.TeleBot(TOKEN)
_id = "609114960"

datos = [HOST, USER, PASSWORD, DATABASE]


@bot.message_handler(content_types=["text"])
def opMenuUsuario(message):
    connection = MySQLdb.connect(*datos)
    cursor = connection.cursor()
    if message.reply_to_message:
        chat_id = None

        if str(message.reply_to_message.from_user.id) != _id:
            chat_id = int(message.reply_to_message.message_id) - 1
        else:
            chat_id = int(message.reply_to_message.message_id)

        sql = "SELECT user_name, chat_id, chat_tofrom FROM chat WHERE chat_id = %s"
        data = chat_id
        cursor.execute(sql, [data])
        result = cursor.fetchone()

        if result:
            try:
                send_message = bot.send_message(message.chat.id, "Reply sent")
                sql = "INSERT INTO chat(user_name,chat_id,chat_message,chat_send,chat_read,chat_tofrom,chat_date)VALUES(%s,%s,%s,%s,%s,%s,%s)"
                data = (
                    str(result[0]),
                    int(send_message.message_id),
                    str(message.text),
                    1,
                    0,
                    2,
                    datetime.datetime.now(),
                )
                cursor.execute(sql, data)
                connection.commit()

                if int(result[2] == 1):
                    update = "UPDATE chat SET chat_read = 1 WHERE user_name = %s and chat_tofrom = 1"
                    data = str(result[0])
                    cursor.execute(update, [data])
                    connection.commit()

            except:
                bot.send_message(message.chat.id, "The answer not sent.")
        else:
            bot.send_message(
                message.chat.id, "You answered a message that does not exist."
            )


bot.polling()
