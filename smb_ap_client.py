import asyncio
import json
import struct
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Set, List, Tuple
from collections import deque
import time
import os
import sys

import ctypes
user32 = ctypes.windll.user32
VK_ESCAPE = 0x1B
KEYEVENTF_KEYUP = 0x0002

# When frozen by PyInstaller, show errors as messageboxes instead of prints
def _fatal_error(msg):
    try:
        import tkinter as _tk
        root = _tk.Tk()
        root.withdraw()
        _tk.messagebox.showerror("SMB AP Client - Error", msg)
        root.destroy()
    except:
        print(msg)
    sys.exit(1)

try:
    import pymem
except ImportError:
    _fatal_error("pymem library not found!\n\nIf running from source:\n  pip install pymem")

try:
    import websockets
except ImportError:
    _fatal_error("websockets library not found!\n\nIf running from source:\n  pip install websockets")

try:
    from smb_apworld_data import (
        # Item IDs
        ITEM_OFFSET, LOC_OFFSET,
    ITEM_BANDAGE, ITEM_BOSS_TOKEN, ITEM_VICTORY,
    ITEM_DW_DR_FETUS_KEY, ITEM_CH7_LW_LEVEL_KEY, ITEM_CH7_DW_LEVEL_KEY,
    ITEM_DEGRADED_BANDAGE,
    ITEM_MEAT_BOY, ITEM_BANDAGE_GIRL,
    ITEM_COMMANDER_VIDEO, ITEM_JILL, ITEM_OGMO, ITEM_FLYWRENCH,
    ITEM_THE_KID, ITEM_JOSEF, ITEM_NAIJA, ITEM_STEVE,
    CHAPTER_KEY_ITEMS, BOSS_KEY_ITEMS, CHARACTER_ITEMS, APLUS_RANK_ITEMS,
    aplus_item_id,
    # Location name generators
    light_completion_name, dark_completion_name,
    light_aplus_name, dark_aplus_name,
    light_bandage_name, dark_bandage_name,
    lw_warp_completion_name, dw_warp_completion_name,
    lw_warp_bandage_name, dw_warp_bandage_name,
    boss_location_name, cutscene_location_name,
    xmas_completion_name, xmas_aplus_name, xmas_bandage_name,
    # Data tables
    WORLD_NAMES, NUM_LEVELS,
    LIGHT_LEVEL_NAMES, DARK_LEVEL_NAMES,
    LW_WARP_NAMES, DW_WARP_NAMES,
    BOSS_LOC_NAMES, DARK_BOSS_LOC_NAME,
    CUTSCENE_LOC_NAMES,
    LIGHT_BANDAGE_LEVELS, DARK_BANDAGE_LEVELS,
    BANDAGE_GRANT_TARGETS,
    # Achievement / speedrun / deathless data
    WARP_MILESTONE_NAMES, WORLD_CLEAR_NAMES,
    BANDAGE_MILESTONE_NAMES,
    SPEEDRUN_ACHIEVEMENTS, DEATHLESS_ACHIEVEMENTS,
    DEATH_COUNT_OFFSET,
    XMAS_LEVEL_NAMES, XMAS_ACHIEVEMENT_NAMES, XMAS_WORLD,
    # Memory layout
    WORLD_BASES, LIGHT_OFFSET, DARK_OFFSET, WARP_BASES, W6_DARK_OFFSET,
    SLOT_SIZE, COMP_BYTE, TIME_BYTE, NUM_WARP_SLOTS,
    FLAG_BANDAGE, FLAG_COMPLETE, FLAG_WARP, MASK_CLEAR_BANDAGE,
    ADDR, TYPE_LIGHT, TYPE_DARK, TYPE_WARP_MIN, TYPE_WARP_MAX,
    BOSS_LEVEL_INDEX, CHARACTER_BITMASK_OFFSET,
    BOSS_COUNTER_OFFSETS, BOSS_UNLOCK_THRESHOLDS,
    # Address helpers
    comp_addr, time_addr, slot_addr,
    # Par time helpers
    get_par_time, is_a_plus,
    # Type helpers
    type_to_region, is_warp,
    PAR_TIMES,
)
except ImportError:
    _fatal_error("smb_apworld_data.py not found!\n\n"
                 "This file must be in the same directory as the client.")



# CONSTANTS


APP_NAME = "Super Meat Boy - Archipelago Client"
APP_VERSION = "3.5.0"
GAME_NAME = "Super Meat Boy"
CONFIG_FILE = Path.home() / ".smb_ap_client.json"

# SMB Theme colors
DARK_BG = "#1e1e1e"         # Clean dark background
DARK_FG = "#e0e0e0"         # Standard light text
DARK_ENTRY_BG = "#2a2a2a"   # Input fields
DARK_FRAME_BG = "#242424"   # Frame background
DARK_ACCENT = "#5a2020"     # Muted red buttons
DARK_BORDER = "#7a3030"     # Hover red
SMB_RED = "#c81e1e"         # Header accent only
SMB_BANDAGE = "#b0a090"     # Subtitle color

# Embedded Meat Boy icon (32x32, base64 GIF)
MEATBOY_ICON_32 = (
    "R0lGODlhIAAgAIcAAP////3///f4+Pb09PDw8Ovu7ubp6d/o6OLl5dzh4dbY2NPR0cbS0bu9vaeq"
    "qamfoJqZmZihoamSkpKVlI57e3aAgXlwcX9VWHNNTmNCQ3gpK18yNDk6OogaJ28aGmoYKlwlJlge"
    "HjcfHzwVFx8ZGhIZGXUMFXIHCXEGCGQNFGIICVYHCVEGB1AICVAGB08GCEwGCEkICUUHCD4GBzoH"
    "CDUJDTIJCjYGBy8GCCsICB8NDR8JCh4ICCUHCBwGBxkICRsGBxYGCBUICRQHCBQGBg4KChEICQ0H"
    "BwkJCQkHCAcGBwALCwUGBgIGBQAGBqgCBKUCAqMCA6EDBKECA6ECAqACAZ4DAp4CA54CAp0DBJ0C"
    "A5sEBJsDApoDApkDA5oCApkCAZgCApgCAZgCAJYCA5YCApYCAZUDBJUCApECAo0EBY0CA4sCBIkD"
    "A4YCA4QCA4ICAoECAn8CA30FBnwCA3gCA3cCBHUCAnMDA3EFBnACA20DBGoCA2gCBGYEBWICBF0E"
    "BVwEBVcDBFMEBFAFBkUDAzkDBDAFBigEBSYFBiEEBhsDBBkDBBYDBBIFBQ8EBA4EBAkDAwYFBgMF"
    "BgIEBAMDAwIDBAAFBQAEBQEDAgECAgACAwACAgACAaoBAqcBAaQBAqMBAaMBAKIBAqIBAaEBAKAB"
    "AZ8BAZ8BAJ4BAZ0BAp0BAZ0BAJwBApwBAZwBAJsBApsBAZsBAJoBApoBAZoBAJkBA5kBApkBAZgB"
    "ApgBAZkBAJgBAJcBApcBAZcBAJYBA5YBApYBAZUBA5UBAJQBApMBApIBApIBAZABAY8BAo4BAo0B"
    "AowBAokBAoYBAoQBAYABAX4BAnsBAnkBAnUBAXQBAnIBAgwBAgEBAQABAgABAQABAJ8AAJ4AAp0A"
    "AJwAApoAApoAAZoAAJgAAZcAApYAAJUAApUAAJEAAI4AAIoAAYgAAYUAAYMAAn4AAH0AAHQAAHEA"
    "GWoAAC8AAhMAAwIAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAEAAAAALAAAAAAgACAA"
    "QAj/APEJHEiwoMGDBO1xuwGKlrpBguJFOyeuGK9du3hVsSaCRCM/p4rl4FTQCQpYZHClUrMhQoIA"
    "AGLKBIDAQIQVpjDymkVHmjMVTfDZ23bDk6xXr7xBW2eoE75t2zgVWkdrVy1Xya4JwXcPYVRMSerR"
    "kxEDBiEXLVi4eAFDBg0cQS5pMtiV0RQ5HzrIk0dnHTpz6tKhQzeO3Tt41NxRcQMIRps6rdQ0wtRj"
    "zx9Uu4Bd5MV5FxhYsWjx6nWrFhphvuIgutcVoevXsGPLTqhphhQouE0wYOAhlplyxYT9+kVMjKtd"
    "xFI1c8Q1Ib5EnqqV4BCpkqFWvnDplKXsUSV8RZBM/1OFKBOKKz+42rt0wpOWQZcmKEAQQEQlAQUI"
    "JFhwoEGEJYuckUswshzzBxrDxPDCJ3fY4U0uvHQRxTfszMPHCSmsgMI17aDTzS+0PKPHID0wsUlC"
    "nLTwCRukPQOHNO0400wzzDATjR7UlFPLLrfEwUhzBlEyyRGPYAOJJE4ENVA2SQCBQw2HJOJDEpbM"
    "ZuWVWGapJUH3XDLEDYSgAM8FHawSRSihjELKmmuWYgoWXrDAhEH2aOPCJ8l4IYUGFFCQRxW+2FJV"
    "Rqak0w4ap+ySjCLb2NOaUAs9YcwIFiwRSR2mnKMLRlYVo4MDHOATyRq0IMLJEDwo0VVXPEwBRz0z"
    "fP/wQQpuYAHGFlx00UUWimyCSQkkKFMGIk7MsQwij0gylA1PhBFIDRdgsAEGIYSQwQYbgBACCB9o"
    "oEIfbpShihZsBBKMHD9ss4MVt9ySRg0VLKAAAQ5AQIAAAwhgwAIOWLBNHqIQw0ssd+ARyxs+2BAF"
    "HGyA0wsr6MxjrQUUPCCBxRJckMEc3YxhjDjfHMMHDUcwkY0RfFizRyrk7PiLGFlskQY71Vzjzhdw"
    "imFVL3UsQhJrA0lixCCipLFGOLSwggorrsjidC3gwIIML2X0oks0PWzzqED2ZCJDKMLggssxewiC"
    "CCRB7LDDIobw8Yw4nOlyBxFADtQVEX7UMQ0ddvwbMYgP2ThqDyUzTLMMOcI0Q00gRWzp+OOQXxkQ"
    "ADs="
)

