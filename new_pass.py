from string import Template
import sys
import re
from datetime import datetime
from imgurpython import ImgurClient
import json

if __name__ == "__main__":
    #assign all the arguments to variables
    now = sys.argv[1] #useless
    title = sys.argv[2]
    main_image = sys.argv[3]
    a = sys.argv[4]
    b = sys.argv[5]
    msa = sys.argv[6]
    raw = sys.argv[7]



    #get imgur creds
    f = open("/home/pi/website/imgur_creds.json")
    data = json.load(f)
    client_id = data["id"]
    client_secret = data["secret"]
    f.close()

    #upload the images to imgur
    client = ImgurClient(client_id, client_secret)
    counter=1
    while True:
        try:
            a = client.upload_from_path(a)
            print("uploaded")
            break
        except:
            print("failed")
            sleep(60*counter)
            counter+=1
            continue
    b = client.upload_from_path(b)
    msa = client.upload_from_path(msa)
    raw = client.upload_from_path(raw)



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

    #find the right spot in the page to insert the new code
    a = re.search(r'\b(main_content)\b', src)
    index = a.start() + 17
    b = src[:index] + result + src[index:]

    #write the code index.html
    html = open("/home/pi/website/weather/index.html", "w")
    html.write(b)
