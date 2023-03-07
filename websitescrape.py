from bs4 import BeautifulSoup
import urllib3
import urllib.request
import urllib.parse
import pandas
import logging
import ssl
import json
import discord
 

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        return obj.__dict__

class PyEcoRoot:
    def __init__(self, currency, eco_element):
        self.currency = currency
        self.eco_element = eco_element

import json
import urllib.request
import ssl
from bs4 import BeautifulSoup

class PyEcoElement:
    def __init__(self, currency, event, impact, time_eastern):
        self.currency = currency
        self.event = event
        self.impact = impact
        self.time_eastern = time_eastern

class PyEcoCal:
    def __init__(self, p1=1):
        self.p1 = p1

    def get_economic_calendar(self, date):
        baseURL = "https://www.forexfactory.com/"
        global dict_

        # Disable SSL certificate verification
        ssl._create_default_https_context = ssl._create_unverified_context

        # Set user agent header to avoid blocking by the server
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        
        urleco = baseURL + date

        try:
            # Open the URL using the opener
            response = opener.open(urleco)
            result = response.read().decode('utf-8', errors='replace')
        except urllib.error.URLError as e:
            print(f"Error: {e.reason}")
            return None, []

        soup = BeautifulSoup(result, "html.parser")
        table = soup.find_all("tr", class_="calendar_row")

        ecoday = []
        for item in table:
            impact = item.find_all("td", {"class":"calendar__impact"})
            if impact:
                dict_ = {}
                dict_["Currency"] = item.find_all("td", {"class":"calendar__currency"})[0].text.strip() #Currency
                dict_["Event"] = item.find_all("td",{"class":"calendar__event"})[0].text.strip() #Event Name
                dict_["Time_Eastern"] = item.find_all("td", {"class":"calendar__time"})[0].text #Time Eastern
                
                for icon in impact:
                    impact_value = icon.find_all("span")[0]['title'].split(' ', 1)[0]
                    if impact_value == "High": 
                        dict_["Impact"] = impact_value

                if "Impact" in dict_:
                    ecoday.append(dict_)

        ecoDict = []
        for item in ecoday:
            ecoelem = PyEcoElement(
                 item["Currency"],
                 item["Event"],
                 item["Impact"],
                 item["Time_Eastern"],
            )
            ecoDict.append(ecoelem.__dict__)
        
        json_object = json.dumps(ecoDict, indent=3)  
        return json_object, ecoday

eco = PyEcoCal()
json_str, ecoday = eco.get_economic_calendar("calendar?day=mar8.2023")
eco_elements = json.loads(json_str)
print(json_str)


def run_discord_bot():
    intents = discord.Intents.default()
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')

        embed = discord.Embed(color=15548997)
        embed.set_footer(text="Alixd91 | © 2023")
        embed.set_author(name='ForexFactory Calendar', icon_url=client.user.avatar.url)
        log = client.get_channel(1051535739919290450)

        for eco_element in eco_elements:
               embed.add_field(name=eco_element['currency'], value=f"{eco_element['event']}\nTime: {eco_element['time_eastern']}", inline=False)

        await log.send(embed=embed)
    client.run(TOKEN)
run_discord_bot()