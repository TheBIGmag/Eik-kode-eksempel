import requests
from bs4 import BeautifulSoup
import re
import json
import os
import shutil
import asyncio
import websockets


# Definér hvilken bil der skal kigges på,
# samt hvilke kolonner de ønskede data står i.
car = "902"          # Bilens startnummer (som tekst)
nrid = 1             # Kolonne-id hvor bilnummeret står
id = ""              # Den interne id for bilen (findes længere nede)
posid = 0            # Kolonne-id for placering
nameid = 3           # Kolonne-id for førerens navn
besttimeid = 6       # Kolonne-id for bedste omgangstid
gapid = 8            # Kolonne-id for tidsgab til foran
lastlapid = 9        # Kolonne-id for seneste omgangstid
# fx: bilnummeret står i kolonne 0, og førerens navn står i kolonne 3

# URL'en på det aktuelle løb
URL = 'https://livetiming.getraceresults.com/actionpics#screen-results'



# Konverterer en tid angivet i mikrosekunder til formatet minutter:sekunder:millisekunder
def convert_to_timestamp(test):
    
    minutes = (test - (test % 60000000)) // 60000000
    test = test - (minutes * 60000000)

    seconds = (test - (test % 1000000)) // 1000000
    milliseconds = (test - (seconds * 1000000)) // 1000
    
    if milliseconds < 100:
        milliseconds = "0"+str(milliseconds)

    return(str(minutes) + ":" + str(seconds) + ":" + str(milliseconds))


# Hent HTML-indholdet fra siden
response = requests.get(URL)
response.raise_for_status() # HTTPError hvis status er 4xx eller 5xx

# Parse HTML BeautifulSoup
soup = BeautifulSoup(response.text, 'html.parser')

# Træk data ud af scriptet og parse det til JSON.
# Regex'en finder alt indholdet inde i raceResultsViewModel.r_c( ... , true)
tester = re.findall(r'(?<=raceResultsViewModel\.r_c\().*?(?=, true)', soup.head.find_all("script")[4].text)
lst = json.loads("".join(tester))

# Find bilens interne id ved at matche på kolonne-id og bilnummer
for x in lst:
    if x[1] == nrid:
        if x[2] == car:
            id = x[0]



# udvælg kun de arrays der matcher bilens id   
data = []
for x in lst:
    if x[0] == id:
        data.append(x)

# Find de ønskede værdier (bedste tid, sidste omgang, fører, gab og placering)
for x in data:
    if x[1] == besttimeid:
        # Find de ønskede værdier (bedste tid, sidste omgang, fører, gab og placering)
        try:
            if bedsttime < 600000000:
                bedsttime=convert_to_timestamp(int(x[2]))
            else:
                bedsttime=convert_to_timestamp(0)
        except:
            bedsttime = ""
    if x[1] == lastlapid:
        # Gem seneste omgangstid (eller blank hvis tiden er urealistisk høj)
        try:
            if lasttime < 600000000:   
                lasttime=convert_to_timestamp(int(x[2]))
            else:
                lasttime=convert_to_timestamp(0)
        except:
            lasttime = ""
    if x[1] == nameid:
        # Gem førerens navn
        try:   
            driver=x[2]
        except:
            driver = ""
    if x[1] == gapid:
        # Gem tidsgabet til foranliggende bil
        try:   
            gaptime = x[2]
        except:
            gaptime = ""
    if x[1] == posid:
        # Gem placering
        try:   
            pos = x[2]
        except:
            pos = "0"

# Skriv de udtrukne værdier til hver sin tekstfil (bruges af streaming-overlay)
with open('last.txt', 'w') as output:
    output.write(lasttime)
with open('pos.txt', 'w') as output:
    output.write(pos)
with open('bedst.txt', 'w') as output:
    output.write(bedsttime)   
with open('gap.txt', 'w') as output:
    output.write(gaptime)       
with open('driver.txt', 'w') as output:
    output.write(driver)   
    

# Kopiér det aktive kørerfoto, så overlayet viser den rigtige kører
source_dir = r"\streaming\driver_photo"
destination_dir = r"\streaming\active"

source_path = os.path.join(source_dir, driver+".png")
destination_path = os.path.join(destination_dir, "active.png")

shutil.copyfile(source_path, destination_path)

# Udskriv de fundne værdier til konsollen som kontrol
print("bedst: ")
print(bedsttime)
print("last: ")
print(lasttime)  
print("driver: ")            
print(driver)
print("gap: ")    
print(gaptime)  
print("pos: ")      
print(pos)
print("id: ")
print(id)

      
async def chat(identfy):
    # forbind til websocket-forbindelse for at modtage live-opdateringer
    async with websockets.connect('wss://livetiming.getraceresults.com/lt/connect?transport=webSockets&clientProtocol=1.5&_tk=84ab209096b3459aa8f409dcc23753b8&_gr=w&_tkdm=170125&connectionToken=LE5EtBT7g8SpKjr3uml1X7G9iSwpFitBuAOICNh76ZFABswI9isbol48bVnHJStVUhNJ4%2BYYSXOOHMAy62e3O7oalrzvdj1bUUKyceM%2Fw3qZMPedrr%2FUpV7K5uzc7CGk&tid=10') as websocket:
        while True:

            response = await websocket.recv()
          
            res = json.loads(response)
            try:
                if res['M'][0][0] == 'r_c':
                    data = []
                  
                  # Udvælg kun de arrays der matcher vores bil-id
                    for x in res['M'][0][1]:
                        if x[0] == identfy:
                            data.append(x)
                  
                if len(data) != 0:
                    print(data)   
                    #find den beste tid
                    for x in data:
                        if x[1] == besttimeid:
                            try:
                                if besttimeid < 600000000:   
                                    besttimeid=convert_to_timestamp(int(x[2]))
                                else:
                                    besttimeid=convert_to_timestamp(0)
                                print("bedst time")
                                with open('bedst.txt', 'w') as output:
                                    print("write bedst")
                                    output.write(bedsttime)
                            except:
                                continue
                                
                            print(bedsttime)
                        if x[1] == lastlapid:
                            try:     
                                if lasttime < 600000000:   
                                    lasttime=convert_to_timestamp(int(x[2]))
                                else:
                                    lasttime=convert_to_timestamp(0)
                                print("bedst time")   
                                lasttime=convert_to_timestamp(int(x[2]))
                                print("lasttime")
                                with open('last.txt', 'w') as output:
                                    print("write last")
                                    output.write(lasttime)
                            except:
                                continue
                        if x[1] == nameid:
                            try:   
                                driver=x[2]
                                print("driver")
                                with open('driver.txt', 'w') as output:
                                    print("driver last")
                                    output.write(driver)
                            except:
                                continue
                        if x[1] == gapid:
                            try:   
                                gaptime = x[2]
                                print("gap")
                                with open('gap.txt', 'w') as output:
                                    print("write gap")
                                    output.write(gaptime)
                            except:
                                continue
                        if x[1] == posid:
                            try:   
                                pos = x[2]
                                print("pos")
                                with open('pos.txt', 'w') as output:
                                    print("write pos")
                                    output.write(pos)
                            except:
                                continue
                    
   
                    source_dir = r"\streaming\driver_photo"
                    destination_dir = r"\streaming\active"

                    source_path = os.path.join(source_dir, driver+".png")
                    destination_path = os.path.join(destination_dir, "active.png")

                    shutil.copyfile(source_path, destination_path)

                    
                    print(lasttime)              
                    print(driver)    
                    print(gaptime)        
                    print(pos)
            except:
                True
            

asyncio.run(chat(id))