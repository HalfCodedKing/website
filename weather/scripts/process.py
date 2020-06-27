import sys
import json
import subprocess
import os
from datetime import datetime, timezone

if __name__ == "__main__":
    #get the index of the pass in daily_passes.json
    pass_index = sys.argv[1]

    #get info about the pass from the daily_passes.json
    f = open("/home/pi/website/weather/scripts/daily_passes.json")
    p = json.load(f)[pass_index]

    #assign variables
    frequency = p['frequency']
    duration = p['duration']
    #string used for naming the files  (aos in %Y-%m-%d %H:%M:%S format)
    local_time = str(datetime.strptime(p['aos'], "%Y-%m-%d %H:%M:%S.%f %Z").replace(tzinfo=timezone.utc).astimezone(tz=None))[:-13]
    #the name of the folder containing all the passes for the day (aos in %Y-%m-%d format)
    day = str(local_time)[:10]
    outfile = "home/pi/drive/weather/images/{}/{}/{}.wav".format(day, local_time, local_time)

    #if this is the first pass of the day, create a new folder for all the images of the day
    if not os.path.exists("/home/pi/drive/weather/images/{}/{}".format(day, local_time)):
        os.makedirs("/home/pi/drive/weather/images/{}/{}".format(day, local_time))

    #record the pass with rtl_fm
    command = "timeout {} rtl_fm -d 0 -f {} -g 37.2 -s 37000 -E deemp -F 9 - | sox -t raw -e signed -c 1 -b 16 -r 37000 - {} rate 11025".format(duration, frequency, outfile)
    subprocess.call([command.split(" ")])

    