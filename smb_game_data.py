"""
Super Meat Boy — Authoritative Game Data Module


Contains:
  - Level names (all worlds, light/dark/warp)
  - Par times (for A+ grade calculation)
  - Bandage locations (authoritative from SMBDatabase)
  - Warp zone host levels and slot mappings
  - Character warp data
  - Save data structure constants
  - Completion byte flags (including GotWarp)
  - All AP location ID helpers
  - Achievement definitions
"""

import struct


# BASE ID (must match APWorld)

BASE_ID = 7700000


# WORLD NAMES

WORLD_NAMES = {
    1: "The Forest", 2: "The Hospital", 3: "The Salt Factory",
    4: "Hell", 5: "Rapture", 6: "The End", 7: "Cotton Alley",
}


# LEVEL NAMES — 
# Indexed as LEVEL_NAMES[world_0idx][type_idx][level_0idx]
# type_idx: 0=light, 1=dark, 2=warp

LEVEL_NAMES = [
    # World 1 - The Forest
    [
        ["Hello World", "Upward", "The Gap", "Nutshell", "Holy Mountain", "Bladecatcher", "Diverge", "The Bit", "Safety Third", "The Levee", "Fired", "Revolve", "Tommy's Cabin", "Blood Mountain", "Cactus Jumper", "Sidewinder", "MorningStar", "Altamont", "Intermission", "The Test"],
        ["oh, hello", "Onward", "BZZZZZ", "Plum Rain", "Creamsoda", "I am the night", "Two Roads", "Big Red", "So close", "Walls", "Doused", "Fireal", "Tommy's Condo", "Mystery Spot", "Kick Machine", "Night Game", "The Clock", "Whitewash", "The Queener", "A perfect end"],
        ["Sky Pup", "Sky Pup", "Sky Pup", "The Commander!", "The Commander!", "The Commander!", "Hand Held Hack", "Hand Held Hack", "Hand Held Hack", "Space boy", "Space boy", "Space boy"],
    ],
    # World 2 - The Hospital
    [
        ["Biohazard", "One Down", "Memories", "Blew", "Big Empty", "The Grain", "Hush", "The Sabbath", "Blood Swamp", "johnny's cage", "Ghost Key", "Above", "Ulcer pop", "Aunt Flo", "Gallbladder", "Synj", "Worm food", "destructoid", "six feet", "Day Breaker"],
        ["back track", "pinkeye falls", "Buzzzzcut", "Blown", "Agent Orange", "Cher noble", "The Moon", "Grape Soda", "Centipede", "The Kracken", "Spineless", "Grey Matter", "Dust Bunnies", "Crawl Space", "Insurance?", "P.S.Y.", "Nels Box", "electrolysis", "Tenebrae", "Solemnity"],
        ["The Blood Shed", "The Blood Shed", "The Blood Shed", "The Bootlicker!", "The Bootlicker!", "The Bootlicker!", "Castle Crushers", "Castle Crushers", "Castle Crushers", "1977", "1977", "1977"],
    ],
    # World 3 - The Salt Factory
    [
        ["Pit Stop", "The Salt Lick", "Push", "Transmissions", "Uptown", "The Shaft", "Mind the Gap", "Boomtown", "Shotzie!", "Breakdown", "Box Tripper", "The Dumper", "The Bend", "Gurdy", "Vertigo", "Mono", "Rustic", "The Grundle", "Dig", "White Noise"],
        ["Step one", "Salt + Wound", "The Red Room", "Assemble", "Wasp", "Not You Again", "Pluck", "Salt Crown", "Goliath", "Exploder", "The Salt Man", "Hellevator", "Black Circle", "Salmon", "Vertebreaker", "The Chaser", "Ashes", "Bile Duct", "El Topo", "Sweet Pea"],
        ["Tunnel Vision", "Tunnel Vision", "Tunnel Vision", "The Jump Man!", "The Jump Man!", "The Jump Man!", "Cartridge Dump", "Cartridge Dump", "Cartridge Dump", "Kontra", "Kontra", "Kontra"],
    ],
    # World 4 - Hell
    [
        ["Boilermaker", "Brindle", "Heck Hole", "Hex", "Pyro", "Leviathan", "Rickets", "Weibe", "Deceiver", "Ball n Chain", "Oracle", "Big Brother", "Lazy", "Adversary", "Abaddon", "Bow", "Lost Highway", "Boris", "The Hive", "Babylon"],
        ["Gretel", "Golgotha", "Char", "Altered", "Wicked One", "The Gnashing", "Thistle", "Billy Boy", "Glut", "Gallow", "Surrender", "Beholder", "Oblivion", "Old Scratch", "Bone Yard", "Starless", "Invocation", "Sag Chamber", "Long Goodbye", "Imperial"],
        ["The Key Master", "The Key Master", "The Key Master", "The Fly Guy!", "The Fly Guy!", "The Fly Guy!", "Brimstone", "Brimstone", "Brimstone", "mmmmmm", "mmmmmm", "mmmmmm"],
    ],
    # World 5 - Rapture
    [
        ["the witness", "evangel", "Ripe Decay", "Rise", "Panic Switch", "Left Behind", "The Fallen", "Descent", "Abomination", "Grinding Mill", "Heretic", "10 Horns", "The Lamb", "King Carrion", "The Flood", "Rotgut", "The Kingdom", "Gate of Ludd", "Wrath", "Judgment"],
        ["The Clot", "Loomer", "Spank", "Alabaster", "Nix", "Ripcord", "Downpthe", "Downer", "Swine", "Pulp Factory", "Blight", "Canker", "Halo of Flies", "Necrosis", "Choke", "Coil", "Millenium", "Stain", "Magog", "Quietus"],
        ["Skyscraper", "Skyscraper", "Skyscraper", "The Guy!", "The Guy!", "The Guy!", "Sunshine Island", "Sunshine Island", "Sunshine Island", "Meat is Death", "Meat is Death", "Meat is Death"],
    ],
    # World 6 - The End
    [
        ["The Pit", "Schism", "Echoes", "Gently", "Omega"],
        ["Detox", "Ghost Tomb", "From Beyond", "Maze of Ith", "No Quarter"],
    ],
    # World 7 - Cotton Alley
    [
        ["Pink Noise", "Run Rabbit Run", "Spinal Tap", "Stag", "Tommunism", "Panic Attack", "Tunnel Blower", "Pig Latin", "Hatch", "Bullet Bob", "Train Eater", "Peel", "Pepto", "Watchtower", "Lock out", "hopscotch", "lead sheets", "Oobs revenge", "The Rash", "4 letter word"],
        ["White  Noise", "Flipside", "Organ Grinder", "The Tower", "Waiting Room", "Bone Machine", "Going up", "In Line", "Salt Shaker", "MasterBlaster", "Thumb", "Pink", "bleach", "20/20", "Patience", "Curls", "bullet proof", "They Bite", "XOXO", "Brag rights"],
    ],
]


