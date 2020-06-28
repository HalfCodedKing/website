#made by Felix (Blobtoe)

import sys
import json
import subprocess
import os
from datetime import datetime, timezone, timedelta
from imgurpython import ImgurClient
from bs4 import BeautifulSoup
from time import sleep
from string import Template
import shlex

if __name__ == "__main__":
    #get the index of the pass in daily_passes.json
    pass_index = int(sys.argv[1])

    #get info about the pass from the daily_passes.json
    f = open("/home/pi/website/weather/scripts/daily_passes.json")
    p = json.load(f)[pass_index]
    f.close()

    #assign variables
    with open("/home/pi/website/weather/scripts/secrets.json") as f:
        data = json.load(f)
        lat = data['lat']
        lon = data['lon']
        elev = data['elev']

    sat = p['satellite']
    frequency = p['frequency']
    duration = p['duration']
    max_elevation = p['max_elevation']
    #string used for naming the files  (aos in %Y-%m-%d %H:%M:%S format)
    local_time = str(datetime.strptime(p['aos'], "%Y-%m-%d %H:%M:%S.%f %Z").replace(tzinfo=timezone.utc).astimezone(tz=None))[:-13].replace(" ", "_")
    #the name of the folder containing all the passes for the day (aos in %Y-%m-%d format)
    day = str(local_time)[:10]
    outfile = "/home/pi/drive/weather/images/{}/{}/{}".format(day, local_time, local_time)

    #if this is the first pass of the day, create a new folder for all the images of the day
    if not os.path.exists("/home/pi/drive/weather/images/{}".format(day)):
        os.makedirs("/home/pi/website/weather/images/{}".format(day))
        os.makedirs("/home/pi/drive/weather/images/{}".format(day))

    #create new directory for this pass
    if not os.path.exists("/home/pi/drive/weather/images/{}/{}".format(day, local_time)):
        os.makedirs("/home/pi/drive/weather/images/{}/{}".format(day, local_time))

    #update the status in daily_passes.json
    with open("/home/pi/website/weather/scripts/daily_passes.json", "r") as f:
        data = json.load(f)
    with open("/home/pi/website/weather/scripts/daily_passes.json", "w") as f:
        data[pass_index]["status"] = "CURRENT"
        json.dump(data, f, indent=4, sort_keys=True)

    #record the pass with rtl_fm
    os.system("timeout {} rtl_fm -d 0 -f {} -g 37.2 -s 37000 -E deemp -F 9 - | sox -traw -esigned -c1 -b16 -r37000 - {}.wav rate 11025".format(duration, frequency, outfile))

    #update the status in daily_passes.json
    with open("/home/pi/website/weather/scripts/daily_passes.json", "r") as f:
        data = json.load(f)
    with open("/home/pi/website/weather/scripts/daily_passes.json", "w") as f:
        data[pass_index]["status"] = "PASSED"
        json.dump(data, f, indent=4, sort_keys=True)

    #create map overlay
    print("creating map")
    date = (datetime.strptime(p['aos'], "%Y-%m-%d %H:%M:%S.%f %Z")+timedelta(0, 90)).strftime("%d %b %Y %H:%M:%S")
    os.system("/usr/local/bin/wxmap -T \"{}\" -H /home/pi/website/weather/scripts/weather.tle -p 0 -o \"{}\" {}-map.png".format(sat, date, outfile))

    #create image from channel a
    print("create image from channel a")
    subprocess.call("/usr/local/bin/wxtoimg -m {}-map.png -A -a -B 120 -L 600 {}.wav {}.a.png".format(outfile, outfile, outfile).split(" "))

    #create image from channel b
    print("creating image from channel b")
    subprocess.call("/usr/local/bin/wxtoimg -m {}-map.png -A -b -B 120 -L 600 {}.wav {}.b.png".format(outfile, outfile, outfile).split(" "))

    #create image with MSA enhancement from channel a
    print("creating MSA image")
    subprocess.call("/usr/local/bin/wxtoimg -m {}-map.png -A -B 120 -L 600 -e MSA {}.wav {}.MSA.png".format(outfile, outfile, outfile).split(" "))
    
    #create image with MSA-precip enhancement from channel a
    print("creagin MSA-precip image")
    subprocess.call("/usr/local/bin/wxtoimg -m {}-map.png -A -B 120 -L 600 -e MSA-precip {}.wav {}.MSA-precip.png".format(outfile, outfile, outfile).split(" "))

    #create raw image
    print("creating raw image")
    subprocess.call("/usr/local/bin/wxtoimg -m {}-map.png -A -B 120 -L 600 {}.wav {}.raw.png".format(outfile, outfile, outfile).split(" "))
