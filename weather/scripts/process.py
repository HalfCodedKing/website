#Made by Felix (Blobtoe)

import sys
import json
import subprocess
import os
from datetime import datetime, timezone, timedelta
from imgurpython import ImgurClient
from bs4 import BeautifulSoup
import time
from string import Template
import shlex
from PIL import Image

def upload(path, title):
    #get imgur credentials from secrets.json
    f = open("/home/pi/website/weather/scripts/secrets.json")
    data = json.load(f)
    client_id = data["id"]
    client_secret = data["secret"]
    f.close()

    #upload the images to imgur
    client = ImgurClient(client_id, client_secret)
    config = {
        'name': title,
        'title': title
    }

    #upload the image
    print("uploading images to imgur")
    link = ""
    count = 0
    while count<10:
        try:
            img = client.upload_from_path(path, config=config)
            link = img["link"]
            print("uploaded image")
            break
        except:
            print("failed to upload image... trying again")
            count += 1
            continue
    
    #return the link of the uploaded image
    return link

def process_METEOR():
    #record pass
    print("recording pass...")
    os.system("timeout {} /usr/local/bin/rtl_fm -Mraw -s768k -f {} -g49.6 -p 0 -F 9 | sox -t raw -r 768k -c 2 -b 16 -e s - -t wav {}.iq.wav rate 192k".format(duration, frequency, outfile))

    #demodulate the signal
    print("demodulating meteor signal...")
    os.system("/usr/bin/meteor_demod -B -s 140000 -o {}.qpsk {}.iq.wav".format(outfile, outfile))

    #decode the signal into an image
    print("decoding image...")
    os.system("/usr/local/bin/medet_arm {}.qpsk {} -cd".format(outfile, outfile))
    
    #convert bmp to png
    img = Image.open("{}.bmp".format(outfile))
    img.save("{}.png".format(outfile), "png")

    #upload image
    link = upload("{}.png".format(outfile), "{} at {}° at {}".format(sat, max_elevation, local_time))

    #write pass info to json file
    with open("/home/pi/website/weather/images/{}/{}/{}.json".format(day, local_time, local_time), "w") as f:
        pass_info = p
        pass_info['link'] = link
        json.dump(pass_info, f, indent=4, sort_keys=True)

def process_NOAA():
    #record the pass with rtl_fm
    print("writing to file: {}.wav".format(outfile))
    os.system("timeout {} /usr/local/bin/rtl_fm -d 0 -f {} -g 49.6 -s 37000 -E deemp -F 9 - | sox -traw -esigned -c1 -b16 -r37000 - {}.wav rate 11025".format(duration, frequency, outfile))

    #update the status in daily_passes.json
    with open("/home/pi/website/weather/scripts/daily_passes.json", "r") as f:
        data = json.load(f)
    with open("/home/pi/website/weather/scripts/daily_passes.json", "w") as f:
        data[pass_index]["status"] = "PASSED"
        json.dump(data, f, indent=4, sort_keys=True)

    #create map overlay
    print("creating map")
    date = (datetime.strptime(p['aos'], "%Y-%m-%d %H:%M:%S.%f %Z")+timedelta(0, 90)).strftime("%d %b %Y %H:%M:%S")
    os.system("/usr/local/bin/wxmap -T \"{}\" -H /home/pi/website/weather/scripts/weather.tle -p 0 -l 0 -o \"{}\" {}-map.png".format(sat, date, outfile))

    #create image from channel a
    print("create image from channel a")
    os.system("/usr/local/bin/wxtoimg -m {}-map.png -A -a -B 120 -L 600 {}.wav {}.a.png".format(outfile, outfile, outfile))

    #create image from channel b
    print("creating image from channel b")
    os.system("/usr/local/bin/wxtoimg -m {}-map.png -A -b -B 120 -L 600 {}.wav {}.b.png".format(outfile, outfile, outfile))

    #create image with MSA enhancement from channel a
    print("creating MSA image")
    os.system("/usr/local/bin/wxtoimg -m {}-map.png -A -B 120 -L 600 -e MSA {}.wav {}.MSA.png".format(outfile, outfile, outfile))
    
    #create image with MSA-precip enhancement from channel a
    print("creagin MSA-precip image")
    os.system("/usr/local/bin/wxtoimg -m {}-map.png -A -B 120 -L 600 -e MSA-precip {}.wav {}.MSA-precip.png".format(outfile, outfile, outfile))

    #create raw image
    print("creating raw image")
    os.system("/usr/local/bin/wxtoimg -m {}-map.png -A -B 120 -L 600 {}.wav {}.raw.png".format(outfile, outfile, outfile))

    links = {}
    
    #upload channel a image
    links["a"] = upload("{}.a.png".format(outfile), "{} at {}° at {}".format(sat, max_elevation, local_time))

    #upload channel b image
    links["b"] = upload("{}.b.png".format(outfile), "{} at {}° at {}".format(sat, max_elevation, local_time))

    #upload channel MSA image
    links["msa"] = upload("{}.MSA.png".format(outfile), "{} at {}° at {}".format(sat, max_elevation, local_time))
    
    #upload channel MSA-precip image
    links["msa-precip"] = upload("{}.MSA-precip.png".format(outfile), "{} at {}° at {}".format(sat, max_elevation, local_time))

    #upload channel raw image
    links["raw"] = upload("{}.raw.png".format(outfile), "{} at {}° at {}".format(sat, max_elevation, local_time))

    #write pass info to json file
    with open("/home/pi/website/weather/images/{}/{}/{}.json".format(day, local_time, local_time), "w") as f:
        pass_info = p
        pass_info['links'] = links
        json.dump(pass_info, f, indent=4, sort_keys=True)


    #will probably delete this soon
    '''
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
        data = json.load(f)
        if pass_index == len(data) - 1:
            soup.find(id="countdown")["next_pass"] = "unavailable"
        else:
            soup.find(id="countdown")["next_pass"] = data[pass_index+1]['los']

    #write the code index.html
    html = open("/home/pi/website/weather/index.html", "w")
    html.write(str(soup))
    '''


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
    #string used for naming the files  (aos in %Y-%m-%d %H.%M.%S format)
    local_time = datetime.strptime(p['aos'], "%Y-%m-%d %H:%M:%S.%f %Z").replace(tzinfo=timezone.utc).astimezone(tz=None).strftime("%Y-%m-%d_%H.%M.%S")#[:-13].replace(" ", "_").replace(":", ".")
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
        os.makedirs("/home/pi/website/weather/images/{}/{}".format(day, local_time))

    #update the status in daily_passes.json
    with open("/home/pi/website/weather/scripts/daily_passes.json", "r") as f:
        data = json.load(f)
    with open("/home/pi/website/weather/scripts/daily_passes.json", "w") as f:
        data[pass_index]["status"] = "CURRENT"
        json.dump(data, f, indent=4, sort_keys=True)

    if sat[:4] == "NOAA":
        process_NOAA()
    elif sat == "METEOR-M 2":
        process_METEOR()

    #add the pass to the top of showing_passes.json
    with open("/home/pi/website/weather/scripts/showing_passes.json", "r") as f:
        showing_passes = json.load(f)
    with open("/home/pi/website/weather/scripts/showing_passes.json", "w") as f:
        showing_passes = showing_passes[-1:] + showing_passes[:-1]
        showing_passes[0] = "/weather/images/{}/{}/{}.json".format(day, local_time, local_time)
        json.dump(showing_passes, f, indent=4, sort_keys=True)

    #commit changes to git repository
    print("commiting to github")
    os.system("/home/pi/website/weather/scripts/commit.sh")

    print("done processing")