# Embedded Meat Boy icon (48x48 for header, base64 GIF)
MEATBOY_ICON_48 = (
    "R0lGODlhMAAwAIcAAP/////+/v7+/vr+/vv6+vf6+vX29vDw8Ozt7Obm5uDm5t3e3tHR0cDDw7q7"
    "vLWwsKalpaecnKeTk5CSkpSAgIGCgXZ/f4NnaGtoaFlbW2ZGRkU3OXQwMUctLzkrLYcTNH0RMGoU"
    "JVobHEohIU8QFj4cHTQTFh0VFQ8SEg8MDJgGB4gHCXIGCG0HCWAGCFIHCkkHDj8GBzQJCjgFBi0I"
    "CicICiQJCiMGCCEJCiEGCh0JChwHCBYJCxcHCBIJCg4JCgoLCwoJCQ4GBwoHBwcKCwULCwQLCwYJ"
    "CQcHBwUFBQQGBwIKCwEJCQIICAAHCAIGBgAGBwIFBQAFBQAFBLYCBK0DA6gDBKQDBKMCAqEDA58E"
    "BZ8DA54DA6ACA58CA54CAp0EBZ0DBJwDAp0CAZsCA5kDBJoCA5oCAZkCApYDBJUDBZcCApYCApUC"
    "A5MDBJMCApADA5ECAo4DBI4CA4sCBIoDBYoCA4YDBYYCA4MDBIECA34CA30CBHkCAnUDBXUCA3ID"
    "BXAEBW8CBGwDA2gDBGUDA2EDBGADBF4DBFwCA1oDBFcDBVIEBE8DBEwDBUoDBEcEBEQCBDoDBC8D"
    "BCQDBhoDBA8DAwsDBAcDBAMDAwIDAwEDAwAEBAADAwADAgACAqgBAqUBAqQBAaIBAqEBAZ8BAZ4B"
    "Ap4BAJ0BApwBApwBAZ0BAJwBAJsBApsBAZsBAJoBApoBAZoBAJkBA5kBApkBAZkBAJgBApgBAZgB"
    "AJcBApcBAZcBAJYBApYBAZUBApYBAJUBAJQBApIBApABAo4BAo0BAYoBAocBAoUBAYMBAYEBAn8B"
    "AX0BAnoBAXkBAXYBAnMBA20BAyEBAgIBAQEBAQABAgABAQABAKcAAaMAAZ8AAZsAApwAAJoAA5oA"
    "ApoAAZoAAJkAApkAAZkAAJgAApcAApgAAJYAAZIAAYsAAYcAAYQAAIIAAYAAAX0AAHcAAWkABGQA"
    "BVoAAEkAACgAAAkAAQMAAQIAAQIAAAEAAQEAAAAAAQAAAAAAAAAAACH5BAEAAAAALAAAAAAwADAA"
    "QAj/APsJHEiwoMGDCBMW1PfEiI4YiPzIucKGgoRC6FCRixWO3LhytkKSCynrFatT2kRVwXPjicJ+"
    "+6CwCLWGksB7NXLkcDQsVq6QQEmyqdTvHqZ8Hk5M8lLrj6VqN8KIArQEZlEjfLDYMZUr1xc8HSoY"
    "AHAAgFmzAQIAIBBAgIEFABwcyFAPTNBc3PAsglYLVZcZnAQS4eEj0Chea+7o+sbNVtfHkH/a+uat"
    "Fi5estr8Cqcr2SEg114KrMZJipPQ/fhBkRIlyb6D1I4wCUKYh5AhSJpA2SS6t+/fBq/5KIMKF64s"
    "aZCxO9fHhZtvsX4JCxoyV5dCluxZmtRnTLlU0lLw/0a4bx8QN6NuvXk0aYQGDR1KwB8xwsSGDTLi"
    "kzAhY8QMGC80cgggcrAByy1qoEIHJHwUY4ckRfRAhyrKKJIHKuXUAlQuvJzRBRhyrLOOM4XIE080"
    "6xQjChZm8AIULckQEskNQEDxyWsH7cPEC6AEIxku3wjjTDN96CBFP5xEMYUU13SSSDvJxBJULcS8"
    "A0kRwGWp5ZZccrlPPvng06RpRChxiQ477GBDJTfU4GYNN9xggw49+PCDEqt1ks9L+XxCAxXDCIMO"
    "MGIwg0EDCTggQhlo2ELLLWZoGBQvuLwiSy67hHTGIkrgmGM/QahhyhaCnOBABvxwUskdrvTyyy3U"
    "hf+kgj0YJJABNZhYE8kosURzCTZR8LBDCkkUdM8ngYSCDgwgfADCsyC0UMYWpXzxBRdbjCHGGGOE"
    "wYIijDTCiCSS1KFKHIfQ0AMjV0iDBx12xNBEP/kswQIVbbwRyiKfpGDBBAQoIMADAk0gQAEFmDWA"
    "AAkAUAEEJ9xTSRrbmKNLLbmwIowib6RiChs4EJFHKMb4UUY54mB8xhXs0FOCBxlIcEEEEkRAQQMS"
    "5HzBBh3Es4ormIrTjSyywHIMIY7owEQTmvSDBBGN4MGIH6TkUss34MQqCyuxzPINLrfAYmktF4ck"
    "paPMEGKPaPkwMVMbc3CTCy3LPCOIINH00cwe7iz/s0w7yiwjCCLSOANSdbMgw6lo+3xyQzPHFENM"
    "McXMsUwf0Cjya0HXDFGIHse0soopY+BiTDPtxIBll6y37vrrsMcu++yx59MJJ1NAIQQOMUTCyApq"
    "pFFGGGFoEca1XxAPBhlmpAFHHXmw8MIORWSi0D6aFGZFFVaIssoV8VAAwAQcoGOGLeOI08sbsTrW"
    "FS/ABIPLI094atA+1uzARS8a8iJGMO+5QAXmkQUX9YIMZwPKLrKgBTfEgQulyJQqCoGEaiTkNUhw"
    "gyl6sYV52EMIlpjBHbLxDXGY4w24oM4utoAIIFggA/3oBCb4kIpWROMHoflEJ5pmrE3UQRtaqMcG"
    "/yoAhIEUohTmGMc4JFUdVszBEkXshwX7MYlWcOMPl+iHD1bAhRcUwX77WEILtNGFSAhBBM8KwQdI"
    "8I5W8CIyjuGFF2ZgDWt8oh8eQMEhsuALaAhhCjhIQxwcIYRLVO8mnQhEj1zQLBC4oAXQYEc73OGO"
    "dkjSHccwhjHUEQxSiAIUoKxCFUaBCjvkYRaBUIMdDDEKboACEALZBydkQIVb0MINNegHBhCgAAQ4"
    "AAAPOMEJLgCABETAAAygAAMggAALKMAC/ZDCIuRQizZoCBdtiIQedoEHPthgH1GgAYtg8QtwqMAS"
    "GHgABBbwAGQ2YAIMMMAB5nkABCRgAgrIwARScP8NRZACGO77hhkGQYhjHCMPkDgCFGRQhWLQoQu7"
    "AIc5TJGOSAyRAQggAAAUAIACCGAAAAApABrAgAVMQARrOEMtwPEYXKwBGcwYhCIUwYNO0MAK4igG"
    "IuAAjlmczxa84IIVzvGOedBDBCLggFJHwAGkQvIcV1hDLl5BDGckAxl6MMQkfOCETeSjPP0wgiT2"
    "4IxE+KEUGXJMUHBhDmLgAQ97IGgh/FCHNrChF7Soji1koYs9GAIJmrDfQGSJAz84YhCH4YYw3nAp"
    "6kjGFuAYiS0sUzZZwMEN3egFMwqBw5dcwwks0MYa8gAHVbQ1F6cgBSlMgQpVsIIVlrqUL4SRjHeR"
    "BEMWtLjULZCRiGK9JIwuyEYwwDGOXIxjFll9xAwsAUIe6AAHNqDENCSBCEGoozHV0YUyHOEJwRpk"
    "T5AABTBkEZKrEQMa8HhGJbCxp4FUYwiHeIYwWCqZVizDGZCoimgyAYQdTEISkQhwJGZAiR6kAAiC"
    "rQYQcNAIwkEDGtEohCIaMYMUIIF2GM6whjfMYYMEBAA7"
)

# Character base bits (Meat Boy always available)
CHARACTER_BASE_BITS = (1 << 0)

# Goal string constants (from APWorld options)
GOAL_LARRIES = "larries"
GOAL_LIGHT_WORLD = "light_world"
GOAL_DARK_WORLD = "dark_world"
GOAL_LW_CHAPTER7 = "light_world_chapter7"
GOAL_DW_CHAPTER7 = "dark_world_chapter7"
GOAL_BANDAGES = "bandages"

# Goal int->string mapping (slot_data may send int or string)
GOAL_INT_TO_STR = {
    0: GOAL_LARRIES, 1: GOAL_LIGHT_WORLD, 2: GOAL_DARK_WORLD,
    3: GOAL_LW_CHAPTER7, 4: GOAL_DW_CHAPTER7, 5: GOAL_BANDAGES,
}

# Warp zone slot mapping: (world, zone_index) -> [(host_level_1based, is_dark)]
# Zone 0,2 = retro warps (light), Zone 1 = character warp (light), Zone 3 = dark warp
# Each zone has 3 sub-levels (slots zone*3, zone*3+1, zone*3+2)
LW_WARP_ZONE_SLOTS = {}  # (world, host_level) -> [slot_indices]
DW_WARP_ZONE_SLOTS = {}

# Build warp slot index lookups from the warp name tables
# Light warp zones: each has 3 sub-levels
# The slot ordering within each world is determined by the zone index
WARP_ZONE_MAP = {
    # world -> [(zone_idx, host_level_1based, is_dark, warp_name)]
    1: [(0, 5, False, "Sky Pup"), (1, 12, False, "The Commander!"),
        (2, 19, False, "Hand Held Hack"), (3, 13, True, "Space Boy")],
    2: [(0, 15, False, "The Blood Shed"), (1, 8, False, "The Bootlicker!"),
        (2, 12, False, "Castle Crushers"), (3, 5, True, "1977")],
    3: [(0, 7, False, "Tunnel Vision"), (1, 16, False, "The Jump Man"),
        (2, 5, False, "Cartridge Dump"), (3, 8, True, "Kontra")],
    4: [(0, 8, False, "Brimstone"), (1, 18, False, "The Fly Guy!"),
        (2, 14, False, "The Key Master"), (3, 7, True, "MMMMMM")],
    5: [(0, 1, False, "Skyscraper"), (1, 7, False, "The Guy!"),
        (2, 12, False, "Sunshine Island"), (3, 20, True, "Meat is Death")],
}

# Build lookup: (world, zone_idx) -> (host_level_1based, is_dark, warp_name)
WARP_ZONE_INFO = {}
for w, zones in WARP_ZONE_MAP.items():
    for zone_idx, host_lv, is_dark, wname in zones:
        WARP_ZONE_INFO[(w, zone_idx)] = (host_lv, is_dark, wname)

# Bandage slot addresses for warp zones
# Each warp zone has 2 bandages (except character warps which have 0)
# Bandages are on sub-levels 1 and 2 (slots zone*3+0 and zone*3+1)
# Character warps (zone 1) and dark warps (zone 3) may or may not have bandages
# From the APWorld data, only retro warps and dark warps have bandages


def get_level_display_name(world, level, lvl_type):
    """Human-readable level name for logging."""
    ln = level + 1
    region = type_to_region(lvl_type)
    if is_warp(lvl_type):
        return f"W{world} Warp L{level}"
    if lvl_type == TYPE_DARK:
        name = DARK_LEVEL_NAMES.get((world, ln), "")
        return f"{world}-{ln}X {name}" if name else f"{world}-{ln}X"
    if level == BOSS_LEVEL_INDEX:
        return f"Boss - {WORLD_NAMES.get(world, f'W{world}')}"
    name = LIGHT_LEVEL_NAMES.get((world, ln), "")
    return f"{world}-{ln} {name}" if name else f"{world}-{ln}"



# GAME INTERFACE 


class GameInterface:
    """Handles all pymem interaction with SuperMeatBoy.exe"""

    def __init__(self):
        self.pm = None
        self.base = 0
        self.connected = False

    def connect(self) -> bool:
        try:
            self.pm = pymem.Pymem("SuperMeatBoy.exe")
            self.base = self.pm.base_address
            self.connected = True
            return True
        except Exception:
            self.connected = False
            return False

    def disconnect(self):
        self.pm = None
        self.base = 0
        self.connected = False

    def send_esc(self):
        user32.keybd_event(VK_ESCAPE, 0x01, 0, 0)
        time.sleep(0.02)
        user32.keybd_event(VK_ESCAPE, 0x01, KEYEVENTF_KEYUP, 0)

    def rb(self, a):
        try: return self.pm.read_uchar(self.base + a)
        except: return -1

    def rp(self, b, o):
        try:
            p = self.pm.read_uint(self.base + b)
            return self.pm.read_uchar(p + o) if p else -1
        except: return -1

    def rpi(self, b, o):
        try:
            p = self.pm.read_uint(self.base + b)
            return self.pm.read_int(p + o) if p else -1
        except: return -1

    def get_sp(self):
        try: return self.pm.read_uint(self.base + ADDR["save_ptr"])
        except: return 0

    def read_comp(self, sp, world, index, region):
        ca = comp_addr(world, index, region)
        if ca is None or sp == 0: return -1
        try: return self.pm.read_uchar(sp + ca)
        except: return -1

    def write_comp(self, sp, world, index, region, value):
        ca = comp_addr(world, index, region)
        if ca is None or sp == 0: return
        try: self.pm.write_uchar(sp + ca, value)
        except: pass

    def read_time(self, sp, world, level_index, region):
        ta = time_addr(world, level_index, region)
        if ta is None or sp == 0: return -1.0
        try: return self.pm.read_float(sp + ta)
        except: return -1.0

    def write_time(self, sp, world, level_index, region, value):
        ta = time_addr(world, level_index, region)
        if ta is None or sp == 0: return
        try: self.pm.write_float(sp + ta, value)
        except: pass

    def read_warp_slots(self, sp, world):
        warp_base = WARP_BASES.get(world)
        if warp_base is None or sp == 0: return [-1] * NUM_WARP_SLOTS
        vals = []
        for i in range(NUM_WARP_SLOTS):
            ca = warp_base + i * SLOT_SIZE + COMP_BYTE
            try: vals.append(self.pm.read_uchar(sp + ca))
            except: vals.append(-1)
        return vals

    def read_warp_slots_full(self, sp, world):
        warp_base = WARP_BASES.get(world)
        if warp_base is None or sp == 0: return [(-1, -1.0)] * NUM_WARP_SLOTS
        result = []
        for i in range(NUM_WARP_SLOTS):
            base_off = warp_base + i * SLOT_SIZE
            try:
                comp = self.pm.read_uchar(sp + base_off + COMP_BYTE)
                tval = self.pm.read_float(sp + base_off + TIME_BYTE)
                result.append((comp, tval))
            except:
                result.append((-1, -1.0))
        return result

    def set_world_unlock(self, sp, bitmask):
        try: self.pm.write_uchar(sp + ADDR["world_unlock"], bitmask)
        except: pass

    def get_world_unlock(self, sp):
        try: return self.pm.read_uchar(sp + ADDR["world_unlock"])
        except: return 0

    def get_char_bitmask(self, sp):
        try: return self.pm.read_uint(sp + CHARACTER_BITMASK_OFFSET)
        except: return 0

    def set_char_bitmask(self, sp, bitmask):
        try: self.pm.write_uint(sp + CHARACTER_BITMASK_OFFSET, bitmask)
        except: pass

    def read_boss_counter(self, sp, world):
        offset = BOSS_COUNTER_OFFSETS.get(world)
        if offset is None or sp == 0: return -1
        try: return self.pm.read_uchar(sp + offset)
        except: return -1

    def write_boss_counter(self, sp, world, value):
        offset = BOSS_COUNTER_OFFSETS.get(world)
        if offset is None or sp == 0: return
        try: self.pm.write_uchar(sp + offset, min(value, 255))
        except: pass

    def read_boss_comp(self, sp, world):
        """Read boss completion byte (at BOSS_COUNTER_OFFSETS[w] + COMP_BYTE)."""
        offset = BOSS_COUNTER_OFFSETS.get(world)
        if offset is None or sp == 0: return -1
        try: return self.pm.read_uchar(sp + offset + COMP_BYTE)
        except: return -1

    def get_state(self):
        try:
            return {
                "playing": self.rb(ADDR["playing"]),
                "world": self.rb(ADDR["world"]),
                "level": self.rp(*ADDR["level"]),
                "beaten": self.rb(ADDR["level_beaten"]),
                "lvl_type": self.rpi(*ADDR["lvl_type"]),
                "ui_state": self.rpi(*ADDR["ui_state"]),
                "trans": self.rb(ADDR["level_trans"]),
            }
        except:
            return None

    def read_death_count(self, sp):
        """Read total death counter from save data."""
        if sp == 0:
            return -1
        try:
            return self.pm.read_int(sp + DEATH_COUNT_OFFSET)
        except:
            return -1



# AP CLIENT - Rewritten for zuils APWorld


