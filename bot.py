from forexfactory import *
import discord
import datetime
import time
import asyncio
import pytz
import json

def run_discord_bot():
    intents = discord.Intents.default()
    client = discord.Client(intents=intents)

    send_time = datetime.time(hour=6, minute=0)
    valid_times = ['all day', 'tentative', 'day 1', 'day 2', 'day 3', 'day 4', 'day 5', 'day 6', 'day 7', '17th-20th']
    interval = 5  # number of seconds

    async def send_embed_highimpact():
        
        eco = PyEcoCal()
        json_str, ecoday = eco.get_economic_calendar("calendar?day=apr17.2023")
        eco_elements = json.loads(json_str)
        print(json_str)
        # create an empty dictionary to group currencies by time
        currencies_by_time = {}
            #group currencies by their time

        for eco_element in eco_elements:
            unixTime = datetime.datetime.fromtimestamp(eco_element["time_parent"])
            amsterdamTime = unixTime + datetime.timedelta(hours=-2)
            timeUntilEvent = unixTime - datetime.datetime.now()
            timeKey = (unixTime.strftime("%H:%M"),amsterdamTime.strftime("%H:%M"))
            if timeKey in currencies_by_time:
                currencies_by_time[timeKey].append(eco_element)
            else:
                currencies_by_time[timeKey] = [eco_element]    
            if timeUntilEvent.total_seconds() > 0:
                print(json.dumps(currencies_by_time, indent=4))
            # APPEND TO EVENT.JSON

        class MyView(discord.ui.View):
            def __init__(self):
                super().__init__()
            @discord.ui.button(label="", style=discord.ButtonStyle.success, emoji="🔔")
            async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
                user_id = interaction.user.id
                with open("data.json", "r") as f:
                    data = json.load(f)
                if any(number == user_id for number in data["storedUserIds"]):
                    data["storedUserIds"].remove(user_id)
                    with open("data.json", "w") as f:
                        data = json.dump(data, f)
                    await interaction.response.send_message("Je krijgt nu geen notificaties meer!", ephemeral=True, delete_after=5.0)    
                else:
                    data["storedUserIds"].append(user_id)
                    with open("data.json", "w") as f:
                        data = json.dump(data, f)
                    await interaction.response.send_message("Je krijgt nu notificaties als er een event binnen 15 minuten begint!", ephemeral=True, delete_after=5.0)



        # create embed and add fields for each group of currencies with the same time
        embed = discord.Embed(color=15548997)
        embed.set_footer(text="Alixd91 | © 2023")
        embed.set_author(name='ForexFactory Calendar', icon_url=client.user.avatar.url)
        embed2 = discord.Embed(color=15548997)
        embed2.set_footer(text="Alixd91 | © 2023")
        embed2.set_author(name='ForexFactory Calendar', icon_url=client.user.avatar.url)
        embed2.add_field(name="ER IS GEEN BELANGRIJKE DATA VANDAAG #REKT", value="", inline=False)
        log = client.get_channel(1051535739919290450)

        for (time, amsterdam_time), currencies in currencies_by_time.items():
            high_impact_currencies = [currency for currency in currencies if currency['impact'] == 'High']
            if len(high_impact_currencies) == 1:
                # if there's only one currency for this time, display the time label
                value = f"{high_impact_currencies[0]['currency']}: {high_impact_currencies[0]['event']}"
                embed.add_field(name=f'Time: {time} ({amsterdam_time})', value=value, inline=False)
            elif len(high_impact_currencies) > 1:
                # if there are multiple currencies with high impact for this time, don't display the time label
                value = '\n'.join([f"{currency['currency']}: {currency['event']}" for currency in high_impact_currencies])
                embed.add_field(name=f'Time: {time} ({amsterdam_time})', value=value, inline=False)

        if len(embed.fields) > 0:
            await log.send(embed=embed, view=MyView())
        else:
            await log.send(embed=embed2, view=MyView())
            print('No fields to send in the embed')

    async def send_embed_otherimpact():
        
        eco = PyEcoCal()
        json_str, ecoday = eco.get_economic_calendar("calendar?day=today")
        eco_elements = json.loads(json_str)
        # create an empty dictionary to group currencies by time
        currencies_by_time = {}
     
        # group currencies by their time
        for eco_element in eco_elements:
                time_str = eco_element['time_eastern']

                if time_str.lower() in valid_times:
                    continue
                    
                date_object = datetime.datetime.strptime(time_str, '%I:%M%p')
                time_conversion = date_object + datetime.timedelta(hours=6)
                amsterdam_time = time_conversion.time().strftime("%H:%M")
                time_key = (time_str, amsterdam_time)
                if time_key in currencies_by_time:
                    currencies_by_time[time_key].append(eco_element)
                else:
                    currencies_by_time[time_key] = [eco_element]

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
            high_impact_currencies = [currency for currency in currencies if currency['impact'] in ['Medium', 'Low']]
            if len(high_impact_currencies) == 1:
                # if there's only one currency for this time, display the time label
                value = f"{high_impact_currencies[0]['currency']}: {high_impact_currencies[0]['event']} \n Impact: **{high_impact_currencies[0]['impact']}** "
                embed.add_field(name=f'Time: {time} ({amsterdam_time})', value=value, inline=False)
            elif len(high_impact_currencies) > 1:
                # if there are multiple currencies with high impact for this time, don't display the time label
                value = '\n'.join([f"{currency['currency']}: {currency['event']} \n Impact: **{currency['impact']}**" for currency in high_impact_currencies])
                embed.add_field(name=f'Time: {time} ({amsterdam_time})', value=value, inline=False)

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
            await send_embed_highimpact()
            # await send_embed_otherimpact()
            # wait for a day before checking the time again
            await asyncio.sleep(86400)

    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="ForexFactory Calendar!"))
        asyncio.create_task(check_time())

    client.run(TOKEN)

run_discord_bot()