# PAR TIMES — 
# Indexed as PAR_TIMES[world_0idx][type_idx][level_0idx]
# type_idx: 0=light, 1=dark, 2=warp
# A+ grade = time <= par_time

PAR_TIMES = [
    # World 1
    [
        [3.0, 5.0, 9.0, 9.0, 11.0, 7.0, 5.0, 4.5, 8.0, 7.5, 8.0, 7.0, 7.0, 8.0, 10.0, 9.0, 9.0, 4.0, 20.0, 22.0],
        [3.0, 4.5, 10.0, 12.0, 10.0, 7.0, 5.0, 6.0, 11.0, 11.0, 13.0, 12.0, 12.0, 14.0, 18.0, 17.0, 12.0, 5.0, 17.0, 25.0],
        [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0],
    ],
    # World 2
    [
        [11.0, 10.5, 14.0, 9.5, 16.0, 15.0, 19.0, 25.0, 11.0, 12.0, 9.0, 11.0, 10.0, 16.0, 19.0, 15.0, 14.0, 16.5, 14.0, 24.0],
        [17.0, 14.0, 13.0, 14.0, 20.0, 19.0, 30.0, 33.0, 14.0, 13.0, 12.5, 22.5, 11.0, 31.0, 32.0, 16.0, 12.0, 17.0, 26.0, 36.0],
        [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0],
    ],
    # World 3
    [
        [9.5, 8.3, 16.0, 12.0, 12.2, 4.5, 12.4, 8.3, 12.5, 10.5, 9.0, 11.6, 15.8, 14.8, 14.8, 14.8, 10.5, 17.0, 17.0, 20.0],
        [23.0, 16.0, 16.5, 20.0, 28.0, 20.0, 15.5, 17.5, 21.0, 18.0, 24.0, 11.6, 40.0, 18.0, 27.0, 24.0, 11.5, 17.0, 17.0, 25.5],
        [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0],
    ],
    # World 4
    [
        [11.0, 23.0, 11.5, 11.5, 12.0, 8.0, 17.0, 16.0, 6.0, 15.0, 12.5, 10.8, 11.5, 17.5, 9.0, 12.0, 12.0, 24.5, 14.0, 22.0],
        [19.0, 16.5, 12.0, 17.5, 14.0, 19.0, 18.0, 19.0, 10.5, 17.0, 16.5, 18.5, 23.0, 20.0, 11.0, 11.5, 18.0, 29.0, 14.0, 31.0],
        [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0],
    ],
    # World 5
    [
        [22.0, 13.0, 18.0, 13.5, 12.5, 11.0, 23.0, 20.0, 19.5, 15.5, 18.5, 16.0, 20.0, 30.5, 13.5, 30.0, 23.0, 17.0, 29.0, 32.0],
        [30.0, 17.0, 35.0, 27.0, 18.0, 12.0, 15.0, 26.0, 40.0, 15.0, 25.0, 26.0, 25.0, 60.0, 15.0, 32.0, 27.0, 19.0, 41.0, 48.0],
        [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0],
    ],
    # World 6
    [
        [30.0, 44.0, 34.0, 33.0, 44.0],
        [40.0, 50.0, 70.0, 50.0, 60.0],
    ],
    # World 7
    [
        [11.0, 13.0, 23.0, 26.0, 30.0, 7.5, 10.5, 26.0, 21.0, 32.0, 18.0, 11.6, 22.0, 40.0, 24.0, 20.0, 20.0, 21.0, 17.0, 45.0],
        [60.0, 60.0, 60.0, 60.0, 60.0, 60.0, 60.0, 60.0, 60.0, 60.0, 60.0, 60.0, 60.0, 60.0, 60.0, 60.5, 60.5, 60.0, 60.0, 60.0],
    ],
]



