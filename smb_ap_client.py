#!/usr/bin/env python3
"""
Super Meat Boy - Archipelago Client (v2.1.0)
A GUI client for connecting Super Meat Boy to Archipelago multiworld.

Features:
- Dark theme GUI with colored log output
- Automatic game detection and memory integration
- World access control via memory manipulation
- Bandage tracking and granting
- Boss completion detection
- Boss Token system (cumulative token-based boss access)
- Goal completion notification
- A+ grade detection (time <= par from SMBDatabase.cs)
- Character unlock tracking (warp slots 3-5)
- Warp zone completion tracking
- W7 (Cotton Alley) level tracking
- GotWarp bit (0x08) detection on host levels
- Achievement locations (world clears, milestones, Golden God, Girl Boy)
- Initial sync scan for pre-existing progress
- Corrected W4/W5 bandage data from SMBDatabase.cs

Requirements:
    pip install pymem websockets

Usage:
    python smb_ap_client.py
    (smb_game_data.py must be in the same directory)
"""

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

# Check dependencies
try:
    import pymem
except ImportError:
    print("ERROR: pymem library required!")
    print("Install with: pip install pymem")
    sys.exit(1)

try:
    import websockets
except ImportError:
    print("ERROR: websockets library required!")
    print("Install with: pip install websockets")
    sys.exit(1)

# Import game data module
try:
    from smb_game_data import (
        # Constants
        BASE_ID, WORLD_NAMES, LEVEL_NAMES, PAR_TIMES, NUM_LEVELS,
        FLAG_BANDAGE, FLAG_COMPLETE, FLAG_WARP,
        MASK_CLEAR_BANDAGE, MASK_CLEAR_WARP,
        # Save structure
        WORLD_BASES, LIGHT_OFFSET, DARK_OFFSET, WARP_OFFSET,
        SLOT_SIZE, COMP_BYTE, TIME_BYTE, NUM_WARP_SLOTS,
        # Bandage data
        LIGHT_BANDAGE_LEVELS, DARK_BANDAGE_LEVELS, WARP_BANDAGE_SLOTS,
        CORRECTED_BANDAGE_DATA, CORRECTED_BANDAGE_BY_ADDR,
        # Warp & character data
        LIGHT_WARP_HOST_LEVELS, DARK_WARP_HOST_LEVELS,
        WARP_HOST_TO_ZONE, WARP_ZONE_NAMES,
        CHARACTER_WARPS, CHARACTER_WARP_SLOTS,
        # Address helpers
        comp_addr, time_addr, slot_addr,
        # Par time / A+ helpers
        get_par_time, is_a_plus, get_level_name, get_warp_zone_name,
        # Location ID functions (existing)
        level_location_id, w6_level_location_id, w6_dark_level_location_id,
        dark_level_location_id, boss_location_id, dark_boss_location_id,
        # Location ID functions (new)
        get_completion_location_id, get_aplus_location_id,
        w7_light_location_id, w7_dark_location_id,
        character_unlock_location_id, warp_completion_location_id,
        world_clear_location_id, world_dark_clear_location_id,
        w6_clear_location_id, w6_dark_clear_location_id,
        w7_clear_location_id, w7_dark_clear_location_id,
        bandage_milestone_location_id, BANDAGE_MILESTONES,
        golden_god_location_id, girl_boy_location_id,
        # Comprehensive name resolver
        get_location_name,
    )
except ImportError:
    print("ERROR: smb_game_data.py not found!")
    print("Place smb_game_data.py in the same directory as this client.")
    sys.exit(1)


# =============================================================================
# W6/W7 ADDRESS CORRECTIONS
# =============================================================================
# W6 (The End) has only 5 levels, no warps. Game packs it as 10 slots (5L+5D)
# instead of the standard 52-slot layout. This means:
#   W6 dark offset = 0x3C (not 0x0F0)
#   W7 base = 0x0D08 
WORLD_BASES[7] = 0x0D08
W6_DARK_OFFSET = 0x3C  # 5 light slots Ã— 12 bytes

_orig_comp_addr = comp_addr
_orig_time_addr = time_addr
_orig_slot_addr = slot_addr


def comp_addr(world, index, region):
    if world == 6 and region == "dark":
        return WORLD_BASES[6] + W6_DARK_OFFSET + index * SLOT_SIZE + COMP_BYTE
    if world == 6 and region == "warp":
        return None  # W6 has no warps
    if world == 7 and region == "warp":
        return None  # W7 has no warps
    return _orig_comp_addr(world, index, region)


def time_addr(world, index, region):
    if world == 6 and region == "dark":
        return WORLD_BASES[6] + W6_DARK_OFFSET + index * SLOT_SIZE + TIME_BYTE
    if world == 6 and region == "warp":
        return None
    if world == 7 and region == "warp":
        return None
    return _orig_time_addr(world, index, region)


def slot_addr(world, index, region):
    if world == 6 and region == "dark":
        return WORLD_BASES[6] + W6_DARK_OFFSET + index * SLOT_SIZE
    if world == 6 and region == "warp":
        return None
    if world == 7 and region == "warp":
        return None
    return _orig_slot_addr(world, index, region)


# =============================================================================
# CONSTANTS
# =============================================================================

APP_NAME = "Super Meat Boy - Archipelago Client"
APP_VERSION = "2.3.0"
GAME_NAME = "Super Meat Boy"

CONFIG_FILE = Path.home() / ".smb_ap_client.json"

# Dark theme colors
DARK_BG = "#1a1a1a"
DARK_FG = "#e0e0e0"
DARK_ENTRY_BG = "#2d2d2d"
DARK_FRAME_BG = "#242424"
DARK_ACCENT = "#3d3d3d"
DARK_BORDER = "#404040"

# Memory addresses (v1.2.5 Steam)
ADDR = {
    "playing":      0x30a1c8,
    "world":        0x2f79ac,
    "level_beaten": 0x30a1e0,
    "level":        (0x30ac90, 0x8dc),
    "lvl_type":     (0x30a1a0, 0x3c68),
    "save_ptr":     0x30a380,
    "world_unlock": 0x3954,
    "ui_state":     (0x30ac90, 0x8e0),
    "level_trans":  0x30ad00,
}

TYPE_LIGHT = 0
TYPE_DARK = 1
TYPE_WARP_MIN = 2
TYPE_WARP_MAX = 5
BOSS_LEVEL_INDEX = 20

# Item IDs (must match APWorld)
ITEM_WORLD2 = BASE_ID + 1
ITEM_WORLD3 = BASE_ID + 2
ITEM_WORLD4 = BASE_ID + 3
ITEM_WORLD5 = BASE_ID + 4
ITEM_BANDAGE = BASE_ID + 5
ITEM_1UP = BASE_ID + 6
ITEM_WORLD6 = BASE_ID + 7
ITEM_WORLD7 = BASE_ID + 8

WORLD_ACCESS_ITEM_IDS = {
    ITEM_WORLD2: 2, ITEM_WORLD3: 3, ITEM_WORLD4: 4,
    ITEM_WORLD5: 5, ITEM_WORLD6: 6, ITEM_WORLD7: 7,
}

# Character items: item_id -> (bitmask_bit, name)
# Bitmask lives at save_ptr + 0x3950
CHARACTER_BITMASK_OFFSET = 0x3950
CHARACTER_ITEMS = {
    BASE_ID + 10: (2,  "4Color Meat Boy"),
    BASE_ID + 11: (3,  "4Bit Meat Boy"),
    BASE_ID + 31: (5,  "Brownie"),
    BASE_ID + 32: (6,  "Bandage Girl"),
    BASE_ID + 12: (7,  "Meat Ninja"),
    BASE_ID + 13: (10, "Naija"),
    BASE_ID + 14: (11, "Commander Video"),
    BASE_ID + 15: (12, "Runman"),
    BASE_ID + 16: (13, "Blob"),
    BASE_ID + 17: (14, "Steve"),
    BASE_ID + 18: (16, "Flywrench"),
    BASE_ID + 19: (18, "Jill"),
    BASE_ID + 20: (19, "Captain Viridian"),
    BASE_ID + 21: (20, "Tofu Boy"),
    BASE_ID + 22: (21, "Josef"),
    BASE_ID + 23: (22, "The Kid"),
    BASE_ID + 24: (23, "Headcrab"),
    BASE_ID + 25: (24, "Ogmo"),
    BASE_ID + 26: (25, "Potato Boy"),
    BASE_ID + 27: (26, "MeatBoy and BandageGirl"),
    BASE_ID + 28: (27, "Alien Hominid"),
    BASE_ID + 29: (28, "Autorun MeatBoy"),
    BASE_ID + 30: (29, "Tim"),
}
# Bit 0 = Meat Boy (always available)
CHARACTER_BASE_BITS = (1 << 0)

# Per-world Boss Token item IDs
BOSS_TOKEN_IDS = {
    BASE_ID + 33: 1,  # Forest Boss Token
    BASE_ID + 34: 2,  # Hospital Boss Token
    BASE_ID + 35: 3,  # Salt Factory Boss Token
    BASE_ID + 36: 4,  # Hell Boss Token
    BASE_ID + 37: 5,  # Rapture Boss Token
    BASE_ID + 38: 6,  # The End Boss Token
}

BOSS_TOKEN_NAMES = {
    1: "Forest Boss Token",
    2: "Hospital Boss Token",
    3: "Salt Factory Boss Token",
    4: "Hell Boss Token",
    5: "Rapture Boss Token",
    6: "The End Boss Token",
}

# Progressive dark access items (per-world, received multiple times)
DARK_ACCESS_IDS: Dict[int, int] = {
    BASE_ID + 100: 1,
    BASE_ID + 101: 2,
    BASE_ID + 102: 3,
    BASE_ID + 103: 4,
    BASE_ID + 104: 5,
}
DARK_ACCESS_NAMES = {
    1: "Forest Dark Access",
    2: "Hospital Dark Access",
    3: "Salt Factory Dark Access",
    4: "Hell Dark Access",
    5: "Rapture Dark Access",
}
DARK_LOCK_TIME_PENALTY = 1.0  # seconds above par to suppress dark unlock

# Boss completion counter offsets (from save_ptr)
BOSS_COUNTER_OFFSETS = {
    1: 0x38D8, 2: 0x38E4, 3: 0x38F0,
    4: 0x38FC, 5: 0x3908, 6: 0x3914,
}

# Game's native thresholds (counter >= this opens boss door)
BOSS_UNLOCK_THRESHOLDS = {
    1: 17, 2: 17, 3: 17, 4: 17, 5: 17, 6: 5,
}

