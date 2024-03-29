import requests as re
from bs4 import BeautifulSoup
import pymongo
import os
import discord
from discord.ext import commands, tasks 
import datetime
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
#try hardcoding the first class


# options = Options()
# options.headless = True
channel = 902770468954734652

mediumbottoken = os.getenv('mediumbottoken')
#mediumclientid = os.getenv('medium-client-id')
#mediumclientsecret = os.getenv('medium-client-secret')
mediumdburl = os.getenv('mediumdburl')



client = pymongo.MongoClient(mediumdburl)
db = client['Medium']

intents = discord.Intents.all()
#intents.guilds = True
#intents.members = True
bot = commands.Bot(command_prefix='!', intents = intents)
bot.remove_command('help')
outputchannel = None
testcounter = 0
classcheckcounter = 0


def pushTag(tag):
    db.create_collection(tag)

def deleteTag(tag):
    db.drop_collection(tag)

def formatClassString(classlist):
    classstring = ''
    length = len(classlist)
    i = 1
    for x in classlist:
        classstring = classstring + x
        if(i < length):
            classstring = classstring + ' '
            i = i + 1
    return classstring


#finds the correct outer class tag for links by finding the highest occurrence class amongst 'a' tags
def findClass():
    request = re.get('https://medium.com/tag/avax')
    source = request.content
    classdict = {}

    soup = BeautifulSoup(source, 'html.parser')

    for a in soup.find_all('a'):

        rawclass = a.get('class')
        if(rawclass != None):
            classname = formatClassString(a.get('class'))

            if(classdict.get(classname) == None):
                classdict.update({classname : 1})
            else:
                classdict[classname] += 1
    value = 0
    key = ''
    for k, v in classdict.items():
        if(v > value):
            value = v
    
    for k, v in classdict.items():
        if(v == value):
            key = key + k

    print(classdict)
    db['tags'].update_one({'name' : 'outerclass'}, {'$set' : {'outerclass' : key}})
    #return key

def getTime():
    nowdate = datetime.datetime.utcnow()


def getHTML(tag):
    options = Options()
    #options.binary_location = os.environ.get('GOOGLE_CHROME_BIN')
    #options.headless = True
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--ignore-certificate-errors')
    #options.add_argument('--disable-dev-sh-usage')
    options.add_argument('enable-automation')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1420,1080')
    #options.add_argument("window-size=1920,1080")
    #driver = webdriver.Chrome(executable_path = "C:\\Users\Dominick\Desktop\chromedriver.exe", options = options)
    #driver = webdriver.Chrome(executable_path= os.environ.get('CHROMEDRIVER_PATH'), options= options)
    driver = webdriver.Chrome(options= options)
    driver.get('https://medium.com/tag/' + tag + '/latest')
    print(driver.page_source)
    print(tag)
    
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:

        # Scroll down to the bottom.
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load the page.
        time.sleep(5)

        # Calculate new scroll height and compare with last scroll height.
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:

            break

        last_height = new_height

    html = driver.page_source
    return html

def searchtags(tag):
    global db

    # classes = db['tags'].find({'tag' : tag}, {'_id' : 0, 'innerclass' : 1, 'outerclass' : 1})
    # classlist = []
    # for x in classes:
    #     classlist.append(x)

    # innerclass = classlist[0]['innerclass']
    # outerclass = classlist[0]['outerclass']
    
    page = getHTML(tag)
    soup = BeautifulSoup(page, 'html.parser')
    
    listoflinks = []
    testcase = ['gv', 'l']
    
    #All links to articles currently have this class value
    for link in soup.find_all('a', class_ = db['tags'].find_one({'name' : 'outerclass'} , {'_id' : 0, 'name' : 0})['outerclass']):
        classdict = link.parent.attrs
        try:
            print(classdict['class'])
            linkclass = formatClassString(classdict['class'])

        # Links that lead to a sign in are for premium and must be removed
        #furthermore links without proper https://medium.com must have it added 
        #Links can be the same but have different query values upon each search so
        #query values are removed
        #All is done only if the length of the class value of the href containing tag is 2. This 
        #ensures that only links to articles are checked and not that of say a button
            if(len(classdict['class']) == 2):
                
                livelink = str(link.get('href'))
                if(livelink.startswith('/m/signin') == False):
                    if(livelink.startswith('https://') == False):
                        livelink = ('https://medium.com' + livelink)
                    livelink = livelink.split('?', 1)[0]
                    check = db[tag].find({'link' : livelink})
                    if(check.count() == 0):
                        db[tag].insert_one({'link' : livelink})
                        listoflinks.append(livelink)    
        except Exception:
            pass
   
    print(listoflinks)
    return listoflinks

@bot.event
async def on_ready():
    global channel
    global outputchannel
    print(f'{bot.user} has connected to Discord!')
    #channel = bot.get_channel(902420735912468490)
    outputchannel = bot.get_channel(channel)
    #test()
    if not search.is_running():
        search.start()

@bot.command()
async def addTag(ctx, arg):
    pushTag(arg.casefold())
    await ctx.channel.send(arg + 'Will now be monitored!')

@bot.command()
async def removeTag(ctx, arg):
    deleteTag(arg.casefold())
    await ctx.channel.send(arg + 'Will no longer be monitored')

@bot.command()
async def hello(ctx):
    await ctx.channel.send('Hello!')

@bot.command()
async def listTags(ctx):
    global db
    collectionlist = db.list_collection_names()
    collectionstring = ''

    for x in collectionlist:
        collectionstring = collectionstring + x +'\n'
    await ctx.channel.send(collectionstring)
    

@bot.command()
async def help(ctx):
    embed = discord.Embed(
        colour = discord.Colour.orange(),
        title = 'Help'
    )
    embed.add_field(name='!addTag tag', value='Adds a Medium tag for the bot to monitor. Bot will post articles published after the time of adding the tag', inline = False)
    embed.add_field(name='!removeTag tag', value ='Removes a tag from the list of tags to be monitored', inline=False)
    embed.add_field(name='!listTags', value='Lists all of the tags currently being monitored', inline=False)
    await ctx.channel.send(embed=embed)

def test():
    chan = None
    chan = bot.get_channel('902420735912468490')
    print(chan)

@tasks.loop(seconds = 60 * 60)
async def search():
    global outputchannel
    global mediumbottoken
    global classcheckcounter
    taglist = db.list_collection_names()
    print(taglist)
    listoflinks = []
    stringoflinks = ''
    for x in taglist:
        if(x != 'tags'):
            resultlist = searchtags(x)
            for y in resultlist:
                listoflinks.append(y)

    print(listoflinks)
    
    for x in listoflinks:
        #await(channel.send(x))


        stringoflinks = stringoflinks + x +'\n'

    if(len(stringoflinks) < 2000 and len(stringoflinks) > 0):
        await(outputchannel.send(stringoflinks))

    classcheckcounter += 1

    if(classcheckcounter == 5):
        findClass()
        classcheckcounter = 0

if testcounter == 0:
    bot.run(mediumbottoken)
    testcounter = testcounter + 1









    

