from string import Template
import sys
import re

if __name__ == "__main__":
    title = sys.argv[0]
    main_image = sys.argv[1]
    a = sys.argv[2]
    b = sys.argv[3]
    msa = sys.argv[4]
    raw = sys.argv[5]
    html = open("/home/pi/website/media/pass.html")
    src = Template(html.read())
    d = {"title":title, "main":main_image, "a":a, "b":b, "msa":msa, "raw":raw}
    result = src.substitute(d)

    html = open("/home/pi/website/weather/index.html")
    src = html.read()
    a = re.search(r'\b(main_content)\b', src)
    index = a.start() + 17
    b = src[:index] + result + src[index:]
