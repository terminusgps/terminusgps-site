from wagtail import hooks


@hooks.register("register_icons")
def register_icons(icons):
    return icons + [
        "home/icons/calendar.svg",
        "home/icons/flames.svg",
        "home/icons/ringing-bell.svg",
        "home/icons/smiley-face.svg",
    ]
