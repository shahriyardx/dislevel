import os
from easy_pil import Editor, Canvas, Font, load_image


def get_card(data):
    profile_image = load_image(data["profile_image"])
    profile = Editor(profile_image).resize((150, 150))

    if data["bg_image"].startswith("http"):
        bg_image = load_image(data["bg_image"])
    else:
        bg_image = os.path.join(os.path.dirname(__file__), "assets", "bg.png")

    background = Editor(bg_image).resize((900, 300), crop=True)

    profile_back = Editor(Canvas((190, 300), "#ffffff42"))
    rep_back = Editor(Canvas((150, 50), "#3FA0FF3B")).rounded_corners(radius=5)
    dark_overlay = Editor(Canvas((900, 300), "#00000066"))
    prog_back = Editor(Canvas((584, 34), "#A7A9AC91")).rounded_corners(radius=10)
    prog_bar = Editor(Canvas((584, 34)))

    background.paste(dark_overlay, (0, 0))
    background.paste(profile_back, (40, 0))
    background.paste(profile, (60, 20))

    background.paste(rep_back, (60, 220))
    background.text(
        (135, 235),
        data["rep"],
        font=Font.montserrat(size=24),
        color="#ffffff",
        align="center",
    )
    background.text(
        (275, 30), data["name"], font=Font.montserrat(size=50), color="#ffffff"
    )
    background.text(
        (275, 85),
        f'#{data["descriminator"]}',
        font=Font.montserrat(size=20),
        color="#BCBEC0",
    )
    background.text(
        (875, 42),
        f'#{data["position"]}',
        font=Font.montserrat(size=45),
        color="#ffffff",
        align="right",
    )

    background.paste(prog_back, (275, 220))
    prog_bar.bar((0, 0), 580, 30, data["percentage"], "#A7A9AC91", radius=8)
    background.paste(prog_bar, (277, 222))
    background.text(
        (570, 226),
        f"{data['current_user_exp']} / {data['next_level_exp']}",
        font=Font.montserrat(size=20),
        color="white",
        align="center",
    )

    background.text(
        (275, 265),
        f"Level : {data['level']}",
        font=Font.montserrat(size=18),
        color="white",
        align="left",
    )
    if data["next_role"]:
        background.text(
            (863, 265),
            f"Next Role : {data['next_role']}",
            font=Font.montserrat(size=18),
            color="white",
            align="right",
        )

    return background.image_bytes