# COMPLETION BYTE FLAGS — from SMBLevel.cs LevelStatus [Flags] enum

FLAG_BANDAGE  = 0x01   # Bit 0: bandage collected
FLAG_COMPLETE = 0x02   # Bit 1: level completed
FLAG_WARP     = 0x08   # Bit 3: warp zone portal entered (on HOST level)
# Bit 2 (0x04) is unused

MASK_CLEAR_BANDAGE = ~FLAG_BANDAGE & 0xFF   # 0xFE
MASK_CLEAR_WARP    = ~FLAG_WARP & 0xFF      # 0xF7


# BANDAGE LOCATIONS — from SMBDatabase.cs (1-indexed level numbers)
# These are AUTHORITATIVE. Cross-validated against game data.


# Which light levels have bandages (1-indexed level number)
LIGHT_BANDAGE_LEVELS = {
    1: [4, 7, 9, 11, 13, 18, 20],
    2: [2, 5, 10, 13, 16, 18, 20],
    3: [1, 2, 4, 10, 11, 18, 20],
    4: [2, 6, 9, 13, 16, 17, 20],
    5: [3, 5, 9, 12, 16, 18, 20],
}

# Which dark levels have bandages (1-indexed level number)
DARK_BANDAGE_LEVELS = {
    1: [3, 5, 10, 14, 15, 17, 19],
    2: [4, 6, 7, 10, 12, 15, 16],
    3: [3, 5, 6, 7, 14, 16, 19],
    4: [3, 4, 8, 10, 14, 18, 19],
    5: [4, 5, 8, 10, 11, 17, 18],
}

# Which warp sub-levels have bandages (1-indexed slot number, 1-12)
WARP_BANDAGE_SLOTS = {
    1: [1, 2, 8, 9, 11, 12],
    2: [1, 3, 7, 8, 10, 12],
    3: [1, 3, 7, 9, 11, 12],
    4: [2, 3, 8, 9, 11, 12],
    5: [2, 3, 7, 9, 10, 11],
}



# WARP ZONE HOST LEVELS 
# Which levels contain warp zone portals

LIGHT_WARP_HOST_LEVELS = {
    1: [5, 12, 19],    # Sky Pup/Commander?/Hand Held Hack
    2: [8, 12, 15],    # Bootlicker(Jill)/Castle Crushers/Blood Shed
    3: [5, 7, 16],     # Cartridge Dump/Tunnel Vision/Jump Man(Ogmo)
    4: [8, 14, 18],    # Brimstone?/Key Master?/Fly Guy(Flywrench)
    5: [1, 7, 12],     # Skyscraper/The Guy(The Kid)/Sunshine Island
}

DARK_WARP_HOST_LEVELS = {
    1: [13],    # Space Boy
    2: [5],     # 1977
    3: [8],     # Kontra
    4: [7],     # MMMMMM
    5: [20],    # Meat is Death
}



# WARP ZONE SLOT MAPPING (from verified memory research)
#
# Each world has 12 warp save slots = 4 zones × 3 sub-levels:
#   Zone 0 (slots 0-2): varies per world
#   Zone 1 (slots 3-5): ALWAYS character warp
#   Zone 2 (slots 6-8): varies per world
#   Zone 3 (slots 9-11): ALWAYS dark world warp
#
# The warp names from LevelNames[w][2] are in SLOT ORDER (0-11).


# Warp zone names indexed by save slot groups
# Read from LevelNames[w-1][2] — each name appears 3x for the 3 sub-levels
WARP_ZONE_NAMES = {
    # (world, zone_index) → warp zone name
    # Zone names come from save slot order in LevelNames
    (1, 0): "Sky Pup",           (1, 1): "The Commander!",     (1, 2): "Hand Held Hack",    (1, 3): "Space Boy",
    (2, 0): "The Blood Shed",    (2, 1): "The Bootlicker!",    (2, 2): "Castle Crushers",   (2, 3): "1977",
    (3, 0): "Tunnel Vision",     (3, 1): "The Jump Man!",      (3, 2): "Cartridge Dump",    (3, 3): "Kontra",
    (4, 0): "The Key Master",    (4, 1): "The Fly Guy!",       (4, 2): "Brimstone",         (4, 3): "MMMMMM",
    (5, 0): "Skyscraper",        (5, 1): "The Guy!",           (5, 2): "Sunshine Island",   (5, 3): "Meat Is Death",
}

