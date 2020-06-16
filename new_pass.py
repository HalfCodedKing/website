from string import Template
import sys
import re

if __name__ == "__main__":
    now = sys.argv[1]
    title = sys.argv[2]
    main_image = sys.argv[3]
    a = sys.argv[4]
    b = sys.argv[5]
    msa = sys.argv[6]
    raw = sys.argv[7]
    html = open("/home/pi/website/media/pass.html")
    src = Template(html.read())
    prefix = "/weather/images/{}/".format(now)
    d = {"title":title, "main":prefix + main_image.split("/")[-1], "a":prefix + a.split("/")[-1], "b":prefix + b.split("/")[-1], "msa":prefix + msa.split("/")[-1], "raw":prefix + raw.split("/")[-1]}
    result = src.substitute(d)

    html = open("/home/pi/website/weather/index.html", "r")
    src = html.read()
    a = re.search(r'\b(main_content)\b', src)
    index = a.start() + 17
    b = src[:index] + result + src[index:]
    html = open("/home/pi/website/weather/index.html", "w")
    html.write(b)
    print("done")
