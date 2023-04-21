from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
import ssl
import json
import pytz
from time import sleep

 

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        return obj.__dict__

class PyEcoRoot:
    def __init__(self, currency, eco_element):
        self.currency = currency
        self.eco_element = eco_element


class PyEcoElement:
    def __init__(self, currency, event, impact, time_eastern, time_parent):
        self.currency = currency
        self.event = event
        self.impact = impact
        self.time_eastern = time_eastern
        self.time_parent = time_parent

class PyEcoCal:
    def __init__(self, p1=1):
        self.p1 = p1

    def get_economic_calendar(self, date):
        baseURL = "https://www.forexfactory.com/"

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
                time_parent = int(time_item.parent.get("data-timestamp"))
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
                            dict_["time_parent"] = time_parent
                            ecoday.append(dict_)
                        elif impact_value == "Medium":
                            dict_["Time_Eastern"] = time_temp #Assign time value to dictionary
                            dict_["Currency"] = item.find_all("td", {"class":"calendar__currency"})[0].text.strip() #Currency
                            dict_["Impact"] = impact_value
                            event = item.find_all("td",{"class":"calendar__event"})[0].text.strip() #Event Name
                            dict_["Event"] = event
                            dict_["time_parent"] = time_parent
                            ecoday.append(dict_)
                        elif impact_value == "Low":
                            dict_["Time_Eastern"] = time_temp #Assign time value to dictionary
                            dict_["Currency"] = item.find_all("td", {"class":"calendar__currency"})[0].text.strip() #Currency
                            dict_["Impact"] = impact_value
                            event = item.find_all("td",{"class":"calendar__event"})[0].text.strip() #Event Name
                            dict_["Event"] = event
                            dict_["time_parent"] = time_parent
                            ecoday.append(dict_)

        ecoDict = []
        for item in ecoday:
            ecoelem = PyEcoElement(
                 item["Currency"],
                 item["Event"],
                 item["Impact"],
                 item["Time_Eastern"],
                 item["time_parent"]
            )
            ecoDict.append(ecoelem.__dict__)
        
        json_object = json.dumps(ecoDict, indent=3)  
        return json_object, ecoday
