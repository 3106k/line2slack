# -*- coding: utf-8 -*-

import MySQLdb
import time
import logger
import urllib
import json
import os
import sys, codecs
MODE = sys.argv

import slack
from requests_oauthlib import OAuth1Session
from slackbot.bot import Bot
from requests import get as GET
from requests import post as POST
from time import sleep
import yaml
from datetime import date, datetime, timedelta

"""
LINE@のフォロワーを取得してDBに入れるよ
"""

# ymlにDBのID/PW類を入れておく
with open('./conf/conf.yml', 'r') as yml:
    config = yaml.load(yml)

HOST     = config[MODE[1]]['database']['host']
DB       = config[MODE[1]]['database']['db']
USER     = config[MODE[1]]['database']['user']
PASSWORD = config[MODE[1]]['database']['password']
CHARSET  = config[MODE[1]]['database']['charset']
TOKEN    = config[MODE[1]]['slack-token']

# logger使ってる
log      = logger.logger('hoge')

today = datetime.today()
yesterday = today - timedelta(days=1)
day = datetime.strftime(yesterday, '%Y%m%d')

## Bearrer のところにline@のauth keyを入れる
headers = {
    'Content-Type':'application/json',
    'Authorization': 'Bearer hogehoge'
}

def main():

    connect = MySQLdb.connect(host=HOST,db=DB,user=USER,passwd=PASSWORD,charset='utf8mb4')
    connect.cursor(MySQLdb.cursors.DictCursor)
    cur = connect.cursor()
    
    # LINE@のエンドポイントに投げる
    res = GET("https://api.line.me/v2/bot/insight/followers?date=" + day , headers=headers)
    data = json.loads(res.text)

    try:
    	
    	"""
    		table line_summary 
    		id int primary key auto_increment
    		followers int default 0
    		targeted_reaches int default 0
    		blocks int default 0
    	"""
        cur.execute("INSERT INTO line_summary( followers, targeted_reaches, blocks ) values ( %s, %s, %s )", (data['followers'], data['targetedReaches'], data['blocks'],))
        connect.commit()
    except Exception as e:
        log.error(data)
        connect.rollback()
        log.error(e)
        raise e

    try:
        client = slack.WebClient(token=TOKEN)
        output = '''
```
LINE登録数:{number}件 / ブロック{block}件
```
'''.format(number=data['followers'], block=data['blocks']).strip()

        r = client.chat_postMessage(
            channel= TARGET,
            text=output
        )
        log.info(TARGET+ ' slack update')

    except Exception as e:
        connect.rollback()
        log.error(e)
        raise e
    finally:
        log.info(' slack finished')
