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
outputchannel = bot.get_channel(channel)
testcounter = 0


def pushTag(tag):
    db.create_collection(tag)
    taglist = predictTagFilter(tag)

    db['tags'].insert_one({'tag' : tag, 'innerclass' : taglist[0], 'outerclass' : taglist[1]})

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

def predictTagFilter(tag):
    linkclass = None
    classstring = ''
    outerclassstring = ''
    request = re.get('https://medium.com/tag/' + tag + '/top/year')
    soup = BeautifulSoup(request.content, 'html.parser')
    for linkhtml in soup.find_all('a'):
        #if((linkhtml.attrs['href']).startwith('/m/signin') == False and linkhtml.attrs['href'].startwith('https://medium.com') == False):
        if(str(linkhtml.get('href')).startswith('/m/signin') == False and str(linkhtml.get('href')).startswith('https://medium.com') == False and str(linkhtml.get('href')).startswith('https') == True):
            if(linkhtml.get('class') != None):
                linkclass = linkhtml.get('class')
                classstring = formatClassString(linkclass)
                print(classstring)
                break
    request2 = re.get('https://medium.com/tag/' + tag + '/latest')
    soup2 = BeautifulSoup(request2.content, 'html.parser')

    for x in soup2.find_all('a', class_ = classstring):
        classdict = x.parent.attrs
        #print('hello')
        try:
            linkclass = classdict['class']
            if(len(linkclass) == 2):
                outerclassstring = formatClassString(linkclass)
                print(outerclassstring)
                break

            
        except Exception:
            pass
    return [classstring, outerclassstring]

def getTime():
    nowdate = datetime.datetime.utcnow()

# def predictTagFilter(tag):
#     request = re.get('https://medium.com/tag/' + tag + '/top/year')
#     soup = BeautifulSoup(request.content, 'html.parser')
#     soup.find('a')

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
    for link in soup.find_all('a', class_ = 'er es et eu ev ew ex ey ez fa fb fc fd fe ff'):
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
    print(f'{bot.user} has connected to Discord!')
    channel = bot.get_channel(902420735912468490)
    #test()
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
    embed.add_field(name='Format', value='Keep tag names all lowercase when adding.')
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

    if(len(stringoflinks) < 4000 and len(stringoflinks) > 0):
        await(outputchannel.send(stringoflinks))

if testcounter == 0:
    bot.run(mediumbottoken)
    testcounter = testcounter + 1









    

