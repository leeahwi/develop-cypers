import discord
import asyncio
import os
import aiohttp
import io
import random
import re
import time as tm
import copy

import requests
import numpy as np
import pandas as pd
import json
import datetime as dt
from bs4 import BeautifulSoup
#내가 만들 모듈
from prac import *

from pytz import timezone
from discord.ext import commands
from collections import Counter

#TOKEN = os.environ['BOT_TOKEN']


client = commands.Bot(command_prefix="?")

@client.event
async def on_ready():
    print('Logged in...')
    print('Username: ' + str(client.user.name))
    print('Client ID: ' + str(client.user.id))

  #봇 상태 바꾸기
    botActivity = discord.Activity(name= "점검", type=discord.ActivityType.playing)
    await client.change_presence(activity=botActivity)
  #check it work

###봇 기본 기능 
bot = bot(client)
#메세지 단일 또는 다중 삭제
@client.command()
async def 삭제(message):
  await bot.delete_user_messages(message)
#봇 스탯 바꾸기
@client.command()
async def 상태(message):
  await bot.set_status(message)
#팀배정 하기
@client.command()
async def 팀배정(message):
  await bot.divide_team(message)

###이미지 업로드 관련 기능
@client.command()
async def 이미지(message):
  image = get_images(client,message)
  search_message = message.message.content[5:]

  result = await image.send_custom_image(search_message)

  if result != True:
    await image.send_random_image(search_message)

###사이퍼즈 관련 기능
@client.command()
async def 전적(message):

  search_message = message

  user = message.author

  cyp = cypers_searcher(client,cyp_TOKEN,message)

  list = ["기본 전적","최근 50판중 TOP 7 모스트 캐릭","유저 플레이 선호도","미정"]

  embed = discord.Embed(title = "사이퍼즈 전적 검색기",description = "번호를 입력해주세요.", colour = 0x3498db)
  embed.add_field(name = "기능", value = "1. {}\n2. {}\n3. {}\n4. {}\n".format(*list), inline = True)

  await message.channel.send(embed=embed)

  def check(message):
    return not message.author.bot and message.author == user

  msg = await client.wait_for('message', check=check)

  if msg.content == '1':
    await cyp.send_basic_record(search_message)
  elif msg.content == '2':
    await cyp.send_top_chars(search_message)
  elif msg.content == '3':
    await cyp.send_prefer_info(search_message)
    

client.run(TOKEN)

#'\u200b' -> 빈공간
#"\n\u200b"