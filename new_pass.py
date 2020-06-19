from string import Template
import sys
from datetime import datetime
from imgurpython import ImgurClient
import json
import requests
from orbit_predictor.sources import EtcTLESource, get_predictor_from_tle_lines
from orbit_predictor.locations import Location
from bs4 import BeautifulSoup

if __name__ == "__main__":
    #assign all the arguments to variables
    now = sys.argv[1] #useless
    title = sys.argv[2]
    main_image = sys.argv[3]
    a = sys.argv[4]
    b = sys.argv[5]
    msa = sys.argv[6]
    raw = sys.argv[7]

    #get secrets from file
    f = open("/home/pi/website/secrets.json")
    data = json.load(f)
    client_id = data["id"]
    client_secret = data["secret"]
    lat = data["lat"]
    lon = data["lon"]
    f.close()

    #upload the images to imgur
    client = ImgurClient(client_id, client_secret)
    a = client.upload_from_path(a)
    b = client.upload_from_path(b)
    msa = client.upload_from_path(msa)
    raw = client.upload_from_path(raw)



    ##### Get the time of the next pass #####

    #get the tle file form celestrak
    url = "https://www.celestrak.com/NORAD/elements/weather.txt"
    r = requests.get(url)
    tle = r.content.decode("utf-8").replace("\r\n", "newline").split("newline")

    #find the satellites in the tle
    NOAA15 = tle.index("NOAA 15                 ")
    NOAA18 = tle.index("NOAA 18                 ")
    NOAA19 = tle.index("NOAA 19                 ")

    #set the ground station location
    loc = Location("ground station", lat, lon, 20)

    #get the next pass of NOAA 15
    predictor = get_predictor_from_tle_lines((tle[NOAA15+1], tle[NOAA15+2]))
    NOAA15_next_pass = predictor.get_next_pass(loc, max_elevation_gt=20).aos

    #get the next pass of NOAA 18
    p1redictor = get_predictor_from_tle_lines((tle[NOAA18+1], tle[NOAA18+2]))
    NOAA18_next_pass = predictor.get_next_pass(loc, max_elevation_gt=20).aos

    #get the next pass of NOAA 19
    predictor = get_predictor_from_tle_lines((tle[NOAA19+1], tle[NOAA19+2]))
    NOAA19_next_pass = predictor.get_next_pass(loc, max_elevation_gt=20).aos

    #get the closest to now
    closest = min([NOAA15_next_pass, NOAA18_next_pass, NOAA19_next_pass], key=lambda x: abs(x - datetime.utcnow()))
        

        
    ##### Append new information to weather.html file #####

    #read the pass.html format file
    html = open("/home/pi/website/media/pass.html")
    src = Template(html.read())

    #change the format of the title
    title = title.split("/")[-1]
    sat = title[:6]
    title = title[6:]
    title = datetime.strptime(title, "%Y%m%d-%H%M%S")
    title = "{} at {}".format(sat, title)

    #substitute arguments into the template
    d = {"title":title, "main":a["link"], "a":a["link"], "b":b["link"], "msa":msa["link"], "raw":raw["link"]}
    result = src.substitute(d)

    #read the index.html file for the weather page
    html = open("/home/pi/website/weather/index.html", "r")
    src = html.read()
    soup = BeautifulSoup(src)

    #find the right spot in the page to insert the new code
    soup.find(id="main_content").insert(0, result)

    #find the spot to add the next pass time
    soup.find(id="countdown")["next_pass"] = str(closest) + " UTC"

    #write the code index.html
    html = open("/home/pi/website/weather/index.html", "w")
    html.write(str(soup))