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

    async def send_embed_highimpact():
        
        eco = PyEcoCal()
        json_str, ecoday = eco.get_economic_calendar("calendar?day=today")
        eco_elements = json.loads(json_str)
        print(json_str)
        # create an empty dictionary to group currencies by time
        currencies_by_time = {}
            #group currencies by their time
        for eco_element in eco_elements:
            unixTime = datetime.datetime.fromtimestamp(eco_element["time_parent"])
            amsterdamTime = unixTime + datetime.timedelta(hours=-6)
            timeUntilEvent = unixTime - datetime.datetime.now()
            timeKey = (unixTime.strftime("%H:%M"),amsterdamTime.strftime("%H:%M"))
            if timeKey in currencies_by_time:
                currencies_by_time[timeKey].append(eco_element)
            else:
                currencies_by_time[timeKey] = [eco_element]    
            if eco_element["impact"] == "High":
                if timeUntilEvent.total_seconds() > 0:
                    with open("event.json", "r") as f:
                        exportData = json.load(f)
                    dataElementParse = eco_element.copy()
                    dataElementParse.pop("event", None)
                    dataElementParse.pop("time_parent", None)
                    
                    if str(eco_element["time_parent"]) in exportData:
                        exportData[str(eco_element["time_parent"])].update({eco_element["event"]: dataElementParse})
                    else:
                        exportData[eco_element["time_parent"]] = {eco_element["event"]: dataElementParse}       
                    with open("event.json", "w") as f:
                        json.dump(exportData, f, indent=4)
        class MyView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)
            @discord.ui.button(label="", style=discord.ButtonStyle.success, emoji="🔔")
            async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
                user_id = interaction.user.id
                username = interaction.user.name
                with open("data.json", "r") as f:
                    data = json.load(f)
                    user_data = {'username': username, 'user_id': user_id}
                if user_data in data["storedUserIds"]:
                    data["storedUserIds"].remove({'username': username, 'user_id': user_id})
                    with open("data.json", "w") as f:
                        data = json.dump(data, f)
                    await interaction.response.send_message("Je krijgt nu geen notificaties meer!", ephemeral=True, delete_after=5.0)    
                else:
                    data["storedUserIds"].append({'username': username, 'user_id': user_id})
                    with open("data.json", "w") as f:
                        data = json.dump(data, f)
                    await interaction.response.send_message("Je krijgt nu notificaties als er een event binnen 15 minuten begint!", ephemeral=True, delete_after=5.0)



        # create embed and add fields for each group of currencies with the same time
        embed = discord.Embed(color=15548997)
        embed.set_footer(text="Alixd91 | © 2023")
        embed.set_author(name='ForexFactory Calendar', icon_url=client.user.avatar.url)
        otherImpactembed = discord.Embed(color=15548997)
        otherImpactembed.set_footer(text="Alixd91 | © 2023")
        otherImpactembed.set_author(name='ForexFactory Calendar', icon_url=client.user.avatar.url)
        embed2 = discord.Embed(color=15548997)
        embed2.set_footer(text="Alixd91 | © 2023")
        embed2.set_author(name='ForexFactory Calendar', icon_url=client.user.avatar.url)
        embed2.add_field(name="ER IS GEEN DATA VANDAAG #REKT", value="", inline=False)
        log = client.get_channel(1051535739919290450)
        otherImpactChannel = client.get_channel(1051535739919290450)
        counterOtherCurrencies = 0
        for (time, amsterdam_time), currencies in currencies_by_time.items():
            high_impactCurrencies = [currency for currency in currencies if currency['impact'] == 'High']
            OtherimpactCurrencies = [currency for currency in currencies if currency['impact'] in ['Medium', 'Low']]
            if len(high_impactCurrencies) == 1:
                # if there's only one currency for this time, display the time label
                value = f"{high_impactCurrencies[0]['currency']}: {high_impactCurrencies[0]['event']}"
                embed.add_field(name=f'Time: {time} ({amsterdam_time})', value=value, inline=False)
            elif len(high_impactCurrencies) > 1:
                # if there are multiple currencies with high impact for this time
                value = '\n'.join([f"{currency['currency']}: {currency['event']}" for currency in high_impactCurrencies])
                embed.add_field(name=f'Time: {time} ({amsterdam_time})', value=value, inline=False)
            if len(OtherimpactCurrencies) == 1:
                # if there's only one currency for this time, display the time label
                value = f"{OtherimpactCurrencies[0]['currency']}: {OtherimpactCurrencies[0]['event']} \n Impact: **{OtherimpactCurrencies[0]['impact']}** "
                otherImpactembed.add_field(name=f'Time: {time} ({amsterdam_time})', value=value, inline=False)
                counterOtherCurrencies = 1
            elif len(OtherimpactCurrencies) > 1:
                # if there are multiple currencies with high impact for this time
                value = '\n'.join([f"{currency['currency']}: {currency['event']} \n Impact: **{currency['impact']}**" for currency in OtherimpactCurrencies])
                otherImpactembed.add_field(name=f'Time: {time} ({amsterdam_time})', value=value, inline=False)
                counterOtherCurrencies = 1
        if len(embed.fields) > 0:   
            await log.send(embed=embed, view=MyView())
        else:
            await log.send(embed=embed2)
            print('No fields to send in the embed')

        if len(otherImpactembed.fields) > 0: 
            await otherImpactChannel.send(embed=otherImpactembed)
        else:
            await otherImpactChannel.send(embed=embed2)
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
            # wait for a day before checking the time again
            await asyncio.sleep(86400)
    async def sendDM():
        with open("event.json", "r") as f:
            eventData = json.load(f)
            print("waar ben ik?")
        with open("data.json", "r") as f:
            userData = json.load(f)
            print("waarom verstop je?")
        timeList = [timeStamp for timeStamp in eventData]
        print("Ik vind dit niet leuk!")
        if len(timeList) == 0:
            await asyncio.sleep(20)
            print("zit ik hier vast?")
            return
        print("of zit ik hier vast dan?")
        recentTime = min(timeList)
        recentTimeIt = datetime.datetime.fromtimestamp(int(recentTime))
        amsterdamTime =  recentTimeIt + datetime.timedelta(hours=-6)
        amsterdamConverted = amsterdamTime.strftime("%H:%M")
        timeUntilEvent = recentTimeIt - datetime.datetime.now()- datetime.timedelta(minutes=15)
        print("oof zit ik hier vast dan?")
        await asyncio.sleep(timeUntilEvent.total_seconds())
        print("zit ik hier vast dan?")
        dmEmbed = discord.Embed(color=15548997)
        dmEmbed.set_footer(text="Alixd91 | © 2023")
        dmEmbed.set_author(name='ForexFactory Calendar', icon_url=client.user.avatar.url)
        combined_events = {}
        for specEvent in eventData[recentTime]:
            event_time = eventData[recentTime][specEvent]['time_eastern']
            if event_time in combined_events:
                combined_events[event_time].append(specEvent)
            else:
                combined_events[event_time] = [specEvent]

        # Create message for each combined event time
        for event_time in combined_events:
            events_str = ""
            for specEvent in combined_events[event_time]:
                value = f"{eventData[recentTime][specEvent]['currency']}: {specEvent} \n Impact: **{eventData[recentTime][specEvent]['impact']}**\n"
                events_str += value
            dmEmbed.add_field(name=f'The event is starting at: {amsterdamConverted}', value=events_str, inline=False)
        for User in userData["storedUserIds"]:
            user = await client.fetch_user(User["user_id"])
            await user.send("Beep, Boop! Ik ben hier weer om je wakker te maken, want er gebeurt zo meteen weer iets spannends!", embed=dmEmbed)
            # SEND EMBED TO USERS

        eventData.pop(recentTime, None)
        with open("event.json", "w") as f:
            json.dump(eventData, f, indent=4)
        



    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="ForexFactory Calendar!"))
        asyncio.create_task(sendDM())
        asyncio.create_task(check_time())
        

    client.run(TOKEN)

run_discord_bot()
