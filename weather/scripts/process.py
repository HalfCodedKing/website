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
from discord_webhook import DiscordWebhook, DiscordEmbed

def upload_discord(path):
    print("sending webhook to discord...")
    #load the json file from the pass
    with open(path) as f:
        data = json.load(f)

        with open("secrets.json") as s:
            secrets = json.load(s)
            webhook_url = secrets["discord_webhook_url"]

        #send a message with the discord webhook
        webhook = DiscordWebhook(url=webhook_url, username="Blobtoe's Kinda Crappy Images")
        embed = DiscordEmbed(title=data["satellite"], description="Pass over Vancouver, Canada", color=242424)
        embed.set_image(url=data["links"]["a"], width='1000')
        embed.add_embed_field(name='Max Elevation', value=str(data["max_elevation"]) + "°")
        embed.add_embed_field(name='Frequency', value=str(data["frequency"]) + " Hz")
        embed.add_embed_field(name="Duration", value=str(round(data["duration"])) + " seconds")
        embed.add_embed_field(name='Pass Start', value=data["aos"])
        embed.add_embed_field(name='Other Image Links', value="[Channel A]({})\n[Channel B]({})\n[MSA Enhanced]({})\n[Raw]({})".format(data["links"]["a"], data["links"]["b"], data["links"]["msa"], data["links"]["raw"]))
        webhook.add_embed(embed)
        response = webhook.execute()
        print("done")

def upload_imgur(path, title):
    #check if the file exists
    if os.path.isfile(path) == False:
        print("Error: Image does not exists.")
        return

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
    print("uploading {} to imgur".format(path))
    link = ""
    count = 0
    while count<10:
        try:
            img = client.upload_from_path(path, config=config)
            link = img["link"]
            break
        except:
            count += 1
            print("failed to upload image... trying again  {}/10".format(count))
            continue
    print("done")
    
    #return the link of the uploaded image
    return link

def process_METEOR():
    #record pass
    print("recording pass...")
    os.system("timeout {} /usr/bin/rtl_fm -M raw -s 768k -f {} -E dc -g 49.6 -p 0 - | sox -t raw -r 768k -c 2 -b 16 -e s - -t wav {}.iq.wav rate 192k".format(duration, frequency, outfile))
    #os.system("timeout {} /usr/bin/rtl_fm -Mraw -s768k -f {} -g49.6 -p 0 -F 9 | sox -t raw -r 768k -c 2 -b 16 -e s - -t wav {}.iq.wav rate 192k".format(duration, frequency, outfile))

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
    link = upload_imgur("{}.png".format(outfile), "{} at {}° at {}".format(sat, max_elevation, local_time))

    #write pass info to json file
    with open("/home/pi/website/weather/images/{}/{}/{}.json".format(day, local_time, local_time), "w") as f:
        pass_info = p
        pass_info['link'] = link
        json.dump(pass_info, f, indent=4, sort_keys=True)

