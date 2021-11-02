import requests as re
from bs4 import BeautifulSoup
import pymongo
import os
import discord
from discord.ext import commands, tasks 
import datetime


# options = Options()
# options.headless = True
channel = None

mediumbottoken = os.getenv('medium-bot-token')
#mediumclientid = os.getenv('medium-client-id')
#mediumclientsecret = os.getenv('medium-client-secret')
mediumdburl = os.getenv('medium-db-url')

client = pymongo.MongoClient(mediumdburl)
db = client['Medium']

intents = discord.Intents.all()
#intents.guilds = True
#intents.members = True
bot = commands.Bot(command_prefix='!', intents = intents)
bot.remove_command('help')
testcounter = 0


def pushTag(tag):
    db.create_collection(tag)

def deleteTag(tag):
    db.drop_collection(tag)

def getTime():
    nowdate = datetime.datetime.utcnow()

def searchtags(tag):
    global db

    headers = {
       # ':authority' : 'medium.com',
       # ':method' : 'GET',
       # ':path' : '/tag/crypto/latest',
       # ':scheme' : 'https',
        'accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding' : 'gzip, deflate, br',
        'accept-language' : 'en-US,en;q=0.9',
        'sec-ch-ua' : '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile' : '?1',
        'sec-ch-ua-platform' : '"Android"',
        'sec-fetch-dest' : 'document',
        'sec-fetch-mode' : 'navigate',
        'sec-fetch-site' : 'none',
        'sec-fetch-user' : '?1',
        'upgrade-insecure-requests' : '1',
        'user-agent' : 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Mobile Safari/537.36'
    }

    request = re.get('https://medium.com/tag/' + tag + '/latest', headers= headers)
    
    soup = BeautifulSoup(request.content, 'html.parser')
    listoflinks = []
    
    for link in soup.find_all('a', class_ = 'er es et eu ev ew ex ey ez fa fb fc fd fe ff'):
        livelink = str(link.get('href'))
        if(livelink.startswith('/m/signin') == False):
            if(livelink.startswith('https://') == False):
                livelink = ('https://medium.com' + livelink)
            check = db[tag].find({'link' : livelink})
            if(check.count() == 0):
                db[tag].insert_one({'link' : livelink})
                listoflinks.append(livelink)
                print('yo')
    print(listoflinks)
    return listoflinks

@bot.event
async def on_ready():
    global channel
    print(f'{bot.user} has connected to Discord!')
    channel = bot.get_channel(902420735912468490)
    test()
    if not search.is_running():
        search.start()

@bot.command()
async def addTag(ctx, arg):
    pushTag(arg)
    await ctx.channel.send(arg + 'Will now be monitored!')

@bot.command()
async def removeTag(ctx, arg):
    deleteTag(arg)
    await ctx.channel.send(arg + 'Will no longer be monitored')

@bot.command()
async def hello(ctx):
    await ctx.channel.send('Hello!')

@bot.command()
async def help(ctx):
    embed = discord.Embed(
        colour = discord.Colour.orange(),
        title = 'Help'
    )
    embed.add_field(name='!addTag tag', value='Adds a Medium tag for the bot to monitor. Bot will post articles published after the time of adding the tag', inline = False)
    embed.add_field(name='!removeTag tag', value ='Removes a tag from the list of tags to be monitored')
    await ctx.channel.send(embed=embed)

def test():
    chan = None
    chan = bot.get_channel('902420735912468490')
    print(chan)

@tasks.loop(seconds = 60 * 60)
async def search():
    global channel
    global mediumbottoken
    taglist = db.list_collection_names()
    print(taglist)
    listoflinks = []
    stringoflinks = ''
    for x in taglist:
        resultlist = searchtags(x)
        for y in resultlist:
            listoflinks.append(y)

    print(listoflinks)
    
    for x in listoflinks:
        await(channel.send(x))
   #     stringoflinks = stringoflinks + x +'\n'

  #  if(len(stringoflinks) < 4000 and len(stringoflinks) > 0):
  #      await(channel.send(stringoflinks))

if testcounter == 0:
    bot.run(mediumbottoken)
    testcounter = testcounter + 1









    

