from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
import pandas
import logging
import ssl
import json
from json import JSONEncoder
import discord
 

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        return obj.__dict__

class PyEcoRoot:
    def __init__(self, currency, eco_element):
        self.currency = currency
        self.eco_element = eco_element

class PyEcoElement:
    def __init__(self,currency,event, impact,time_eastern, actual,forecast, previous ):
        self.currency = currency
        self.event = event
        self.impact = impact
        self.time_eastern = time_eastern
        self.actual = actual
        self.forecast = forecast
        self.previous = previous

class PyEcoCal:
    def __init__(self, p1 = 1):
        self.p1 = p1

    def get_economic_calendar(self, date):
        global dict_
        baseURL = "https://www.forexfactory.com/"

        ssl._create_default_https_context = ssl._create_unverified_context
    
        # ctx = ssl.create_default_context()
        # ctx.check_hostname = False
        # ctx.verify_mode = ssl.CERT_NONE
 
        # html = urllib.request.urlopen(url, context=ctx).read()

        # get the page and make the soup
        urleco = baseURL + date

        opener = urllib.request.build_opener()
        #opener = urllib.request.build_
        
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        response = opener.open(urleco)
        result = response.read().decode('utf-8', errors='replace')
        soup = BeautifulSoup(result,"html.parser")
        table = soup.find_all("tr", class_="calendar_row")

        ecoday = []
        for item in table:
            dict_ = {}
        
            dict_["Currency"] = item.find_all("td", {"class":"calendar__currency"})[0].text.strip() #Currency
            dict_["Event"] = item.find_all("td",{"class":"calendar__event"})[0].text.strip() #Event Name
            dict_["Time_Eastern"] = item.find_all("td", {"class":"calendar__time"})[0].text #Time Eastern
            impact = item.find_all("td", {"class":"impact"})


            for icon in range(0,len(impact)):
                  if (impact_value := impact[icon].find_all("span")[0]['title'].split(' ', 1)[0]) == "High":
                        dict_["Impact"] = impact_value
                        dict_["Actual"] = item.find_all("td", {"class":"calendar__actual"})[0].text #Actual Value
                        dict_["Forecast"] = item.find_all("td", {"class":"calendar__forecast"})[0].text #forecasted Value
                        dict_["Previous"] = item.find_all("td", {"class":"calendar__previous"})[0].text # Previous
            if "Impact" in dict_:
                ecoday.append(dict_)
                print(dict_)
        ecoDict=[]
    
        for item in ecoday:
            rec = ComplexEncoder() 
            ecoelem = PyEcoElement(
                 item["Currency"],
                 item["Event"],
                 item["Impact"],
                 item["Time_Eastern"],
                 item["Actual"],
                 item["Forecast"],  
                 item["Previous"]
             )
            rec.ecoobject = ecoelem
            ecoDict.append(rec)

        json_object = json.dumps(ComplexEncoder().encode(ecoDict), indent = 3)  
        return json_object
eco = PyEcoCal()
json = eco.get_economic_calendar("calendar?day=jan11.2023")

intents = discord.Intents.all()
client = discord.Client(command_prefix='!', intents=intents)
 
@client.event
async def on_ready():
    print('We have logged in as ' + client.user.name)
 
@client.event
async def on_message(message):
    if message.author == client.user:
        return
 
 
client.run('YOUR_TOKEN_HERE')