# Maps (world, host_level_1indexed, host_region) → zone_index
# For light warps: the 3 light host levels per world map to zones 0, 1, 2
#   BUT the order depends on which zone each host actually leads to.
#   This was verified empirically via bandage pattern matching.
#
# From the verified documentation:
#   W1: 1-5→Sky Pup(z0), 1-12→Commander(z1), 1-19→HHH(z2), 1-13X→Space Boy(z3)
#   W2: 2-15→Blood Shed(z0), 2-8→Bootlicker(z1), 2-12→Castle Crushers(z2), 2-5X→1977(z3)
#   W3: 3-7→Tunnel Vision(z0), 3-16→Jump Man(z1), 3-5→Cartridge Dump(z2), 3-8X→Kontra(z3)
#   W4: 4-8→zone0(Key Master?), 4-18→Fly Guy(z1), 4-14→zone2(Brimstone?), 4-7X→MMMMMM(z3)
#   W5: 5-1→zone0(Skyscraper), 5-7→The Guy(z1), 5-12→zone2(Sunshine Island), 5-20X→MiD(z3)
#
# Note: For W4, the verified slot mapping says zone0=slots0-2, zone1=slots3-5, etc.
# LevelNames says slots0-2="Key Master", slots3-5="Fly Guy", slots6-8="Brimstone", slots9-11="mmmmmm"
# So zone0=Key Master (host 4-8), zone2=Brimstone (host 4-14). This is consistent.

WARP_HOST_TO_ZONE = {}

# Build from verified host→zone mapping
_HOST_ZONE_MAP = {
    # (world, host_1idx, region): zone_index
    (1, 5, "light"): 0,   (1, 12, "light"): 1,  (1, 19, "light"): 2,  (1, 13, "dark"): 3,
    (2, 15, "light"): 0,  (2, 8, "light"): 1,   (2, 12, "light"): 2,  (2, 5, "dark"): 3,
    (3, 7, "light"): 0,   (3, 16, "light"): 1,  (3, 5, "light"): 2,   (3, 8, "dark"): 3,
    (4, 8, "light"): 0,   (4, 18, "light"): 1,  (4, 14, "light"): 2,  (4, 7, "dark"): 3,
    (5, 1, "light"): 0,   (5, 7, "light"): 1,   (5, 12, "light"): 2,  (5, 20, "dark"): 3,
}
WARP_HOST_TO_ZONE = _HOST_ZONE_MAP


# =============================================================================
# CHARACTER WARPS
# Zone 1 (slots 3-5) is ALWAYS the character warp
# =============================================================================
CHARACTER_WARPS = {
    # world → (character_name, host_level_1indexed)
    1: ("Commander Video", 12),
    2: ("Jill", 8),
    3: ("Ogmo", 16),              # Has double jump — needed for 3-4 bandage
    4: ("Flywrench", 18),
    5: ("The Kid", 7),            # Has double jump
}

CHARACTER_WARP_SLOTS = (3, 4, 5)  # Slots 3, 4, 5 in each world's warp region


# =============================================================================
# SAVE DATA STRUCTURE
# =============================================================================
WORLD_BASES = {
    1: 0x0060, 2: 0x02D0, 3: 0x0540, 4: 0x07B0,
    5: 0x0A20, 6: 0x0C90, 7: 0x0F00,
}
LIGHT_OFFSET = 0x000
DARK_OFFSET  = 0x0F0
WARP_OFFSET  = 0x1E0
SLOT_SIZE    = 0x0C    # 12 bytes per slot
TIME_BYTE    = 0       # Bytes 0-3: float IL time
COMP_BYTE    = 4       # Byte 4: completion flags
NUM_WARP_SLOTS = 12

NUM_LEVELS = {
    1: 20, 2: 20, 3: 20, 4: 20, 5: 20, 6: 5, 7: 20,
}



# ADDRESS HELPERS


def slot_addr(world, level_index, region):
    """Get save offset for slot start. 0-indexed level_index."""
    wb = WORLD_BASES.get(world)
    if wb is None:
        return None
    if region == "light":
        return wb + LIGHT_OFFSET + level_index * SLOT_SIZE
    elif region == "dark":
        return wb + DARK_OFFSET + level_index * SLOT_SIZE
    elif region == "warp":
        return wb + WARP_OFFSET + level_index * SLOT_SIZE
    return None


def comp_addr(world, level_index, region):
    """Get save offset for completion byte. 0-indexed level_index."""
    sa = slot_addr(world, level_index, region)
    return sa + COMP_BYTE if sa is not None else None


def time_addr(world, level_index, region):
    """Get save offset for IL time float. 0-indexed level_index."""
    sa = slot_addr(world, level_index, region)
    return sa + TIME_BYTE if sa is not None else None



# PAR TIME / A+ HELPERS


def get_par_time(world, level_index, region):
    """
    Get par time for a level. 0-indexed level_index.
    Returns par time as float, or None if no par time exists.
    """
    wi = world - 1
    if wi < 0 or wi >= len(PAR_TIMES):
        return None

    type_map = {"light": 0, "dark": 1, "warp": 2}
    ti = type_map.get(region)
    if ti is None:
        return None

    if ti >= len(PAR_TIMES[wi]):
        return None
    if level_index < 0 or level_index >= len(PAR_TIMES[wi][ti]):
        return None

    return PAR_TIMES[wi][ti][level_index]


def is_a_plus(time_val, world, level_index, region):
    """Check if a time qualifies for A+ grade (time <= par_time)."""
    par = get_par_time(world, level_index, region)
    if par is None or time_val <= 0:
        return False
    return time_val <= par



# LEVEL NAME HELPERS


