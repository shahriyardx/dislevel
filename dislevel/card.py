import os
import re

from easy_pil import Canvas, Editor, Font, load_image
from numerize.numerize import numerize

URL_REGEX = re.compile(
    r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)"
)


def get_card(data):
    profile_image = load_image(data["profile_image"])
    profile = Editor(profile_image).resize((200, 200))
    tcolor=(data["text_color"])
    tcolor2=(data["text_color2"])
    tcolor3=(data["text_color3"])
    if tcolor == None:
        tcolor = "white"
    if tcolor2 == None:
        tcolor2 = "white"
    if tcolor3 == None:
        tcolor3 = "white"
    if data["bg_image"] and URL_REGEX.match(data["bg_image"]):
        try:
            bg_image = load_image(data["bg_image"])
        except Exception as e:
            bg_image = os.path.join(os.path.dirname(__file__), "assets", "bg.png")
    else:
        bg_image = os.path.join(os.path.dirname(__file__), "assets", "bg.png")

    background = Editor(bg_image).resize((800, 240), crop=True)

    font_25 = Font.poppins(size=25)
    font_30 = Font.poppins(size=30)
    font_40 = Font.poppins(size=40)
    font_40_bold = Font.poppins(size=40, variant="bold")

    background.paste(profile, (20, 20))
    background.text(
        (240, 20),
        f"{data['name']}",
        font=font_40,
        color=f"{tcolor}",
    )

    background.text(
        (240, 60),
        f"#{data['descriminator']}",
        font=font_30,
        color=f"{tcolor2}"
    )

    background.text((250, 170), "LVL", font=font_25, color=f"{tcolor3}")
    background.text((310, 160), str(data["level"]), font=font_40_bold, color=f"{tcolor3}")

    background.rectangle((390, 170), 360, 25, outline=f"{tcolor3}", stroke_width=2)
    background.bar(
        (394, 174),
        352,
        17,
        percentage=data["percentage"],
        fill=f"{tcolor3}",
        stroke_width=2,
    )
    background.text(
        (875, 42),
        f'#{data["position"]}',
        font=Font.montserrat(size=45),
        color="#ffffff",
        align="right",
    )

    background.text(
        (390, 135), f"Rank : {data['position']}", font=font_25, color=f"{tcolor3}"
    )
    background.text(
        (750, 135),
        f"XP : {numerize(data['xp'])}/{numerize(data['next_level_xp'])}",
        font=font_25,
        color="white",
        align="right",
    )

    return background.image_bytes