ITEM_NAMES = {
    ITEM_WORLD2: "World 2 Access",
    ITEM_WORLD3: "World 3 Access",
    ITEM_WORLD4: "World 4 Access",
    ITEM_WORLD5: "World 5 Access",
    ITEM_WORLD6: "World 6 Access",
    ITEM_WORLD7: "World 7 Access",
    ITEM_BANDAGE: "Bandage",
    ITEM_1UP: "1-Up",
    **{iid: BOSS_TOKEN_NAMES[w] for iid, w in BOSS_TOKEN_IDS.items()},
    **{iid: name for iid, (bit, name) in CHARACTER_ITEMS.items()},
    **{iid: DARK_ACCESS_NAMES[w] for iid, w in DARK_ACCESS_IDS.items()},
}

# Warp zone milestone achievement location IDs
WARP_MILESTONE_LOCS = {
    1:  BASE_ID + 933,  # Nostalgia
    5:  BASE_ID + 934,  # Living in the Past
    10: BASE_ID + 935,  # Old School
    20: BASE_ID + 936,  # Retro Rampage
}
WARP_MILESTONE_NAMES = {
    1: "Nostalgia", 5: "Living in the Past",
    10: "Old School", 20: "Retro Rampage",
}

# Per-world light A+ achievement location IDs
WORLD_APLUS_LOCS = {
    1: BASE_ID + 937,  # Rare
    2: BASE_ID + 938,  # Medium Rare
    3: BASE_ID + 939,  # Medium
    4: BASE_ID + 940,  # Medium Well
    5: BASE_ID + 941,  # Well Done
}
WORLD_APLUS_NAMES = {
    1: "Rare", 2: "Medium Rare", 3: "Medium",
    4: "Medium Well", 5: "Well Done",
}


# =============================================================================
# BANDAGE DATA â€” using corrected SMBDatabase.cs data
# =============================================================================

BANDAGE_DATA = CORRECTED_BANDAGE_DATA
BANDAGE_BY_ADDR = CORRECTED_BANDAGE_BY_ADDR

# Bandage grant targets (ordered list for granting received bandages)
# These are levels WITHOUT bandages â€” safe to set bit 0 on to increase count
BANDAGE_GRANT_TARGETS = []
for w in range(1, 6):
    light_has = set(lv - 1 for lv in LIGHT_BANDAGE_LEVELS.get(w, []))
    for li in range(20):
        if li not in light_has:
            BANDAGE_GRANT_TARGETS.append((w, li, "light"))
for w in range(1, 6):
    dark_has = set(lv - 1 for lv in DARK_BANDAGE_LEVELS.get(w, []))
    for li in range(20):
        if li not in dark_has:
            BANDAGE_GRANT_TARGETS.append((w, li, "dark"))


# HELPER FUNCTIONS

def type_to_region(lvl_type):
    if lvl_type == TYPE_LIGHT:
        return "light"
    elif lvl_type == TYPE_DARK:
        return "dark"
    elif TYPE_WARP_MIN <= lvl_type <= TYPE_WARP_MAX:
        return "warp"
    return None


def is_warp(t):
    return t is not None and TYPE_WARP_MIN <= t <= TYPE_WARP_MAX


def get_level_display_name(world, level, lvl_type):
    ln = level + 1
    region = type_to_region(lvl_type)
    name = get_level_name(world, level, region) if region else None

    if is_warp(lvl_type):
        wname = get_warp_zone_name(world, level) if level >= 0 else "?"
        sub = (level % 3) + 1 if level >= 0 else "?"
        return f"{wname} {sub}" if wname else f"{world}-? Warp Sub {ln}"
    if lvl_type == TYPE_DARK:
        return f"{world}-{ln}X {name}" if name else f"{world}-{ln}X"
    if level == BOSS_LEVEL_INDEX:
        return f"Boss - {WORLD_NAMES.get(world, f'W{world}')}"
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
        try:
            return self.pm.read_uchar(self.base + a)
        except:
            return -1

    def rp(self, b, o):
        try:
            p = self.pm.read_uint(self.base + b)
            return self.pm.read_uchar(p + o) if p else -1
        except:
            return -1

    def rpi(self, b, o):
        try:
            p = self.pm.read_uint(self.base + b)
            return self.pm.read_int(p + o) if p else -1
        except:
            return -1

    def get_sp(self):
        try:
            return self.pm.read_uint(self.base + ADDR["save_ptr"])
        except:
            return 0

    def read_comp(self, sp, world, index, region):
        ca = comp_addr(world, index, region)
        if ca is None or sp == 0:
            return -1
        try:
            return self.pm.read_uchar(sp + ca)
        except:
            return -1

    def write_comp(self, sp, world, index, region, value):
        ca = comp_addr(world, index, region)
        if ca is None or sp == 0:
            return
        try:
            self.pm.write_uchar(sp + ca, value)
        except:
            pass

    def read_time(self, sp, world, level_index, region):
        """Read IL best time (float) from save slot."""
        ta = time_addr(world, level_index, region)
        if ta is None or sp == 0:
            return -1.0
        try:
            return self.pm.read_float(sp + ta)
        except:
            return -1.0

    def write_time(self, sp, world, level_index, region, value):
        """Write IL best time (float) to save slot."""
        ta = time_addr(world, level_index, region)
        if ta is None or sp == 0:
            return
        try:
            self.pm.write_float(sp + ta, value)
        except:
            pass

    def read_warp_slots(self, sp, world):
        """Read completion bytes for all 12 warp slots."""
        wb = WORLD_BASES.get(world)
        if wb is None or sp == 0:
            return [-1] * NUM_WARP_SLOTS
        vals = []
        for i in range(NUM_WARP_SLOTS):
            ca = wb + WARP_OFFSET + i * SLOT_SIZE + COMP_BYTE
            try:
                vals.append(self.pm.read_uchar(sp + ca))
            except:
                vals.append(-1)
        return vals

    def read_warp_slots_full(self, sp, world):
        """Read all 12 warp slot (comp, time) tuples."""
        wb = WORLD_BASES.get(world)
        if wb is None or sp == 0:
            return [(-1, -1.0)] * NUM_WARP_SLOTS
        result = []
        for i in range(NUM_WARP_SLOTS):
            base_off = wb + WARP_OFFSET + i * SLOT_SIZE
            try:
                comp = self.pm.read_uchar(sp + base_off + COMP_BYTE)
                tval = self.pm.read_float(sp + base_off + TIME_BYTE)
                result.append((comp, tval))
            except:
                result.append((-1, -1.0))
        return result

    def set_world_unlock(self, sp, bitmask):
        try:
            self.pm.write_uchar(sp + ADDR["world_unlock"], bitmask)
        except:
            pass

    def get_world_unlock(self, sp):
        try:
            return self.pm.read_uchar(sp + ADDR["world_unlock"])
        except:
            return 0

    def get_char_bitmask(self, sp):
        try:
            return self.pm.read_uint(sp + CHARACTER_BITMASK_OFFSET)
        except:
            return 0

    def set_char_bitmask(self, sp, bitmask):
        try:
            self.pm.write_uint(sp + CHARACTER_BITMASK_OFFSET, bitmask)
        except:
            pass

    def read_boss_counter(self, sp, world):
        """Read the boss completion counter for a world."""
        offset = BOSS_COUNTER_OFFSETS.get(world)
        if offset is None or sp == 0:
            return -1
        try:
            return self.pm.read_uchar(sp + offset)
        except:
            return -1

    def write_boss_counter(self, sp, world, value):
        """Write the boss completion counter for a world."""
        offset = BOSS_COUNTER_OFFSETS.get(world)
        if offset is None or sp == 0:
            return
        try:
            self.pm.write_uchar(sp + offset, min(value, 255))
        except:
            pass

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


# AP NETWORK CLIENT