class APClient:
    """Archipelago client logic for zuils' Super Meat Boy APWorld."""

    def __init__(self, log_callback, status_callback):
        self.log = log_callback
        self.set_status = status_callback

        # Connection
        self.server: str = ""
        self.slot: str = ""
        self.password: str = ""
        self.ws = None
        self.connected: bool = False
        self.slot_data: Dict = {}
        self.team: int = 0
        self.players: Dict[int, str] = {}

        # AP state
        self.locations_checked: Set[int] = set()
        self.items_received: List[Dict] = []
        self.items_processed: int = 0

        # DataPackage: name <-> id mappings
        self.loc_name_to_id: Dict[str, int] = {}
        self.item_id_to_name: Dict[int, str] = {}
        self.loc_id_to_name: Dict[int, str] = {}

        # Game state tracking
        self.allowed_worlds: Set[int] = set()
        self.character_bits: int = CHARACTER_BASE_BITS
        self.bandage_count: int = 0
        self.boss_key_counts: Dict[int, int] = {w: 0 for w in range(1, 7)}
        self.boss_unlocked: Set[int] = set()
        self.boss_token_count: int = 0
        self.dw_fetus_key_count: int = 0
        self.ch7_lw_key_count: int = 0
        self.ch7_dw_key_count: int = 0
        self.victory_received: bool = False
        self.goal_completed: bool = False

        # A+ Rank items received: set of (world, level_1based)
        self.aplus_items_received: Set[Tuple[int, int]] = set()
        # All received item IDs (for has_meat_boy / has_bandage_girl checks)
        self._received_item_ids: Set[int] = set()
        # Real best times preserved before suppression
        self.real_best_times: Dict[Tuple[int, int], float] = {}
        # Levels with fake sub-par times from A+ item grants
        self.fake_aplus_times: Set[Tuple[int, int]] = set()
        self._pending_aplus_recheck: Set[Tuple[int, int, str]] = set()  # (world, level_0based, region)

        self._running = False
        self.loop = None

    
    # NAME/ID RESOLUTION (DataPackage-based)
    

    def loc_id(self, name: str) -> Optional[int]:
        """Resolve location name to ID via DataPackage."""
        return self.loc_name_to_id.get(name)

    def get_item_name(self, item_id: int) -> str:
        return self.item_id_to_name.get(item_id, f"Unknown({item_id})")

    def get_location_name(self, loc_id: int) -> str:
        return self.loc_id_to_name.get(loc_id, f"Unknown({loc_id})")

    def get_player_name(self, player_id: int) -> str:
        return self.players.get(player_id, f"Player {player_id}")

    
    # SLOT DATA PARSING
    

    def _parse_goal(self, raw) -> str:
        """Parse goal from slot_data (may be int or string)."""
        if isinstance(raw, int):
            return GOAL_INT_TO_STR.get(raw, GOAL_LARRIES)
        if isinstance(raw, str):
            return raw
        return GOAL_LARRIES

    
    # WORLD ACCESS
    

    def _compute_world_bitmask(self):
        """Compute world unlock bitmask respecting character requirements.

        APWorld rules:
        - W6 requires Chapter 6 Key AND Meat Boy
        - W7 requires Chapter 7 Key AND Bandage Girl
        - W7 with ch7 goal requires ALL 7 chapter keys AND Bandage Girl
        """
        bitmask = 0
        goal = self._parse_goal(self.slot_data.get("goal", 0))
        for w in self.allowed_worlds:
            if w == 6:
                if not self._has_meat_boy():
                    continue
            elif w == 7:
                if not self._has_bandage_girl():
                    continue
                if goal in (GOAL_LW_CHAPTER7, GOAL_DW_CHAPTER7):
                    if not all(cw in self.allowed_worlds for cw in range(1, 8)):
                        continue
            bitmask |= (1 << (w - 1))
        return bitmask

    
    # BOSS GATING (matches APWorld rules.py exactly)
    
    # APWorld access functions:
    #   boss_req(chpt): Chapter {chpt} Boss Key × boss_req AND Meat Boy
    #   larries(): boss_req(5) AND (¬tokens OR goal≠"larries" OR Token×4)
    #   lw_drfetus(): Ch5 Boss Key × lw_dr_fetus_req AND (¬tokens OR goal≠"light_world" OR Token×5)
    #   dw_drfetus(): DW Dr. Fetus Key × dw_dr_fetus_req AND (¬tokens OR goal≠"dark_world" OR Token×6)
    #
    # The game has ONE boss counter per world. W6 counter gates both LW and DW boss.


    PROG_CHARACTER_ITEMS = None  

    def _has_meat_boy(self):
        return ITEM_MEAT_BOY in self._received_item_ids

    def _has_bandage_girl(self):
        return ITEM_BANDAGE_GIRL in self._received_item_ids

    def _has_prog_character(self):
        """Check if any ProgCharacters item has been received."""
        if self.PROG_CHARACTER_ITEMS is None:
            from smb_apworld_data import (ITEM_COMMANDER_VIDEO, ITEM_JILL, ITEM_OGMO,
                                           ITEM_FLYWRENCH, ITEM_THE_KID, ITEM_JOSEF,
                                           ITEM_NAIJA, ITEM_STEVE)
            APClient.PROG_CHARACTER_ITEMS = {
                ITEM_COMMANDER_VIDEO, ITEM_JILL, ITEM_OGMO, ITEM_FLYWRENCH,
                ITEM_THE_KID, ITEM_JOSEF, ITEM_NAIJA, ITEM_STEVE,
            }
        return bool(self._received_item_ids & self.PROG_CHARACTER_ITEMS)

    def _boss_req_met(self, world, boss_req_val):
        """Check boss_req(chpt): Chapter {chpt} Boss Key × boss_req AND Meat Boy."""
        if not self._has_meat_boy():
            return False
        return self.boss_key_counts.get(world, 0) >= boss_req_val

    def _larries_accessible(self, boss_req_val):
        """Check larries(): boss_req(5) AND token gating for larries goal."""
        if not self._boss_req_met(5, boss_req_val):
            return False
        goal = self._parse_goal(self.slot_data.get("goal", 0))
        tokens_enabled = bool(self.slot_data.get("boss_tokens", 0))
        if tokens_enabled and goal == GOAL_LARRIES:
            return self.boss_token_count >= 4
        return True

    def _lw_drfetus_accessible(self):
        """Check lw_drfetus(): Ch5 Boss Key × lw_dr_fetus_req + token gating."""
        lw_req = self.slot_data.get("lw_dr_fetus_req", 5)
        if self.boss_key_counts.get(5, 0) < lw_req:
            return False
        goal = self._parse_goal(self.slot_data.get("goal", 0))
        tokens_enabled = bool(self.slot_data.get("boss_tokens", 0))
        if tokens_enabled and goal == GOAL_LIGHT_WORLD:
            return self.boss_token_count >= 5
        return True

    def _dw_drfetus_accessible(self):
        """Check dw_drfetus(): DW Dr. Fetus Key × dw_dr_fetus_req + token gating."""
        dw_req = self.slot_data.get("dw_dr_fetus_req", 85)
        if self.dw_fetus_key_count < dw_req:
            return False
        goal = self._parse_goal(self.slot_data.get("goal", 0))
        tokens_enabled = bool(self.slot_data.get("boss_tokens", 0))
        if tokens_enabled and goal == GOAL_DARK_WORLD:
            return self.boss_token_count >= 6
        return True

    def _w6_boss_should_unlock(self):
        """W6 boss counter should be unlocked if EITHER LW or DW Dr. Fetus is accessible."""
        return self._lw_drfetus_accessible() or self._dw_drfetus_accessible()

    def _can_send_boss_check(self, world, is_dark, boss_req_val):
        """Check if we should send a boss defeat check based on APWorld access rules.

        This gates CHECK SENDING, not physical access (which is counter-based).
        """
        if world <= 4:
            return self._boss_req_met(world, boss_req_val)
        elif world == 5:
            if is_dark:
                return False  # W5 has no dark boss
            return self._larries_accessible(boss_req_val)
        elif world == 6:
            if is_dark:
                return self._dw_drfetus_accessible()
            return self._lw_drfetus_accessible()
        return True

    def _can_send_cutscene_check(self, world, boss_req_val):
        """Check if cutscene check can be sent. Cutscenes use boss_req or lw_drfetus."""
        if world <= 5:
            return self._boss_req_met(world, boss_req_val)
        elif world == 6:
            return self._lw_drfetus_accessible()
        return True

    def _update_boss_unlocks(self, game, sp, boss_req_val):
        """Check all bosses and unlock any newly accessible ones."""
        newly = []
        for w in range(1, 7):
            if w in self.boss_unlocked:
                continue
            should_unlock = False
            if w <= 4:
                should_unlock = self._boss_req_met(w, boss_req_val)
            elif w == 5:
                should_unlock = self._larries_accessible(boss_req_val)
            elif w == 6:
                should_unlock = self._w6_boss_should_unlock()
            if should_unlock:
                self.boss_unlocked.add(w)
                threshold = BOSS_UNLOCK_THRESHOLDS.get(w, 17)
                game.write_boss_counter(sp, w, threshold)
                newly.append(w)
        return newly

    def _enforce_boss_counters(self, game, sp, boss_req_val):
        """Keep boss counters in sync with AP boss key state.

        Unlocked bosses: counter stays at/above threshold.
        Locked bosses: counter shows boss key progress (below threshold).
        """
        for w in range(1, 7):
            should_be_unlocked = False
            if w <= 4:
                should_be_unlocked = self._boss_req_met(w, boss_req_val)
            elif w == 5:
                should_be_unlocked = self._larries_accessible(boss_req_val)
            elif w == 6:
                should_be_unlocked = self._w6_boss_should_unlock()

            threshold = BOSS_UNLOCK_THRESHOLDS.get(w)
            if should_be_unlocked:
                self.boss_unlocked.add(w)
                if threshold:
                    current = game.read_boss_counter(sp, w)
                    if 0 <= current < threshold:
                        game.write_boss_counter(sp, w, threshold)
            else:
                self.boss_unlocked.discard(w)
                # Show boss key progress instead of 0
                if w <= 5:
                    progress = min(self.boss_key_counts.get(w, 0),
                                   threshold - 1 if threshold else 0)
                elif w == 6:
                    # W6 threshold is 5; show progress toward LW or DW req
                    lw_req = max(self.slot_data.get("lw_dr_fetus_req", 5), 1)
                    dw_req = max(self.slot_data.get("dw_dr_fetus_req", 85), 1)
                    lw_keys = self.boss_key_counts.get(5, 0)
                    lw_progress = min(4, int(lw_keys * 5 / lw_req))
                    dw_progress = min(4, int(self.dw_fetus_key_count * 5 / dw_req))
                    progress = max(lw_progress, dw_progress)
                else:
                    progress = 0
                current = game.read_boss_counter(sp, w)
                if current != progress:
                    game.write_boss_counter(sp, w, progress)

    
    # A+ RANK / DARK WORLD GATING
    

    def _dark_level_unlocked(self, world, level_1based):
        """Check if a dark level is unlocked via received A+ Rank item."""
        if not self.slot_data.get("dark_world", 0):
            return False
        return (world, level_1based) in self.aplus_items_received

    def _enforce_dark_locks(self, game, sp):
        """Suppress A+ times on light levels whose dark counterpart is locked.
        Write par+1s to keep dark locked until AP sends the A+ Rank item.
        """
        if not self.slot_data.get("dark_world", 0):
            return
        for w in range(1, 8):
            num = NUM_LEVELS.get(w, 20)
            for li in range(num):
                lv1 = li + 1
                if self._dark_level_unlocked(w, lv1):
                    # Restore real time if we suppressed it
                    real = self.real_best_times.get((w, li))
                    par = get_par_time(w, li, "light")
                    if real is not None and par is not None and real <= par:
                        current = game.read_time(sp, w, li, "light")
                        if current > par:
                            game.write_time(sp, w, li, "light", real)
                    # Clear fake flag if player replayed with real time
                    if (w, li) in self.fake_aplus_times and par is not None:
                        current = game.read_time(sp, w, li, "light")
                        fake_val = par - 0.001
                        if abs(current - fake_val) > 0.0005:
                            self.fake_aplus_times.discard((w, li))
                    continue
                # Not unlocked - suppress if A+ time exists
                par = get_par_time(w, li, "light")
                if par is None:
                    continue
                t = game.read_time(sp, w, li, "light")
                if t > 0 and t <= par:
                    self.real_best_times[(w, li)] = t
                    game.write_time(sp, w, li, "light", par + 1.0)

    def _grant_aplus_item(self, game, sp, world, level_1based):
        """Apply an A+ Rank item - make the dark level appear."""
        li = level_1based - 1
        par = get_par_time(world, li, "light")
        if par is None:
            return
        real = self.real_best_times.get((world, li))
        if real is not None and real > 0 and real <= par:
            game.write_time(sp, world, li, "light", real)
            self.fake_aplus_times.discard((world, li))
        else:
            # Write fake sub-par time to unlock dark level visually
            comp = game.read_comp(sp, world, li, "light")
            if comp >= 0 and (comp & FLAG_COMPLETE):
                current_t = game.read_time(sp, world, li, "light")
                if current_t > par:
                    game.write_time(sp, world, li, "light", par - 0.001)
                    self.fake_aplus_times.add((world, li))

    
    # LOCATION CHECKING HELPERS
    

    async def _check_location_by_name(self, name: str, checks_list: list):
        """Add location to checks list if it exists and hasn't been checked."""
        loc = self.loc_id(name)
        if loc is not None and loc not in self.locations_checked:
            checks_list.append(loc)
            return True
        return False

    async def send_location_checks(self, locations: List[int]):
        if not self.connected or not locations:
            return
        new_locs = [loc for loc in locations if loc not in self.locations_checked]
        if not new_locs:
            return
        self.locations_checked.update(new_locs)
        await self.send_message({"cmd": "LocationChecks", "locations": new_locs})
        for loc in new_locs:
            self.log(f"Checked: {self.get_location_name(loc)}", "location")

    async def send_goal_complete(self):
        if not self.goal_completed:
            self.goal_completed = True
            await self.send_message({"cmd": "StatusUpdate", "status": 30})
            self.log("GOAL COMPLETE!", "success")

    
    # A+ DETECTION
    

    def _check_aplus_location(self, game, sp, world, level_0based, region, checks):
        """Check if level qualifies for A+ and add location check."""
        comp = game.read_comp(sp, world, level_0based, region)
        if comp < 0 or not (comp & FLAG_COMPLETE):
            return
        time_val = game.read_time(sp, world, level_0based, region)
        par = get_par_time(world, level_0based, region)
        if par is None:
            return
        if time_val <= 0:
            # Time not yet flushed to save — add to pending recheck
            self._pending_aplus_recheck.add((world, level_0based, region))
            return
        # Use real time if dark lock suppressed it
        if region == "light" and time_val > par:
            real = self.real_best_times.get((world, level_0based))
            if real is not None and real > 0 and real <= par:
                time_val = real
        # Skip fake sub-par times from A+ item grants — but if the player
        # replayed and got a REAL A+, the game overwrites the fake value.
        # Detect this by comparing against the known fake value (par - 0.001).
        if (world, level_0based) in self.fake_aplus_times and region == "light":
            fake_val = par - 0.001
            if abs(time_val - fake_val) < 0.0005:
                # Time is still the fake value we wrote — skip
                self._pending_aplus_recheck.discard((world, level_0based, region))
                return
            else:
                # Player replayed and got a real time — clear the fake flag
                self.fake_aplus_times.discard((world, level_0based))
        if time_val > par:
            # Time is written but player didn't get A+ — remove from pending
            self._pending_aplus_recheck.discard((world, level_0based, region))
            return
        lv1 = level_0based + 1
        if region == "light":
            name = light_aplus_name(world, lv1)
        else:
            name = dark_aplus_name(world, lv1)
        if name:
            loc = self.loc_id(name)
            if loc and loc not in self.locations_checked:
                checks.append(loc)
                self.log(f"A+ {name} ({time_val:.3f}s <= {par:.3f}s)", "location")
                # Clear from pending if it was there
                self._pending_aplus_recheck.discard((world, level_0based, region))

    
    # BANDAGE DETECTION
    

    def _check_bandage(self, game, sp, world, level_0based, region, entry_val, current_val, checks):
        """Check if bandage bit was newly set, revoke it, send check."""
        if entry_val < 0 or current_val < 0:
            return
        if not (entry_val & FLAG_BANDAGE) and (current_val & FLAG_BANDAGE):
            lv1 = level_0based + 1
            if region == "light":
                bname = light_bandage_name(world, lv1)
            elif region == "dark":
                bname = dark_bandage_name(world, lv1)
            else:
                bname = None  # Warp bandages handled separately
            if bname:
                loc = self.loc_id(bname)
                if loc and loc not in self.locations_checked:
                    checks.append(loc)
                    self.log(f"Bandage: {bname}", "location")
            # Always revoke bandage bit
            game.write_comp(sp, world, level_0based, region,
                            current_val & MASK_CLEAR_BANDAGE)

    def _check_warp_bandages(self, game, sp, world, entry_slots, current_slots, checks):
        """Check warp zone bandages by diffing slot snapshots."""
        # Track loc IDs queued in THIS pass so we don't double-send
        queued_this_pass = set()
        for si in range(NUM_WARP_SLOTS):
            ev = entry_slots[si]
            cv = current_slots[si]
            if ev < 0 or cv < 0 or ev == cv:
                continue
            if not (ev & FLAG_BANDAGE) and (cv & FLAG_BANDAGE):
                zone_idx = si // 3
                info = WARP_ZONE_INFO.get((world, zone_idx))
                if info:
                    host_lv, is_dark, wname = info
                    name_fn = dw_warp_bandage_name if is_dark else lw_warp_bandage_name
                    sent = False
                    for try_num in (1, 2):
                        bname = name_fn(world, host_lv, try_num)
                        if bname:
                            loc = self.loc_id(bname)
                            if loc and loc not in self.locations_checked and loc not in queued_this_pass:
                                checks.append(loc)
                                queued_this_pass.add(loc)
                                self.log(f"Bandage: {bname}", "location")
                                sent = True
                                break
                # Revoke
                game.write_comp(sp, world, si, "warp", cv & MASK_CLEAR_BANDAGE)

    
    # WARP ZONE COMPLETION
    

    def _check_warp_completions(self, game, sp, world, checks, warps_completed):
        """Check if any warp zone (3 sub-levels all complete) is newly done."""
        if world > 5:
            return
        for zone_idx in range(4):
            if (world, zone_idx) in warps_completed:
                continue
            all_done = True
            for sub in range(3):
                si = zone_idx * 3 + sub
                comp = game.read_comp(sp, world, si, "warp")
                if comp < 0 or not (comp & FLAG_COMPLETE):
                    all_done = False
                    break
            if all_done:
                warps_completed.add((world, zone_idx))
                info = WARP_ZONE_INFO.get((world, zone_idx))
                if info:
                    host_lv, is_dark, wname = info
                    if is_dark:
                        loc_name = dw_warp_completion_name(world, host_lv)
                    else:
                        loc_name = lw_warp_completion_name(world, host_lv)
                    if loc_name:
                        loc = self.loc_id(loc_name)
                        if loc and loc not in self.locations_checked:
                            checks.append(loc)
                            self.log(f"Warp Complete: {loc_name}", "location")

    
    # ACHIEVEMENT DETECTION
    

    def _check_achievements(self, game, sp, checks,
                            achievements_enabled, dark_enabled,
                            worlds_cleared, worlds_dark_cleared,
                            milestones_sent, warp_milestones_sent,
                            warps_completed,
                            speedrun_sent, speedrun_enabled,
                            deathless_sent, deathless_enabled):
        """Check for all achievement-type locations."""
        if not achievements_enabled:
            return

        # World clear achievements (W6/W7 only — W1-W5 don't have clear achievements)
        for (w, region), ach_name in WORLD_CLEAR_NAMES.items():
            tracking = worlds_cleared if region == "light" else worlds_dark_cleared
            if w in tracking:
                continue
            if region == "dark" and not dark_enabled:
                continue
            num = NUM_LEVELS.get(w, 20)
            all_done = True
            for li in range(num):
                comp = game.read_comp(sp, w, li, region)
                if comp < 0 or not (comp & FLAG_COMPLETE):
                    all_done = False
                    break
            if all_done:
                tracking.add(w)
                loc = self.loc_id(ach_name)
                if loc and loc not in self.locations_checked:
                    checks.append(loc)
                    self.log(f"Achievement: {ach_name}", "success")

        # Warp zone milestones
        # Count total completed warp zones from save data
        total_warps_done = 0
        for w in range(1, 6):
            for zone_idx in range(4):
                zone_done = True
                for sub in range(3):
                    si = zone_idx * 3 + sub
                    comp = game.read_comp(sp, w, si, "warp")
                    if comp < 0 or not (comp & FLAG_COMPLETE):
                        zone_done = False
                        break
                if zone_done:
                    total_warps_done += 1

        for threshold, ach_name in WARP_MILESTONE_NAMES.items():
            if threshold in warp_milestones_sent:
                continue
            # Old School (10) and Retro Rampage (20) require dark world
            if threshold >= 10 and not dark_enabled:
                continue
            if total_warps_done >= threshold:
                warp_milestones_sent.add(threshold)
                loc = self.loc_id(ach_name)
                if loc and loc not in self.locations_checked:
                    checks.append(loc)
                    self.log(f"Achievement: {ach_name}", "success")

        # Bandage milestones
        for threshold, ach_name in BANDAGE_MILESTONE_NAMES.items():
            if threshold in milestones_sent:
                continue
            # 70/90/100 require dark world
            if threshold >= 70 and not dark_enabled:
                continue
            if self.bandage_count >= threshold:
                milestones_sent.add(threshold)
                loc = self.loc_id(ach_name)
                if loc and loc not in self.locations_checked:
                    checks.append(loc)
                    self.log(f"Achievement: {ach_name}", "success")

        # Speedrun achievements (sum of light+dark IL times per world)
        if speedrun_enabled and dark_enabled:
            for w, (threshold, ach_name) in SPEEDRUN_ACHIEVEMENTS.items():
                if w in speedrun_sent:
                    continue
                # Check: all 20 light + 20 dark levels complete with A+
                all_aplus = True
                total_time = 0.0
                for region in ("light", "dark"):
                    for li in range(20):
                        comp = game.read_comp(sp, w, li, region)
                        if comp < 0 or not (comp & FLAG_COMPLETE):
                            all_aplus = False
                            break
                        t = game.read_time(sp, w, li, region)
                        if t <= 0:
                            all_aplus = False
                            break
                        par = get_par_time(w, li, region)
                        if par is None or t > par:
                            all_aplus = False
                            break
                        total_time += t
                    if not all_aplus:
                        break
                if all_aplus and total_time <= threshold:
                    speedrun_sent.add(w)
                    loc = self.loc_id(ach_name)
                    if loc and loc not in self.locations_checked:
                        checks.append(loc)
                        self.log(f"Speedrun: {ach_name} ({total_time:.1f}s)", "success")

        # Deathless achievements checked separately via _check_deathless

    def _check_deathless(self, game, sp, checks,
                          deathless_enabled, dark_enabled, deathless_sent,
                          deathless_tracker):
        """Check deathless achievements based on tracked deathless runs.

        deathless_tracker: dict of (world, region) -> {
            'levels_done': set of level_0based completed without dying,
            'death_count_at_start': int,
            'active': bool
        }
        """
        if not deathless_enabled:
            return

        for (w, region), ach_name in DEATHLESS_ACHIEVEMENTS.items():
            if (w, region) in deathless_sent:
                continue
            if region == "dark" and not dark_enabled:
                continue
            tracker = deathless_tracker.get((w, region))
            if not tracker or not tracker.get('active'):
                continue
            num = NUM_LEVELS.get(w, 20)
            if len(tracker['levels_done']) >= num:
                # All levels completed without dying!
                deathless_sent.add((w, region))
                loc = self.loc_id(ach_name)
                if loc and loc not in self.locations_checked:
                    checks.append(loc)
                    self.log(f"DEATHLESS: {ach_name}!", "success")

    def _check_goal(self, goal, boss_tokens_enabled):
        """Check if goal conditions are met. Returns True if goal complete.

        APWorld completion conditions:
        - larries/light_world/dark_world: state.has("Victory")
        - bandages: Bandage count >= bandages_amount (+ Boss Tokens if enabled)
        - ch7 goals: Key count >= 20 (+ Boss Tokens if enabled)
        """
        if self.goal_completed:
            return False

        if goal in (GOAL_LARRIES, GOAL_LIGHT_WORLD, GOAL_DARK_WORLD):
            return self.victory_received

        elif goal == GOAL_LW_CHAPTER7:
            if self.ch7_lw_key_count < 20:
                return False
            return self._boss_tokens_sufficient(goal, boss_tokens_enabled)

        elif goal == GOAL_DW_CHAPTER7:
            if self.ch7_dw_key_count < 20:
                return False
            return self._boss_tokens_sufficient(goal, boss_tokens_enabled)

        elif goal == GOAL_BANDAGES:
            bandages_needed = self.slot_data.get("bandages_amount", 100)
            if self.bandage_count < bandages_needed:
                return False
            return self._boss_tokens_sufficient(goal, boss_tokens_enabled)

        return False

    def _boss_tokens_sufficient(self, goal, boss_tokens_enabled):
        """Check if enough Boss Tokens for the goal.

        Replicates APWorld rules.py boss_tokens_amount calculation:
        - Base: 4 (for first 4 bosses: W1-W4)
        - +1 for Larries if "6" in hard_chapter_levels
        - +1 for LW Dr. Fetus if goal==dark_world, or ("6" in hard AND goal!=light_world)
        - +1 for DW Dr. Fetus if dark_world AND "6" in hard AND goal in (ch7s, bandages)
        """
        if not boss_tokens_enabled:
            return True

        hard_chapters = self.slot_data.get("hard_chapter_levels", set())
        if isinstance(hard_chapters, list):
            hard_chapters = set(str(x) for x in hard_chapters)
        elif not isinstance(hard_chapters, set):
            hard_chapters = set()
        dw = bool(self.slot_data.get("dark_world", 0))

        needed = 4  # First 4 bosses (W1-W4)

        # Larries (W5 boss)
        if "6" in hard_chapters:
            needed += 1

        # LW Dr. Fetus
        if goal == GOAL_DARK_WORLD or ("6" in hard_chapters and goal != GOAL_LIGHT_WORLD):
            needed += 1

        # DW Dr. Fetus
        if dw and "6" in hard_chapters and goal in (GOAL_LW_CHAPTER7, GOAL_DW_CHAPTER7, GOAL_BANDAGES):
            needed += 1

        return self.boss_token_count >= needed

    
    # SWEEP (catch missed completions/A+ on level select)
    

    def _sweep_world(self, game, sp, world, dark_enabled,
                     warps_completed=None):
        """Sweep a world for missed completion, A+, and warp checks."""
        checks = []
        num = NUM_LEVELS.get(world, 20)

        for region in ("light", "dark"):
            if region == "dark" and not dark_enabled:
                continue
            for li in range(num):
                comp = game.read_comp(sp, world, li, region)
                if comp < 0 or not (comp & FLAG_COMPLETE):
                    continue
                lv1 = li + 1
                # Completion check
                if region == "light":
                    cname = light_completion_name(world, lv1)
                else:
                    cname = dark_completion_name(world, lv1)
                if cname:
                    loc = self.loc_id(cname)
                    if loc and loc not in self.locations_checked:
                        checks.append(loc)
                # A+ check
                self._check_aplus_location(game, sp, world, li, region, checks)

        # Warp zone completion check
        if warps_completed is not None and world <= 5:
            self._check_warp_completions(game, sp, world, checks, warps_completed)

        return checks

    
    # INITIAL SYNC SCAN
    

    async def _initial_sync_scan(self, game, sp, dark_enabled,
                                  warps_completed,
                                  achievements_enabled, speedrun_enabled, deathless_enabled,
                                  worlds_cleared, worlds_dark_cleared,
                                  milestones_sent, warp_milestones_sent,
                                  speedrun_sent, deathless_sent):
        """Scan save data for pre-existing progress on connect."""
        self.log("Scanning save data for pre-existing progress...", "info")
        precheck = []

        # Level completions
        comp_count = 0
        for w in range(1, 8):
            num = NUM_LEVELS.get(w, 20)
            for region in ("light", "dark"):
                if region == "dark" and not dark_enabled:
                    continue
                for li in range(num):
                    comp = game.read_comp(sp, w, li, region)
                    if comp >= 0 and (comp & FLAG_COMPLETE):
                        lv1 = li + 1
                        if region == "light":
                            cname = light_completion_name(w, lv1)
                        else:
                            cname = dark_completion_name(w, lv1)
                        if cname:
                            loc = self.loc_id(cname)
                            if loc and loc not in self.locations_checked:
                                precheck.append(loc)
                                comp_count += 1
        if comp_count:
            self.log(f"  Pre-existing completions: {comp_count}", "info")

        # Bandages
        bandage_count = 0
        bandages_enabled = self.slot_data.get("bandages", 0)
        if bandages_enabled:
            for w in range(1, 6):
                for region in ("light", "dark"):
                    indices = range(20)
                    for li in indices:
                        comp = game.read_comp(sp, w, li, region)
                        if comp >= 0 and (comp & FLAG_BANDAGE):
                            lv1 = li + 1
                            bname = None
                            if region == "light":
                                bname = light_bandage_name(w, lv1)
                            elif region == "dark":
                                bname = dark_bandage_name(w, lv1)
                            if bname:
                                loc = self.loc_id(bname)
                                if loc and loc not in self.locations_checked:
                                    precheck.append(loc)
                                    bandage_count += 1
                            # Revoke bandage bit
                            game.write_comp(sp, w, li, region, comp & MASK_CLEAR_BANDAGE)

                # Warp bandages: collect per-zone, assign Bandage 1/2 in slot order
                for zone_idx in range(4):
                    info = WARP_ZONE_INFO.get((w, zone_idx))
                    if not info:
                        continue
                    host_lv, is_dark, wname = info
                    name_fn = dw_warp_bandage_name if is_dark else lw_warp_bandage_name
                    bandage_num = 0
                    for sub in range(3):
                        si = zone_idx * 3 + sub
                        comp = game.read_comp(sp, w, si, "warp")
                        if comp >= 0 and (comp & FLAG_BANDAGE):
                            bandage_num += 1
                            bname = name_fn(w, host_lv, bandage_num)
                            if bname:
                                loc = self.loc_id(bname)
                                if loc and loc not in self.locations_checked:
                                    precheck.append(loc)
                                    bandage_count += 1
                            # Revoke
                            game.write_comp(sp, w, si, "warp", comp & MASK_CLEAR_BANDAGE)
        if bandage_count:
            self.log(f"  Pre-existing bandages: {bandage_count}", "info")

        # A+ grades
        aplus_count = 0
        aplus_miss = 0
        for w in range(1, 8):
            num = NUM_LEVELS.get(w, 20)
            for region in ("light", "dark"):
                if region == "dark" and not dark_enabled:
                    continue
                for li in range(num):
                    comp = game.read_comp(sp, w, li, region)
                    if comp >= 0 and (comp & FLAG_COMPLETE):
                        tval = game.read_time(sp, w, li, region)
                        if (w, li) in self.fake_aplus_times and region == "light":
                            fake_val = get_par_time(w, li, region)
                            if fake_val is not None and abs(tval - (fake_val - 0.001)) < 0.0005:
                                continue
                            else:
                                self.fake_aplus_times.discard((w, li))
                        if tval > 0 and is_a_plus(tval, w, li, region):
                            aplus_count += 1
                            lv1 = li + 1
                            if region == "light":
                                aname = light_aplus_name(w, lv1)
                            else:
                                aname = dark_aplus_name(w, lv1)
                            if aname:
                                loc = self.loc_id(aname)
                                if loc and loc not in self.locations_checked:
                                    precheck.append(loc)
                                elif not loc:
                                    aplus_miss += 1
        if aplus_count:
            self.log(f"  Pre-existing A+ grades: {aplus_count}"
                     f"{f' ({aplus_miss} not in DataPackage)' if aplus_miss else ''}",
                     "info")

        # Warp zone completions
        warp_count = 0
        for w in range(1, 6):
            for zone_idx in range(4):
                all_done = True
                for sub in range(3):
                    si = zone_idx * 3 + sub
                    comp = game.read_comp(sp, w, si, "warp")
                    if comp < 0 or not (comp & FLAG_COMPLETE):
                        all_done = False
                        break
                if all_done:
                    warps_completed.add((w, zone_idx))
                    info = WARP_ZONE_INFO.get((w, zone_idx))
                    if info:
                        host_lv, is_dark, wname = info
                        if is_dark:
                            loc_name = dw_warp_completion_name(w, host_lv)
                        else:
                            loc_name = lw_warp_completion_name(w, host_lv)
                        if loc_name:
                            loc = self.loc_id(loc_name)
                            if loc and loc not in self.locations_checked:
                                precheck.append(loc)
                                warp_count += 1
        if warp_count:
            self.log(f"  Pre-existing warp completions: {warp_count}", "info")

        # Achievement pre-scan
        if achievements_enabled:
            ach_checks = []
            self._check_achievements(
                game, sp, ach_checks,
                achievements_enabled, dark_enabled,
                worlds_cleared, worlds_dark_cleared,
                milestones_sent, warp_milestones_sent,
                warps_completed,
                speedrun_sent, speedrun_enabled,
                deathless_sent, deathless_enabled,
            )
            precheck.extend(ach_checks)
            if ach_checks:
                self.log(f"  Pre-existing achievements: {len(ach_checks)}", "info")

        if precheck:
            await self.send_location_checks(precheck)
            self.log(f"Pre-existing progress: {len(precheck)} locations sent", "success")

    
    # NETWORK
    

    async def send_message(self, msg: dict):
        if self.ws:
            await self.ws.send(json.dumps([msg]))

    async def handle_message(self, msg: dict):
        cmd = msg.get("cmd", "")

        if cmd == "RoomInfo":
            self.server_version = msg.get("version", {"major": 0, "minor": 5, "build": 1})
            sv = self.server_version
            self.log(f"Connected to room (AP v{sv.get('major',0)}.{sv.get('minor',0)}.{sv.get('build',0)}), requesting data...", "info")
            await self.send_message({
                "cmd": "GetDataPackage",
                "games": msg.get("games", [])
            })
            await self._send_connect()

        elif cmd == "DataPackage":
            data = msg.get("data", {}).get("games", {})
            for game_name, game_data in data.items():
                for name, iid in game_data.get("item_name_to_id", {}).items():
                    self.item_id_to_name[iid] = name
                for name, lid in game_data.get("location_name_to_id", {}).items():
                    self.loc_name_to_id[name] = lid
                    self.loc_id_to_name[lid] = name
            self.log(f"Loaded DataPackage: {len(self.loc_name_to_id)} locations, "
                     f"{len(self.item_id_to_name)} items", "info")
            # Diagnostic: check if A+ locations exist in DataPackage
            test_names = [
                light_aplus_name(1, 1),   # "1-1 Hello World (A+ Rank)"
                dark_aplus_name(2, 8),    # "2-8X Grape Soda (A+ Rank)"
                light_aplus_name(6, 1),   # "6-1 The Pit (A+ Rank)"
            ]
            found = sum(1 for n in test_names if n and n in self.loc_name_to_id)
            if found < len(test_names):
                missing = [n for n in test_names if n and n not in self.loc_name_to_id]
                self.log(f"WARNING: A+ locations missing from DataPackage: {missing}", "error")
                # Try to find what A+ names look like
                aplus_locs = [n for n in self.loc_name_to_id if "A+" in n or "Rank" in n]
                if aplus_locs:
                    self.log(f"  DataPackage A+ samples: {aplus_locs[:5]}", "debug")
                else:
                    self.log("  No A+/Rank locations found in DataPackage", "debug")

        elif cmd == "Connected":
            self.connected = True
            self.team = msg.get("team", 0)
            self.slot_data = msg.get("slot_data", {})
            self.locations_checked = set(msg.get("checked_locations", []))

            for player in msg.get("players", []):
                self.players[player["slot"]] = player["name"]

            slot_num = msg.get("slot", 0)
            self.log(f"Connected as {self.slot} (Slot {slot_num})", "success")
            self.log(f"  Players: {', '.join(self.players.values())}", "info")
            self.log(f"  Already checked: {len(self.locations_checked)} locations", "info")

            # Log slot data
            goal = self._parse_goal(self.slot_data.get("goal", 0))
            self.log(f"  Goal: {goal}", "info")
            if self.slot_data.get("dark_world", 0):
                self.log("  Dark World: ENABLED", "info")
            hard = self.slot_data.get("hard_chapter_levels", set())
            if hard:
                self.log(f"  Hard Chapters: {hard}", "info")
            if self.slot_data.get("bandages", 0):
                self.log("  Bandages: ENABLED", "info")
            if self.slot_data.get("boss_tokens", 0):
                self.log("  Boss Tokens: ENABLED", "info")
            boss_req = self.slot_data.get("boss_req", 17)
            self.log(f"  Boss Req: {boss_req}", "info")

            self.set_status("Connected", "#00ff00")

        elif cmd == "ReceivedItems":
            start_index = msg.get("index", 0)
            if start_index == 0:
                self.items_received = []
                self.items_processed = 0
            for item in msg.get("items", []):
                iid = item["item"]
                sender = self.players.get(item["player"], "Server")
                iname = self.get_item_name(iid)
                self.items_received.append({
                    "id": iid, "name": iname, "sender": sender,
                })
                self.log(f"Received: {iname} from {sender}", "item")

        elif cmd == "PrintJSON":
            parts = []
            for part in msg.get("data", []):
                if isinstance(part, dict):
                    pt = part.get("type")
                    txt = part.get("text", "")
                    if pt == "player_id":
                        try: parts.append(self.get_player_name(int(txt)))
                        except: parts.append(txt)
                    elif pt == "item_id":
                        try: parts.append(self.get_item_name(int(txt)))
                        except: parts.append(txt)
                    elif pt == "location_id":
                        try: parts.append(self.get_location_name(int(txt)))
                        except: parts.append(txt)
                    else:
                        parts.append(txt)
                else:
                    parts.append(str(part))
            text = "".join(parts)
            if text:
                self.log(f"[Server] {text}", "server")

        elif cmd == "ConnectionRefused":
            errors = msg.get("errors", ["Unknown error"])
            self.log(f"Connection refused: {', '.join(errors)}", "error")
            self.set_status("Refused", "#ff4444")

    async def _send_connect(self):
        import uuid
        # Use server version from RoomInfo to guarantee compatibility.
        # Fallback to 0.6.4 (minimum required by the SMB APWorld).
        version = getattr(self, 'server_version',
                          {"major": 0, "minor": 6, "build": 4})
        # Ensure class field is present (required for dict-based versions)
        if isinstance(version, dict) and "class" not in version:
            version = dict(version)
            version["class"] = "Version"
        await self.send_message({
            "cmd": "Connect",
            "game": GAME_NAME,
            "name": self.slot,
            "uuid": str(uuid.uuid4()),
            "version": version,
            "items_handling": 0b111,
            "tags": [],
            "password": self.password,
            "slot_data": True,
        })

    def get_new_items(self) -> List[Dict]:
        new = self.items_received[self.items_processed:]
        self.items_processed = len(self.items_received)
        return new

    
    # ITEM PROCESSING
    

    def _process_item(self, item, game, sp):
        """Process a received item and apply game effects. Returns log message or None."""
        iid = item["id"]
        self._received_item_ids.add(iid)

        # Chapter Keys -> world unlock
        if iid in CHAPTER_KEY_ITEMS:
            w = CHAPTER_KEY_ITEMS[iid]
            if w not in self.allowed_worlds:
                # W6 needs Meat Boy, W7 needs Bandage Girl
                if w == 6 and not self._has_meat_boy():
                    self.allowed_worlds.add(w)  # Track it, but don't unlock yet
                    return f"Received: {WORLD_NAMES.get(w)} Key (need Meat Boy to enter)"
                elif w == 7 and not self._has_bandage_girl():
                    self.allowed_worlds.add(w)
                    return f"Received: {WORLD_NAMES.get(w)} Key (need Bandage Girl to enter)"
                else:
                    self.allowed_worlds.add(w)
                    bitmask = self._compute_world_bitmask()
                    if sp:
                        game.set_world_unlock(sp, bitmask)
                    return f"Unlocked: {WORLD_NAMES.get(w, f'Chapter {w}')}"
            return None

        # Boss Keys -> boss unlock counting
        elif iid in BOSS_KEY_ITEMS:
            w = BOSS_KEY_ITEMS[iid]
            self.boss_key_counts[w] = self.boss_key_counts.get(w, 0) + 1
            boss_req = self.slot_data.get("boss_req", 17)
            if sp:
                newly = self._update_boss_unlocks(game, sp, boss_req)
                for bw in newly:
                    self.log(f"Boss Unlocked: {WORLD_NAMES.get(bw, f'W{bw}')}!", "success")
            needed = boss_req if w <= 5 else self.slot_data.get("lw_dr_fetus_req", 5)
            have = self.boss_key_counts.get(w, 0)
            return f"Chapter {w} Boss Key ({have}/{needed})"

        # Characters
        elif iid in CHARACTER_ITEMS:
            bit, name = CHARACTER_ITEMS[iid]
            self.character_bits |= (1 << bit)
            if sp:
                game.set_char_bitmask(sp, self.character_bits)
                # Meat Boy received -> re-check W6 access and all boss unlocks
                if iid == ITEM_MEAT_BOY:
                    bitmask = self._compute_world_bitmask()
                    game.set_world_unlock(sp, bitmask)
                    boss_req = self.slot_data.get("boss_req", 17)
                    newly = self._update_boss_unlocks(game, sp, boss_req)
                    for bw in newly:
                        self.log(f"Boss Unlocked: {WORLD_NAMES.get(bw, f'W{bw}')}!", "success")
                    if 6 in self.allowed_worlds:
                        self.log(f"Chapter 6 now accessible!", "success")
                # Bandage Girl received -> re-check W7 access
                elif iid == ITEM_BANDAGE_GIRL:
                    bitmask = self._compute_world_bitmask()
                    game.set_world_unlock(sp, bitmask)
                    if 7 in self.allowed_worlds:
                        self.log(f"Chapter 7 now accessible!", "success")
            return f"Unlocked: {name}"

        # A+ Rank items -> dark level unlock
        elif iid in APLUS_RANK_ITEMS:
            w, lv1 = APLUS_RANK_ITEMS[iid]
            self.aplus_items_received.add((w, lv1))
            if sp and self.slot_data.get("dark_world", 0):
                self._grant_aplus_item(game, sp, w, lv1)
            return f"A+ Rank: {w}-{lv1} (dark {w}-{lv1}X unlocked)"

        # Bandage
        elif iid == ITEM_BANDAGE:
            self.bandage_count += 1
            if sp and self.bandage_count <= len(BANDAGE_GRANT_TARGETS):
                gw, gi, gr = BANDAGE_GRANT_TARGETS[self.bandage_count - 1]
                val = game.read_comp(sp, gw, gi, gr)
                if val >= 0:
                    game.write_comp(sp, gw, gi, gr, val | FLAG_BANDAGE)
            return f"Bandage ({self.bandage_count} total)"

        # Boss Token
        elif iid == ITEM_BOSS_TOKEN:
            self.boss_token_count += 1
            # Boss tokens can gate Larries/LW Dr. Fetus/DW Dr. Fetus
            if sp:
                boss_req_val = self.slot_data.get("boss_req", 17)
                newly = self._update_boss_unlocks(game, sp, boss_req_val)
                for bw in newly:
                    self.log(f"Boss Unlocked: {WORLD_NAMES.get(bw, f'W{bw}')}!", "success")
            return f"Boss Token ({self.boss_token_count})"

        # Victory
        elif iid == ITEM_VICTORY:
            self.victory_received = True
            return "VICTORY!"

        # DW Dr. Fetus Key
        elif iid == ITEM_DW_DR_FETUS_KEY:
            self.dw_fetus_key_count += 1
            needed = self.slot_data.get("dw_dr_fetus_req", 85)
            # Re-check W6 boss unlock (DW keys can unlock W6 counter)
            if sp:
                boss_req_val = self.slot_data.get("boss_req", 17)
                newly = self._update_boss_unlocks(game, sp, boss_req_val)
                for bw in newly:
                    self.log(f"Boss Unlocked: {WORLD_NAMES.get(bw, f'W{bw}')}!", "success")
            return f"DW Dr. Fetus Key ({self.dw_fetus_key_count}/{needed})"

        # Ch7 Level Keys
        elif iid == ITEM_CH7_LW_LEVEL_KEY:
            self.ch7_lw_key_count += 1
            return f"Ch7 LW Level Key ({self.ch7_lw_key_count}/20)"

        elif iid == ITEM_CH7_DW_LEVEL_KEY:
            self.ch7_dw_key_count += 1
            return f"Ch7 DW Level Key ({self.ch7_dw_key_count}/20)"

        # Degraded Bandage (filler, does nothing)
        elif iid == ITEM_DEGRADED_BANDAGE:
            return None  # Silent

        return None

    
    # MAIN RUN + GAME MONITOR
    

    async def run(self, game: GameInterface):
        self._running = True
        self.loop = asyncio.get_event_loop()
        url = f"wss://{self.server}" if not self.server.startswith("ws") else self.server
        self.log(f"Connecting to {self.server}...", "info")
        self.set_status("Connecting...", "#ffcc00")

        try:
            async with websockets.connect(url, max_size=None) as ws:
                self.ws = ws
                self.log("WebSocket connected!", "success")
                monitor_task = asyncio.create_task(self.game_monitor(game))
                try:
                    async for message in ws:
                        if not self._running:
                            break
                        try:
                            for msg in json.loads(message):
                                await self.handle_message(msg)
                        except json.JSONDecodeError:
                            pass
                except websockets.exceptions.ConnectionClosed as e:
                    self.log(f"Connection closed: {e}", "error")
                finally:
                    monitor_task.cancel()
        except Exception as e:
            self.log(f"Connection error: {e}", "error")

        self.connected = False
        self.ws = None
        self.set_status("Disconnected", "#ff4444")
        self._running = False

    async def game_monitor(self, game: GameInterface):
        """Monitor game state and send location checks."""
        # State tracking
        last_playing = last_world = last_level = last_beaten = -1
        last_lvl_type = last_ui_state = -1
        entry_comp = {}
        entry_region = {}           # (world, level) -> region at entry time
        entry_dual = {}             # (world, level) -> (light_comp, dark_comp) at entry
        warp_entry_slots = {}
        warp_entry_full = {}
        pending_boss_world = 0
        pending_boss_time = 0
        pending_boss_dark = False
        boss_entry_comp = -1  # Boss comp byte snapshot when entering level 99
        last_detected_region = None  # Last region detected from dual snapshot
        warps_completed: Set[Tuple[int, int]] = set()
        bosses_beaten: Set[int] = set()
        cutscenes_checked: Set[int] = set()
        worlds_cleared: Set[int] = set()       # W6/W7 light clears
        worlds_dark_cleared: Set[int] = set()   # W6/W7 dark clears
        milestones_sent: Set[int] = set()       # Bandage milestones sent
        warp_milestones_sent: Set[int] = set()  # Warp milestones sent
        speedrun_sent: Set[int] = set()         # Speedrun achievements sent
        deathless_sent: Set[Tuple[int, str]] = set()  # Deathless achievements sent
        deathless_tracker: Dict = {}  # (world, region) -> tracking state
        esc_cooldown = 0
        poll_count = 0

        # Wait for connection + slot data
        for _ in range(50):
            if self.connected and self.slot_data:
                break
            await asyncio.sleep(0.1)
        if not self.connected:
            self.log("Connection failed, stopping monitor", "error")
            return

        # Parse slot data
        goal = self._parse_goal(self.slot_data.get("goal", 0))
        dark_enabled = bool(self.slot_data.get("dark_world", 0))
        boss_req = self.slot_data.get("boss_req", 17)
        boss_tokens_enabled = bool(self.slot_data.get("boss_tokens", 0))
        bandages_enabled = bool(self.slot_data.get("bandages", 0))
        hard_chapters = self.slot_data.get("hard_chapter_levels", set())
        if isinstance(hard_chapters, list):
            hard_chapters = set(hard_chapters)
        starting_chpt = self.slot_data.get("starting_chpt", 1)
        achievements_enabled = bool(self.slot_data.get("achievements", 0))
        deathless_enabled = bool(self.slot_data.get("deathless_achievements", 0))
        speedrun_enabled = bool(self.slot_data.get("speedrun_achievements", 0))
        xmas_enabled = bool(self.slot_data.get("xmas", 0))

        self.log(f"Config: goal={goal}, dark={dark_enabled}, boss_req={boss_req}, "
                 f"tokens={'ON' if boss_tokens_enabled else 'OFF'}, "
                 f"bandages={'ON' if bandages_enabled else 'OFF'}, "
                 f"achievements={'ON' if achievements_enabled else 'OFF'}, "
                 f"deathless={'ON' if deathless_enabled else 'OFF'}, "
                 f"speedrun={'ON' if speedrun_enabled else 'OFF'}, "
                 f"xmas={'ON' if xmas_enabled else 'OFF'}", "info")

        # Clear stale client-written state BEFORE scanning.
        # Previous sessions may have left bandage grants and fake A+ times
        # in save data that would be falsely detected as player progress.
        sp = game.get_sp()
        if sp:
            # Clear bandage grant slots (all dark + non-bandage light levels)
            for gw, gi, gr in BANDAGE_GRANT_TARGETS:
                val = game.read_comp(sp, gw, gi, gr)
                if val >= 0 and (val & FLAG_BANDAGE):
                    game.write_comp(sp, gw, gi, gr, val & MASK_CLEAR_BANDAGE)

            # Clear fake A+ times (par - 0.001) left by previous session
            for w in range(1, 8):
                num = NUM_LEVELS.get(w, 20)
                for li in range(num):
                    par = get_par_time(w, li, "light")
                    if par is None:
                        continue
                    tval = game.read_time(sp, w, li, "light")
                    if tval > 0 and abs(tval - (par - 0.001)) < 0.0005:
                        # This is a fake time — clear it to a non-A+ value
                        game.write_time(sp, w, li, "light", par + 1.0)

            self.log("Cleared stale bandage grants and fake A+ times", "info")

        # Initial sync scan — now sees only genuine player progress
        sp = game.get_sp()
        if sp:
            await self._initial_sync_scan(
                game, sp, dark_enabled, warps_completed,
                achievements_enabled, speedrun_enabled, deathless_enabled,
                worlds_cleared, worlds_dark_cleared,
                milestones_sent, warp_milestones_sent,
                speedrun_sent, deathless_sent,
            )

        # Process initial items
        for _ in range(20):
            await asyncio.sleep(0.1)
            new_items = self.get_new_items()
            sp = game.get_sp()
            for item in new_items:
                self._process_item(item, game, sp)
            if new_items:
                break

        # Apply initial state
        sp = game.get_sp()
        if sp:
            bitmask = self._compute_world_bitmask()
            game.set_world_unlock(sp, bitmask)
            game.set_char_bitmask(sp, self.character_bits)

            # Clear stale bandage grant slots
            for gw, gi, gr in BANDAGE_GRANT_TARGETS:
                val = game.read_comp(sp, gw, gi, gr)
                if val >= 0 and (val & FLAG_BANDAGE):
                    game.write_comp(sp, gw, gi, gr, val & MASK_CLEAR_BANDAGE)
            # Grant bandages
            for i in range(self.bandage_count):
                if i < len(BANDAGE_GRANT_TARGETS):
                    gw, gi, gr = BANDAGE_GRANT_TARGETS[i]
                    val = game.read_comp(sp, gw, gi, gr)
                    if val >= 0:
                        game.write_comp(sp, gw, gi, gr, val | FLAG_BANDAGE)

            # Boss unlocks
            self._update_boss_unlocks(game, sp, boss_req)
            self._enforce_boss_counters(game, sp, boss_req)

            # Dark lock enforcement + A+ item grants
            if dark_enabled:
                self._enforce_dark_locks(game, sp)
                for w, lv1 in self.aplus_items_received:
                    self._grant_aplus_item(game, sp, w, lv1)

        self.log(f"Synced: Worlds {sorted(self.allowed_worlds)}, "
                 f"Bandages {self.bandage_count}, "
                 f"Boss Keys {dict(self.boss_key_counts)}", "success")

        self.log("Monitoring game...", "info")

        while self._running and game.connected:
            poll_count += 1
            try:
                # Process new items
                new_items = self.get_new_items()
                sp = game.get_sp()
                for item in new_items:
                    msg = self._process_item(item, game, sp)
                    if msg:
                        self.log(f"Applied: {msg}", "game")

                    # Check goal after each item
                    if self._check_goal(goal, boss_tokens_enabled):
                        await self.send_goal_complete()

                    # Check bandage milestones on bandage receipt
                    if item["id"] == ITEM_BANDAGE and achievements_enabled:
                        ach_checks = []
                        for threshold, ach_name in BANDAGE_MILESTONE_NAMES.items():
                            if threshold not in milestones_sent:
                                if threshold >= 70 and not dark_enabled:
                                    continue
                                if self.bandage_count >= threshold:
                                    milestones_sent.add(threshold)
                                    loc = self.loc_id(ach_name)
                                    if loc and loc not in self.locations_checked:
                                        ach_checks.append(loc)
                                        self.log(f"Achievement: {ach_name}", "success")
                        if ach_checks:
                            await self.send_location_checks(ach_checks)

                # Read game state
                state = game.get_state()
                if state is None:
                    await asyncio.sleep(0.1)
                    continue

                playing = state["playing"]
                world = state["world"]
                level = state["level"]
                beaten = state["beaten"]
                lvl_type = state["lvl_type"]
                ui_state = state["ui_state"]
                trans = state["trans"]

                if playing < 0 or world < 0 or level < -1:
                    await asyncio.sleep(0.01)
                    last_playing, last_world, last_level = playing, world, level
                    last_beaten, last_lvl_type = beaten, lvl_type
                    continue

                actual_level = level if 0 <= level < 99 else -1
                in_warp = is_warp(lvl_type)
                sp = game.get_sp()
                if not sp:
                    await asyncio.sleep(0.01)
                    last_playing, last_world, last_level = playing, world, level
                    last_beaten, last_lvl_type = beaten, lvl_type
                    continue

                # Clear snapshots on world change
                if world != last_world and last_world > 0 and world > 0:
                    entry_comp.clear()
                    entry_region.clear()
                    entry_dual.clear()
                    warp_entry_slots.clear()
                    warp_entry_full.clear()
                    # Reset deathless trackers when changing worlds
                    deathless_tracker.clear()

                # Ensure warp slots captured while playing (safety net)
                if playing == 1 and world <= 5 and world not in warp_entry_slots:
                    warp_entry_slots[world] = game.read_warp_slots(sp, world)
                    warp_entry_full[world] = game.read_warp_slots_full(sp, world)

                # --- World select enforcement ---
                on_world_select = (
                    (level == 99 and ui_state == 3 and trans == 0) or
                    (level == 0 and playing == 0)
                )
                if on_world_select:
                    bitmask = self._compute_world_bitmask()
                    game.set_world_unlock(sp, bitmask)
                    game.set_char_bitmask(sp, self.character_bits)
                    self._enforce_boss_counters(game, sp, boss_req)
                    if dark_enabled:
                        self._enforce_dark_locks(game, sp)

                # Level select: sweep + enforce
                on_level_select = (playing == 0 and ui_state == 1 and 1 <= world <= 7)
                if on_level_select:
                    just_arrived = (last_playing == 1 or last_ui_state != 1)
                    pending_recheck = (self._pending_aplus_recheck and poll_count % 50 == 0)
                    if just_arrived or pending_recheck or poll_count % 500 == 499:
                        if dark_enabled:
                            self._enforce_dark_locks(game, sp)
                        sweep_checks = self._sweep_world(game, sp, world, dark_enabled, warps_completed)
                        if sweep_checks:
                            await self.send_location_checks(sweep_checks)
                        # Achievement check after sweep
                        if achievements_enabled:
                            ach_checks = []
                            self._check_achievements(
                                game, sp, ach_checks,
                                achievements_enabled, dark_enabled,
                                worlds_cleared, worlds_dark_cleared,
                                milestones_sent, warp_milestones_sent,
                                warps_completed,
                                speedrun_sent, speedrun_enabled,
                                deathless_sent, deathless_enabled,
                            )
                            if deathless_enabled:
                                self._check_deathless(
                                    game, sp, ach_checks,
                                    deathless_enabled, dark_enabled,
                                    deathless_sent, deathless_tracker,
                                )
                            if ach_checks:
                                await self.send_location_checks(ach_checks)

                # Kick from unauthorized world
                if (playing == 0 and ui_state == 1 and 0 <= level <= 20
                        and world not in self.allowed_worlds and world > 0):
                    bitmask = self._compute_world_bitmask()
                    game.set_world_unlock(sp, bitmask)
                    now = time.time()
                    if now - esc_cooldown > 0.3:
                        self.log(f"Unauthorized world {world} - kicking", "game")
                        game.send_esc()
                        esc_cooldown = now

                # Character bitmask enforcement on menus
                if playing == 0:
                    game.set_char_bitmask(sp, self.character_bits)

                # Periodic enforcement
                if poll_count & 0x3F == 0:
                    if playing == 1:
                        game.set_char_bitmask(sp, self.character_bits)
                        # Check for deaths during gameplay (deathless tracking)
                        if deathless_enabled and not in_warp:
                            for dr in ("light", "dark"):
                                tracker_key = (world, dr)
                                tracker = deathless_tracker.get(tracker_key)
                                if tracker and tracker.get('active'):
                                    current_deaths = game.read_death_count(sp)
                                    entry_deaths = tracker.get('death_count_at_entry', -1)
                                    if current_deaths >= 0 and entry_deaths >= 0 and current_deaths > entry_deaths:
                                        tracker['active'] = False
                                        tracker['levels_done'].clear()
                    self._enforce_boss_counters(game, sp, boss_req)
                    if dark_enabled:
                        self._enforce_dark_locks(game, sp)

                    # Process pending A+ rechecks (time wasn't flushed on first read)
                    if self._pending_aplus_recheck:
                        recheck_checks = []
                        for (rw, rli, rregion) in list(self._pending_aplus_recheck):
                            self._check_aplus_location(
                                game, sp, rw, rli, rregion, recheck_checks)
                        if recheck_checks:
                            await self.send_location_checks(recheck_checks)

                # --- Pending boss check ---
                if pending_boss_world > 0:
                    time_since = time.time() - pending_boss_time
                    if time_since > 1.0:
                        boss_confirmed = False
                        if pending_boss_world == 6:
                            boss_confirmed = (playing == 0)
                        else:
                            boss_confirmed = (playing == 0 and ui_state == 3)

                        if boss_confirmed:
                            # Check access rules before sending boss check
                            can_send = self._can_send_boss_check(
                                pending_boss_world, pending_boss_dark, boss_req)
                            loc_name = boss_location_name(pending_boss_world, pending_boss_dark)
                            if can_send and loc_name:
                                loc = self.loc_id(loc_name)
                                if loc and loc not in self.locations_checked:
                                    await self.send_location_checks([loc])
                                    if not pending_boss_dark:
                                        bosses_beaten.add(pending_boss_world)
                                    self.log(f"Boss defeated: {loc_name}", "success")
                            elif not can_send and loc_name:
                                self.log(f"Boss defeated but requirements not met for: {loc_name}", "game")

                            # Cutscene check (uses boss_req or lw_drfetus rules)
                            can_send_cs = self._can_send_cutscene_check(
                                pending_boss_world, boss_req)
                            cs_name = cutscene_location_name(pending_boss_world)
                            if can_send_cs and cs_name and pending_boss_world not in cutscenes_checked:
                                cs_loc = self.loc_id(cs_name)
                                if cs_loc and cs_loc not in self.locations_checked:
                                    await self.send_location_checks([cs_loc])
                                    cutscenes_checked.add(pending_boss_world)

                            # Goal check after boss
                            if self._check_goal(goal, boss_tokens_enabled):
                                await self.send_goal_complete()

                            # Achievement check after boss
                            if achievements_enabled:
                                ach_checks = []
                                self._check_achievements(
                                    game, sp, ach_checks,
                                    achievements_enabled, dark_enabled,
                                    worlds_cleared, worlds_dark_cleared,
                                    milestones_sent, warp_milestones_sent,
                                    warps_completed,
                                    speedrun_sent, speedrun_enabled,
                                    deathless_sent, deathless_enabled,
                                )
                                if ach_checks:
                                    await self.send_location_checks(ach_checks)

                            self._enforce_boss_counters(game, sp, boss_req)
                            if dark_enabled:
                                self._enforce_dark_locks(game, sp)
                            pending_boss_world = 0
                            pending_boss_dark = False

                        elif time_since > 10.0:
                            pending_boss_world = 0
                            pending_boss_dark = False

                # --- Level entry snapshot ---
                if playing == 1 and last_playing != 1:
                    if actual_level >= 0:
                        region = type_to_region(lvl_type)
                        # Always snapshot both light/dark comp AND warp slots,
                        # since lvl_type is unreliable
                        # warp from light world at entry time.
                        key = (world, actual_level)
                        lc = game.read_comp(sp, world, actual_level, "light")
                        dc = game.read_comp(sp, world, actual_level, "dark")
                        entry_dual[key] = (lc, dc)

                        
                        if world <= 5 and world not in warp_entry_slots:
                            warp_entry_slots[world] = game.read_warp_slots(sp, world)
                            warp_entry_full[world] = game.read_warp_slots_full(sp, world)

                        # Deathless tracking: record death count at level entry
                        death_count = game.read_death_count(sp)
                        for dr in ("light", "dark"):
                            tracker_key = (world, dr)
                            if deathless_enabled:
                                if tracker_key not in deathless_tracker:
                                    deathless_tracker[tracker_key] = {
                                        'levels_done': set(),
                                        'death_count_at_entry': death_count,
                                        'active': True,
                                    }
                                else:
                                    deathless_tracker[tracker_key]['death_count_at_entry'] = death_count

                    # Boss entry: snapshot boss comp byte
                    if level == 99 and 1 <= world <= 7:
                        boss_entry_comp = game.read_boss_comp(sp, world)


                # --- Mid-play level change ---
                # Also fires on boss transition (level → 99, actual_level = -1)
                # so the previous level's A+ and completion get checked.
                if (playing == 1 and last_playing == 1
                        and (actual_level >= 0 or level == 99)
                        and (actual_level != last_level or world != last_world)
                        and last_level >= 0 and last_level < 99 and last_world > 0):
                    await asyncio.sleep(0.15)  # 150ms: game needs time to flush IL time to save
                    sp2 = game.get_sp()
                    if sp2:
                        checks = []
                        was_warp_transition = False

                        # Check if warp slots changed (warp zone activity)
                        if last_world in warp_entry_slots and last_world <= 5:
                            entry_slots = warp_entry_slots[last_world]
                            current_slots = game.read_warp_slots(sp2, last_world)
                            if entry_slots != current_slots:
                                was_warp_transition = True
                                if bandages_enabled:
                                    self._check_warp_bandages(
                                        game, sp2, last_world, entry_slots, current_slots, checks)
                                self._check_warp_completions(
                                    game, sp2, last_world, checks, warps_completed)
                                # Update warp entry slots
                                warp_entry_slots[last_world] = current_slots
                                warp_entry_full[last_world] = game.read_warp_slots_full(sp2, last_world)

                        # Check light/dark dual snapshot (only if not a warp transition)
                        if not was_warp_transition:
                            old_key = (last_world, last_level)
                            dual = entry_dual.get(old_key)
                            if dual:
                                el, ed = dual
                                cl = game.read_comp(sp2, last_world, last_level, "light")
                                cd = game.read_comp(sp2, last_world, last_level, "dark")
                                old_region = None
                                if cl >= 0 and el >= 0 and cl != el:
                                    old_region = "light"
                                    ev, cv = el, cl
                                elif cd >= 0 and ed >= 0 and cd != ed:
                                    old_region = "dark"
                                    ev, cv = ed, cd
                                if old_region:
                                    last_detected_region = old_region
                                if old_region and ev >= 0 and cv >= 0:
                                    # Completion
                                    if not (ev & FLAG_COMPLETE) and (cv & FLAG_COMPLETE):
                                        lv1 = last_level + 1
                                        if old_region == "light":
                                            cname = light_completion_name(last_world, lv1)
                                        else:
                                            cname = dark_completion_name(last_world, lv1)
                                        if cname:
                                            loc = self.loc_id(cname)
                                            if loc and loc not in self.locations_checked:
                                                checks.append(loc)
                                    # Bandage
                                    if bandages_enabled:
                                        self._check_bandage(
                                            game, sp2, last_world, last_level,
                                            old_region, ev, cv, checks)
                                # A+ check
                                if old_region:
                                    self._check_aplus_location(
                                        game, sp2, last_world, last_level, old_region, checks)
                                else:
                                    self._check_aplus_location(
                                        game, sp2, last_world, last_level, "light", checks)
                                    if dark_enabled:
                                        self._check_aplus_location(
                                            game, sp2, last_world, last_level, "dark", checks)

                        if checks:
                            await self.send_location_checks(checks)

                        # Snapshot new level (always dual + warp)
                        if actual_level >= 0:
                            new_key = (world, actual_level)
                            nl = game.read_comp(sp2, world, actual_level, "light")
                            nd = game.read_comp(sp2, world, actual_level, "dark")
                            entry_dual[new_key] = (nl, nd)
                        if world <= 5:
                            warp_entry_slots[world] = game.read_warp_slots(sp2, world)
                            warp_entry_full[world] = game.read_warp_slots_full(sp2, world)

                        # Boss entry via mid-play (e.g. level 19 → 99)
                        if level == 99 and 1 <= world <= 7:
                            boss_entry_comp = game.read_boss_comp(sp2, world)

                # --- Level exit ---
                if playing == 0 and last_playing == 1:
                    await asyncio.sleep(0.15)  # 150ms: game needs time to flush IL time to save
                    sp2 = game.get_sp()
                    if sp2 and last_world > 0:
                        # Boss detection — compare boss comp byte to entry snapshot
                        if last_level == 99 and 1 <= last_world <= 7:
                            current_comp = game.read_boss_comp(sp2, last_world)
                            boss_changed = (boss_entry_comp >= 0
                                            and current_comp >= 0
                                            and current_comp != boss_entry_comp)
                            if boss_changed:
                                pending_boss_world = last_world
                                pending_boss_time = time.time()
                                pending_boss_dark = (last_world == 6 and last_detected_region == "dark")
                                self.log(f"Boss defeated: W{last_world}", "success")
                            boss_entry_comp = -1

                        exit_level = last_level if last_level < 99 else -1
                        checks = []
                        warp_changed = False
                        exit_region_detected = None

                        # Check warp slot changes (detects warp zone activity)
                        if last_world in warp_entry_slots and last_world <= 5:
                            entry_slots = warp_entry_slots[last_world]
                            current_slots = game.read_warp_slots(sp2, last_world)
                            if entry_slots != current_slots:
                                warp_changed = True
                                if bandages_enabled:
                                    self._check_warp_bandages(
                                        game, sp2, last_world, entry_slots, current_slots, checks)
                                self._check_warp_completions(
                                    game, sp2, last_world, checks, warps_completed)
                                # Update warp snapshots
                                warp_entry_slots[last_world] = current_slots
                                warp_entry_full[last_world] = game.read_warp_slots_full(sp2, last_world)

                        # Check light/dark dual snapshot (only if not a warp transition)
                        if not warp_changed and exit_level >= 0:
                            key = (last_world, exit_level)
                            dual = entry_dual.get(key)

                            if dual:
                                el, ed = dual
                                cl = game.read_comp(sp2, last_world, exit_level, "light")
                                cd = game.read_comp(sp2, last_world, exit_level, "dark")
                                if cl >= 0 and el >= 0 and cl != el:
                                    exit_region_detected = "light"
                                    ev, cv = el, cl
                                elif cd >= 0 and ed >= 0 and cd != ed:
                                    exit_region_detected = "dark"
                                    ev, cv = ed, cd

                                if exit_region_detected:
                                    last_detected_region = exit_region_detected
                                if exit_region_detected and ev >= 0 and cv >= 0:
                                    # Completion
                                    if not (ev & FLAG_COMPLETE) and (cv & FLAG_COMPLETE):
                                        lv1 = exit_level + 1
                                        if exit_region_detected == "light":
                                            cname = light_completion_name(last_world, lv1)
                                        else:
                                            cname = dark_completion_name(last_world, lv1)
                                        if cname:
                                            loc = self.loc_id(cname)
                                            if loc and loc not in self.locations_checked:
                                                checks.append(loc)
                                    # Bandage
                                    if bandages_enabled:
                                        self._check_bandage(
                                            game, sp2, last_world, exit_level,
                                            exit_region_detected, ev, cv, checks)

                            # A+ check
                            if exit_region_detected:
                                self._check_aplus_location(
                                    game, sp2, last_world, exit_level, exit_region_detected, checks)
                            else:
                                self._check_aplus_location(
                                    game, sp2, last_world, exit_level, "light", checks)
                                if dark_enabled:
                                    self._check_aplus_location(
                                        game, sp2, last_world, exit_level, "dark", checks)

                        if checks:
                            await self.send_location_checks(checks)

                        # Deathless tracking on level exit
                        if deathless_enabled and exit_region_detected in ("light", "dark"):
                            tracker_key = (last_world, exit_region_detected)
                            tracker = deathless_tracker.get(tracker_key)
                            if tracker and tracker.get('active'):
                                current_deaths = game.read_death_count(sp2)
                                entry_deaths = tracker.get('death_count_at_entry', -1)
                                if current_deaths >= 0 and entry_deaths >= 0:
                                    if current_deaths > entry_deaths:
                                        tracker['active'] = False
                                        tracker['levels_done'].clear()
                                    else:
                                        cur_comp = game.read_comp(
                                            sp2, last_world, exit_level, exit_region_detected)
                                        if cur_comp >= 0 and (cur_comp & FLAG_COMPLETE):
                                            tracker['levels_done'].add(exit_level)

                        # Achievement check on every exit
                        if achievements_enabled:
                            ach_checks = []
                            self._check_achievements(
                                game, sp2, ach_checks,
                                achievements_enabled, dark_enabled,
                                worlds_cleared, worlds_dark_cleared,
                                milestones_sent, warp_milestones_sent,
                                warps_completed,
                                speedrun_sent, speedrun_enabled,
                                deathless_sent, deathless_enabled,
                            )
                            if deathless_enabled:
                                self._check_deathless(
                                    game, sp2, ach_checks,
                                    deathless_enabled, dark_enabled,
                                    deathless_sent, deathless_tracker,
                                )
                            if ach_checks:
                                await self.send_location_checks(ach_checks)

                        self._enforce_boss_counters(game, sp2, boss_req)
                        if dark_enabled:
                            self._enforce_dark_locks(game, sp2)
                        game.set_char_bitmask(sp2, self.character_bits)

                        # A+ sweep on exit
                        if 1 <= last_world <= 7:
                            sweep_checks = self._sweep_world(
                                game, sp2, last_world, dark_enabled, warps_completed)
                            if sweep_checks:
                                await self.send_location_checks(sweep_checks)

                last_playing = playing
                last_world = world
                last_level = level
                last_beaten = beaten
                last_lvl_type = lvl_type
                last_ui_state = ui_state

            except Exception as e:
                if self.goal_completed:
                    await asyncio.sleep(1.0)
                else:
                    self.log(f"Monitor error: {e}", "debug")

            await asyncio.sleep(0.001)

    def stop(self):
        self._running = False
        if self.ws and self.loop and self.loop.is_running():
            try:
                asyncio.run_coroutine_threadsafe(self.ws.close(), self.loop)
            except:
                pass



