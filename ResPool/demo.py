__author__ = 'jason'

from res_manager import *
from res_pool import *
from random import *

add("time", "day", lambda value: {"day": "night", "night": "day"}[value])
add("sound", 20, lambda: randint(0, 100))
add("location", "Register Province", lambda: ["Other Country", "Register Province", "Other Province"][randint(0, 2)])
add("wifi", "strong", lambda: ["strong", "weak"][randint(0, 1)])
add("bluetooth", "exit", lambda: ["exit", "not exit"][randint(0, 1)])
add("user event", {"meeting": True, "sleeping": False, "waiting": False},
    lambda: {"meeting": bool(randint(0, 1)), "sleeping": bool(randint(0, 1)), "waiting": bool(randint(0, 1))})
add("Internal Memory", 1000, lambda value: value - 5 if value > 5 else 100)
add("SD card", 8000, lambda value: value - 5 if value > 5 else 8000)
add("Memory", {"Internal Memory": 1000, "SD card": 8000},
    lambda: {"Internal Memory": get("Internal Memory"), "SD card": get("SD card")})
add("LED", "on", lambda value: {"on": "off", "off": "on"}[value])
add("Battery", 100, lambda value: value - 1 if value > 1 else 0)
add("surrounding", {"sound": 20, "wifi": "strong", "bluetooth": "exit"},
    lambda: {"sound": get("sound"), "wifi": get("wifi"), "bluetooth": get("wifi")})
tick()
tock()

update("time", 1)
update("location", 1)
update("sound", 1)
update("wifi", 1)
update("bluetooth", 1)
update("user event", 1)
update("Internal Memory", 1)
update("SD card", 1)
update("Memory", 1)
update("LED", 1)
update("Battery", 1)
update("surrounding", 1)

for i in range(1000):
    tick()
    tock()
