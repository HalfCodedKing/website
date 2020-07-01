#made by Felix (Blobtoe)

import json
from datetime import datetime, timedelta
import subprocess
import requests
from orbit_predictor.sources import get_predictor_from_tle_lines
from orbit_predictor.locations import Location
from tzwhere import tzwhere
import os

#get lat and lon from private file
f = open("/home/pi/website/weather/scripts/secrets.json")
data = json.load(f)
lat = data["lat"]
lon = data["lon"]
f.close()

#get the tle file form celestrak
url = "https://www.celestrak.com/NORAD/elements/weather.txt"
r = requests.get(url)
tle = r.content.decode("utf-8").replace("\r\n", "newline").split("newline")

#write tle to file for use with wxmap
# = open("/home/pi/website/weather/scripts/weather.tle", "w+")
f.write(r.text.replace("\r", ""))
f.close()

#find the satellites in the tle
NOAA15 = tle.index("NOAA 15                 ")
NOAA18 = tle.index("NOAA 18                 ")
NOAA19 = tle.index("NOAA 19                 ")
METEOR = tle.index("METEOR-M 2              ")

#set the ground station location
loc = Location("ground station", lat, lon, 5)

#get the next passes of NOAA 15 within the next 24 hours
print("getting NOAA 15 passes")
NOAA15_predictor = get_predictor_from_tle_lines((tle[NOAA15+1], tle[NOAA15+2]))
NOAA15_passes = NOAA15_predictor.passes_over(location=loc, when_utc=datetime.utcnow(), limit_date=datetime.utcnow() + timedelta(hours=24), max_elevation_gt=20)

#get the next passes of NOAA 18 within the next 24 hours
print("getting NOAA 18 passes")
NOAA18_predictor = get_predictor_from_tle_lines((tle[NOAA18+1], tle[NOAA18+2]))
NOAA18_passes = NOAA18_predictor.passes_over(location=loc, when_utc=datetime.utcnow(), limit_date=datetime.utcnow() + timedelta(hours=24), max_elevation_gt=20)

#get the next passes of NOAA 19 within the next 24 hours
print("getting NOAA 19 passes")
NOAA19_predictor = get_predictor_from_tle_lines((tle[NOAA19+1], tle[NOAA19+2]))
NOAA19_passes = NOAA19_predictor.passes_over(location=loc, when_utc=datetime.utcnow(), limit_date=datetime.utcnow() + timedelta(hours=24), max_elevation_gt=20)

#get the next passes of METEOR-M 2 within the next 24 hours
print("getting METEOR-M 2 passes")
METEOR_predictor = get_predictor_from_tle_lines((tle[METEOR+1], tle[METEOR+2]))
METEOR_passes = METEOR_predictor.passes_over(location=loc, when_utc=datetime.utcnow(), limit_date=datetime.utcnow() + timedelta(hours=24), max_elevation_gt=20)

#create one big list of all the passes
print("sorting passes by time")
passes = []
for p in NOAA15_passes:
    passes.append(["NOAA 15", p])
for p in NOAA18_passes:
    passes.append(["NOAA 18", p])
for p in NOAA19_passes:
    passes.append(["NOAA 19", p])
for p in METEOR_passes:
    passes.append(["METEOR-M 2", p])

#sort them by their date
passes.sort(key=lambda x: x[1].aos)

freqs = {
    'NOAA 15': 137620000,
    'NOAA 18': 137912500,
    'NOAA 19': 137100000,
    'METEOR-M 2': 137100000,
}



#turn the info into json data
print("writing to file: /home/pi/website/weather/scripts/daily_passes.json")
data = []
for p in passes:
    sat = p[0]
    info = p[1]
    data.append({
        #name of the sat
        'satellite': sat,
        #the frequency in MHz the satellite transmits
        'frequency': freqs[sat],
        #time the sat rises above the horizon
        'aos': str(info.aos) + " UTC",
        #time the sat reaches its max elevation
        'tca': str(info.max_elevation_date) + " UTC",
        #time the sat passes below the horizon 
        'los': str(info.los) + " UTC",
        #maximum degrees of elevation
        'max_elevation': round(info.max_elevation_deg, 1),
        #duration of the pass in seconds
        'duration': info.duration_s,
        #status INCOMING, CURRENT or PASSED
        'status': "INCOMING"
    })

#check if passes overlap and choose which one to prioritize
i = 0
while i < len(data) - 2:
    if datetime.strptime(data[i]["los"], "%Y-%m-%d %H:%M:%S.%f %Z") > datetime.strptime(data[i+1]["aos"], "%Y-%m-%d %H:%M:%S.%f %Z"):
        #prioritize higher elevation passes
        priority1 = data[i]['max_elevation']
        priority2 = data[i+1]['max_elevation']

        #meteor gets more priority
        if data[i]['satellite'] == "METEOR-M 2":
            priority1 += 30
        elif data[i+1]['satellite'] == "METEOR-M 2":
            priority2 += 30

        #keep the pass with higher priority
        if priority1 >= priority2:
            data.pop(i+1)
        elif priority2 > priority1:
            data.pop(i)
    else:
        i += 1

#write to the json file
with open("/home/pi/website/weather/scripts/daily_passes.json", "w") as outfile:
    json.dump(data, outfile, indent=4, sort_keys=True)

#get timezone of groundstation
tzwhere = tzwhere.tzwhere()
timezone_str = tzwhere.tzNameAt(lat, lon)

#schedule the passes for the day
print("scheduling at jobs")
i = 0
for p in data:
    #calculate minutes until start of each pass
    delta = datetime.strptime(p["aos"], "%Y-%m-%d %H:%M:%S.%f %Z") - datetime.utcnow()
    delta_min = round(delta.total_seconds() / 60)
    #create an 'at' job
    ps = subprocess.Popen(('echo', 'python3 /home/pi/website/weather/scripts/process.py {}'.format(i)), stdout=subprocess.PIPE)
    subprocess.check_output(('at', 'now + {} minutes'.format(delta_min)), stdin=ps.stdout)
    i += 1

#commit changes to git repository
print("commiting to github")
os.system("/home/pi/website/weather/scripts/commit.sh")

print("done scheduling")