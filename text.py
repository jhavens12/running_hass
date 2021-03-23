import data
import pprint
import copy

database = data.run()





def gen_text(): #takes in dictionary of titles and values
    w = 600
    h = 60
    filename = png_location+"Last_Run_Stats.png"
    img = Image.new('RGBA', (w, h), (255, 0, 0, 0))
    fnt = ImageFont.truetype('./resource/din_medium_regular.ttf', 30)
    d = ImageDraw.Draw(img)
    #
    # shoe_print = Image.open("./Icons/shoe-print.png")
    # timer = Image.open("./Icons/timer.png")
    # speedometer = Image.open("./Icons/speedometer.png")

    #x,y
    row_1 = 10
    row_2 = 15

    d.text((60,row_2), str(database['distance_miles']) , font=fnt, fill=(255, 255, 255))
    d.text((260,row_2), str(database['elapsed']) , font=fnt, fill=(255, 255, 255))
    d.text((460,row_2), str(database['pace']) , font=fnt, fill=(255, 255, 255))

    img.save(filename)
    #d = Image.open(filename)

    # d.paste(shoe_print, (0, row_1), shoe_print)
    # d.paste(timer, (200, row_1), timer)
    # d.paste(speedometer, (400, row_1), speedometer)

    # d.save(filename)
    # photos.create_image_asset(filename) #ios