def process_NOAA():
    #record the pass with rtl_fm
    print("writing to file: {}.wav".format(outfile))
    os.system("timeout {} /usr/bin/rtl_fm -d 0 -f {} -g 49.6 -s 37000 -E deemp -F 9 - | sox -traw -esigned -c1 -b16 -r37000 - {}.wav rate 11025".format(duration, frequency, outfile))

    #check if the wav file was properly created
    if os.path.isfile(outfile + ".wav") == True and os.stat(outfile + ".wav").st_size > 10:
        pass
    else:
        print("wav file was not created correctly. Aborting")
        exit()

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
    os.system("/usr/local/bin/wxtoimg -m {}-map.png -A -a {}.wav {}.a.png".format(outfile, outfile, outfile))

    #create image from channel b
    print("creating image from channel b")
    os.system("/usr/local/bin/wxtoimg -m {}-map.png -A -b {}.wav {}.b.png".format(outfile, outfile, outfile))

    #create image with MSA enhancement from channel a
    print("creating MSA image")
    os.system("/usr/local/bin/wxtoimg -m {}-map.png -A -e MSA {}.wav {}.MSA.png".format(outfile, outfile, outfile))
    
    #create image with MSA-precip enhancement from channel a
    print("creagin MSA-precip image")
    os.system("/usr/local/bin/wxtoimg -m {}-map.png -A -e MSA-precip {}.wav {}.MSA-precip.png".format(outfile, outfile, outfile))

    #create raw image
    print("creating raw image")
    os.system("/usr/local/bin/wxtoimg -m {}-map.png -A {}.wav {}.raw.png".format(outfile, outfile, outfile))

    links = {}
    
    #upload channel a image
    links["a"] = upload_imgur("{}.a.png".format(outfile), "{} at {}° at {}".format(sat, max_elevation, local_time))

    #upload channel b image
    links["b"] = upload_imgur("{}.b.png".format(outfile), "{} at {}° at {}".format(sat, max_elevation, local_time))

    #upload channel MSA image
    links["msa"] = upload_imgur("{}.MSA.png".format(outfile), "{} at {}° at {}".format(sat, max_elevation, local_time))
    
    #upload channel MSA-precip image
    links["msa-precip"] = upload_imgur("{}.MSA-precip.png".format(outfile), "{} at {}° at {}".format(sat, max_elevation, local_time))

    #upload channel raw image
    links["raw"] = upload_imgur("{}.raw.png".format(outfile), "{} at {}° at {}".format(sat, max_elevation, local_time))

    #write pass info to json file
    with open("/home/pi/website/weather/images/{}/{}/{}.json".format(day, local_time, local_time), "w") as f:
        pass_info = p
        pass_info['links'] = links
        json.dump(pass_info, f, indent=4, sort_keys=True)

    upload_discord("/home/pi/website/weather/images/{}/{}/{}.json".format(day, local_time, local_time))

if __name__ == "__main__":
    #get the index of the pass in daily_passes.json
    pass_index = int(sys.argv[1])

    #update the status in daily_passes.json
    with open("/home/pi/website/weather/scripts/daily_passes.json", "r") as f:
        data = json.load(f)
    with open("/home/pi/website/weather/scripts/daily_passes.json", "w") as f:
        data[pass_index]["status"] = "CURRENT"
        json.dump(data, f, indent=4, sort_keys=True)

    #get info about the pass from the daily_passes.json
    f = open("/home/pi/website/weather/scripts/daily_passes.json")
    p = json.load(f)[pass_index]
    f.close()

    #assign variables
    try:
        with open("/home/pi/website/weather/scripts/secrets.json") as f:
            data = json.load(f)
            lat = data['lat']
            lon = data['lon']
            elev = data['elev']
    except:
        print("Failed to open secrets.json. Aborting")
        exit()

    sat = p['satellite']
    frequency = p['frequency']
    duration = p['duration']
    max_elevation = p['max_elevation']
    #string used for naming the files  (aos in %Y-%m-%d %H.%M.%S format)
    local_time = datetime.strptime(p['aos'], "%Y-%m-%d %H:%M:%S.%f %Z").replace(tzinfo=timezone.utc).astimezone(tz=None).strftime("%Y-%m-%d_%H.%M.%S")#[:-13].replace(" ", "_").replace(":", ".")
    #the name of the folder containing all the passes for the day (aos in %Y-%m-%d format)
    day = str(local_time)[:10]
    outfile = "/home/pi/drive/weather/images/{}/{}/{}".format(day, local_time, local_time)

    try:
        #if this is the first pass of the day, create a new folder for all the images of the day
        if not os.path.exists("/home/pi/drive/weather/images/{}".format(day)):
            os.makedirs("/home/pi/website/weather/images/{}".format(day))
            os.makedirs("/home/pi/drive/weather/images/{}".format(day))

        #create new directory for this pass
        if not os.path.exists("/home/pi/drive/weather/images/{}/{}".format(day, local_time)):
            os.makedirs("/home/pi/drive/weather/images/{}/{}".format(day, local_time))
            os.makedirs("/home/pi/website/weather/images/{}/{}".format(day, local_time))
    except:
        print("Failed creating new directories for the pass. Aborting")
        exit()

    #process depending on the satellite
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
    os.system("/home/pi/website/weather/scripts/commit.sh 'auto commit for pass'")

    print("done processing")