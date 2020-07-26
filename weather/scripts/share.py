#Made by Felix (Blobtoe)

import json
import os
from imgurpython import ImgurClient
from discord_webhook import DiscordWebhook, DiscordEmbed


#######################################
#sends a message to a discord webhook given the json file for the pass and the webhook url
def discord_webhook(path, webhook_url):
    print("sharing to discord")

    #load the json file from the pass
    with open(path) as f:
        data = json.load(f)

    #send a message with the discord webhook
    webhook = DiscordWebhook(url=webhook_url, username="Blobtoe's Kinda Crappy Images")
    embed = DiscordEmbed(title=data["satellite"], description="Pass over Vancouver, Canada", color=242424)
    embed.add_embed_field(name='Max Elevation', value=str(data["max_elevation"]) + "°")
    embed.add_embed_field(name='Frequency', value=str(data["frequency"]) + " Hz")
    embed.add_embed_field(name="Duration", value=str(round(data["duration"])) + " seconds")
    embed.add_embed_field(name='Pass Start', value=data["aos"])
    embed.add_embed_field(name='Sun Elevation', value=str(data["sun_elev"]))
    if data["satellite"][:4] == "NOAA":
        embed.set_image(url=data["links"]["a"])
        embed.add_embed_field(name='Other Image Links', value="[Channel A]({})\n[Channel B]({})\n[HVCT Enhanced]({})\n[MSA Enhanced]({})\n[Raw]({})".format(data["links"]["a"], data["links"]["b"], data["links"]["HVCT"], data["links"]["MSA"], data["links"]["raw"]))
    elif data["satellite"] == "METEOR-M 2":
        embed.set_image(url=data["links"]["rgb123"])
    webhook.add_embed(embed)
    response = webhook.execute()

    print("done")
    return response


#######################################
#uploads an image to imgur given the json file for the pass and the image's file path, then returns the link
def imgur(path, image):
    print("sharing to imgur")

    #check if the file exists
    if os.path.isfile(image) == False:
        print("Error: Image does not exists.")
        return

    #get imgur credentials from secrets.json
    with open("/home/pi/website/weather/scripts/secrets.json") as f:
        data = json.load(f)
        client_id = data["id"]
        client_secret = data["secret"]

    #create title for imgur post
    with open(path) as f:
        data = json.load(f)
        title = "{} at {}° at {}".format(data["satellite"], data["max_elevation"], data["aos"])

    #upload the image
    print("uploading {} to imgur".format(image))

    client = ImgurClient(client_id, client_secret)
    config = {
        'name': title,
        'title': title
    }

    #try 10 times to upload image
    count = 0
    while True:
        try:
            img = client.upload_from_path(image, config=config)
            link = img["link"]
            print("done")
            return link
        except Exception as e:
            count += 1
            print("failed to upload image... trying again  {}/10".format(count))
            print(e)

            if count >= 10:
                return None

        