def get_level_name(world, level_index, region):
    """Get level name string. 0-indexed level_index."""
    wi = world - 1
    if wi < 0 or wi >= len(LEVEL_NAMES):
        return None

    type_map = {"light": 0, "dark": 1, "warp": 2}
    ti = type_map.get(region)
    if ti is None:
        return None

    if ti >= len(LEVEL_NAMES[wi]):
        return None
    if level_index < 0 or level_index >= len(LEVEL_NAMES[wi][ti]):
        return None

    return LEVEL_NAMES[wi][ti][level_index]


def get_warp_zone_name(world, slot_index):
    """Get warp zone name from slot index (0-11). Returns zone name."""
    zone_idx = slot_index // 3
    return WARP_ZONE_NAMES.get((world, zone_idx), f"W{world} Zone {zone_idx}")



# AP LOCATION ID SCHEME

#
# Existing (preserved from v1.0):
#   +1..+100     Light level completions W1-W5 (20 per world)
#   +101..+106   Boss completions W1-W6
#   +107         Dark Boss (W6 dark Dr. Fetus)
#   +201..+300   Bandage locations (100 bandages, assigned order)
#   +301..+400   Dark level completions W1-W5 (20 per world)
#   +401..+405   W6 light level completions
#   +406..+410   W6 dark level completions
#
# NEW — A+ grades:
#   +501..+600   A+ Light W1-W5 (20 per world)
#   +601..+700   A+ Dark W1-W5 (20 per world)
#   +701..+705   A+ W6 Light
#   +706..+710   A+ W6 Dark
#   +711..+730   A+ W7 Light (20 levels)
#   +731..+750   A+ W7 Dark (20 levels)
#   +751..+810   A+ Warp sub-levels (12 per world × 5 worlds)
#
# NEW — W7 (Cotton Alley) completions:
#   +811..+830   W7 Light level completions (20 levels)
#   +831..+850   W7 Dark level completions (20 levels)
#
# NEW — Character & Warp:
#   +851..+855   Character unlock locations (W1-W5, one per world)
#   +861..+880   Warp zone completions (4 per world × 5 worlds)
#
# NEW — Achievements:
#   +901..+905   World clear (all 20 light levels beaten, W1-W5)
#   +906..+910   World dark clear (all 20 dark levels beaten, W1-W5)
#   +911         W6 clear (5 light levels)
#   +912         W6 dark clear (5 dark levels)
#   +913         W7 clear (20 light levels)
#   +914         W7 dark clear (20 dark levels)
#   +921..+930   Bandage milestones (10, 20, 30, 40, 50, 60, 70, 80, 90, 100)
#   +931         Golden God (all light A+)
#   +932         Girl Boy (100% — all dark A+)
#


# --- Existing ID functions (unchanged) ---

def level_location_id(world, level_index):
    """W1-W5 light levels: BASE + (w-1)*20 + (idx+1) = BASE+1..+100"""
    return BASE_ID + (world - 1) * 20 + (level_index + 1)

def w6_level_location_id(level_index):
    """W6 light levels: BASE+401..+405"""
    return BASE_ID + 401 + level_index

def w6_dark_level_location_id(level_index):
    """W6 dark levels: BASE+406..+410"""
    return BASE_ID + 406 + level_index

def dark_level_location_id(world, level_index):
    """W1-W5 dark levels: BASE+301..+400"""
    return BASE_ID + 300 + (world - 1) * 20 + (level_index + 1)

def boss_location_id(world):
    """Bosses W1-W6: BASE+101..+106"""
    return BASE_ID + 100 + world

def dark_boss_location_id():
    """Dark World Dr. Fetus boss: BASE+107"""
    return BASE_ID + 107


# --- NEW: A+ Location IDs ---

def aplus_light_location_id(world, level_index):
    """A+ Light W1-W5: BASE+501..+600"""
    return BASE_ID + 500 + (world - 1) * 20 + (level_index + 1)

def aplus_dark_location_id(world, level_index):
    """A+ Dark W1-W5: BASE+601..+700"""
    return BASE_ID + 600 + (world - 1) * 20 + (level_index + 1)

def aplus_w6_light_location_id(level_index):
    """A+ W6 Light: BASE+701..+705"""
    return BASE_ID + 701 + level_index

def aplus_w6_dark_location_id(level_index):
    """A+ W6 Dark: BASE+706..+710"""
    return BASE_ID + 706 + level_index

def aplus_w7_light_location_id(level_index):
    """A+ W7 Light: BASE+711..+730"""
    return BASE_ID + 711 + level_index

def aplus_w7_dark_location_id(level_index):
    """A+ W7 Dark: BASE+731..+750"""
    return BASE_ID + 731 + level_index

def aplus_warp_location_id(world, warp_slot_index):
    """A+ Warp sub-levels: BASE+751..+810 (12 per world × 5 worlds)"""
    return BASE_ID + 751 + (world - 1) * 12 + warp_slot_index


# --- NEW: W7 Level IDs ---

def w7_light_location_id(level_index):
    """W7 Light levels: BASE+811..+830"""
    return BASE_ID + 811 + level_index

def w7_dark_location_id(level_index):
    """W7 Dark levels: BASE+831..+850"""
    return BASE_ID + 831 + level_index


