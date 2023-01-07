from bs4 import BeautifulSoup
import urllib3
import urllib.request
import urllib.parse
import pandas
import logging
import ssl
import json
from json import loads
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
        baseURL = "https://www.forexfactory.com/"
        global dict_

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
        MyBoolean = False
        dict_ = {}
        for item in table:

            dict_["Currency"] = item.find_all("td", {"class":"calendar__currency"})[0].text.strip() #Currency
            dict_["Event"] = item.find_all("td",{"class":"calendar__event"})[0].text.strip() #Event Name
            dict_["Time_Eastern"] = item.find_all("td", {"class":"calendar__time"})[0].text #Time Eastern
            impact = item.find_all("td", {"class":"calendar__impact"})
            
            for icon in range(0,len(impact)):
                if (impact_value := impact[icon].find_all("span")[0]['title'].split(' ', 1)[0]) == "High": 
                    dict_["Impact"] = impact_value
                    dict_["Actual"] = item.find_all("td", {"class":"calendar__actual"})[0].text #Actual Value
                    dict_["Forecast"] = item.find_all("td", {"class":"calendar__forecast"})[0].text #forecasted Value
                    dict_["Previous"] = item.find_all("td", {"class":"calendar__previous"})[0].text # Previous
                elif not (impact_value := impact[icon].find_all("span")[0]['title'].split(' ', 1)[0]) == "High" and MyBoolean  == False: 
                    MyBoolean = True
                    print("True & 25!")
                else:
                    print("hoi")
                
                print(dict_)
            if "Impact" in dict_:
                ecoday.append(dict_)
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
        return json_object, ecoday
eco = PyEcoCal()

json, ecoday = eco.get_economic_calendar("calendar?day=today")

def run_discord_bot():
    intents = discord.Intents.default()
    client = discord.Client(intents=intents)
    TOKEN = 'MTA1NzI5Njg2OTQ4NDY2Njk4Mg.GxPZ3A.M3UWqssZ74lhcPNRk7VGo7MEQT_7k-PgV66cA0'

    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')

        
        embed = discord.Embed(color=15548997)
        embed.add_field(name="", value= dict_["Event"] + " " + dict_["Time_Eastern"] + " " + dict_["Impact"] + " " + dict_["Currency"])
        embed.add_field(name= '\u200b', value='\u200b')
        embed.add_field(name="Long", value=' \u200b')
        embed.set_footer(text="Alixd91 | © 2022")
        embed.set_author(name='ForexFactory Calendar', icon_url=client.user.avatar.url)
        log = client.get_channel(1051535739919290450)
        await log.send(embed=embed)
    client.run(TOKEN)
run_discord_bot()