'''
    #get imgur credentials from secrets.json
    f = open("/home/pi/website/weather/scripts/secrets.json")
    data = json.load(f)
    client_id = data["id"]
    client_secret = data["secret"]
    f.close()

    #upload the images to imgur
    client = ImgurClient(client_id, client_secret)
    config = {
        'name': "{} at {} at {}".format(sat, max_elevation, local_time),
        'title': "{} at {} at {}".format(sat, max_elevation, local_time)
    }

    links = {}
    
    #upload channel a image
    print("uploading images to imgur")
    count = 0
    while count<10:
        try:
            img = client.upload_from_path("{}.a.png".format(outfile), config=config)
            links["a"] = img["link"]
            print("uploaded image")
            break
        except:
            print("failed to upload image... trying again")
            count += 1
            continue

    #upload channel b image
    count = 0
    while count<10:
        try:
            img = client.upload_from_path("{}.b.png".format(outfile), config=config)
            links["b"] = img["link"]
            print("uploaded image")
            break
        except:
            print("failed to upload image... trying again")
            count += 1
            continue

    #upload channel MSA image
    count = 0
    while count<10:
        try:
            img = client.upload_from_path("{}.MSA.png".format(outfile), config=config)
            links["MSA"] = img["link"]
            print("uploaded image")
            break
        except:
            print("failed to upload image... trying again")
            count += 1
            continue

    #upload channel MSA-precip image
    count = 0
    while count<10:
        try:
            img = client.upload_from_path("{}.MSA-precip.png".format(outfile), config=config)
            links["MSA-precip"] = img["link"]
            print("uploaded image")
            break
        except:
            print("failed to upload image... trying again")
            count += 1
            continue

    #upload channel raw image
    count = 0
    while count<10:
        try:
            img = client.upload_from_path("{}.raw.png".format(outfile), config=config)
            links["raw"] = img["link"]
            print("uploaded image")
            break
        except:
            print("failed to upload image... trying again")
            count += 1
            continue

    #read the pass.html template file
    html = open("/home/pi/website/media/pass.html")
    src = Template(html.read())

    #substitute arguments into the template
    d = {"title":local_time, "main":links['a'], "a":links['a'], "b":links['b'], "msa":links['MSA'], "raw":links['raw']}
    result = src.substitute(d)
    result = BeautifulSoup(result)

    #read the index.html file for the weather page
    html = open("/home/pi/website/weather/index.html", "r")
    src = html.read()
    soup = BeautifulSoup(src)

    #find the right spot in the page to insert the new code
    soup.find(id="main_content").insert(0, result)

    #find the spot to add the next pass time
    with open("/home/pi/website/weather/scripts/daily_passes.json", "r") as f:
        for d in data:
            if d['status'] == "INCOMING":
                soup.find(id="countdown")["next_pass"] = d['los']
                break

    #write the code index.html
    html = open("/home/pi/website/weather/index.html", "w")
    html.write(str(soup))

    #commit changes to git repository
    subprocess.call("git -C /home/pi/website/ pull origin master".split(" "))
    subprocess.call("git -C /home/pi/website/ add --all".split(" "))
    subprocess.call("git -C /home/pi/website/ commit -m \"weather auto commit\"".split(" "))
    subprocess.call("git -C /home/pi/website/ push origin master".split(" "))

    print("done processing")
'''