import discord
import asyncio
import random
import aiohttp
import cchardet
import aiodns
import pycares
from multiprocessing import Process
from discord.ext import commands


import os 
import time as tm
import requests
import numpy as np
import pandas as pd
import json
import datetime as dt
 
from pytz import timezone
from collections import Counter

class cypers_searcher:
  block ='''
```유저 이름: {}

클랜: {}
티어: {}

일반 승률: {}%
승: {}, 패: {}, 탈주: {}

공식 승률: {}%
승: {}, 패: {}, 탈주: {}
```'''

  
  def __init__(self,client,cyp_TOKEN,message):#클래스 변수 세팅
    self.client = client
    self.cyp_TOKEN = cyp_TOKEN
    self.ctx = message.channel
    self.user = message.author
    self.message = message

    self.limit = 200  #매치 id limit 

    self.cypers_user_name = ''

  async def get_info(self,message):#기본 정보 가져오기
    '''
    parameter = 'message'

    returns:
      player_info_data:
        'playerid':playerId,
        'nickname':nickname,
        'grade':grade
    '''
    msg = message.message.content
    
    search_name = msg[4:]

    print(search_name)

    try:

      url = "https://api.neople.co.kr/cy/players?nickname=" + search_name + "&wordType=match&apikey=" + self.cyp_TOKEN

      dict = requests.get(url).json()

      playerId = dict['rows'][0]['playerId']#유저 고유 아이디
      nickname = dict['rows'][0]['nickname']#유저 닉네임
      grade = dict['rows'][0]['grade']#유저 급수

      self.cypers_user_name = nickname #뒤에 포지션 끌어오기에서 쓸 예정

      player_info_data = {'playerid':playerId,
                          'nickname':nickname,
                          'grade':grade}

      return  player_info_data #기본 정보 반환

    except IndexError:
        msg = await self.ctx.send(embed=discord.Embed(title=None,description= "검색할 유저의 닉네임을 입력해주세요"))
        await msg.delete(delay=3)
        return IndexError

    except requests.exceptions.RequestException:
      await self.ctx.send(embed=discord.Embed(title="서버가 응답하지 않습니다."))
      await msg.delete(delay=3)

  async def get_vict(self,playerId):#승리,패배,탈주 정보 가져오기

    url = "https://api.neople.co.kr/cy/players/" + playerId + "?apikey=" + self.cyp_TOKEN
  
    dict = requests.get(url).json()
  
    #1. 공식과 일반 둘다 존재하는 경우
    #2. 일반만 존재 하는 경우(공식 조건 안되는 경우가 이에 해당함)
    #3. 둘다 존재 안하는 경우(협력만 돌렸거나, 랭크가 1인경우가 이에 해당함)
    
    print(dict)
    #공식 매치 결과 기본값
    rank_wincount = 0
    rank_lostcount = 0
    rank_stopcount = 0

    #일반 매치 결과 기본값
    normal_wincount = 0
    normal_losecount = 0
    normal_stopcount = 0

    if dict['records'] == []:
      discord_message = await self.ctx.send(embed=discord.Embed(title=None,description= "일반, 공식 기록이 없습니다."))
      await discord_message.delete(delay=3)

    #일반전
    elif dict['records'][0]['gameTypeId'] == 'normal':
      normal_wincount = dict['records'][1]['winCount']
      normal_losecount = dict['records'][1]['loseCount']
      normal_stopcount = dict['records'][1]['stopCount']

    #공식전
    else:
      #공식 기록
      rank_wincount = dict['records'][0]['winCount']
      rank_lostcount = dict['records'][0]['loseCount']
      rank_stopcount = dict['records'][0]['stopCount']
      #일반 기록
      normal_wincount = dict['records'][1]['winCount']
      normal_losecount = dict['records'][1]['loseCount']
      normal_stopcount = dict['records'][1]['stopCount']


    play_count_dict = {
    "normal": [normal_wincount,normal_losecount,normal_stopcount],
    "rank":[rank_wincount,rank_lostcount,rank_stopcount],
    "clantier":[dict['clanName'],dict['tierName']]
    }

    return play_count_dict
  
  async def get_match(self,playerId):#매치 정보 가져오기
    ''' 
      returns:
        dict
    '''
    #시간 설정
    now = dt.datetime.now(timezone('Asia/Seoul'))
    now_time = dt.datetime.strftime(now, "%Y-%m-%d %H:%M")
    past = now - dt.timedelta(days=30)
    past_time = dt.datetime.strftime(past, "%Y-%m-%d %H:%M")      

    try:
      url = "https://api.neople.co.kr/cy/players/" + str(playerId) + "/matches?gameTypeId=normal&startDate=" + str(past_time) + "&endDate=" + str(now_time) + "&limit=" + str(self.limit) + "&apikey=" + self.cyp_TOKEN #30일 기준 최대 200판 까지

      dict = requests.get(url).json()

      #print(dict,sep = '\n')

      return dict

    except requests.exceptions.RequestException:
          msg = await self.ctx.send(embed=discord.Embed(title="서버가 응답하지 않습니다."))
          await msg.delete(delay=3)
    
    except Exception as ex:
      print(ex)

  def get_character(self,dict, limit = 200): #각 매치의 유저의 플레이한 캐릭터 가져오기, 제한판수 입력 없을시 self.limit 값 들어감
    '''
      returns:
        character_name_list
    '''
    character_name_list = []

    try:
      for i in range(0, limit):
        count = dict['matches']['rows'][i]['playInfo']['characterName']
        #전적이 리미트에 다 다 채워지지 않을 경우
        character_name_list.append(count)

    #50판이 다 채워지지 않은 상황이면 for문 중간에 IndexError가 떠서 return 값이 제대로 return이 되지 않음
    except IndexError:#아무것도 없을 경우 
      print('get_character: IndexError')
      pass
      
    return character_name_list


  def get_party_list(self,dict): #각 매치 판의 파티원 수 가져오기
    party_count_list = []
    
    try:
      for i in range(0, self.limit):
        count = dict['matches']['rows'][i]['playInfo']['partyUserCount']
        party_count_list.append(count)

    except IndexError:#아무것도 없을 경우 
      print('get_party_list: IndexError')
      pass

    return party_count_list

  def get_start_playtime(self,dict): #각 매치의 시작한 시간 가져오기
    time_count = []
    
    try:
      for i in range(0, self.limit):
        time = dict['matches']['rows'][i]['date'][11:13]
        time_count.append(time)
    
    except IndexError:#아무것도 없을 경우 
      print('get_start_playtime: IndexError')
      pass

    return time_count


  def get_matchid(self,dict): #각 매치의 고유 ID 가져오기
    matchid_list = [] 

    try:
      for i in range(0, int(self.limit)):
        matchid = dict['matches']['rows'][i]['matchId']
        matchid_list.append(matchid)

    except IndexError:#아무것도 없을 경우 
      print('get_matchid: IndexError')
      pass

    return matchid_list
  
  def get_match_result(self,dict): #각 매치 결과 가져오기

    result_list = []

    try:
      for i in range(0,self.limit):
        result = dict['matches']['rows'][i]['playInfo']['result']
        result_list.append(result)

    except IndexError:#아무것도 없을 경우 
      print('get_match_result: IndexError')
      pass

    return result_list

  def get_match_kda(self,dict): #각 매치 kda, 피해량 등 가져오기
    kill_count_list = []
    death_count_list = []
    assist_count_list = []
    attack_count_list = []
    damage_count_list = []
    battle_count_list = []
    sight_count_list = []
    playtime_count_list = []

    '''
      "playInfo":
      "result" : "(win,lose)",
      "random" : (bool),
      "partyUserCount" : (int),
      "characterId" : "***",
      "characterName" : "---",
      "level" : (int),
      "killCount" : (int),
      "deathCount" : (int),
      "assistCount" : (int),
      "attackPoint" : (int),
      "damagePoint" : (int),
      "battlePoint" : (int),
      "sightPoint" : (int),
      "playTime" : (int)
    '''

    try:
      for i in range(0,self.limit):
        kill_count = dict['matches']['rows'][i]['playInfo']['killCount']
        death_count = dict['matches']['rows'][i]['playInfo']['deathCount']
        assist_count = dict['matches']['rows'][i]['playInfo']['assisCount']
        attack_count = dict['matches']['rows'][i]['playInfo']['atttackPoint']
        damage_count = dict['matches']['rows'][i]['playInfo']['damagePoint']
        battle_count = dict['matches']['rows'][i]['playInfo']['battlePoint']
        sight_count = dict['matches']['rows'][i]['playInfo']['sightPoint']
        playtime_count = dict['matches']['rows'][i]['playInfo']['playTime']

        kill_count_list.append(kill_count)
        death_count_list.append(death_count)
        assist_count_list.append(assist_count)
        attack_count_list.append(attack_count)
        damage_count_list.append(damage_count)
        battle_count_list.append(battle_count)
        sight_count_list.append(sight_count)
        playtime_count_list.append(playtime_count)


  
    except IndexError:
      return False

  async def get_position_info(self,matchid):#포지션 정보 크롤링
      async with aiohttp.ClientSession() as client:
        async with client.get('https://api.neople.co.kr/cy/matches/'+ matchid + '?&apikey=' + self.cyp_TOKEN) as resp:

          if resp.status == 400:
            print("error")
            raise IndexError
              
          if resp.status == 200:
            pass
            #print("done")

          temp_dict = await resp.text()

          temp_dict = json.loads(temp_dict)
      
          try:
              for i in range(0, 10):
                  if temp_dict['players'][i]['nickname'] == self.cypers_user_name:
                      position_name = temp_dict['players'][i]['position']['name']
                  
          except IndexError:
              pass

         
          return position_name

  async def sync_get_position(self,matchid_list):#포지션 함수 비동기 처리
    
    coroutines = (self.get_position_info(matchid) for matchid in matchid_list)

    return await asyncio.gather(*coroutines)

  async def fetch_position_info(self,matchid_list):#포지션 리스트로 내보내기

    position_dict = []

    for i in range(0,int(len(matchid_list) / 25) + 1):
      for i,response in enumerate(await self.sync_get_position(matchid_list[25*i : 25*(i+1)])): # 1초에 50개 이상 요청시 error 뜨기 때문에 25개로 나눠서 텀을 둠
        position_dict.append(response)
      
      print("delayed 1.0 second")
      await asyncio.sleep(delay = 1.0, result = "delayed")

    #for key, value in position_dict.items():
     # print('{} : {}'.format(key,value))

    return position_dict

  def count_most_common(self,list): #가장 많이 나온 요소 가져오기
    '''
      return:
        most_list: "(1번값)": "(나온 횟수)"
    
    '''

    most_list = Counter(list).most_common(1)
    return most_list

  async def send_basic_record(self,search_message): #기본 전적 discord 메세지 보내기
    player_info_data = await self.get_info(search_message)
    vict_count_dict = await self.get_vict(player_info_data['playerid'])

    try: 
      normal_countkda = vict_count_dict['normal'][0] /(vict_count_dict['normal'][0] + vict_count_dict['normal'][1]) 
      vict_normal_persent = round(normal_countkda * 100 , 2)
    except:
      vict_normal_persent = 0

    try:
      rank_countkda = vict_count_dict['rank'][0] / (vict_count_dict['rank'][0] + vict_count_dict['rank'][1])

      vict_rank_persent = round(rank_countkda * 100 , 2)
    except:
      vict_rank_persent = 0

    basic_info = self.block.format(player_info_data['nickname'],
              *vict_count_dict['clantier'],
               vict_normal_persent, *vict_count_dict['normal'],
               vict_rank_persent, *vict_count_dict['rank'])
    
    await self.ctx.send(basic_info)

  async def send_top_chars(self,search_message): #최근 50판중 most 7 캐릭터 discord 출력
    player_info_data = await self.get_info(search_message)

    dict = await self.get_match(player_info_data['playerid'])

    character_name_list = self.get_character(dict,50)
    print(character_name_list)

    most_charlist = Counter(character_name_list).most_common(7)

    send_list = []

    for i, char in enumerate(most_charlist,start=1):
      send_list.append("{}. {} : {}판".format(i,char[0],char[1]))


    send_message = ""

    for list in send_list:
      send_message += list + '\n' 

    await self.ctx.send(f"```{player_info_data['nickname']}의 최근 50판 중 TOP 7\n{send_message}```")

  async def send_prefer_info(self,search_message):#유저 선호 정보들 출력 (포지션, 시간대, 파티원, 최근 승률)
    player_info_data = await self.get_info(search_message)

    dict = await self.get_match(player_info_data['playerid'])

    matchid_list = self.get_matchid(dict) #매치 id 리스트
    party_count_list = self.get_party_list(dict) #선호 파티 구성
    match_result_list = self.get_match_result(dict) #최근 승률 계산
    playtime_count_list = self.get_start_playtime(dict) #선호 시작 시간대
    position_list = await self.fetch_position_info(matchid_list)#포지션 리스트
    most_time = self.count_most_common(playtime_count_list)#시작 시간 리스트

    user_nickname = player_info_data['nickname'] + '\n'

    time_count = most_time[0][0] + '시'

    position_list = Counter(position_list).most_common(4)
    
    try:
      win_count = Counter(match_result_list).get('win')
      lose_count = Counter(match_result_list).get('lose')

      if lose_count == None:
        win_persent = '100%'
      elif win_count == None:
        win_persent = '0%'
      else:
        win_persent = str(round(win_count/(win_count+lose_count) * 100,2)) + '%'
    except:
      await self.ctx.send('전적이 존재하지 않거나 오류입니다.')

    party_count = str(Counter(party_count_list).most_common(1)[0][0]) + '명'
    
    list = [user_nickname,time_count,win_persent,party_count]
    text_list = ['유저이름: ','선호 플레이 시간대: ','최근 승률: ','선호 파티구성: ']

    send_message = ''
    for k,i in zip(text_list,list):
      send_message += k + i + "\n"
    send_message += '\n최근 플레이한 포지션\n'
    for i,k in enumerate(position_list):
     send_message += position_list[i][0] + ': ' + str(position_list[i][1]) + '판' + '\n'

    await self.ctx.send(f"```{send_message}```")
      
      


    

