#기본적인 봇의 기능들 추가
#메세지 삭제, 봇 상태 설정, 기타 기능
import discord
import asyncio
import random

class bot:
  def __init__(self, client):
    self.client = client

  async def delete_user_messages(self,message):#메세지 단일 또는 다중 삭제

    user = message.author
    ctx = message.channel
    che = False
    
    number = message.message.content[4:]
  
    async def delete_message(num,info_user): #num 갯수의 메세지 삭제 다 삭제 후 True return

      counter = 0

      #가져올 메세지의 조건
      def predicate(message):
        return not message.author.bot #not bot message

      async for message in ctx.history(limit=500).filter(predicate):

        #메세지의 user가 명령어 호출한 유저와 같은지 확인
        if message.author == info_user:
          
          await message.delete(delay=0)

          await asyncio.sleep(0.2)

          counter += 1

        #정해진 갯수의 메세지 삭제 후
        if counter == num:
          return True
          break

    # msg에 입력된 값이 없을경우
    if number == '':
      s_msg = await ctx.send(embed=discord.Embed(title=None,description= "삭제할 메세지의 갯수를 입력해주세요", colour=0x7289da))
      await s_msg.delete(delay=3)
    # msg에 숫자값이 입력됬을경우
    elif int(number) > 0:
    #<class 'int'> -> int 타입을 뜻하는 구절
      s_msg = await ctx.send(embed=discord.Embed(title=None,description=
      "3초뒤 "+ str(number) + "개의 메세지 삭제됩니다.", colour=0x7289da))
      await s_msg.delete(delay=3)
      await asyncio.sleep(3)
      che = await delete_message(int(number),user)
      if che == True:
        await asyncio.sleep(int(number)/5)
        s_msg = await ctx.send(embed=discord.Embed(title=None,description=
        "메세지가 삭제되었습니다.", colour=0x7289da))
        await s_msg.delete(delay=3)
    #그 외의 경우
    else:
      s_msg = await ctx.send(embed=discord.Embed(title=None,description= "잘못된 값이 입력되었습니다.", colour=0x7289da))
      await s_msg.delete(delay=3)

  async def set_status(self,msg):  #봇 상태 바꾸기
    ctx = msg.channel
    msg = msg.message.content[4:]

    await self.client.change_presence(activity=discord.Game(name=msg))
    s_msg = await ctx.send(embed = discord.Embed(title = None, description = "상태 바꿨어요!", colour=0x7289da))

    await s_msg.delete(delay=3)
  
  async def divide_team(self,message):#팀배정 기능

    voice = message.author.voice.channel
    ctx = message.channel

    members = voice.members[:]
  
    members_list = []
    
    count = 0
    
    for i in members:
      if members[count].bot == False:
        members_list.append(members[count].display_name)
      else:
        pass
      
      count += 1

    team_list = [[],[]]

    members_count = len(members_list)

    count = 0

    for i in range(0,members_count): #team_list[0] == 1팀, team_list[1] == 2팀
      choiced_member = random.choice(members_list)
      team_list[count].append(choiced_member)
      members_list.remove(choiced_member)
      if count == 0:
        count = 1
      else:
        count = 0

    await ctx.send(embed=discord.Embed(title= "1팀: " + ' ,'.join(member for member in team_list[0]),colour=0xe74c3c))

    await ctx.send(embed=discord.Embed(title= "2팀: " + ' ,'.join(member for member in team_list[1]),colour=0x3498db))