# GUI APPLICATION


class SMBClientApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(APP_NAME)
        self.root.geometry("700x600")
        self.root.minsize(600, 500)
        self.root.configure(bg=DARK_BG)
        self.setup_dark_theme()

        self.client: Optional[APClient] = None
        self.game: Optional[GameInterface] = None
        self.client_thread = None
        self.loop = None
        self.config = self.load_config()

        self.server_var = tk.StringVar()
        self.slot_var = tk.StringVar()
        self.password_var = tk.StringVar()

        self.create_widgets()
        self.load_settings()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.check_game_connection()

    def setup_dark_theme(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(".", background=DARK_BG, foreground=DARK_FG,
                        fieldbackground=DARK_ENTRY_BG)
        style.configure("TFrame", background=DARK_FRAME_BG)
        style.configure("TLabel", background=DARK_FRAME_BG, foreground=DARK_FG)
        style.configure("TButton", background=DARK_ACCENT, foreground="#ffffff",
                        borderwidth=1, focuscolor=DARK_ACCENT)
        style.map("TButton",
                  background=[("active", DARK_BORDER), ("pressed", DARK_BG)])
        style.configure("TEntry", fieldbackground=DARK_ENTRY_BG,
                        foreground=DARK_FG, insertcolor=DARK_FG)
        style.configure("TLabelframe", background=DARK_FRAME_BG)
        style.configure("TLabelframe.Label", background=DARK_FRAME_BG,
                        foreground=DARK_FG)
        # Header style
        style.configure("Header.TLabel", background=DARK_FRAME_BG,
                        foreground=SMB_RED, font=("Helvetica", 16, "bold"))
        style.configure("Version.TLabel", background=DARK_FRAME_BG,
                        foreground=SMB_BANDAGE, font=("Helvetica", 9))

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Set window icon
        try:
            self._icon_img = tk.PhotoImage(data=MEATBOY_ICON_32)
            self.root.iconphoto(True, self._icon_img)
        except Exception:
            pass

        # Header with Meat Boy icon
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(pady=(0, 10))
        try:
            self._header_icon = tk.PhotoImage(data=MEATBOY_ICON_48)
            icon_label = ttk.Label(header_frame, image=self._header_icon,
                                    background=DARK_FRAME_BG)
            icon_label.pack(side=tk.LEFT, padx=(0, 8))
        except Exception:
            pass
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT)
        header = ttk.Label(title_frame, text="Super Meat Boy", style="Header.TLabel")
        header.pack(anchor="w")
        subtitle = ttk.Label(title_frame, text=f"Archipelago Client v{APP_VERSION}",
                              style="Version.TLabel")
        subtitle.pack(anchor="w")

        # Game status
        game_frame = ttk.LabelFrame(main_frame, text="Game Status", padding="10")
        game_frame.pack(fill=tk.X, pady=5)
        self.game_status = ttk.Label(game_frame, text="Checking...", font=("Helvetica", 10))
        self.game_status.pack(side=tk.LEFT)
        self.refresh_btn = ttk.Button(game_frame, text="Refresh",
                                       command=self.check_game_connection)
        self.refresh_btn.pack(side=tk.RIGHT)

        # Connection
        conn_frame = ttk.LabelFrame(main_frame, text="Connection", padding="10")
        conn_frame.pack(fill=tk.X, pady=5)
        ttk.Label(conn_frame, text="Server:").grid(row=0, column=0, sticky="w", pady=2)
        self.server_entry = ttk.Entry(conn_frame, textvariable=self.server_var, width=35)
        self.server_entry.grid(row=0, column=1, columnspan=2, sticky="ew", pady=2, padx=5)
        ttk.Label(conn_frame, text="Slot Name:").grid(row=1, column=0, sticky="w", pady=2)
        self.slot_entry = ttk.Entry(conn_frame, textvariable=self.slot_var, width=35)
        self.slot_entry.grid(row=1, column=1, columnspan=2, sticky="ew", pady=2, padx=5)
        ttk.Label(conn_frame, text="Password:").grid(row=2, column=0, sticky="w", pady=2)
        self.password_entry = ttk.Entry(conn_frame, textvariable=self.password_var,
                                         show="*", width=35)
        self.password_entry.grid(row=2, column=1, columnspan=2, sticky="ew", pady=2, padx=5)
        conn_frame.columnconfigure(1, weight=1)

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        self.connect_btn = ttk.Button(btn_frame, text="Connect", command=self.connect)
        self.connect_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.disconnect_btn = ttk.Button(btn_frame, text="Disconnect",
                                          command=self.disconnect, state=tk.DISABLED)
        self.disconnect_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.clear_btn = ttk.Button(btn_frame, text="Clear Log", command=self.clear_log)
        self.clear_btn.pack(side=tk.RIGHT)

        self.status_label = ttk.Label(main_frame, text="Disconnected",
                                       font=("Helvetica", 10, "bold"))
        self.status_label.pack(pady=5)

        # Log
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.log_text = scrolledtext.ScrolledText(
            log_frame, height=15, wrap=tk.WORD, state=tk.DISABLED,
            bg=DARK_ENTRY_BG, fg=DARK_FG, insertbackground=DARK_FG,
            font=("Consolas", 9),
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.tag_configure("info", foreground="#e0e0e0")
        self.log_text.tag_configure("success", foreground="#00ff00")
        self.log_text.tag_configure("error", foreground="#ff4444")
        self.log_text.tag_configure("item", foreground="#ffcc00")
        self.log_text.tag_configure("location", foreground="#00ccff")
        self.log_text.tag_configure("game", foreground="#ff99ff")
        self.log_text.tag_configure("server", foreground="#cc99ff")
        self.log_text.tag_configure("debug", foreground="#aaaaaa")

    def log(self, message: str, tag: str = "info"):
        def _log():
            self.log_text.configure(state=tk.NORMAL)
            ts = datetime.now().strftime("%H:%M:%S")
            self.log_text.insert(tk.END, f"[{ts}] {message}\n", tag)
            self.log_text.see(tk.END)
            self.log_text.configure(state=tk.DISABLED)
        self.root.after(0, _log)

    def set_status(self, text: str, color: str):
        self.root.after(0, lambda: self.status_label.configure(text=text, foreground=color))

    def clear_log(self):
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def check_game_connection(self):
        if self.game is None:
            self.game = GameInterface()
        if self.game.connect():
            self.game_status.configure(text="SuperMeatBoy.exe detected", foreground="#00ff00")
            self.log("Game detected: SuperMeatBoy.exe", "success")
        else:
            self.game_status.configure(text="SuperMeatBoy.exe not running", foreground="#ff4444")
            self.log("Game not detected. Please start Super Meat Boy.", "error")

    def load_config(self) -> dict:
        try:
            if CONFIG_FILE.exists():
                return json.loads(CONFIG_FILE.read_text())
        except: pass
        return {}

    def save_config(self):
        try:
            CONFIG_FILE.write_text(json.dumps({
                "server": self.server_var.get(),
                "slot": self.slot_var.get(),
            }, indent=2))
        except: pass

    def load_settings(self):
        self.server_var.set(self.config.get("server", "archipelago.gg:38281"))
        self.slot_var.set(self.config.get("slot", ""))

    def validate_inputs(self) -> bool:
        if not self.server_var.get().strip():
            messagebox.showerror("Error", "Please enter a server address")
            return False
        if not self.slot_var.get().strip():
            messagebox.showerror("Error", "Please enter your slot name")
            return False
        if not self.game or not self.game.connected:
            self.check_game_connection()
            if not self.game or not self.game.connected:
                messagebox.showerror("Error",
                    "Super Meat Boy is not running!\nPlease start the game first.")
                return False
        return True

    def connect(self):
        if not self.validate_inputs():
            return
        self.save_config()
        self.connect_btn.configure(state=tk.DISABLED)
        self.disconnect_btn.configure(state=tk.NORMAL)
        self.server_entry.configure(state=tk.DISABLED)
        self.slot_entry.configure(state=tk.DISABLED)
        self.password_entry.configure(state=tk.DISABLED)
        self.refresh_btn.configure(state=tk.DISABLED)

        self.client = APClient(self.log, self.set_status)
        self.client.server = self.server_var.get().strip()
        self.client.slot = self.slot_var.get().strip()
        self.client.password = self.password_var.get()

        self.client_thread = threading.Thread(target=self.run_client, daemon=True)
        self.client_thread.start()

    def run_client(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self.client.run(self.game))
        except Exception as e:
            self.log(f"Client error: {e}", "error")
        finally:
            self.loop.close()
            self.root.after(0, self.on_disconnect)

    def disconnect(self):
        if self.client:
            self.client.stop()
        self.log("Disconnecting...", "info")

    def on_disconnect(self):
        self.connect_btn.configure(state=tk.NORMAL)
        self.disconnect_btn.configure(state=tk.DISABLED)
        self.server_entry.configure(state=tk.NORMAL)
        self.slot_entry.configure(state=tk.NORMAL)
        self.password_entry.configure(state=tk.NORMAL)
        self.refresh_btn.configure(state=tk.NORMAL)
        self.set_status("Disconnected", "#888888")

    def on_close(self):
        if self.client:
            self.client.stop()
        self.save_config()
        self.root.destroy()

    def run(self):
        self.log(f"Welcome to {APP_NAME} v{APP_VERSION}", "info")
        self.log("Start Super Meat Boy, then enter server details and click Connect", "info")
        self.root.mainloop()


if __name__ == "__main__":
    try:
        app = SMBClientApp()
        app.run()
    except Exception as e:
        # In frozen exe with no console, show error dialog
        try:
            import traceback
            err = traceback.format_exc()
            messagebox.showerror("SMB AP Client - Fatal Error", f"{e}\n\n{err}")
        except:
            pass
        sys.exit(1)
