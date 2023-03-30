from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
import ssl
import json
import discord
import datetime
import asyncio
import pytz

 

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        return obj.__dict__

class PyEcoRoot:
    def __init__(self, currency, eco_element):
        self.currency = currency
        self.eco_element = eco_element


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
        print(f"Scraping {baseURL}...")

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
        time_temp = ""
        for item in table:
            dict_ = {}

            time_eastern = item.find_all("td", {"class":"calendar__time"})
            for time_item in time_eastern:
                time_item = time_item.text.strip()
                if time_item != "": # only save values that have text, otherwise dont replace the value
                  time_temp = time_item

                impact = item.find_all("td", {"class":"calendar__impact"})
                for icon in impact:
                    spans = icon.find_all("span")
                    if spans:
                        impact_value = spans[0]['title'].split(' ', 1)[0]
                        
                        if impact_value == "High":
                            dict_["Time_Eastern"] = time_temp #Assign time value to dictionary
                            dict_["Currency"] = item.find_all("td", {"class":"calendar__currency"})[0].text.strip() #Currency
                            dict_["Impact"] = impact_value
                            event = item.find_all("td",{"class":"calendar__event"})[0].text.strip() #Event Name
                            dict_["Event"] = event
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


def run_discord_bot():
    intents = discord.Intents.default()
    client = discord.Client(intents=intents)
    TOKEN = 'YOUR_TOKEN_HERE'

    # specify the time to send the embed every day (in 24-hour format)
    et_tz = pytz.timezone('US/Eastern')

    # Define the Amsterdam Timezone
    am_tz = pytz.timezone('Europe/Amsterdam')
    send_time = datetime.time(hour=6, minute=0)

    async def send_embed():
        
        eco = PyEcoCal()
        json_str, ecoday = eco.get_economic_calendar("calendar?day=mar16.2023")
        eco_elements = json.loads(json_str)
        print(json_str)
        # create an empty dictionary to group currencies by time
        currencies_by_time = {}
     
        # group currencies by their time
        for eco_element in eco_elements:
            time = eco_element['time_eastern']
            if time in currencies_by_time:
                currencies_by_time[time].append(eco_element)
            else:
                currencies_by_time[time] = [eco_element]
        class MyView(discord.ui.View):
            def __init__(self):
                super().__init__()
                self.pressed_users = set()
            @discord.ui.button(label="", style=discord.ButtonStyle.success, emoji="🔔")
            async def button_callback(self, button, interaction):
                user_id = button.user.id
                
                if user_id not in self.pressed_users:
                    self.pressed_users.add(user_id)
                    await button.response.send_message("Je krijgt nu notificaties als er een event binnen 15 minuten begint!", ephemeral=True, delete_after=5.0)
                else:
                    self.pressed_users.discard(user_id)  # remove the user from the set
                    await button.response.send_message("Je krijgt nu geen notificaties meer!", ephemeral=True, delete_after=5.0)


        
        for eco_element in eco_elements:
            time_str = eco_element['time_eastern']

            if time_str.lower() == 'all day':
                continue
            
            time_obj = datetime.datetime.strptime(time_str, '%I:%M%p')

            # Convert the Eastern Time to UTC
            time_et = et_tz.localize(time_obj)
            time_utc = time_et.astimezone(datetime.timezone.utc)

            # Convert the UTC time to Amsterdam time
            time_am = time_utc.astimezone(am_tz)
            print("Eastern time:", time_et.strftime('%I:%M %p'))

            # Print the Amsterdam time
            print("amsterdam time:", time_am.strftime('%I:%M %p'))


        # create embed and add fields for each group of currencies with the same time
        embed = discord.Embed(color=15548997)
        embed.set_footer(text="Alixd91 | © 2023")
        embed.set_author(name='ForexFactory Calendar', icon_url=client.user.avatar.url)
        embed2 = discord.Embed(color=15548997)
        embed2.set_footer(text="Alixd91 | © 2023")
        embed2.set_author(name='ForexFactory Calendar', icon_url=client.user.avatar.url)
        embed2.add_field(name="ER IS GEEN BELANGRIJKE DATA VANDAAG #REKT", value="", inline=False)
        log = client.get_channel(1051535739919290450)

        for time, currencies in currencies_by_time.items():
            if len(currencies) == 1:
                # if there's only one currency for this time, display the time label
                value = f"{currencies[0]['currency']}: {currencies[0]['event']}"
                embed.add_field(name=f'Time: {time}', value=value, inline=False)
            else:
                # if there are multiple currencies for this time, don't display the time label
                value = '\n'.join([f"{currency['currency']}: {currency['event']}" for currency in currencies])
                embed.add_field(name=f'Time: {time}', value=value, inline=False)

        if len(embed.fields) > 0:
            await log.send(embed=embed, view=MyView())
        else:
            await log.send(embed=embed2, view=MyView())
            print('No fields to send in the embed')

    async def check_time():
        # now = datetime.datetime.now()
        # target_time = datetime.datetime.combine(now.date(), send_time)
        # if now.time() >= send_time:
        #     # if the current time is already past the target time, schedule the first message for tomorrow
        #     target_time += datetime.timedelta(days=1)
        # delay_seconds = (target_time - now).total_seconds()
        # print(f"Waiting for {delay_seconds} seconds before sending the first message")
        # await asyncio.sleep(delay_seconds)
        while True:
            await send_embed()
            # wait for a day before checking the time again
            await asyncio.sleep(86400)

    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="ForexFactory Calendar!"))
        asyncio.create_task(check_time())

    client.run(TOKEN)

run_discord_bot()

