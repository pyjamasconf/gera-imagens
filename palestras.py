import csv
import json
import textwrap
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont


CSVPATH = "./aprovadas_all.csv"
JSONPATH = "./aprovadas_all.json"
COLS = [
    'Hora', 'Dia', 'Palestra',
    'Link', 'Palestrante', 'Descrição', 'Email', 'Minutos'
]
talks = list(csv.DictReader(open(CSVPATH)))

template = Image.open("./template.png")

speaker = ImageFont.truetype("Verdana.ttf", 60)
title = ImageFont.truetype("Verdana.ttf", 25)
description = ImageFont.truetype("Verdana.ttf", 20)
info = ImageFont.truetype("Verdana.ttf", 22)
obs = ImageFont.truetype("Verdana.ttf", 10)

AVATAR_SIZE = (322, 322)
LEFT_BORDER = 40


def get_time_from_json_time(datestr):
    obj = datetime.strptime(datestr, "%Y-%m-%dT%H:%M:%S.000")
    return f"{obj.day}/{obj.month}/{obj.year} às {obj.hour}:{obj.minute}"


def find_image(email):
    for ext in ["jpg", "png", "jpeg", "gif"]:
        path = f"{email}.{ext}"
        if Path(path).exists():
            return path
    return False


def write(xy, writer, text, font, size=40, fill="#fff"):
    margin, offset = xy
    for line in textwrap.wrap(text, width=size):
        writer.text((margin, offset), line, font=font, fill=fill)
        offset += font.getsize(line)[1]
    return offset + 20


for talk in talks:
    image = find_image(f"./originais/{talk['Email']}")
    if image:
        avatar = Image.open(image).resize(AVATAR_SIZE, Image.ANTIALIAS)
        bigsize = (avatar.size[0] * 3, avatar.size[1] * 3)
        mask = Image.new("L", bigsize, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + bigsize, fill=255)
        mask = mask.resize(avatar.size, Image.ANTIALIAS)
        avatar.putalpha(mask)

        new = template.convert("RGBA")
        new.paste(avatar, (628, 96), mask)

        writer = ImageDraw.Draw(new)
        offset = write((LEFT_BORDER, 95), writer, talk["Palestrante"], speaker)
        offset = write((LEFT_BORDER, offset), writer, talk["Palestra"], title)
        offset = write(
            (LEFT_BORDER, offset),
            writer,
            talk["Descrição"][:140] + "...",
            description,
            fill="#000",
        )
        offset = write(
            (LEFT_BORDER, offset),
            writer,
            f"{talk['Dia']} às {talk['Hora']}",
            info,
            fill="#000",
        )
        offset = write((LEFT_BORDER, offset - 20), writer, "BRT(GMT-3)", obs)

        new.save(f"./talks/{talk['Email']}.png")


# save json

json.dump(
    [
        {
            "title": talk["Palestra"],
            "description": talk["Descrição"],
            "speaker": talk["Palestrante"],
            "email": talk["Email"],
            "datetime": "2019-12-02T16:40:00.000",  # TODO: tranform datetime
            "duration": talk["Minutos"],
            "embed_link": "",
            "link": talk["Link"]
        }
        for talk in talks
    ],
    open(JSONPATH, "w", encoding="utf-8"),
    ensure_ascii=False
)
