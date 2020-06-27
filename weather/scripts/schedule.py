import requests
from orbit_predictor.sources import EtcTLESource, get_predictor_from_tle_lines
from orbit_predictor.locations import Location
import json
from datetime import datetime
from datetime import timedelta
import sched
import time
from process import process
import subprocess

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

#find the satellites in the tle
NOAA15 = tle.index("NOAA 15                 ")
NOAA18 = tle.index("NOAA 18                 ")
NOAA19 = tle.index("NOAA 19                 ")

#set the ground station location
loc = Location("ground station", lat, lon, 5)

#get the next passes of NOAA 15 within the next 24 hours
NOAA15_predictor = get_predictor_from_tle_lines((tle[NOAA15+1], tle[NOAA15+2]))
NOAA15_passes = NOAA15_predictor.passes_over(location=loc, when_utc=datetime.utcnow(), limit_date=datetime.utcnow() + timedelta(hours=24), max_elevation_gt=20)

#get the next passes of NOAA 18 within the next 24 hours
NOAA18_predictor = get_predictor_from_tle_lines((tle[NOAA18+1], tle[NOAA18+2]))
NOAA18_passes = NOAA18_predictor.passes_over(location=loc, when_utc=datetime.utcnow(), limit_date=datetime.utcnow() + timedelta(hours=24), max_elevation_gt=20)

#get the next passes of NOAA 19 within the next 24 hours
NOAA19_predictor = get_predictor_from_tle_lines((tle[NOAA19+1], tle[NOAA19+2]))
NOAA19_passes = NOAA19_predictor.passes_over(location=loc, when_utc=datetime.utcnow(), limit_date=datetime.utcnow() + timedelta(hours=24), max_elevation_gt=20)

#create one big list of all the passes
passes = []
for p in NOAA15_passes:
    passes.append(["NOAA15", p])
for p in NOAA18_passes:
    passes.append(["NOAA18", p])
for p in NOAA19_passes:
    passes.append(["NOAA19", p])

#sort them by their date
passes.sort(key=lambda x: x[1].aos)

#turn the info into json data
data = []
for p in passes:
    sat = p[0]
    info = p[1]
    data.append({
        #name of the sat
        'satellite': sat,
        #time the sat rises above the horizon
        'aos': str(info.aos) + " UTC",
        #time the sat reaches its max elevation
        'tca': str(info.max_elevation_date) + " UTC",
        #time the sat passes below the horizon 
        'los': str(info.los) + " UTC",
        #maximum degrees of elevation
        'max_elevation': info.max_elevation_deg,
        #duration of the pass in seconds
        'duration': info.duration_s,
        #status INCOMING, CURRENT or PASSED
        'status': "INCOMING"
    })

#write to the json file
with open("/home/pi/website/weather/scripts/daily_passes.json", "w") as outfile:
    json.dump(data, outfile, indent=4, sort_keys=True)

#schedule the passes for the day
i = 0
for p in data:
    delta = datetime.strptime(p["aos"], "%Y-%m-%d %H:%M:%S.%f %Z") - datetime.utcnow()
    delta_min = round(delta.total_seconds() / 60)
    ps = subprocess.Popen(('echo', 'python3 /home/pi/website/weather/scripts/process.py {}'.format(i)), stdout=subprocess.PIPE)
    subprocess.check_output(('at', 'now + {} minutes'.format(delta_min)), stdin=ps.stdout)
    i += 1