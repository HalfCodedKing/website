from string import Template
import sys
import re
from datetime import datetime

if __name__ == "__main__":
    #assign all the arguments to variables
    now = sys.argv[1]
    title = sys.argv[2]
    main_image = sys.argv[3]
    a = sys.argv[4]
    b = sys.argv[5]
    msa = sys.argv[6]
    raw = sys.argv[7]

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
    prefix = "/weather/images/{}/".format(now)
    d = {"title":title, "main":prefix + main_image.split("/")[-1], "a":prefix + a.split("/")[-1], "b":prefix + b.split("/")[-1], "msa":prefix + msa.split("/")[-1], "raw":prefix + raw.split("/")[-1]}
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
    print("done")