# --- NEW: Character Unlock IDs ---

def character_unlock_location_id(world):
    """Character unlocks: BASE+851..+855 (one per world 1-5)"""
    return BASE_ID + 850 + world


# --- NEW: Warp Zone Completion IDs ---

def warp_completion_location_id(world, zone_index):
    """Warp zone completion: BASE+861..+880 (4 per world × 5 worlds)"""
    return BASE_ID + 861 + (world - 1) * 4 + zone_index


# --- NEW: Achievement IDs ---

def world_clear_location_id(world):
    """All light levels complete in a world: BASE+901..+905 (W1-W5)"""
    return BASE_ID + 900 + world

def world_dark_clear_location_id(world):
    """All dark levels complete in a world: BASE+906..+910 (W1-W5)"""
    return BASE_ID + 905 + world

def w6_clear_location_id():
    return BASE_ID + 911

def w6_dark_clear_location_id():
    return BASE_ID + 912

def w7_clear_location_id():
    return BASE_ID + 913

def w7_dark_clear_location_id():
    return BASE_ID + 914

def bandage_milestone_location_id(count):
    """Bandage milestones: BASE+921..+930 (10, 20, 30... 100)"""
    return BASE_ID + 920 + (count // 10)

BANDAGE_MILESTONES = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

def golden_god_location_id():
    """All light world A+ grades: BASE+931"""
    return BASE_ID + 931

def girl_boy_location_id():
    """All dark world A+ grades: BASE+932"""
    return BASE_ID + 932



# UNIFIED DISPATCHERS


def get_completion_location_id(world, level_index, region):
    """Get the completion location ID for any level. 0-indexed level_index."""
    if region == "light":
        if 1 <= world <= 5 and 0 <= level_index < 20:
            return level_location_id(world, level_index)
        elif world == 6 and 0 <= level_index < 5:
            return w6_level_location_id(level_index)
        elif world == 7 and 0 <= level_index < 20:
            return w7_light_location_id(level_index)
    elif region == "dark":
        if 1 <= world <= 5 and 0 <= level_index < 20:
            return dark_level_location_id(world, level_index)
        elif world == 6 and 0 <= level_index < 5:
            return w6_dark_level_location_id(level_index)
        elif world == 7 and 0 <= level_index < 20:
            return w7_dark_location_id(level_index)
    return None


def get_aplus_location_id(world, level_index, region):
    """Get the A+ location ID for any level. 0-indexed level_index."""
    if region == "light":
        if 1 <= world <= 5 and 0 <= level_index < 20:
            return aplus_light_location_id(world, level_index)
        elif world == 6 and 0 <= level_index < 5:
            return aplus_w6_light_location_id(level_index)
        elif world == 7 and 0 <= level_index < 20:
            return aplus_w7_light_location_id(level_index)
    elif region == "dark":
        if 1 <= world <= 5 and 0 <= level_index < 20:
            return aplus_dark_location_id(world, level_index)
        elif world == 6 and 0 <= level_index < 5:
            return aplus_w6_dark_location_id(level_index)
        elif world == 7 and 0 <= level_index < 20:
            return aplus_w7_dark_location_id(level_index)
    elif region == "warp":
        if 1 <= world <= 5 and 0 <= level_index < 12:
            return aplus_warp_location_id(world, level_index)
    return None



# COMPREHENSIVE get_location_name


def get_location_name(loc_id: int) -> str:
    """Get human-readable location name from AP location ID."""
    lid = loc_id - BASE_ID

    # Light levels W1-W5: 1-100
    if 1 <= lid <= 100:
        w = (lid - 1) // 20 + 1
        lv = (lid - 1) % 20
        name = get_level_name(w, lv, "light") or f"Level {lv+1}"
        return f"{w}-{lv+1} {name}"

    # Bosses: 101-106
    if 101 <= lid <= 106:
        w = lid - 100
        return f"Boss - {WORLD_NAMES.get(w, f'W{w}')}"

    if lid == 107:
        return "Boss - The End (Dark)"

    # Bandages: 201-300 (names come from BANDAGE_DATA in client)
    if 201 <= lid <= 300:
        return f"Bandage #{lid - 200}"

    # Dark levels W1-W5: 301-400
    if 301 <= lid <= 400:
        did = lid - 300
        w = (did - 1) // 20 + 1
        lv = (did - 1) % 20
        name = get_level_name(w, lv, "dark") or f"Level {lv+1}"
        return f"{w}-{lv+1}X {name}"

    # W6 light: 401-405
    if 401 <= lid <= 405:
        lv = lid - 401
        name = get_level_name(6, lv, "light") or f"Level {lv+1}"
        return f"6-{lv+1} {name}"

    # W6 dark: 406-410
    if 406 <= lid <= 410:
        lv = lid - 406
        name = get_level_name(6, lv, "dark") or f"Level {lv+1}"
        return f"6-{lv+1}X {name}"

    # A+ Light W1-W5: 501-600
    if 501 <= lid <= 600:
        aid = lid - 500
        w = (aid - 1) // 20 + 1
        lv = (aid - 1) % 20
        name = get_level_name(w, lv, "light") or f"Level {lv+1}"
        return f"A+ {w}-{lv+1} {name}"

    # A+ Dark W1-W5: 601-700
    if 601 <= lid <= 700:
        aid = lid - 600
        w = (aid - 1) // 20 + 1
        lv = (aid - 1) % 20
        name = get_level_name(w, lv, "dark") or f"Level {lv+1}"
        return f"A+ {w}-{lv+1}X {name}"

    # A+ W6 Light: 701-705
    if 701 <= lid <= 705:
        lv = lid - 701
        name = get_level_name(6, lv, "light") or f"Level {lv+1}"
        return f"A+ 6-{lv+1} {name}"

    # A+ W6 Dark: 706-710
    if 706 <= lid <= 710:
        lv = lid - 706
        name = get_level_name(6, lv, "dark") or f"Level {lv+1}"
        return f"A+ 6-{lv+1}X {name}"

    # A+ W7 Light: 711-730
    if 711 <= lid <= 730:
        lv = lid - 711
        name = get_level_name(7, lv, "light") or f"Level {lv+1}"
        return f"A+ 7-{lv+1} {name}"

    # A+ W7 Dark: 731-750
    if 731 <= lid <= 750:
        lv = lid - 731
        name = get_level_name(7, lv, "dark") or f"Level {lv+1}"
        return f"A+ 7-{lv+1}X {name}"

    # A+ Warp: 751-810
    if 751 <= lid <= 810:
        wi = (lid - 751) // 12
        si = (lid - 751) % 12
        w = wi + 1
        zone_idx = si // 3
        sub = (si % 3) + 1
        wname = WARP_ZONE_NAMES.get((w, zone_idx), f"Zone {zone_idx}")
        return f"A+ {wname} {sub}"

    # W7 Light: 811-830
    if 811 <= lid <= 830:
        lv = lid - 811
        name = get_level_name(7, lv, "light") or f"Level {lv+1}"
        return f"7-{lv+1} {name}"

    # W7 Dark: 831-850
    if 831 <= lid <= 850:
        lv = lid - 831
        name = get_level_name(7, lv, "dark") or f"Level {lv+1}"
        return f"7-{lv+1}X {name}"

    # Character unlocks: 851-855
    if 851 <= lid <= 855:
        w = lid - 850
        char_name = CHARACTER_WARPS.get(w, ("Unknown",))[0]
        return f"Character - {char_name}"

    # Warp completions: 861-880
    if 861 <= lid <= 880:
        wi = (lid - 861) // 4
        zi = (lid - 861) % 4
        w = wi + 1
        wname = WARP_ZONE_NAMES.get((w, zi), f"Zone {zi}")
        return f"Warp Complete - {wname}"

    # World clears: 901-905
    if 901 <= lid <= 905:
        w = lid - 900
        return f"World Clear - {WORLD_NAMES.get(w, f'W{w}')}"

    # World dark clears: 906-910
    if 906 <= lid <= 910:
        w = lid - 905
        return f"Dark Clear - {WORLD_NAMES.get(w, f'W{w}')}"

    if lid == 911: return "World Clear - The End"
    if lid == 912: return "Dark Clear - The End"
    if lid == 913: return "World Clear - Cotton Alley"
    if lid == 914: return "Dark Clear - Cotton Alley"

    # Bandage milestones: 921-930
    if 921 <= lid <= 930:
        count = (lid - 920) * 10
        return f"Bandage Milestone - {count}"

    if lid == 931: return "The Golden God (All Light A+)"
    if lid == 932: return "Girl Boy (All Dark A+)"

    return f"Unknown Location {loc_id}"



# CROSS-VALIDATION OF EXISTING BANDAGE DATA

#
# The client's _BANDAGE_RAW uses (world, 0-indexed save_index, region, name).

# W1 Light: the=[3,6,8,10,12,17,19]+1=[4,7,9,11,13,18,20]  DB=[4,7,9,11,13,18,20]  ✓ MATCH
# W1 Dark:  the=[2,4,9,13,14,16,18]+1=[3,5,10,14,15,17,19] DB=[3,5,10,14,15,17,19] ✓ MATCH
# W1 Warp:  the=[0,1,7,8,10,11]+1=[1,2,8,9,11,12]          DB=[1,2,8,9,11,12]       ✓ MATCH
#
# W2 Light: the=[1,4,9,12,15,17,19]+1=[2,5,10,13,16,18,20] DB=[2,5,10,13,16,18,20]  ✓ MATCH
# W2 Dark:  the=[3,5,6,9,11,14,15]+1=[4,6,7,10,12,15,16]   DB=[4,6,7,10,12,15,16]   ✓ MATCH
# W2 Warp:  the=[0,2,6,7,9,11]+1=[1,3,7,8,10,12]           DB=[1,3,7,8,10,12]        ✓ MATCH
#
# W3 Light: the=[0,1,3,9,10,17,19]+1=[1,2,4,10,11,18,20]   DB=[1,2,4,10,11,18,20]   ✓ MATCH
# W3 Dark:  the=[2,4,5,6,13,15,18]+1=[3,5,6,7,14,16,19]    DB=[3,5,6,7,14,16,19]    ✓ MATCH
# W3 Warp:  the=[0,2,6,8,10,11]+1=[1,3,7,9,11,12]          DB=[1,3,7,9,11,12]        ✓ MATCH
#
# W4 Light: the=[1,5,7,10,14,17,19]+1=[2,6,8,11,15,18,20]
#           DB=[2,6,9,13,16,17,20]
#           ✗ DISCREPANCY at positions 3-6: thes=[8,11,15,18] vs DB=[9,13,16,17]
#
# W4 Dark:  the=[0,2,3,4,6,8,9]+1=[1,3,4,5,7,9,10]
#           DB=[3,4,8,10,14,18,19]
#           ✗ SEVERE DISCREPANCY — almost entirely wrong
#
# W4 Warp:  the=[1,2,6,8,9,10]+1=[2,3,7,9,10,11]
#           DB=[2,3,8,9,11,12]
#           ✗ DISCREPANCY at slots 3-6
#
# W5 Light: the=[1,4,6,7,10,13,17]+1=[2,5,7,8,11,14,18]
#           DB=[3,5,9,12,16,18,20]
#           ✗ SEVERE DISCREPANCY
#
# W5 Dark:  the=[0,3,5,9,12,14,18]+1=[1,4,6,10,13,15,19]
#           DB=[4,5,8,10,11,17,18]
#           ✗ SEVERE DISCREPANCY
#
# W5 Warp:  the=[0,2,7,8,9,11]+1=[1,3,8,9,10,12]
#           DB=[2,3,7,9,10,11]
#           ✗ DISCREPANCY
#
# CONCLUSION: W1-W3 bandage data is PERFECT. W4-W5 has significant errors.
# The W4/W5 level names in the data are also wrong (names that don't exist
# in the game, e.g. "Goat Climber", "Wormwood", "Anvil", "Flamin'").
# SMBDatabase.cs should be treated as authoritative.
#
# ⚠️  EXISTING AP IDs (BASE+201..+300) ARE ALREADY ASSIGNED.
#     Changing bandage save indices would break existing multiworlds.
#     Fix should be done in a new version with migration support.
#
# For now, generate CORRECTED bandage data from SMBDatabase for NEW installs:

def build_corrected_bandage_data():
    """Build bandage data using authoritative SMBDatabase indices.
    Returns list of dicts matching BANDAGE_DATA format.
    Order: W1-W5 light, W1-W5 dark, W1-W5 warp (same AP ID order)."""
    data = []
    ap_idx = 0

    # Light bandages W1-W5
    for w in range(1, 6):
        for lv_1idx in LIGHT_BANDAGE_LEVELS[w]:
            idx_0 = lv_1idx - 1
            name = get_level_name(w, idx_0, "light") or f"Level {lv_1idx}"
            data.append({
                "world": w, "index": idx_0, "region": "light",
                "name": f"{w}-{lv_1idx} {name}",
                "ap_id": BASE_ID + 201 + ap_idx,
            })
            ap_idx += 1

    # Dark bandages W1-W5
    for w in range(1, 6):
        for lv_1idx in DARK_BANDAGE_LEVELS[w]:
            idx_0 = lv_1idx - 1
            name = get_level_name(w, idx_0, "dark") or f"Level {lv_1idx}"
            data.append({
                "world": w, "index": idx_0, "region": "dark",
                "name": f"{w}-{lv_1idx}X {name}",
                "ap_id": BASE_ID + 201 + ap_idx,
            })
            ap_idx += 1

    # Warp bandages W1-W5
    for w in range(1, 6):
        for slot_1idx in WARP_BANDAGE_SLOTS[w]:
            idx_0 = slot_1idx - 1
            zone_idx = idx_0 // 3
            sub = (idx_0 % 3) + 1
            wname = WARP_ZONE_NAMES.get((w, zone_idx), f"Zone {zone_idx}")
            data.append({
                "world": w, "index": idx_0, "region": "warp",
                "name": f"{wname} {sub}",
                "ap_id": BASE_ID + 201 + ap_idx,
            })
            ap_idx += 1

    return data


# Pre-build for import
CORRECTED_BANDAGE_DATA = build_corrected_bandage_data()

# Build address lookup for corrected data
CORRECTED_BANDAGE_BY_ADDR = {}
for b in CORRECTED_BANDAGE_DATA:
    ca = comp_addr(b["world"], b["index"], b["region"])
    if ca is not None:
        CORRECTED_BANDAGE_BY_ADDR[ca] = b



# LOCATION COUNTS SUMMARY

#
# Level completions:
#   Light W1-W5: 100   Dark W1-W5: 100   W6: 5+5   W7: 20+20  = 250
# Bosses:
#   W1-W6 + Dark Boss = 7
# Bandages:
#   100 (7 per world × 5 worlds × 3 regions ≈ but actual: 35 light + 35 dark + 30 warp)
# A+ grades:
#   Light W1-W5: 100   Dark W1-W5: 100   W6: 5+5   W7: 20+20
#   Warp W1-W5: 60 = 310
# Character unlocks: 5
# Warp zone completions: 20
# Achievements:
#   World clears: 7 light + 7 dark = 14
#   Bandage milestones: 10
#   Golden God + Girl Boy: 2
#   Total: 26
#
# GRAND TOTAL: ~718 locations (can be scaled via slot_data options)
