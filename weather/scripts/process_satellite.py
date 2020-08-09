#Made by Felix (Blobtoe)

import os
import json
from PIL import Image
from datetime import datetime, timedelta


#######################################
#records, demodulates, and decodes METEOR-M 2 given the json file for the pass and the output file name, then returns the image's file path
def METEOR(path, outfile):
    #set variables
    with open(path) as f:
        data = json.load(f)
        duration = data["duration"]
        frequency = data["frequency"]

    #record pass baseband with rtl_fm
    print("recording pass...")
    os.system("timeout {} /usr/bin/rtl_fm -M raw -s 110k -f {} -E dc -g 49.6 -p 0 - | sox -t raw -r 110k -c 2 -b 16 -e s - -t wav {}.iq.wav rate 192k".format(duration, frequency, outfile))

    #demodulate the signal
    print("demodulating meteor signal...")
    os.system("/usr/bin/meteor_demod -B -r 72000 -m qpsk -o {}.qpsk {}.iq.wav".format(outfile, outfile))

    #decode the signal into an image
    print("decoding image...")
    os.system("/usr/local/bin/medet_arm {}.qpsk {} -q -cd".format(outfile, outfile))
    
    #convert bmp to jpg and rotate 180 deg
    os.system("convert {}.bmp -rotate 180 {}.jpg".format(outfile, outfile))

    #get rid of the blue tint in the image (thanks to PotatoSalad for the code)
    img = Image.open(outfile + ".jpg")
    pix = img.load()
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            if pix[x, y][2] > 140 and pix[x, y][0] < pix[x, y][2]:
                pix[x, y] = (pix[x, y][2], pix[x, y][1], pix[x, y][2])
    img.save(outfile + ".equalized.jpg")

    #rectify images
    os.system("/usr/local/bin/rectify-jpg {}.equalized.jpg".format(outfile))

    #rename file
    os.rename("{}.equalized-rectified.jpg".format(outfile), "{}.rgb123.jpg".format(outfile))

    #return the image's file path
    return ["{}.rgb123.jpg".format(outfile)], "rgb123"


#######################################
#records and decodes NOAA APT satellites given the json file for the pass and the output file name, then returns the images' file paths
def NOAA(path, outfile):
    #set variables
    with open(path) as f:
        data = json.load(f)
        duration = data["duration"]
        frequency = data["frequency"]
        satellite = data["satellite"]
        aos = data["aos"]
        sun_elev = data["sun_elev"]

    #record the pass with rtl_fm
    print("writing to file: {}.wav".format(outfile))
    os.system("timeout {} /usr/bin/rtl_fm -d 0 -f {} -g 49.6 -s 37000 -E deemp -F 9 - | sox -traw -esigned -c1 -b16 -r37000 - {}.wav rate 11025".format(duration, frequency, outfile))

    #check if the wav file was properly created
    if os.path.isfile(outfile + ".wav") == True and os.stat(outfile + ".wav").st_size > 10:
        pass
    else:
        print("wav file was not created correctly. Aborting")
        exit()

    #create map overlay
    print("creating map")
    date = (datetime.strptime(aos, "%Y-%m-%d %H:%M:%S.%f %Z")+timedelta(0, 90)).strftime("%d %b %Y %H:%M:%S")
    os.system("/usr/local/bin/wxmap -T \"{}\" -H /home/pi/website/weather/scripts/weather.tle -p 0 -l 0 -g 0 -o \"{}\" {}-map.png".format(satellite, date, outfile))

    #create images
    os.system("/usr/local/bin/wxtoimg -m {}-map.png -A -i JPEG -a -e contrast {}.wav {}.a.jpg".format(outfile, outfile, outfile))
    os.system("/usr/local/bin/wxtoimg -m {}-map.png -A -i JPEG -b -e contrast {}.wav {}.b.jpg".format(outfile, outfile, outfile))
    os.system("/usr/local/bin/wxtoimg -m {}-map.png -A -i JPEG -e HVCT {}.wav {}.HVCT.jpg".format(outfile, outfile, outfile))
    os.system("/usr/local/bin/wxtoimg -m {}-map.png -A -i JPEG -e MSA {}.wav {}.MSA.jpg".format(outfile, outfile, outfile))
    os.system("/usr/local/bin/wxtoimg -m {}-map.png -A -i JPEG -e MSA-precip {}.wav {}.MSA-precip.jpg".format(outfile, outfile, outfile))
    os.system("/usr/local/bin/wxtoimg -m {}-map.png -A -i JPEG {}.wav {}.raw.jpg".format(outfile, outfile, outfile))

    #change the main image depending on the sun elevation
    if sun_elev <= 10 :
        main_tag = "b"
    elif sun_elev <= 20:
        main_tag = "HVCT"
    else:
        main_tag = "MSA-precip"

    #return the images' file paths
    return [
        "{}.a.jpg".format(outfile),
        "{}.b.jpg".format(outfile),
        "{}.HVCT.jpg".format(outfile),
        "{}.MSA.jpg".format(outfile),
        "{}.MSA-precip.jpg".format(outfile),
        "{}.raw.jpg".format(outfile)], main_tag
