import discord
import asyncio
import aiohttp
import io
import requests


class get_images:

  def __init__(self,client,message):#기본 정보 세팅
    self.client = client
    self.ctx = message.channel
    self.user = message.author
    self.message = message

  custom_images_dict = {
    "울지참":"https://cdn.discordapp.com/attachments/646877332187119616/665544158773248021/IMG_20200111_093841.jpg",
    "오르카":"https://cdn.discordapp.com/attachments/646154916288790541/674192386703753216/95ce8ba75d0986dd.jpg",
    "제이":"https://cdn.discordapp.com/attachments/646154916288790541/674201337210077194/j.jpg",
    "갑수냥이들":"https://cdn.ppomppu.co.kr/zboard/data3/2019/0910/m_20190910001740_upyzieih.jpeg",
    }

  async def send_custom_image(self,message): #따로 지정한 이미지 보내기

    result = False

    for key, value in self.custom_images_dict.items():
      if key == message:

        file_url = value

        await self.get_image_jpg(file_url)

        result = True
        break

    return result

  async def send_random_image(self,message):

    if message == "냥이.gif":

      file_url = self.getCatGif()

      await self.get_image_gif(file_url)
      
    if message == "냥이":
      
      file_url = self.getCatPicture()

      await self.get_image_jpg(file_url)
    
  async def get_image_jpg(self,url): #url에서 jpg 파일 가져오기

    file_url = url

    async with aiohttp.ClientSession() as session:
      async with session.get(file_url) as resp:
        if resp.status != 200:
          return await self.ctx.send('Could not download file...')
        
        data = io.BytesIO(await resp.read())

    await self.ctx.send(file=discord.File(data, 'image.jpg'))

    return True

  async def get_image_gif(self,url): #url에서 gif 파일 가져오기

    file_url = url

    async with aiohttp.ClientSession() as session:
      async with session.get(file_url) as resp:
        if resp.status != 200:
          return await self.ctx.send('Could not download file...')
        data = io.BytesIO(await resp.read())

    await self.ctx.send(file=discord.File(data, 'image.gif'))

    return True
 
  def getCatGif(self): #랜덤 고양이 gif url 가져오기
    catGif = requests.get('http://thecatapi.com/api/images/get?format=src&type=gif')
    if catGif.status_code == 200:
        catGif = catGif.url
        return catGif

    else:
        return 'Error 404. Website may be down.'

  def getCatPicture(self): #랜덤 고양이 jpg url 가져오기
      catPicture = requests.get('http://thecatapi.com/api/images/get.php')
      if catPicture.status_code == 200:
          catPicture = catPicture.url
          return catPicture

      else:
          return 'Error 404. Website may be down.'

  