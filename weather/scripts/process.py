#Made by Felix (Blobtoe)

import sys
import json
import os
from datetime import datetime, timezone
import ephem
import piexif
import piexif.helper

#local imports
import process_satellite
import share


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
    with open("/home/pi/website/weather/scripts/daily_passes.json") as f:
        p = json.load(f)[pass_index]

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
    day = str(local_time)[:10]
    #the name of the folder containing all the passes for the day (aos in %Y-%m-%d format)
    outfile = "/home/pi/drive/weather/images/{}/{}/{}".format(day, local_time, local_time)
    #the name of the json file containing all the info about the pass
    pass_file = "/home/pi/website/weather/images/{}/{}/{}.json".format(day, local_time, local_time)

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

    #compute sun elevation
    obs = ephem.Observer()
    obs.lat = str(lat)
    obs.long = str(lon)
    obs.date = datetime.strptime(p['tca'], "%Y-%m-%d %H:%M:%S.%f %Z")

    sun = ephem.Sun(obs)
    sun.compute(obs)
    sun_elev = round(float(sun.alt) * 57.2957795, 1) #convert to degrees from radians

    #write sun elevation to pass file
    with open(pass_file, "w") as f:
        pass_info = p
        pass_info["sun_elev"] = sun_elev
        json.dump(pass_info, f, indent=4, sort_keys=True)

    #process depending on the satellite
    if sat[:4] == "NOAA":
        images, main_tag = process_satellite.NOAA(pass_file, outfile)
    elif sat == "METEOR-M 2":
        images, main_tag = process_satellite.METEOR(pass_file, outfile)

    #upload each image to imgur
    links = {}
    with open(pass_file) as f:
        data = json.load(f)
        for image in images:
            #add metadata to image
            exif_dict = piexif.load(image)
            exif_dict["Exif"][piexif.ExifIFD.UserComment] = piexif.helper.UserComment.dump(json.dumps(data), encoding="unicode")
            piexif.insert(piexif.dump(exif_dict), image)

            #upload image and get a link
            tag = image.split(".")[-2]
            link = share.imgbb(image)
            if tag == main_tag:
                main_image = link
            links[tag] = link

    #write pass info to json file
    with open(pass_file) as fr:
        pass_info = json.load(fr)
        with open(pass_file, "w") as fw:
            pass_info['links'] = links
            pass_info["main_image"] = main_image
            json.dump(pass_info, fw, indent=4, sort_keys=True)

    #send discord webhook
    with open("/home/pi/website/weather/scripts/secrets.json") as f:
        data = json.load(f)
        result = share.discord_webhook(pass_file, data["discord_webhook_url"])
        print(result)

    #update the status in daily_passes.json
    with open("/home/pi/website/weather/scripts/daily_passes.json", "r") as f:
        data = json.load(f)
    with open("/home/pi/website/weather/scripts/daily_passes.json", "w") as f:
        data[pass_index]["status"] = "PASSED"
        json.dump(data, f, indent=4, sort_keys=True)

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