class APClient:
    """Core Archipelago client logic with game memory integration."""

    def __init__(self, log_callback, status_callback):
        self.log = log_callback
        self.set_status = status_callback

        self.server: str = ""
        self.slot: str = ""
        self.password: str = ""

        self.ws = None
        self.connected: bool = False
        self.slot_info: Dict = {}
        self.slot_data: Dict = {}
        self.team: int = 0
        self.players: Dict[int, str] = {}

        self.locations_checked: Set[int] = set()
        self.items_received: List[Dict] = []
        self.items_processed: int = 0

        # ID to name mappings from DataPackage
        self.all_items: Dict[int, str] = {}
        self.all_locations: Dict[int, str] = {}

        # Game state
        self.allowed_worlds: Set[int] = {1}
        self.bandage_count: int = 0
        self.character_bits: int = CHARACTER_BASE_BITS  # Start with Meat Boy + menu
        self.goal_completed: bool = False
        self.aplus_logged: Set[int] = set()  # Track A+ grades we've already logged
        self.boss_token_count: int = 0
        self.boss_token_counts: Dict[int, int] = {w: 0 for w in range(1, 7)}
        self.boss_unlocked: Set[int] = set()  # Worlds with boss unlocked via tokens
        self.dark_lock_enabled: bool = False
        self.dark_unlocks_per_world: int = 4
        self.dark_access_counts: Dict[int, int] = {w: 0 for w in range(1, 6)}
        self.real_best_times: Dict = {}  # (world, level_index) -> actual time
        self.fake_aplus_times: Set[Tuple[int, int]] = set()  # (world, level_index) with grant-only sub-par times

        self._running = False
        self.loop = None

    def get_item_name(self, item_id: int) -> str:
        if item_id in self.all_items:
            return self.all_items[item_id]
        if item_id in ITEM_NAMES:
            return ITEM_NAMES[item_id]
        return f"Unknown Item {item_id}"

    def get_location_name_by_id(self, loc_id: int) -> str:
        if loc_id in self.all_locations:
            return self.all_locations[loc_id]
        return get_location_name(loc_id)

    def get_player_name(self, player_id: int) -> str:
        return self.players.get(player_id, f"Player {player_id}")

    async def send_message(self, msg: dict):
        if self.ws:
            await self.ws.send(json.dumps([msg]))

    async def handle_message(self, msg: dict):
        cmd = msg.get("cmd", "")

        if cmd == "RoomInfo":
            self.log("Connected to room, requesting data...", "info")
            games = msg.get("games", [])
            await self.send_message({
                "cmd": "GetDataPackage",
                "games": games
            })
            await self.send_connect()

        elif cmd == "DataPackage":
            data = msg.get("data", {}).get("games", {})
            for game_name, game_data in data.items():
                items = game_data.get("item_name_to_id", {})
                locations = game_data.get("location_name_to_id", {})
                for name, id in items.items():
                    self.all_items[id] = name
                for name, id in locations.items():
                    self.all_locations[id] = name
            self.log(f"Loaded data for {len(data)} game(s)", "info")

        elif cmd == "Connected":
            self.connected = True
            self.team = msg.get("team", 0)
            self.slot_info = msg.get("slot_info", {})
            self.slot_data = msg.get("slot_data", {})
            checked = msg.get("checked_locations", [])
            self.locations_checked = set(checked)

            for player in msg.get("players", []):
                self.players[player["slot"]] = player["name"]

            slot_num = msg.get("slot", 0)
            self.log(f"Connected as {self.slot} (Slot {slot_num})", "success")
            self.log(f"  Players: {', '.join(self.players.values())}", "info")
            self.log(f"  Already checked: {len(self.locations_checked)} locations", "info")

            # Log slot data
            goal = self.slot_data.get("goal", 0)
            goal_names = {
                0: "Beat Rapture Boss", 1: "Beat All Bosses",
                2: "Beat Dr. Fetus", 3: "Beat Dark Dr. Fetus",
            }
            self.log(f"  Goal: {goal_names.get(goal, f'Unknown({goal})')}", "info")
            if self.slot_data.get("dark_world_levels"):
                self.log("  Dark World Levels: ENABLED", "info")
            if self.slot_data.get("aplus_locations"):
                self.log("  A+ Locations: ENABLED", "info")
            if self.slot_data.get("w7_locations"):
                self.log("  Cotton Alley: ENABLED", "info")
            if self.slot_data.get("character_warp_locations", False):
                self.log("  Character Warp Locations: ENABLED", "info")
            if self.slot_data.get("warp_completion_locations", False):
                self.log("  Warp Completion Locations: ENABLED", "info")
            if self.slot_data.get("achievement_locations", False):
                self.log("  Achievement Locations: ENABLED", "info")
            bandages_req = self.slot_data.get("bandages_required", 0)
            if bandages_req > 0:
                self.log(f"  Bandages Required: {bandages_req}", "info")
            boss_mode = self.slot_data.get("boss_token_mode", "vanilla")
            if boss_mode == "tokens":
                costs = {w: self.slot_data.get(f"boss_tokens_w{w}", 0) for w in range(1, 7)}
                total = sum(costs.values())
                self.log(f"  Boss Tokens: ENABLED ({total} total)", "info")
                per_world = ", ".join(f"{BOSS_TOKEN_NAMES[w]}={costs[w]}" for w in range(1, 7) if costs[w] > 0)
                self.log(f"    {per_world}", "info")
            if self.slot_data.get("require_all_bosses", False):
                self.log("  Require All Bosses: W1-W5 bosses needed for The End", "info")

            self.set_status("Connected", "#00ff00")

        elif cmd == "ReceivedItems":
            start_index = msg.get("index", 0)
            if start_index == 0:
                self.items_received = []
                self.items_processed = 0

            for item in msg.get("items", []):
                item_id = item["item"]
                sender = self.players.get(item["player"], "Server")
                item_name = self.get_item_name(item_id)
                self.items_received.append({
                    "id": item_id,
                    "name": item_name,
                    "sender": sender,
                })
                self.log(f"Received: {item_name} from {sender}", "item")

        elif cmd == "PrintJSON":
            text_parts = []
            for part in msg.get("data", []):
                if isinstance(part, dict):
                    part_type = part.get("type")
                    part_text = part.get("text", "")

                    if part_type == "player_id":
                        try:
                            text_parts.append(self.get_player_name(int(part_text)))
                        except ValueError:
                            text_parts.append(part_text)
                    elif part_type == "item_id":
                        try:
                            text_parts.append(self.get_item_name(int(part_text)))
                        except ValueError:
                            text_parts.append(part_text)
                    elif part_type == "location_id":
                        try:
                            text_parts.append(self.get_location_name_by_id(int(part_text)))
                        except ValueError:
                            text_parts.append(part_text)
                    else:
                        text_parts.append(part_text)
                else:
                    text_parts.append(str(part))

            text = "".join(text_parts)
            if text:
                self.log(f"[Server] {text}", "server")

        elif cmd == "ConnectionRefused":
            errors = msg.get("errors", ["Unknown error"])
            self.log(f"Connection refused: {', '.join(errors)}", "error")
            self.set_status("Refused", "#ff4444")

    async def send_connect(self):
        import uuid
        msg = {
            "cmd": "Connect",
            "game": GAME_NAME,
            "name": self.slot,
            "uuid": str(uuid.uuid4()),
            "version": {"major": 0, "minor": 5, "build": 1, "class": "Version"},
            "items_handling": 0b111,
            "tags": [],
            "password": self.password,
            "slot_data": True,
        }
        await self.send_message(msg)

    async def send_location_checks(self, locations: List[int]):
        if not self.connected or not locations:
            return

        new_locs = [loc for loc in locations if loc not in self.locations_checked]
        if not new_locs:
            return

        self.locations_checked.update(new_locs)
        await self.send_message({"cmd": "LocationChecks", "locations": new_locs})

        for loc in new_locs:
            loc_name = self.get_location_name_by_id(loc)
            self.log(f"Checked: {loc_name}", "location")

    async def send_goal_complete(self):
        if not self.goal_completed:
            self.goal_completed = True
            await self.send_message({"cmd": "StatusUpdate", "status": 30})
            self.log("GOAL COMPLETE!", "success")
            self.log("Congratulations! You can disconnect or keep playing.", "info")

    def get_new_items(self) -> List[Dict]:
        """Get items that haven't been processed yet."""
        new = self.items_received[self.items_processed:]
        self.items_processed = len(self.items_received)
        return new

    # =========================================================================
    # BOSS TOKEN HELPERS
    # =========================================================================

    def _update_boss_tokens(self, game, sp, boss_token_costs):
        """Check if any new bosses should unlock based on per-world token counts.

        Each boss requires N of its own world's token type.
        Returns list of newly unlocked world numbers.
        """
        newly_unlocked = []
        for w, needed in boss_token_costs.items():
            if needed <= 0 or w in self.boss_unlocked:
                continue
            if self.boss_token_counts.get(w, 0) >= needed:
                self.boss_unlocked.add(w)
                threshold = BOSS_UNLOCK_THRESHOLDS[w]
                game.write_boss_counter(sp, w, threshold)
                newly_unlocked.append(w)
        return newly_unlocked

    def _enforce_boss_counters(self, game, sp, boss_token_costs=None):
        """Enforce boss counter values for all token-gated worlds.

        - Unlocked bosses: ensure counter stays at/above threshold
          (game resets it to real completion count on level beat).
        - Locked bosses: suppress counter to 0 so normal level
          completions can't bypass the token requirement.
        """
        # Re-raise unlocked boss counters
        for w in self.boss_unlocked:
            threshold = BOSS_UNLOCK_THRESHOLDS.get(w)
            if threshold is not None:
                current = game.read_boss_counter(sp, w)
                if 0 <= current < threshold:
                    game.write_boss_counter(sp, w, threshold)

        # Suppress locked boss counters
        if boss_token_costs:
            for w in boss_token_costs:
                if w not in self.boss_unlocked:
                    current = game.read_boss_counter(sp, w)
                    if current > 0:
                        game.write_boss_counter(sp, w, 0)

    def _dark_level_unlocked(self, world, level_index):
        """Check if a dark level is unlocked based on progressive item count."""
        if not self.dark_lock_enabled:
            return True
        if world < 1 or world > 5:
            return True
        levels_per_item = 20 // self.dark_unlocks_per_world
        needed = (level_index // levels_per_item) + 1
        return self.dark_access_counts.get(world, 0) >= needed

    def _enforce_dark_locks(self, game, sp):
        """Suppress A+ times on light levels whose dark counterpart is locked.

        The game unlocks dark versions when light best time <= par.
        Write par + 1.0s to keep dark locked until AP sends the unlock item.
        """
        if not self.dark_lock_enabled:
            return
        for w in range(1, 6):
            for li in range(20):
                if self._dark_level_unlocked(w, li):
                    # Restore real time if we have it and level is now unlocked
                    real = self.real_best_times.get((w, li))
                    par = get_par_time(w, li, "light")
                    if real is not None and par is not None and real <= par:
                        current = game.read_time(sp, w, li, "light")
                        if current > par:
                            game.write_time(sp, w, li, "light", real)
                    # If level has a fake grant time and player replayed,
                    # the game wrote a new real time — clear the fake flag
                    if (w, li) in self.fake_aplus_times and par is not None:
                        current = game.read_time(sp, w, li, "light")
                        fake_val = par - 0.001
                        if abs(current - fake_val) > 0.0005:
                            self.fake_aplus_times.discard((w, li))
                    continue
                par = get_par_time(w, li, "light")
                if par is None:
                    continue
                t = game.read_time(sp, w, li, "light")
                if t > 0 and t <= par:
                    self.real_best_times[(w, li)] = t
                    game.write_time(sp, w, li, "light", par + DARK_LOCK_TIME_PENALTY)

    def _grant_dark_access(self, game, sp, world):
        """Apply a dark access item for a world — restore times for newly unlocked levels."""
        for li in range(20):
            if not self._dark_level_unlocked(world, li):
                continue
            real = self.real_best_times.get((world, li))
            par = get_par_time(world, li, "light")
            if par is None:
                continue
            if real is not None and real > 0 and real <= par:
                game.write_time(sp, world, li, "light", real)
                self.fake_aplus_times.discard((world, li))
            else:
                # Player hasn't gotten A+ yet — write fake sub-par time
                # to unlock dark level visually, but mark as fake
                comp = game.read_comp(sp, world, li, "light")
                if comp >= 0 and (comp & FLAG_COMPLETE):
                    current_t = game.read_time(sp, world, li, "light")
                    if current_t > par:
                        game.write_time(sp, world, li, "light", par - 0.001)
                        self.fake_aplus_times.add((world, li))

    # =========================================================================
    # DETECTION HELPERS
    # =========================================================================

    def _check_aplus(self, game, sp, world, level_index, region, checks,
                     aplus_enabled):
        """Check if a level now qualifies for A+ and add to checks if new.
        
        Always logs A+ achievements regardless of aplus_enabled.
        Only sends AP location checks when aplus_enabled is True.
        """
        comp = game.read_comp(sp, world, level_index, region)
        if comp < 0 or not (comp & FLAG_COMPLETE):
            return
        time_val = game.read_time(sp, world, level_index, region)
        par = get_par_time(world, level_index, region)
        if time_val <= 0:
            self.log(f"DEBUG A+: W{world} L{level_index} {region} "
                     f"time={time_val} (not written yet?)", "debug")
            return
        if par is None:
            self.log(f"DEBUG A+: W{world} L{level_index} {region} "
                     f"no par time!", "debug")
            return
        # If dark lock suppressed this time, use the real best time instead
        if (self.dark_lock_enabled and region == "light"
                and 1 <= world <= 5 and time_val > par):
            real = self.real_best_times.get((world, level_index))
            if real is not None and real > 0 and real <= par:
                time_val = real
        # Skip fake sub-par times written by _grant_dark_access
        if (world, level_index) in self.fake_aplus_times and region == "light":
            return
        if time_val > par:
            return
        # Always log A+ grade
        name = get_level_name(world, level_index, region) or "?"
        suffix = "X" if region == "dark" else ""
        aplus_id = get_aplus_location_id(world, level_index, region)
        if aplus_id and aplus_id not in self.locations_checked and aplus_id not in self.aplus_logged:
            self.aplus_logged.add(aplus_id)
            self.log(f"A+ {world}-{level_index+1}{suffix} {name} "
                     f"({time_val:.3f}s <= {par:.3f}s)", "location")
            if aplus_enabled:
                checks.append(aplus_id)
            else:
                self.log(f"DEBUG A+: detected but aplus_enabled=False", "debug")

    def _aplus_sweep(self, game, sp, world, aplus_enabled,
                     dark_world_enabled, w7_enabled):
        """Sweep all levels in a world for unchecked A+ grades and completions.

        During mid-play auto-transitions the game may not flush the best
        time to save data before our handler reads it.  This sweep runs
        when the player returns to level select (save fully flushed) and
        catches any A+ grades that were missed.

        Also catches completions that may have been missed for similar
        timing reasons.
        """
        checks = []
        num_lv = NUM_LEVELS.get(world, 20)

        for region in ("light", "dark"):
            # Skip regions that aren't enabled
            if region == "dark":
                if world <= 5 and not dark_world_enabled:
                    continue
                if world == 6 and not dark_world_enabled:
                    continue
                if world == 7 and not w7_enabled:
                    continue
            if region == "light":
                if world == 7 and not w7_enabled:
                    continue

            for li in range(num_lv):
                comp = game.read_comp(sp, world, li, region)
                if comp < 0 or not (comp & FLAG_COMPLETE):
                    continue

                # Check completion location
                loc_id = get_completion_location_id(world, li, region)
                if loc_id and loc_id not in self.locations_checked:
                    checks.append(loc_id)

                # Check A+
                if aplus_enabled:
                    time_val = game.read_time(sp, world, li, region)
                    if time_val <= 0:
                        continue
                    par = get_par_time(world, li, region)
                    if par is None:
                        continue
                    # If dark lock suppressed this time, use real best time
                    if (self.dark_lock_enabled and region == "light"
                            and 1 <= world <= 5 and time_val > par):
                        real = self.real_best_times.get((world, li))
                        if real is not None and real > 0 and real <= par:
                            time_val = real
                    # Skip fake sub-par times written by _grant_dark_access
                    if (world, li) in self.fake_aplus_times and region == "light":
                        continue
                    if time_val > par:
                        continue
                    aplus_id = get_aplus_location_id(world, li, region)
                    if aplus_id and aplus_id not in self.locations_checked and aplus_id not in self.aplus_logged:
                        self.aplus_logged.add(aplus_id)
                        name = get_level_name(world, li, region) or "?"
                        suffix = "X" if region == "dark" else ""
                        self.log(f"A+ {world}-{li+1}{suffix} {name} "
                                 f"({time_val:.3f}s <= {par:.3f}s) [sweep]", "location")
                        checks.append(aplus_id)

        return checks

    def _check_gotwarp(self, ev, cv, world, level_index, region, checks):
        """Log if GotWarp bit (0x08) was newly set on a host level."""
        if ev < 0 or cv < 0:
            return
        if not (ev & FLAG_WARP) and (cv & FLAG_WARP):
            lv_1idx = level_index + 1
            host_key = (world, lv_1idx, region)
            zone_idx = WARP_HOST_TO_ZONE.get(host_key)
            if zone_idx is not None:
                wname = WARP_ZONE_NAMES.get((world, zone_idx), "?")
                suffix = "X" if region == "dark" else ""
                self.log(f"Warp Found: {wname} (from {world}-{lv_1idx}{suffix})", "game")

    def _check_character_unlock(self, game, sp, world, checks,
                                char_warp_enabled, characters_unlocked):
        """Check if all 3 character warp sub-levels are complete."""
        if not char_warp_enabled or world not in CHARACTER_WARPS:
            return
        if world in characters_unlocked:
            return
        for slot_idx in CHARACTER_WARP_SLOTS:  # 3, 4, 5
            comp = game.read_comp(sp, world, slot_idx, "warp")
            if comp < 0 or not (comp & FLAG_COMPLETE):
                return
        characters_unlocked.add(world)
        char_id = character_unlock_location_id(world)
        if char_id not in self.locations_checked:
            char_name = CHARACTER_WARPS[world][0]
            checks.append(char_id)
            self.log(f"Character Unlocked: {char_name}!", "success")

    def _check_warp_completion(self, game, sp, world, checks,
                               warp_complete_enabled, warps_completed):
        """Check if any warp zone (3 sub-levels) is fully complete."""
        if not warp_complete_enabled or world > 5:
            return
        for zone_idx in range(4):
            if (world, zone_idx) in warps_completed:
                continue
            all_done = True
            for sub in range(3):
                slot_idx = zone_idx * 3 + sub
                comp = game.read_comp(sp, world, slot_idx, "warp")
                if comp < 0 or not (comp & FLAG_COMPLETE):
                    all_done = False
                    break
            if all_done:
                warps_completed.add((world, zone_idx))
                wc_id = warp_completion_location_id(world, zone_idx)
                if wc_id not in self.locations_checked:
                    wname = WARP_ZONE_NAMES.get((world, zone_idx), f"Zone {zone_idx}")
                    checks.append(wc_id)
                    self.log(f"Warp Complete: {wname}", "location")

    def _check_achievements(self, game, sp, checks,
                            achievements_enabled, worlds_cleared, worlds_dark_cleared,
                            milestones_sent, aplus_enabled,
                            warps_completed=None, warp_milestones_sent=None,
                            world_aplus_sent=None):
        """Check for world clears, bandage milestones, warp milestones,
        per-world A+, and meta-achievements."""
        if not achievements_enabled:
            return

        # World clear checks
        for w in range(1, 8):
            num_lv = NUM_LEVELS.get(w, 20)

            if w not in worlds_cleared:
                all_light = True
                for li in range(num_lv):
                    comp = game.read_comp(sp, w, li, "light")
                    if comp < 0 or not (comp & FLAG_COMPLETE):
                        all_light = False
                        break
                if all_light:
                    worlds_cleared.add(w)
                    if w <= 5:
                        cid = world_clear_location_id(w)
                    elif w == 6:
                        cid = w6_clear_location_id()
                    else:
                        cid = w7_clear_location_id()
                    if cid not in self.locations_checked:
                        checks.append(cid)
                        self.log(f"World Clear: {WORLD_NAMES.get(w, f'W{w}')}!", "success")

            if w not in worlds_dark_cleared:
                all_dark = True
                for li in range(num_lv):
                    comp = game.read_comp(sp, w, li, "dark")
                    if comp < 0 or not (comp & FLAG_COMPLETE):
                        all_dark = False
                        break
                if all_dark:
                    worlds_dark_cleared.add(w)
                    if w <= 5:
                        cid = world_dark_clear_location_id(w)
                    elif w == 6:
                        cid = w6_dark_clear_location_id()
                    else:
                        cid = w7_dark_clear_location_id()
                    if cid not in self.locations_checked:
                        checks.append(cid)
                        self.log(f"Dark Clear: {WORLD_NAMES.get(w, f'W{w}')}!", "success")

        # Bandage milestones
        for milestone in BANDAGE_MILESTONES:
            if milestone in milestones_sent:
                continue
            if self.bandage_count >= milestone:
                milestones_sent.add(milestone)
                mid = bandage_milestone_location_id(milestone)
                if mid not in self.locations_checked:
                    checks.append(mid)
                    self.log(f"Bandage Milestone: {milestone}!", "success")

        # Warp zone milestones (Nostalgia, Living in the Past, etc.)
        if warp_milestones_sent is not None:
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

            for threshold, loc_id in WARP_MILESTONE_LOCS.items():
                if threshold in warp_milestones_sent:
                    continue
                if total_warps_done >= threshold:
                    warp_milestones_sent.add(threshold)
                    if loc_id not in self.locations_checked:
                        name = WARP_MILESTONE_NAMES[threshold]
                        checks.append(loc_id)
                        self.log(f"Warp Milestone: {name} ({total_warps_done} warps)!", "success")

        # Per-world light A+ achievements (Rare, Medium Rare, etc.)
        if world_aplus_sent is not None and aplus_enabled:
            for w in range(1, 6):
                if w in world_aplus_sent:
                    continue
                loc_id = WORLD_APLUS_LOCS.get(w)
                if not loc_id or loc_id in self.locations_checked:
                    continue
                all_aplus = True
                for li in range(20):
                    comp = game.read_comp(sp, w, li, "light")
                    if comp < 0 or not (comp & FLAG_COMPLETE):
                        all_aplus = False
                        break
                    if (w, li) in self.fake_aplus_times:
                        all_aplus = False
                        break
                    tval = game.read_time(sp, w, li, "light")
                    if not is_a_plus(tval, w, li, "light"):
                        all_aplus = False
                        break
                if all_aplus:
                    world_aplus_sent.add(w)
                    checks.append(loc_id)
                    name = WORLD_APLUS_NAMES[w]
                    self.log(f"World A+: {name} ({WORLD_NAMES.get(w, f'W{w}')})!", "success")

        # Golden God (all light A+) - always check, only send if enabled
        gg_id = golden_god_location_id()
        if gg_id not in self.locations_checked and gg_id not in self.aplus_logged:
            all_aplus = True
            for w in range(1, 6):
                for li in range(20):
                    comp = game.read_comp(sp, w, li, "light")
                    if comp < 0 or not (comp & FLAG_COMPLETE):
                        all_aplus = False
                        break
                    if (w, li) in self.fake_aplus_times:
                        all_aplus = False
                        break
                    tval = game.read_time(sp, w, li, "light")
                    if not is_a_plus(tval, w, li, "light"):
                        all_aplus = False
                        break
                if not all_aplus:
                    break
            if all_aplus:
                self.aplus_logged.add(gg_id)
                self.log("THE GOLDEN GOD! All Light A+!", "success")
                if aplus_enabled:
                    checks.append(gg_id)

        # Girl Boy (all dark A+) - always check, only send if enabled
        gb_id = girl_boy_location_id()
        if gb_id not in self.locations_checked and gb_id not in self.aplus_logged:
            all_dark_aplus = True
            for w in range(1, 6):
                for li in range(20):
                    comp = game.read_comp(sp, w, li, "dark")
                    if comp < 0 or not (comp & FLAG_COMPLETE):
                        all_dark_aplus = False
                        break
                    tval = game.read_time(sp, w, li, "dark")
                    if not is_a_plus(tval, w, li, "dark"):
                        all_dark_aplus = False
                        break
                if not all_dark_aplus:
                    break
            if all_dark_aplus:
                self.aplus_logged.add(gb_id)
                self.log("GIRL BOY! All Dark A+!", "success")
                if aplus_enabled:
                    checks.append(gb_id)

    # =========================================================================
    # INITIAL SYNC SCAN
    # =========================================================================

    async def _initial_sync_scan(self, game, sp,
                                  aplus_enabled, w7_enabled, char_warp_enabled,
                                  warp_complete_enabled, achievements_enabled,
                                  dark_world_enabled,
                                  characters_unlocked, warps_completed,
                                  worlds_cleared, worlds_dark_cleared, milestones_sent,
                                  warp_milestones_sent=None, world_aplus_sent=None):
        """Scan save data on connection for pre-existing completions."""
        self.log("Scanning save data for pre-existing progress...", "info")
        precheck = []

        # Pre-existing level completions â€” ALL worlds
        comp_count = 0
        for w in range(1, 8):
            num_lv = NUM_LEVELS.get(w, 20)
            for region in ("light", "dark"):
                # Check enablement
                if region == "light":
                    if 1 <= w <= 6:
                        pass  # always enabled
                    elif w == 7 and not w7_enabled:
                        continue
                elif region == "dark":
                    if 1 <= w <= 6 and not dark_world_enabled:
                        continue
                    elif w == 7 and not w7_enabled:
                        continue

                for li in range(num_lv):
                    comp = game.read_comp(sp, w, li, region)
                    if comp >= 0 and (comp & FLAG_COMPLETE):
                        loc_id = get_completion_location_id(w, li, region)
                        if loc_id and loc_id not in self.locations_checked:
                            precheck.append(loc_id)
                            comp_count += 1
        if comp_count > 0:
            self.log(f"  Pre-existing completions: {comp_count}", "info")

        # Pre-existing bandages (collected before client was running)
        bandage_count = 0
        for w in range(1, 6):  # Only W1-W5 have bandages
            for region in ("light", "dark", "warp"):
                if region == "warp":
                    indices = range(12)
                else:
                    indices = range(20)
                for li in indices:
                    comp = game.read_comp(sp, w, li, region)
                    if comp >= 0 and (comp & FLAG_BANDAGE):
                        ca = comp_addr(w, li, region)
                        be = BANDAGE_BY_ADDR.get(ca)
                        if be and be["ap_id"] not in self.locations_checked:
                            precheck.append(be["ap_id"])
                            bandage_count += 1
                            # Revoke the bandage bit
                            game.write_comp(sp, w, li, region, comp & MASK_CLEAR_BANDAGE)
        if bandage_count > 0:
            self.log(f"  Pre-existing bandages: {bandage_count}", "info")

        # Pre-existing A+ grades (always scan & log, only send if enabled)
        aplus_count = 0
        for w in range(1, 8):
            num_lv = NUM_LEVELS.get(w, 20)
            for region in ("light", "dark"):
                for li in range(num_lv):
                    comp = game.read_comp(sp, w, li, region)
                    if comp >= 0 and (comp & FLAG_COMPLETE):
                        tval = game.read_time(sp, w, li, region)
                        # Skip fake sub-par times from _grant_dark_access
                        if (w, li) in self.fake_aplus_times and region == "light":
                            continue
                        if tval > 0 and is_a_plus(tval, w, li, region):
                            aplus_count += 1
                            if aplus_enabled:
                                aid = get_aplus_location_id(w, li, region)
                                if aid and aid not in self.locations_checked:
                                    precheck.append(aid)
            # Warps W1-W5 (sub-level checks, gated with aplus)
            if w <= 5:
                for si in range(12):
                    comp = game.read_comp(sp, w, si, "warp")
                    if comp >= 0 and (comp & FLAG_COMPLETE):
                        tval = game.read_time(sp, w, si, "warp")
                        if tval > 0 and is_a_plus(tval, w, si, "warp"):
                            aplus_count += 1
                            if aplus_enabled:
                                aid = get_aplus_location_id(w, si, "warp")
                                if aid and aid not in self.locations_checked:
                                    precheck.append(aid)
        if aplus_count > 0:
            self.log(f"  A+ grades found: {aplus_count}"
                     f"{'' if aplus_enabled else ' (tracking only, not sending)'}", "info")

        # Pre-existing character unlocks
        if char_warp_enabled:
            for w in range(1, 6):
                all_done = True
                for slot_idx in CHARACTER_WARP_SLOTS:
                    comp = game.read_comp(sp, w, slot_idx, "warp")
                    if comp < 0 or not (comp & FLAG_COMPLETE):
                        all_done = False
                        break
                if all_done:
                    characters_unlocked.add(w)
                    cid = character_unlock_location_id(w)
                    if cid not in self.locations_checked:
                        precheck.append(cid)
                        char_name = CHARACTER_WARPS[w][0]
                        self.log(f"  Pre-existing character: {char_name}", "info")

        # Pre-existing warp completions
        if warp_complete_enabled:
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
                        wid = warp_completion_location_id(w, zone_idx)
                        if wid not in self.locations_checked:
                            precheck.append(wid)

        # Pre-existing world clears & achievements
        if achievements_enabled:
            for w in range(1, 8):
                num_lv = NUM_LEVELS.get(w, 20)
                # Light
                all_light = all(
                    (game.read_comp(sp, w, li, "light") or 0) & FLAG_COMPLETE
                    for li in range(num_lv)
                )
                if all_light:
                    worlds_cleared.add(w)
                    if w <= 5:
                        cid = world_clear_location_id(w)
                    elif w == 6:
                        cid = w6_clear_location_id()
                    else:
                        cid = w7_clear_location_id()
                    if cid not in self.locations_checked:
                        precheck.append(cid)
                # Dark
                all_dark = all(
                    (game.read_comp(sp, w, li, "dark") or 0) & FLAG_COMPLETE
                    for li in range(num_lv)
                )
                if all_dark:
                    worlds_dark_cleared.add(w)
                    if w <= 5:
                        cid = world_dark_clear_location_id(w)
                    elif w == 6:
                        cid = w6_dark_clear_location_id()
                    else:
                        cid = w7_dark_clear_location_id()
                    if cid not in self.locations_checked:
                        precheck.append(cid)

            # Bandage milestones
            for milestone in BANDAGE_MILESTONES:
                if self.bandage_count >= milestone:
                    milestones_sent.add(milestone)
                    mid = bandage_milestone_location_id(milestone)
                    if mid not in self.locations_checked:
                        precheck.append(mid)

            # Warp zone milestones
            if warp_milestones_sent is not None:
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
                for threshold, loc_id in WARP_MILESTONE_LOCS.items():
                    if total_warps_done >= threshold:
                        warp_milestones_sent.add(threshold)
                        if loc_id not in self.locations_checked:
                            precheck.append(loc_id)
                if total_warps_done > 0:
                    self.log(f"  Warp zones completed: {total_warps_done}", "info")

            # Per-world light A+ achievements
            if world_aplus_sent is not None and aplus_enabled:
                for w in range(1, 6):
                    loc_id = WORLD_APLUS_LOCS.get(w)
                    if not loc_id or loc_id in self.locations_checked:
                        continue
                    all_ap = True
                    for li in range(20):
                        comp = game.read_comp(sp, w, li, "light")
                        if comp < 0 or not (comp & FLAG_COMPLETE):
                            all_ap = False
                            break
                        if (w, li) in self.fake_aplus_times:
                            all_ap = False
                            break
                        tval = game.read_time(sp, w, li, "light")
                        if not is_a_plus(tval, w, li, "light"):
                            all_ap = False
                            break
                    if all_ap:
                        world_aplus_sent.add(w)
                        precheck.append(loc_id)

        if precheck:
            await self.send_location_checks(precheck)
            self.log(f"Pre-existing progress: {len(precheck)} locations sent", "success")

    # =========================================================================
    # MAIN RUN + GAME MONITOR
    # =========================================================================

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
                            data = json.loads(message)
                            for msg in data:
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
        # --- State tracking ---
        last_playing = last_world = last_level = last_beaten = -1
        last_lvl_type = -1
        last_ui_state = -1
        entry_comp = {}             # key â†’ comp byte at level entry
        entry_times = {}            # key â†’ (comp, time) at level entry
        warp_entry_slots = {}       # world â†’ [12 comp bytes]
        warp_entry_full = {}        # world â†’ [(comp, time)] Ã— 12
        pending_boss_world = 0
        pending_boss_time = 0
        pending_boss_dark = False

        # New tracking state
        characters_unlocked: Set[int] = set()
        warps_completed: Set[Tuple[int, int]] = set()
        worlds_cleared: Set[int] = set()
        worlds_dark_cleared: Set[int] = set()
        milestones_sent: Set[int] = set()
        warp_milestones_sent: Set[int] = set()  # 1, 5, 10, 20
        world_aplus_sent: Set[int] = set()  # worlds with all-A+ achievement sent

        # Wait for connection
        self.log("Waiting for connection...", "info")
        for _ in range(50):
            if self.connected and self.slot_data:
                break
            await asyncio.sleep(0.1)

        if not self.connected:
            self.log("Connection failed, stopping monitor", "error")
            return

        # Read slot data options
        dark_world_enabled = self.slot_data.get("dark_world_levels", False)
        goal = self.slot_data.get("goal", 0)
        bandages_req = self.slot_data.get("bandages_required", 0)
        aplus_enabled = self.slot_data.get("aplus_locations", False)
        w7_enabled = self.slot_data.get("w7_locations", False)
        char_warp_enabled = self.slot_data.get("character_warp_locations", False)
        warp_complete_enabled = self.slot_data.get("warp_completion_locations", False)
        achievements_enabled = self.slot_data.get("achievement_locations", False)
        boss_token_mode = self.slot_data.get("boss_token_mode", "vanilla")
        boss_token_costs = {
            w: self.slot_data.get(f"boss_tokens_w{w}", 0) for w in range(1, 7)
        }
        boss_tokens_enabled = (boss_token_mode == "tokens")
        dark_lock_enabled = self.slot_data.get("dark_lock_mode", False)
        self.dark_lock_enabled = dark_lock_enabled
        self.dark_unlocks_per_world = self.slot_data.get("dark_unlocks_per_world", 4)

        self.log(f"Slot data: goal={goal}, dark={dark_world_enabled}, "
                 f"aplus={aplus_enabled}, w7={w7_enabled}, "
                 f"bandages_req={bandages_req}, "
                 f"boss_tokens={'ON' if boss_tokens_enabled else 'OFF'}, "
                 f"dark_lock={'ON' if dark_lock_enabled else 'OFF'}", "info")

        # Wait for initial items sync
        self.log("Waiting for item sync...", "info")
        for _ in range(20):
            await asyncio.sleep(0.1)
            new_items = self.get_new_items()
            for item in new_items:
                iid = item["id"]
                if iid in WORLD_ACCESS_ITEM_IDS:
                    self.allowed_worlds.add(WORLD_ACCESS_ITEM_IDS[iid])
                elif iid == ITEM_BANDAGE:
                    self.bandage_count += 1
                elif iid in CHARACTER_ITEMS:
                    bit, name = CHARACTER_ITEMS[iid]
                    self.character_bits |= (1 << bit)
                elif iid in BOSS_TOKEN_IDS:
                    w = BOSS_TOKEN_IDS[iid]
                    self.boss_token_counts[w] = self.boss_token_counts.get(w, 0) + 1
                    self.boss_token_count += 1
                elif iid in DARK_ACCESS_IDS:
                    w = DARK_ACCESS_IDS[iid]
                    self.dark_access_counts[w] = self.dark_access_counts.get(w, 0) + 1
            if new_items:
                break

        # Apply initial world unlock + bandages + characters
        bitmask = sum(1 << (w - 1) for w in self.allowed_worlds)
        sp = game.get_sp()
        if sp:
            game.set_world_unlock(sp, bitmask)
            game.set_char_bitmask(sp, self.character_bits)
            for i in range(self.bandage_count):
                if i < len(BANDAGE_GRANT_TARGETS):
                    gw, gi, gr = BANDAGE_GRANT_TARGETS[i]
                    val = game.read_comp(sp, gw, gi, gr)
                    if val >= 0:
                        game.write_comp(sp, gw, gi, gr, val | FLAG_BANDAGE)

            # Apply initial boss tokens
            if boss_tokens_enabled:
                newly = self._update_boss_tokens(game, sp, boss_token_costs)
                for w in newly:
                    self.log(f"Boss pre-unlocked: {WORLD_NAMES.get(w, f'W{w}')}", "game")

            # Apply initial dark lock enforcement
            if dark_lock_enabled:
                self._enforce_dark_locks(game, sp)
                for w in range(1, 6):
                    if self.dark_access_counts.get(w, 0) > 0:
                        self._grant_dark_access(game, sp, w)

        boss_str = ""
        if boss_tokens_enabled:
            token_parts = []
            for w in range(1, 7):
                have = self.boss_token_counts.get(w, 0)
                need = boss_token_costs.get(w, 0)
                if need > 0:
                    token_parts.append(f"W{w}:{have}/{need}")
            boss_str = f", Tokens [{', '.join(token_parts)}]"
        chars_unlocked = bin(self.character_bits).count('1') - 2  # minus Meat Boy + menu
        dark_str = ""
        if dark_lock_enabled:
            dark_parts = []
            for w in range(1, 6):
                have = self.dark_access_counts.get(w, 0)
                need = self.dark_unlocks_per_world
                levels_per = 20 // need
                unlocked = min(have * levels_per, 20)
                dark_parts.append(f"W{w}:{unlocked}/20")
            dark_str = f", Dark [{', '.join(dark_parts)}]"
        self.log(f"Synced: Worlds {sorted(self.allowed_worlds)}, "
                 f"Bandages {self.bandage_count}, "
                 f"Characters {chars_unlocked}{boss_str}{dark_str}", "success")

        # Initial sync scan for pre-existing progress
        if sp:
            await self._initial_sync_scan(
                game, sp, aplus_enabled, w7_enabled, char_warp_enabled,
                warp_complete_enabled, achievements_enabled, dark_world_enabled,
                characters_unlocked, warps_completed,
                worlds_cleared, worlds_dark_cleared, milestones_sent,
                warp_milestones_sent, world_aplus_sent,
            )

        self.log("Monitoring game...", "info")

        bosses_beaten = set()
        esc_cooldown = 0
        poll_count = 0

        while self._running and game.connected:
            poll_count += 1
            try:
                # --- Process new items ---
                new_items = self.get_new_items()
                for item in new_items:
                    iid = item["id"]
                    if iid in WORLD_ACCESS_ITEM_IDS:
                        w = WORLD_ACCESS_ITEM_IDS[iid]
                        if w not in self.allowed_worlds:
                            self.allowed_worlds.add(w)
                            bitmask = sum(1 << (ww - 1) for ww in self.allowed_worlds)
                            sp = game.get_sp()
                            if sp:
                                game.set_world_unlock(sp, bitmask)
                            self.log(f"Unlocked: {WORLD_NAMES.get(w, f'World {w}')}", "game")
                    elif iid == ITEM_BANDAGE:
                        self.bandage_count += 1
                        sp = game.get_sp()
                        if sp and self.bandage_count <= len(BANDAGE_GRANT_TARGETS):
                            gw, gi, gr = BANDAGE_GRANT_TARGETS[self.bandage_count - 1]
                            val = game.read_comp(sp, gw, gi, gr)
                            if val >= 0:
                                game.write_comp(sp, gw, gi, gr, val | FLAG_BANDAGE)
                        self.log(f"Granted: Bandage ({self.bandage_count} total)", "game")
                        # Check bandage milestones
                        if achievements_enabled:
                            ach_checks = []
                            for milestone in BANDAGE_MILESTONES:
                                if milestone not in milestones_sent and self.bandage_count >= milestone:
                                    milestones_sent.add(milestone)
                                    mid = bandage_milestone_location_id(milestone)
                                    if mid not in self.locations_checked:
                                        ach_checks.append(mid)
                                        self.log(f"Bandage Milestone: {milestone}!", "success")
                            if ach_checks:
                                await self.send_location_checks(ach_checks)
                    elif iid in CHARACTER_ITEMS:
                        bit, name = CHARACTER_ITEMS[iid]
                        self.character_bits |= (1 << bit)
                        sp = game.get_sp()
                        if sp:
                            game.set_char_bitmask(sp, self.character_bits)
                        self.log(f"Unlocked: {name}", "game")
                    elif iid in BOSS_TOKEN_IDS:
                        token_world = BOSS_TOKEN_IDS[iid]
                        self.boss_token_counts[token_world] = self.boss_token_counts.get(token_world, 0) + 1
                        self.boss_token_count += 1
                        token_name = BOSS_TOKEN_NAMES[token_world]
                        if boss_tokens_enabled:
                            sp = game.get_sp()
                            if sp:
                                newly = self._update_boss_tokens(game, sp, boss_token_costs)
                                for w in newly:
                                    self.log(f"Boss Unlocked: {WORLD_NAMES.get(w, f'W{w}')}!", "success")
                            needed = boss_token_costs.get(token_world, 0)
                            have = self.boss_token_counts.get(token_world, 0)
                            if token_world in self.boss_unlocked:
                                self.log(f"{token_name} ({have}/{needed} - boss unlocked!)", "item")
                            else:
                                self.log(f"{token_name} ({have}/{needed})", "item")
                        else:
                            self.log(f"{token_name}", "item")
                    elif iid in DARK_ACCESS_IDS:
                        dw = DARK_ACCESS_IDS[iid]
                        self.dark_access_counts[dw] = self.dark_access_counts.get(dw, 0) + 1
                        sp = game.get_sp()
                        if sp and dark_lock_enabled:
                            self._grant_dark_access(game, sp, dw)
                        count = self.dark_access_counts[dw]
                        levels_per = 20 // self.dark_unlocks_per_world
                        unlocked = min(count * levels_per, 20)
                        self.log(f"Dark Access: {DARK_ACCESS_NAMES[dw]} "
                                 f"({count}/{self.dark_unlocks_per_world}, "
                                 f"{unlocked}/20 levels)", "game")

                # --- Read game state ---
                try:
                    state = game.get_state()
                except Exception:
                    if self.goal_completed:
                        await asyncio.sleep(0.5)
                        continue
                    await asyncio.sleep(0.1)
                    continue

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

                # Debug boss state changes
                if level == 99 or last_level == 99:
                    if playing != last_playing or level != last_level:
                        self.log(f"DEBUG BOSS: playing={last_playing}->{playing} "
                                 f"level={last_level}->{level} world={world}", "debug")

                # Skip bad reads
                if playing < 0 or world < 0 or level < -1:
                    await asyncio.sleep(0.01)
                    last_playing, last_world, last_level = playing, world, level
                    last_beaten, last_lvl_type = beaten, lvl_type
                    continue

                actual_level = level if 0 <= level < 99 else -1
                in_warp = is_warp(lvl_type)
                last_in_warp = is_warp(last_lvl_type)
                sp = game.get_sp()

                # Debug: log any lvl_type change while playing
                if playing == 1 and lvl_type != last_lvl_type:
                    self.log(f"DEBUG lvl_type change: {last_lvl_type}->{lvl_type} "
                             f"W{world} L{level} in_warp={in_warp}", "debug")

                if not sp:
                    await asyncio.sleep(0.01)
                    last_playing, last_world, last_level = playing, world, level
                    last_beaten, last_lvl_type = beaten, lvl_type
                    continue

                # Detect warp entry from within a level (e.g., entering Space Boy
                # from dark level 1-13X).  The level index may not change, so the
                # mid-play handler won't fire â€” take the snapshot here instead.
                if playing == 1 and in_warp and world not in warp_entry_slots:
                    warp_entry_slots[world] = game.read_warp_slots(sp, world)
                    warp_entry_full[world] = game.read_warp_slots_full(sp, world)
                    slots = warp_entry_slots[world]
                    nonzero = [(i, v) for i, v in enumerate(slots) if v > 0]
                    self.log(f"DEBUG: Warp snapshot W{world} "
                             f"(lvl_type {last_lvl_type}->{lvl_type}) "
                             f"nonzero: {nonzero}", "debug")

                # --- World unlock + character bitmask enforcement ---
                on_world_select = (
                    (level == 99 and ui_state == 3 and trans == 0) or
                    (level == 0 and playing == 0)
                )
                if on_world_select:
                    bitmask = sum(1 << (w - 1) for w in self.allowed_worlds)
                    game.set_world_unlock(sp, bitmask)
                    # Enforce character bitmask (game recalculates from bandage counts)
                    game.set_char_bitmask(sp, self.character_bits)
                    # Enforce boss counters (game overwrites on level completion)
                    if boss_tokens_enabled:
                        self._enforce_boss_counters(game, sp, boss_token_costs)
                    if dark_lock_enabled:
                        self._enforce_dark_locks(game, sp)

                # A+ sweep on level select: runs on first arrival AND periodically
                on_level_select = (playing == 0 and ui_state == 1 and 1 <= world <= 7)
                if on_level_select and aplus_enabled:
                    # Run sweep on first arrival (last poll wasn't level select)
                    # or periodically every ~500 polls (~0.5 seconds)
                    just_arrived = (last_playing == 1 or last_ui_state != 1)
                    if just_arrived or poll_count % 500 == 499:
                        sweep_checks = self._aplus_sweep(
                            game, sp, world, aplus_enabled,
                            dark_world_enabled, w7_enabled,
                        )
                        if sweep_checks:
                            await self.send_location_checks(sweep_checks)

                if (playing == 0 and ui_state == 1 and 0 <= level <= 20
                        and world not in self.allowed_worlds and world > 0):
                    bitmask = sum(1 << (w - 1) for w in self.allowed_worlds)
                    game.set_world_unlock(sp, bitmask)
                    now = time.time()
                    if now - esc_cooldown > 0.3:
                        self.log(f"Unauthorized world {world} - kicking to world select", "game")
                        game.send_esc()
                        esc_cooldown = now

                # Enforce character bitmask + boss counters periodically (every ~64 polls)
                if poll_count & 0x3F == 0:
                    game.set_char_bitmask(sp, self.character_bits)
                    if boss_tokens_enabled:
                        self._enforce_boss_counters(game, sp, boss_token_costs)
                    if dark_lock_enabled:
                        self._enforce_dark_locks(game, sp)

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
                            if pending_boss_world == 6 and pending_boss_dark and dark_world_enabled:
                                loc_id = dark_boss_location_id()
                                boss_name = "Dr. Fetus (Dark)"
                            else:
                                loc_id = boss_location_id(pending_boss_world)
                                boss_name = WORLD_NAMES.get(pending_boss_world, '?')

                            if loc_id not in self.locations_checked:
                                await self.send_location_checks([loc_id])
                                if not pending_boss_dark:
                                    bosses_beaten.add(pending_boss_world)
                                self.log(f"Boss defeated: {boss_name}", "success")

                                # Goal checks
                                if pending_boss_dark:
                                    if goal == 3 and self.bandage_count >= bandages_req:
                                        await self.send_goal_complete()
                                    elif goal == 3:
                                        self.log(f"Goal not met: need {bandages_req} bandages, "
                                                 f"have {self.bandage_count}", "info")
                                else:
                                    if goal == 0 and pending_boss_world == 5:
                                        if self.bandage_count >= bandages_req:
                                            await self.send_goal_complete()
                                        else:
                                            self.log(f"Goal not met: need {bandages_req} bandages, "
                                                     f"have {self.bandage_count}", "info")
                                    elif goal == 1 and len(bosses_beaten) >= 5:
                                        if self.bandage_count >= bandages_req:
                                            await self.send_goal_complete()
                                        else:
                                            self.log(f"Goal not met: need {bandages_req} bandages, "
                                                     f"have {self.bandage_count}", "info")
                                    elif goal == 2 and pending_boss_world == 6:
                                        if self.bandage_count >= bandages_req:
                                            await self.send_goal_complete()
                                        else:
                                            self.log(f"Goal not met: need {bandages_req} bandages, "
                                                     f"have {self.bandage_count}", "info")
                            pending_boss_world = 0
                            pending_boss_dark = False

                            # Achievement check after boss (boss can affect world state)
                            if achievements_enabled:
                                ach_checks = []
                                self._check_achievements(
                                    game, sp, ach_checks,
                                    achievements_enabled, worlds_cleared,
                                    worlds_dark_cleared, milestones_sent,
                                    aplus_enabled, warps_completed,
                                    warp_milestones_sent, world_aplus_sent,
                                )
                                if ach_checks:
                                    await self.send_location_checks(ach_checks)

                            # Re-enforce boss counters after boss defeat
                            if boss_tokens_enabled:
                                self._enforce_boss_counters(game, sp, boss_token_costs)
                            if dark_lock_enabled:
                                self._enforce_dark_locks(game, sp)
                            pending_boss_world = 0
                            pending_boss_dark = False

                        elif time_since > 10.0:
                            pending_boss_world = 0
                            pending_boss_dark = False

                # --- Level entry snapshot ---
                if playing == 1 and last_playing != 1 and actual_level >= 0:
                    region = type_to_region(lvl_type)
                    if in_warp:
                        warp_entry_slots[world] = game.read_warp_slots(sp, world)
                        warp_entry_full[world] = game.read_warp_slots_full(sp, world)
                    elif region:
                        key = f"{world}_{actual_level}_{lvl_type}"
                        val = game.read_comp(sp, world, actual_level, region)
                        time_val = game.read_time(sp, world, actual_level, region)
                        entry_comp[key] = val
                        entry_times[key] = (val, time_val)

                # --- Beaten flag check (light world levels) ---
                if beaten == 1 and last_beaten == 0:
                    if lvl_type == TYPE_LIGHT and actual_level >= 0 and actual_level < 20:
                        if 1 <= world <= 5:
                            loc_id = level_location_id(world, actual_level)
                            if loc_id not in self.locations_checked:
                                await self.send_location_checks([loc_id])
                        elif world == 6 and actual_level < 5:
                            loc_id = w6_level_location_id(actual_level)
                            if loc_id not in self.locations_checked:
                                await self.send_location_checks([loc_id])
                        elif world == 7 and w7_enabled:
                            loc_id = w7_light_location_id(actual_level)
                            if loc_id not in self.locations_checked:
                                await self.send_location_checks([loc_id])

                # --- Mid-play level change ---
                if (playing == 1 and last_playing == 1 and actual_level >= 0
                        and (actual_level != last_level or world != last_world)
                        and last_level >= 0 and last_level < 99 and last_world > 0):
                    # Wait for save data to settle (game may still be writing)
                    await asyncio.sleep(0.05)
                    sp2 = game.get_sp()
                    if sp2:
                        # Warp mid-play: check via snapshot presence (independent
                        # of entry_comp â€” avoids lvl_type race condition)
                        if last_world in warp_entry_slots:
                            entry_slots = warp_entry_slots[last_world]
                            current_slots = game.read_warp_slots(sp2, last_world)
                            checks = []
                            for si in range(NUM_WARP_SLOTS):
                                sev = entry_slots[si]
                                scv = current_slots[si]
                                if sev < 0 or scv < 0 or sev == scv:
                                    continue
                                if not (sev & FLAG_BANDAGE) and (scv & FLAG_BANDAGE):
                                    ca = comp_addr(last_world, si, "warp")
                                    be = BANDAGE_BY_ADDR.get(ca)
                                    if be:
                                        checks.append(be["ap_id"])
                                        self.log(f"Bandage: {be['name']} (mid-play)", "location")
                                    game.write_comp(sp2, last_world, si, "warp",
                                                    scv & MASK_CLEAR_BANDAGE)
                            if checks:
                                await self.send_location_checks(checks)

                        else:
                            # Light/Dark mid-play
                            old_region = type_to_region(last_lvl_type)
                            old_key = f"{last_world}_{last_level}_{last_lvl_type}"
                            ev = entry_comp.get(old_key, -1)
                            checks = []

                            if old_region in ("light", "dark") and ev >= 0:
                                cv = game.read_comp(sp2, last_world, last_level, old_region)
                                if ev >= 0 and cv >= 0 and ev != cv:
                                    # Completion: bit 1 newly set
                                    if not (ev & FLAG_COMPLETE) and (cv & FLAG_COMPLETE):
                                        loc_id = get_completion_location_id(last_world, last_level, old_region)
                                        if loc_id:
                                            # Check region-specific enablement
                                            should_check = False
                                            if old_region == "light":
                                                should_check = (1 <= last_world <= 6) or (last_world == 7 and w7_enabled)
                                            elif old_region == "dark":
                                                should_check = dark_world_enabled or (last_world == 7 and w7_enabled)
                                            if should_check and loc_id not in self.locations_checked:
                                                checks.append(loc_id)

                                    # Bandage: bit 0 newly set
                                    if not (ev & FLAG_BANDAGE) and (cv & FLAG_BANDAGE):
                                        ca = comp_addr(last_world, last_level, old_region)
                                        be = BANDAGE_BY_ADDR.get(ca)
                                        if be:
                                            checks.append(be["ap_id"])
                                            self.log(f"Bandage: {be['name']} (mid-play)", "location")
                                        else:
                                            self.log(f"DEBUG: bandage bit set on W{last_world} L{last_level} "
                                                     f"{old_region} (addr 0x{ca:04X}) but no mapping!", "debug")
                                        game.write_comp(sp2, last_world, last_level, old_region,
                                                        cv & MASK_CLEAR_BANDAGE)

                                    # GotWarp bit
                                    self._check_gotwarp(ev, cv, last_world, last_level, old_region, checks)

                                elif ev >= 0 and cv >= 0 and ev == cv:
                                    self.log(f"DEBUG mid-play: no change W{last_world} L{last_level} "
                                             f"T{last_lvl_type} ev={ev} cv={cv}", "debug")

                            # A+ check runs regardless of entry snapshot
                            if old_region in ("light", "dark"):
                                self._check_aplus(game, sp2, last_world, last_level, old_region,
                                                  checks, aplus_enabled)

                            if checks:
                                await self.send_location_checks(checks)

                        # Snapshot the NEW level
                        new_region = type_to_region(lvl_type)
                        if in_warp:
                            warp_entry_slots[world] = game.read_warp_slots(sp2, world)
                            warp_entry_full[world] = game.read_warp_slots_full(sp2, world)
                        elif new_region:
                            new_key = f"{world}_{actual_level}_{lvl_type}"
                            new_val = game.read_comp(sp2, world, actual_level, new_region)
                            new_time = game.read_time(sp2, world, actual_level, new_region)
                            entry_comp[new_key] = new_val
                            entry_times[new_key] = (new_val, new_time)

                # --- Level exit ---
                if playing == 0 and last_playing == 1:
                    await asyncio.sleep(0.05)
                    sp2 = game.get_sp()

                    if sp2 and last_world > 0:
                        # Boss detection
                        if last_level == 99 and 1 <= last_world <= 7:
                            pending_boss_world = last_world
                            pending_boss_time = time.time()
                            pending_boss_dark = (last_world == 6 and last_lvl_type == TYPE_DARK)

                        exit_level = last_level if last_level < 99 else -1
                        exit_type = last_lvl_type
                        exit_region = type_to_region(exit_type)
                        # Use entry snapshot presence to detect warp exit â€” lvl_type
                        # can race back to 0 while playing is still 1, making
                        # is_warp(last_lvl_type) unreliable.
                        was_warp = last_world in warp_entry_slots

                        if was_warp:
                            # --- Warp exit ---
                            entry_slots = warp_entry_slots[last_world]
                            current_slots = game.read_warp_slots(sp2, last_world)
                            current_full = game.read_warp_slots_full(sp2, last_world)
                            entry_full = warp_entry_full.get(last_world, [(-1, -1.0)] * 12)
                            checks = []

                            # Debug: dump all changed slots
                            for si in range(NUM_WARP_SLOTS):
                                sev = entry_slots[si]
                                scv = current_slots[si]
                                if sev != scv:
                                    ca = comp_addr(last_world, si, "warp")
                                    be = BANDAGE_BY_ADDR.get(ca)
                                    be_name = be['name'] if be else 'NO MAPPING'
                                    self.log(f"DEBUG warp slot {si}: entry={sev} "
                                             f"current={scv} (comp={scv&2} band={scv&1}) "
                                             f"addr=0x{ca:04X} map={be_name}", "debug")
                                elif sev > 0:
                                    self.log(f"DEBUG warp slot {si}: unchanged={sev} "
                                             f"(comp={sev&2} band={sev&1})", "debug")

                            for si in range(NUM_WARP_SLOTS):
                                sev = entry_slots[si]
                                scv = current_slots[si]
                                if sev < 0 or scv < 0 or sev == scv:
                                    continue

                                # Bandage
                                if not (sev & FLAG_BANDAGE) and (scv & FLAG_BANDAGE):
                                    ca = comp_addr(last_world, si, "warp")
                                    be = BANDAGE_BY_ADDR.get(ca)
                                    if be:
                                        checks.append(be["ap_id"])
                                        self.log(f"Bandage: {be['name']}", "location")
                                    game.write_comp(sp2, last_world, si, "warp",
                                                    scv & MASK_CLEAR_BANDAGE)

                                # Warp sub-level completion
                                if not (sev & FLAG_COMPLETE) and (scv & FLAG_COMPLETE):
                                    zone_idx = si // 3
                                    sub = (si % 3) + 1
                                    wname = WARP_ZONE_NAMES.get((last_world, zone_idx), f"Zone {zone_idx}")
                                    self.log(f"Warp sub-level: {wname} {sub} complete", "game")

                            # Warp sub-level completion check (par-time based)
                            for si in range(NUM_WARP_SLOTS):
                                curr_comp, curr_time = current_full[si]
                                if curr_comp < 0 or not (curr_comp & FLAG_COMPLETE):
                                    continue
                                if curr_time <= 0:
                                    continue
                                par = get_par_time(last_world, si, "warp")
                                if par is None or curr_time > par:
                                    continue
                                old_comp, old_time = entry_full[si] if si < len(entry_full) else (-1, -1.0)
                                was_aplus = (old_time > 0 and par is not None and old_time <= par)
                                if not was_aplus:
                                    aplus_id = get_aplus_location_id(last_world, si, "warp")
                                    if aplus_id and aplus_id not in self.locations_checked and aplus_id not in self.aplus_logged:
                                        self.aplus_logged.add(aplus_id)
                                        zone_idx = si // 3
                                        sub = (si % 3) + 1
                                        wname = WARP_ZONE_NAMES.get((last_world, zone_idx), "?")
                                        self.log(f"{wname} {sub} "
                                                 f"({curr_time:.3f}s <= {par:.3f}s)", "location")
                                        if aplus_enabled:
                                            checks.append(aplus_id)

                            # Character unlock check
                            self._check_character_unlock(game, sp2, last_world, checks,
                                                         char_warp_enabled, characters_unlocked)

                            # Warp zone completion check
                            self._check_warp_completion(game, sp2, last_world, checks,
                                                        warp_complete_enabled, warps_completed)

                            if checks:
                                await self.send_location_checks(checks)

                            # Achievement check on every warp exit too
                            if achievements_enabled:
                                ach_checks = []
                                self._check_achievements(
                                    game, sp2, ach_checks,
                                    achievements_enabled, worlds_cleared,
                                    worlds_dark_cleared, milestones_sent,
                                    aplus_enabled, warps_completed,
                                    warp_milestones_sent, world_aplus_sent,
                                )
                                if ach_checks:
                                    await self.send_location_checks(ach_checks)

                            # Re-enforce boss counters after warp exit
                            if boss_tokens_enabled:
                                self._enforce_boss_counters(game, sp2, boss_token_costs)
                            if dark_lock_enabled:
                                self._enforce_dark_locks(game, sp2)
                            game.set_char_bitmask(sp2, self.character_bits)

                            # Clear warp snapshot so next non-warp exit
                            # in same world doesn't re-enter this path
                            del warp_entry_slots[last_world]
                            warp_entry_full.pop(last_world, None)

                        elif exit_level >= 0 and exit_region in ("light", "dark"):
                            key = f"{last_world}_{exit_level}_{exit_type}"
                            ev = entry_comp.get(key, -1)
                            cv = game.read_comp(sp2, last_world, exit_level, exit_region)
                            checks = []

                            if ev >= 0 and cv >= 0 and ev != cv:
                                # Completion
                                if not (ev & FLAG_COMPLETE) and (cv & FLAG_COMPLETE):
                                    loc_id = get_completion_location_id(last_world, exit_level, exit_region)
                                    if loc_id:
                                        should_check = False
                                        if exit_region == "light":
                                            should_check = (1 <= last_world <= 6) or (last_world == 7 and w7_enabled)
                                        elif exit_region == "dark":
                                            if 1 <= last_world <= 5:
                                                should_check = dark_world_enabled
                                            elif last_world == 6:
                                                should_check = dark_world_enabled
                                            elif last_world == 7:
                                                should_check = w7_enabled
                                        if should_check and loc_id not in self.locations_checked:
                                            checks.append(loc_id)

                                # Bandage
                                if not (ev & FLAG_BANDAGE) and (cv & FLAG_BANDAGE):
                                    ca = comp_addr(last_world, exit_level, exit_region)
                                    be = BANDAGE_BY_ADDR.get(ca)
                                    if be:
                                        checks.append(be["ap_id"])
                                        self.log(f"Bandage: {be['name']}", "location")
                                    else:
                                        self.log(f"DEBUG: bandage bit set on W{last_world} L{exit_level} "
                                                 f"{exit_region} (addr 0x{ca:04X}) but no mapping!", "debug")
                                    game.write_comp(sp2, last_world, exit_level, exit_region,
                                                    cv & MASK_CLEAR_BANDAGE)

                                # GotWarp bit
                                self._check_gotwarp(ev, cv, last_world, exit_level, exit_region, checks)

                            elif ev >= 0 and cv >= 0 and ev == cv:
                                self.log(f"DEBUG exit: no change W{last_world} L{exit_level} "
                                         f"T{exit_type} ev={ev} cv={cv}", "debug")
                            self._check_aplus(game, sp2, last_world, exit_level, exit_region,
                                              checks, aplus_enabled)

                            if checks:
                                await self.send_location_checks(checks)

                            # Achievement check runs on EVERY level exit, not just
                            # when new checks fired â€” otherwise achievements for
                            # already-checked levels (replays, reconnects) never trigger
                            if achievements_enabled:
                                ach_checks = []
                                self._check_achievements(
                                    game, sp2, ach_checks,
                                    achievements_enabled, worlds_cleared,
                                    worlds_dark_cleared, milestones_sent,
                                    aplus_enabled, warps_completed,
                                    warp_milestones_sent, world_aplus_sent,
                                )
                                if ach_checks:
                                    await self.send_location_checks(ach_checks)

                            # Re-enforce boss counters (game overwrites on level complete)
                            if boss_tokens_enabled:
                                self._enforce_boss_counters(game, sp2, boss_token_costs)
                            if dark_lock_enabled:
                                self._enforce_dark_locks(game, sp2)
                            game.set_char_bitmask(sp2, self.character_bits)

                        # A+ sweep: catch grades missed during mid-play transitions
                        # (game may not flush best time to save until level select)
                        if aplus_enabled and 1 <= last_world <= 7:
                            sweep_checks = self._aplus_sweep(
                                game, sp2, last_world, aplus_enabled,
                                dark_world_enabled, w7_enabled,
                            )
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
                    self.log(f"DEBUG loop error: {e}", "debug")

            await asyncio.sleep(0.001)

    def stop(self):
        self._running = False
        if self.ws and self.loop and self.loop.is_running():
            try:
                asyncio.run_coroutine_threadsafe(self.ws.close(), self.loop)
            except:
                pass


# =============================================================================
# GUI APPLICATION
# =============================================================================

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
        style.configure("TButton", background=DARK_ACCENT, foreground=DARK_FG,
                        borderwidth=1, focuscolor=DARK_ACCENT)
        style.map("TButton",
                  background=[("active", DARK_BORDER), ("pressed", DARK_BG)])
        style.configure("TEntry", fieldbackground=DARK_ENTRY_BG,
                        foreground=DARK_FG, insertcolor=DARK_FG)
        style.configure("TLabelframe", background=DARK_FRAME_BG)
        style.configure("TLabelframe.Label", background=DARK_FRAME_BG,
                        foreground=DARK_FG)

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        header = ttk.Label(main_frame, text=APP_NAME, font=("Helvetica", 14, "bold"))
        header.pack(pady=(0, 5))

        version_label = ttk.Label(main_frame, text=f"v{APP_VERSION}", font=("Helvetica", 9))
        version_label.pack(pady=(0, 10))

        # Game status
        game_frame = ttk.LabelFrame(main_frame, text="Game Status", padding="10")
        game_frame.pack(fill=tk.X, pady=5)

        self.game_status = ttk.Label(game_frame, text="Checking...", font=("Helvetica", 10))
        self.game_status.pack(side=tk.LEFT)

        self.refresh_btn = ttk.Button(game_frame, text="Refresh", command=self.check_game_connection)
        self.refresh_btn.pack(side=tk.RIGHT)

        # Connection settings
        conn_frame = ttk.LabelFrame(main_frame, text="Connection", padding="10")
        conn_frame.pack(fill=tk.X, pady=5)

        ttk.Label(conn_frame, text="Server:").grid(row=0, column=0, sticky="w", pady=2)
        self.server_entry = ttk.Entry(conn_frame, textvariable=self.server_var, width=35)
        self.server_entry.grid(row=0, column=1, columnspan=2, sticky="ew", pady=2, padx=5)

        ttk.Label(conn_frame, text="Slot Name:").grid(row=1, column=0, sticky="w", pady=2)
        self.slot_entry = ttk.Entry(conn_frame, textvariable=self.slot_var, width=35)
        self.slot_entry.grid(row=1, column=1, columnspan=2, sticky="ew", pady=2, padx=5)

        ttk.Label(conn_frame, text="Password:").grid(row=2, column=0, sticky="w", pady=2)
        self.password_entry = ttk.Entry(conn_frame, textvariable=self.password_var, show="*", width=35)
        self.password_entry.grid(row=2, column=1, columnspan=2, sticky="ew", pady=2, padx=5)

        conn_frame.columnconfigure(1, weight=1)

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)

        self.connect_btn = ttk.Button(btn_frame, text="Connect", command=self.connect)
        self.connect_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.disconnect_btn = ttk.Button(btn_frame, text="Disconnect", command=self.disconnect,
                                         state=tk.DISABLED)
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

        self.log_text.tag_configure("info", foreground="#ffffff")
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
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.log_text.insert(tk.END, f"[{timestamp}] {message}\n", tag)
            self.log_text.see(tk.END)
            self.log_text.configure(state=tk.DISABLED)
        self.root.after(0, _log)

    def set_status(self, text: str, color: str):
        def _status():
            self.status_label.configure(text=text, foreground=color)
        self.root.after(0, _status)

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
        except:
            pass
        return {}

    def save_config(self):
        config = {
            "server": self.server_var.get(),
            "slot": self.slot_var.get(),
        }
        try:
            CONFIG_FILE.write_text(json.dumps(config, indent=2))
        except:
            pass

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
                    "Super Meat Boy is not running!\n\nPlease start the game first.")
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
    app = SMBClientApp()
    app.run()
