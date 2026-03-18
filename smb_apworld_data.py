# APWorld ID Offsets

ITEM_OFFSET = 20101130000
LOC_OFFSET  = 30112010000

# Item IDs (from items.json)

# Boss/progression keys
ITEM_DW_DR_FETUS_KEY     = ITEM_OFFSET + 1
ITEM_CH1_BOSS_KEY        = ITEM_OFFSET + 2
ITEM_CH2_BOSS_KEY        = ITEM_OFFSET + 3
ITEM_CH3_BOSS_KEY        = ITEM_OFFSET + 4
ITEM_CH4_BOSS_KEY        = ITEM_OFFSET + 5
ITEM_CH5_BOSS_KEY        = ITEM_OFFSET + 6
ITEM_CH6_BOSS_KEY        = ITEM_OFFSET + 7
ITEM_CH7_LW_LEVEL_KEY    = ITEM_OFFSET + 8
ITEM_CH7_DW_LEVEL_KEY    = ITEM_OFFSET + 9
ITEM_BANDAGE             = ITEM_OFFSET + 10

# Chapter (world) access keys
ITEM_CH1_KEY = ITEM_OFFSET + 11
ITEM_CH2_KEY = ITEM_OFFSET + 12
ITEM_CH3_KEY = ITEM_OFFSET + 13
ITEM_CH4_KEY = ITEM_OFFSET + 14
ITEM_CH5_KEY = ITEM_OFFSET + 15
ITEM_CH6_KEY = ITEM_OFFSET + 16
ITEM_CH7_KEY = ITEM_OFFSET + 17

# Characters
ITEM_MEAT_BOY         = ITEM_OFFSET + 18
ITEM_8BIT_MEAT_BOY    = ITEM_OFFSET + 19
ITEM_4BIT_MEAT_BOY    = ITEM_OFFSET + 20
ITEM_4COLOR_MEAT_BOY  = ITEM_OFFSET + 21
ITEM_COMMANDER_VIDEO  = ITEM_OFFSET + 22
ITEM_JILL             = ITEM_OFFSET + 23
ITEM_OGMO             = ITEM_OFFSET + 24
ITEM_FLYWRENCH        = ITEM_OFFSET + 25
ITEM_THE_KID          = ITEM_OFFSET + 26
ITEM_HEADCRAB         = ITEM_OFFSET + 27
ITEM_ALIEN_HOMINID    = ITEM_OFFSET + 28
ITEM_JOSEF            = ITEM_OFFSET + 29
ITEM_NAIJA            = ITEM_OFFSET + 30
ITEM_RUNMAN           = ITEM_OFFSET + 31
ITEM_CAPTAIN_VIRIDIAN = ITEM_OFFSET + 32
ITEM_STEVE            = ITEM_OFFSET + 33
ITEM_MEAT_NINJA       = ITEM_OFFSET + 34
ITEM_BROWNIE          = ITEM_OFFSET + 35
ITEM_GOO_BALL         = ITEM_OFFSET + 36
ITEM_BANDAGE_GIRL     = ITEM_OFFSET + 37

# A+ Rank items (W-L format, IDs 38-162)
# Generated: ITEM_OFFSET + 37 + (world_offset) + level
# W1: 38-57, W2: 58-77, W3: 78-97, W4: 98-117, W5: 118-137
# W6: 138-142, W7: 143-162
def aplus_item_id(world, level_1based):
    """Get item ID for a W-L A+ Rank item."""
    if world <= 5:
        return ITEM_OFFSET + 37 + (world - 1) * 20 + level_1based
    elif world == 6:
        return ITEM_OFFSET + 137 + level_1based
    elif world == 7:
        return ITEM_OFFSET + 142 + level_1based
    return None

ITEM_BOSS_TOKEN       = ITEM_OFFSET + 163
ITEM_VICTORY          = ITEM_OFFSET + 164
ITEM_DEGRADED_BANDAGE = ITEM_OFFSET + 165


# Item lookup tables

# Chapter Key item ID → world number
CHAPTER_KEY_ITEMS = {
    ITEM_CH1_KEY: 1, ITEM_CH2_KEY: 2, ITEM_CH3_KEY: 3,
    ITEM_CH4_KEY: 4, ITEM_CH5_KEY: 5, ITEM_CH6_KEY: 6,
    ITEM_CH7_KEY: 7,
}

# Boss Key item ID → chapter number
BOSS_KEY_ITEMS = {
    ITEM_CH1_BOSS_KEY: 1, ITEM_CH2_BOSS_KEY: 2, ITEM_CH3_BOSS_KEY: 3,
    ITEM_CH4_BOSS_KEY: 4, ITEM_CH5_BOSS_KEY: 5, ITEM_CH6_BOSS_KEY: 6,
}

# Character item ID → (bitmask_bit, display_name)
CHARACTER_ITEMS = {
    ITEM_MEAT_BOY:         (0,  "Meat Boy"),
    ITEM_4COLOR_MEAT_BOY:  (2,  "4-Color Meat Boy"),
    ITEM_4BIT_MEAT_BOY:    (3,  "4-Bit Meat Boy"),
    ITEM_8BIT_MEAT_BOY:    (4,  "8-Bit Meat Boy"),
    ITEM_BROWNIE:          (5,  "Brownie"),
    ITEM_BANDAGE_GIRL:     (6,  "Bandage Girl"),
    ITEM_MEAT_NINJA:       (7,  "Meat Ninja"),
    ITEM_NAIJA:            (10, "Naija"),
    ITEM_COMMANDER_VIDEO:  (11, "Commander Video"),
    ITEM_RUNMAN:           (12, "RunMan"),
    ITEM_GOO_BALL:         (13, "Goo Ball"),
    ITEM_STEVE:            (14, "Steve"),
    ITEM_FLYWRENCH:        (16, "Flywrench"),
    ITEM_JILL:             (18, "Jill"),
    ITEM_CAPTAIN_VIRIDIAN: (19, "Captain Viridian"),
    ITEM_JOSEF:            (21, "Josef"),
    ITEM_THE_KID:          (22, "The Kid"),
    ITEM_HEADCRAB:         (23, "Headcrab"),
    ITEM_OGMO:             (24, "Ogmo"),
    ITEM_ALIEN_HOMINID:    (27, "Alien Hominid"),
}

# Build A+ Rank item ID → (world, level_1based) lookup
APLUS_RANK_ITEMS = {}
for w in range(1, 8):
    num = 5 if w == 6 else 20
    for lv in range(1, num + 1):
        iid = aplus_item_id(w, lv)
        if iid:
            APLUS_RANK_ITEMS[iid] = (w, lv)


# World / level names


WORLD_NAMES = {
    1: "The Forest", 2: "The Hospital", 3: "The Salt Factory",
    4: "Hell", 5: "Rapture", 6: "The End", 7: "Cotton Alley",
}

NUM_LEVELS = {1: 20, 2: 20, 3: 20, 4: 20, 5: 20, 6: 5, 7: 20}

LIGHT_LEVEL_NAMES = {
    (1, 1): "Hello World", (1, 2): "Upward", (1, 3): "The Gap",
    (1, 4): "Nutshell", (1, 5): "Holy Mountain", (1, 6): "Bladecatcher",
    (1, 7): "Diverge", (1, 8): "The Bit", (1, 9): "Safety Third",
    (1, 10): "The Levee", (1, 11): "Fired", (1, 12): "Resolve",
    (1, 13): "Tommy's Cabin", (1, 14): "Blood Mountain", (1, 15): "Cactus Jumper",
    (1, 16): "Sidewinder", (1, 17): "Morningstar", (1, 18): "Altamont",
    (1, 19): "Intermission", (1, 20): "The Test",
    (2, 1): "Biohazard", (2, 2): "One Down", (2, 3): "Memories",
    (2, 4): "Blew", (2, 5): "Big Empty", (2, 6): "The Grain",
    (2, 7): "Hush", (2, 8): "The Sabbath", (2, 9): "Blood Swamp",
    (2, 10): "Johnny's Cage", (2, 11): "Ghost Key", (2, 12): "Above",
    (2, 13): "Ulcer Pop", (2, 14): "Aunt Flo", (2, 15): "Gallbladder",
    (2, 16): "Synj", (2, 17): "Worm Food", (2, 18): "Destructoid",
    (2, 19): "Six Feet", (2, 20): "Day Breaker",
    (3, 1): "Pit Stop", (3, 2): "The Salt Lick", (3, 3): "Push",
    (3, 4): "Transmissions", (3, 5): "Uptown", (3, 6): "The Shaft",
    (3, 7): "Mind the Gap", (3, 8): "Boomtown", (3, 9): "Shotzie!",
    (3, 10): "Breakdown", (3, 11): "Box Tripper", (3, 12): "The Dumper",
    (3, 13): "The Bend", (3, 14): "Gurdy", (3, 15): "Vertigo",
    (3, 16): "Mono", (3, 17): "Rustic", (3, 18): "The Grundle",
    (3, 19): "Dig", (3, 20): "White Noise",
    (4, 1): "Boilermaker", (4, 2): "Brindle", (4, 3): "Heck Hole",
    (4, 4): "Hex", (4, 5): "Pyro", (4, 6): "Leviathan",
    (4, 7): "Rickets", (4, 8): "Weibe", (4, 9): "Deceiver",
    (4, 10): "Ball N Chain", (4, 11): "Oracle", (4, 12): "Big Brother",
    (4, 13): "Lazy", (4, 15): "Abaddon", (4, 16): "Bow",
    (4, 17): "Lost Highway", (4, 18): "Boris", (4, 19): "The Hive",
    (4, 20): "Babylon",
    (5, 1): "The Witness", (5, 2): "Evangel", (5, 3): "Ripe Decay",
    (5, 4): "Rise", (5, 5): "Panic Switch", (5, 6): "Left Behind",
    (5, 7): "The Fallen", (5, 8): "Descent", (5, 9): "Abomination",
    (5, 10): "Grinding Mill", (5, 11): "Heretic", (5, 13): "The Lamb",
    (5, 14): "King Carrion", (5, 15): "The Flood", (5, 16): "Rotgut",
    (5, 17): "The Kingdom", (5, 18): "Gate of Ludd", (5, 19): "Wrath",
    (5, 20): "Judgment",
    (6, 1): "The Pit", (6, 2): "Schism", (6, 3): "Echoes",
    (6, 4): "Gently", (6, 5): "Omega",
    (7, 1): "Pink Noise", (7, 2): "Run Rabbit Run", (7, 3): "Spinal Tap",
    (7, 4): "Stag", (7, 5): "Tommunism", (7, 6): "Panic Attack",
    (7, 7): "Tunnel Blower", (7, 8): "Pig Latin", (7, 9): "Hatch",
    (7, 10): "Bullet Bob", (7, 11): "Train Eater", (7, 12): "Peel",
    (7, 13): "Pepto", (7, 14): "Watchtower", (7, 15): "Lock Out",
    (7, 16): "Hopscotch", (7, 17): "Lead Sheets", (7, 18): "Oobs Revenge",
    (7, 19): "The Rash", (7, 20): "4 Letter Word",
}

DARK_LEVEL_NAMES = {
    (1, 1): "Oh, Hello", (1, 2): "Onward", (1, 3): "Bzzzzz",
    (1, 4): "Plum Rain", (1, 5): "Creamsoda", (1, 6): "I Am The Night",
    (1, 7): "Two Roads", (1, 8): "Big Red", (1, 9): "So Close",
    (1, 10): "Walls", (1, 11): "Doused", (1, 12): "Fireal",
    (1, 13): "Tommy's Condo", (1, 14): "Mystery Spot", (1, 15): "Kick Machine",
    (1, 16): "Night Game", (1, 17): "The Clock", (1, 18): "Whitewash",
    (1, 19): "The Queener", (1, 20): "A Perfect End",
    (2, 1): "Back Track", (2, 2): "Pinkeye Falls", (2, 3): "Buzzzzcut",
    (2, 4): "Blown", (2, 5): "Agent Orange", (2, 6): "Cher Noble",
    (2, 7): "The Moon", (2, 8): "Grape Soda", (2, 9): "Centipede",
    (2, 10): "The Kracken", (2, 11): "Spineless", (2, 12): "Grey Matter",
    (2, 13): "Dust Bunnies", (2, 14): "Back Track", (2, 15): "Insurance?",
    (2, 16): "P.S.Y.", (2, 17): "Nels Box", (2, 18): "Electrolysis",
    (2, 19): "Tenebrae", (2, 20): "Back Track",
    (3, 1): "Step One", (3, 2): "Salt + Wound", (3, 3): "The Red Room",
    (3, 4): "Assemble", (3, 5): "Wasp", (3, 6): "Not You Again",
    (3, 7): "Pluck", (3, 8): "Salt Crown", (3, 9): "Goliath",
    (3, 10): "Exploder", (3, 11): "The Salt Man", (3, 12): "Hellevator",
    (3, 13): "Black Circle", (3, 14): "Step One", (3, 15): "Vertebreaker",
    (3, 16): "The Chaser", (3, 17): "Ashes", (3, 18): "Bile Duct",
    (3, 19): "El Topo", (3, 20): "Sweet Pea",
    (4, 1): "Gretel", (4, 2): "Brindle", (4, 3): "Char",
    (4, 4): "Altered", (4, 5): "Wicked One", (4, 6): "Leviathan",
    (4, 7): "Thistle", (4, 8): "Billy Boy", (4, 9): "Glut",
    (4, 10): "Gallow", (4, 11): "Surrender", (4, 12): "Beholder",
    (4, 13): "Oblivion", (4, 14): "Old Scratch", (4, 15): "Bone Yard",
    (4, 16): "Starless", (4, 17): "Invocation", (4, 18): "Sag Chamber",
    (4, 19): "Long Goodbye", (4, 20): "Imperial",
    (5, 1): "The Clot", (5, 2): "Loomer", (5, 3): "Spank",
    (5, 4): "Alabaster", (5, 5): "Nix", (5, 6): "Ripcord",
    (5, 7): "Downpour", (5, 8): "Downer", (5, 9): "Swine",
    (5, 10): "Pulp Factory", (5, 11): "Blight", (5, 12): "Canker",
    (5, 13): "Halo of Flies", (5, 14): "Necrosis", (5, 15): "Choke",
    (5, 16): "Coil", (5, 17): "Millenium", (5, 18): "Stain",
    (5, 19): "Magog", (5, 20): "Quietus",
    (6, 1): "Detox", (6, 2): "Ghost Tomb", (6, 3): "From Beyond",
    (6, 4): "Maze of Ith", (6, 5): "No Quarter",
    (7, 1): "White Noise", (7, 2): "Flipside", (7, 3): "Organ Grinder",
    (7, 4): "The Tower", (7, 5): "Waiting Room", (7, 6): "Bone Machine",
    (7, 7): "Going Up", (7, 8): "In Line", (7, 9): "Salt Shaker",
    (7, 10): "Masterblaster", (7, 11): "Thumb", (7, 12): "Pink",
    (7, 13): "Bleach", (7, 14): "20/20", (7, 15): "Patience",
    (7, 16): "Curls", (7, 17): "Bullet Proof", (7, 18): "They Bite",
    (7, 19): "XOXO", (7, 20): "Brag Rights",
}

# Warp zone names keyed by (world, host_level_1based)
LW_WARP_NAMES = {
    (1, 5): "Sky Pup", (1, 12): "The Commander!", (1, 19): "Hand Held Hack",
    (2, 8): "The Bootlicker!", (2, 12): "Castle Crushers", (2, 15): "The Blood Shed",
    (3, 5): "Cartridge Dump", (3, 7): "Tunnel Vision", (3, 16): "The Jump Man",
    (4, 8): "Brimstone", (4, 14): "The Key Master", (4, 18): "The Fly Guy!",
    (5, 1): "Skyscraper", (5, 7): "The Guy!", (5, 12): "Sunshine Island",
}

DW_WARP_NAMES = {
    (1, 13): "Space Boy", (2, 5): "1977", (3, 8): "Kontra",
    (4, 7): "MMMMMM", (5, 20): "Meat is Death",
}

# Boss location names
BOSS_LOC_NAMES = {
    1: "1-Boss Lil' Slugger",
    2: "2-Boss C.H.A.D",
    3: "3-Boss Brownie",
    4: "4-Boss Little Horn",
    5: "5-Boss Larries Lament",
    6: "6-Boss LW Dr. Fetus",  # Light world boss
}
DARK_BOSS_LOC_NAME = "6-Boss DW Dr. Fetus"

# Cutscene (post-boss) location names
CUTSCENE_LOC_NAMES = {
    1: "-1 |>'-'|>",
    2: "-2 |'-'|>",
    3: "-3 |'-'|>",
    4: "-4 |'-'|>",
    5: "-5 |'-'|>",
    6: "-6 |'-'|>",
}


# Location name generators


def light_completion_name(world, level_1based):
    """Get location name for completing a light world level."""
    name = LIGHT_LEVEL_NAMES.get((world, level_1based))
    if name:
        return f"{world}-{level_1based} {name}"
    return None

def light_aplus_name(world, level_1based):
    """Get location name for A+ on a light world level."""
    name = LIGHT_LEVEL_NAMES.get((world, level_1based))
    if name:
        return f"{world}-{level_1based} {name} (A+ Rank)"
    return None

def dark_completion_name(world, level_1based):
    """Get location name for completing a dark world level."""
    name = DARK_LEVEL_NAMES.get((world, level_1based))
    if name:
        return f"{world}-{level_1based}X {name}"
    return None

def dark_aplus_name(world, level_1based):
    """Get location name for A+ on a dark world level."""
    name = DARK_LEVEL_NAMES.get((world, level_1based))
    if name:
        return f"{world}-{level_1based}X {name} (A+ Rank)"
    return None

def light_bandage_name(world, level_1based):
    """Get location name for a light world bandage."""
    name = LIGHT_LEVEL_NAMES.get((world, level_1based))
    if name:
        return f"{world}-{level_1based} {name} (Bandage)"
    return None

def dark_bandage_name(world, level_1based):
    """Get location name for a dark world bandage."""
    name = DARK_LEVEL_NAMES.get((world, level_1based))
    if name:
        return f"{world}-{level_1based}X {name} (Bandage)"
    return None

def lw_warp_completion_name(world, host_level_1based):
    """Get location name for completing a light world warp zone."""
    wname = LW_WARP_NAMES.get((world, host_level_1based))
    if wname:
        return f"{world}-{host_level_1based}WZ {wname}"
    return None

def dw_warp_completion_name(world, host_level_1based):
    """Get location name for completing a dark world warp zone."""
    wname = DW_WARP_NAMES.get((world, host_level_1based))
    if wname:
        return f"{world}-{host_level_1based}XWZ {wname}"
    return None

def lw_warp_bandage_name(world, host_level_1based, bandage_num):
    """Get location name for a light world warp zone bandage (1 or 2)."""
    wname = LW_WARP_NAMES.get((world, host_level_1based))
    if wname:
        return f"{world}-{host_level_1based}WZ {wname} (Bandage {bandage_num})"
    return None

def dw_warp_bandage_name(world, host_level_1based, bandage_num):
    """Get location name for a dark world warp zone bandage (1 or 2)."""
    wname = DW_WARP_NAMES.get((world, host_level_1based))
    if wname:
        return f"{world}-{host_level_1based}XWZ {wname} (Bandage {bandage_num})"
    return None

def boss_location_name(world, is_dark=False):
    """Get location name for beating a boss."""
    if is_dark and world == 6:
        return DARK_BOSS_LOC_NAME
    return BOSS_LOC_NAMES.get(world)

def cutscene_location_name(world):
    """Get location name for a post-boss cutscene."""
    return CUTSCENE_LOC_NAMES.get(world)

def aplus_rank_item_name(world, level_1based):
    """Get item name for an A+ Rank item (e.g. '1-1 A+ Rank')."""
    return f"{world}-{level_1based} A+ Rank"



# Save data base addresses per world (offset from save_ptr)
WORLD_BASES = {
    1: 0x0060, 2: 0x02D0, 3: 0x0540, 4: 0x07B0,
    5: 0x0A20, 6: 0x0C90, 7: 0x0D08,  # W7 corrected
}

LIGHT_OFFSET = 0x000
DARK_OFFSET  = 0x0F0
WARP_OFFSET  = 0x1E0    # Works for W1-W4 (confirmed for W4)
W6_DARK_OFFSET = 0x3C   # W6 has only 5 levels, compact layout


WARP_BASES = {
    1: 0x0060 + 0x1E0,  # 0x0240 (unconfirmed, matches layout)
    2: 0x02D0 + 0x1E0,  # 0x04B0 (unconfirmed, matches layout)
    3: 0x0540 + 0x1E0,  # 0x0720 (unconfirmed, matches layout)
    4: 0x07B0 + 0x1E0,  # 0x0990 (CONFIRMED: MMMMMM data found here)
    5: 0x0EC4,          # CONFIRMED: The Guy data found here
}

SLOT_SIZE = 0x0C   # 12 bytes per level slot
COMP_BYTE = 4      # Completion byte offset within slot
TIME_BYTE = 0      # IL time (float) offset within slot
NUM_WARP_SLOTS = 12

# Completion byte flags
FLAG_BANDAGE = 0x01
FLAG_COMPLETE = 0x02
FLAG_WARP = 0x08
MASK_CLEAR_BANDAGE = 0xFE

# Memory addresses (relative to base or save_ptr)
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
BOSS_LEVEL_INDEX = 20  # Level index 20 (0-based) = boss

# Character bitmask offset from save_ptr
CHARACTER_BITMASK_OFFSET = 0x3950

# Boss completion counter offsets from save_ptr
BOSS_COUNTER_OFFSETS = {
    1: 0x38D8, 2: 0x38E4, 3: 0x38F0,
    4: 0x38FC, 5: 0x3908, 6: 0x3914,
}

# Native boss unlock thresholds
BOSS_UNLOCK_THRESHOLDS = {
    1: 17, 2: 17, 3: 17, 4: 17, 5: 17, 6: 5,
}



# Address calculation helpers


def comp_addr(world, index, region):
    """Get completion byte address offset from save_ptr."""
    if region == "warp":
        warp_base = WARP_BASES.get(world)
        if warp_base is None:
            return None
        return warp_base + index * SLOT_SIZE + COMP_BYTE
    wb = WORLD_BASES.get(world)
    if wb is None:
        return None
    if region == "light":
        return wb + LIGHT_OFFSET + index * SLOT_SIZE + COMP_BYTE
    elif region == "dark":
        if world == 6:
            return wb + W6_DARK_OFFSET + index * SLOT_SIZE + COMP_BYTE
        return wb + DARK_OFFSET + index * SLOT_SIZE + COMP_BYTE
    return None

def time_addr(world, index, region):
    """Get IL time address offset from save_ptr."""
    if region == "warp":
        warp_base = WARP_BASES.get(world)
        if warp_base is None:
            return None
        return warp_base + index * SLOT_SIZE + TIME_BYTE
    wb = WORLD_BASES.get(world)
    if wb is None:
        return None
    if region == "light":
        return wb + LIGHT_OFFSET + index * SLOT_SIZE + TIME_BYTE
    elif region == "dark":
        if world == 6:
            return wb + W6_DARK_OFFSET + index * SLOT_SIZE + TIME_BYTE
        return wb + DARK_OFFSET + index * SLOT_SIZE + TIME_BYTE
    return None

def slot_addr(world, index, region):
    """Get slot base address offset from save_ptr."""
    if region == "warp":
        warp_base = WARP_BASES.get(world)
        if warp_base is None:
            return None
        return warp_base + index * SLOT_SIZE
    wb = WORLD_BASES.get(world)
    if wb is None:
        return None
    if region == "light":
        return wb + LIGHT_OFFSET + index * SLOT_SIZE
    elif region == "dark":
        if world == 6:
            return wb + W6_DARK_OFFSET + index * SLOT_SIZE
        return wb + DARK_OFFSET + index * SLOT_SIZE
    return None



# Bandage grant targets (levels WITHOUT bandages, safe for count manipulation)


# Levels that have bandages (world -> set of 1-based level nums)
LIGHT_BANDAGE_LEVELS = {
    1: {4, 7, 9, 11, 13, 18, 20},
    2: {2, 5, 10, 13, 16, 18, 20},
    3: {1, 2, 4, 10, 11, 18, 20},
    4: {2, 6, 9, 13, 16, 17, 20},
    5: {3, 5, 9, 16, 18, 20},
}

DARK_BANDAGE_LEVELS = {
    1: {3, 5, 10, 14, 15, 19},
    2: {4, 6, 7, 10, 12, 15, 16},
    3: {3, 5, 6, 7, 14, 16, 19},
    4: {6, 8, 10, 14, 18, 19},
    5: {4, 5, 8, 10, 11, 17, 18},
}

BANDAGE_GRANT_TARGETS = []
for w in range(1, 6):
    has = LIGHT_BANDAGE_LEVELS.get(w, set())
    for li in range(20):
        lv1 = li + 1
        if lv1 not in has:
            BANDAGE_GRANT_TARGETS.append((w, li, "light"))
# Add dark world non-bandage levels as additional targets
for w in range(1, 6):
    for li in range(20):
        BANDAGE_GRANT_TARGETS.append((w, li, "dark"))



# Par times for A+ detection (from SMBDatabase.cs)


# Par times extracted from SMBDatabase.cs ParTimes array
PAR_TIMES = {
    # World 1 Light (Forest)
    (1, 0, "light"): 3.0, (1, 1, "light"): 5.0, (1, 2, "light"): 9.0,
    (1, 3, "light"): 9.0, (1, 4, "light"): 11.0, (1, 5, "light"): 7.0,
    (1, 6, "light"): 5.0, (1, 7, "light"): 4.5, (1, 8, "light"): 8.0,
    (1, 9, "light"): 7.5, (1, 10, "light"): 8.0, (1, 11, "light"): 7.0,
    (1, 12, "light"): 7.0, (1, 13, "light"): 8.0, (1, 14, "light"): 10.0,
    (1, 15, "light"): 9.0, (1, 16, "light"): 9.0, (1, 17, "light"): 4.0,
    (1, 18, "light"): 20.0, (1, 19, "light"): 22.0,
    # World 1 Dark
    (1, 0, "dark"): 3.0, (1, 1, "dark"): 4.5, (1, 2, "dark"): 10.0,
    (1, 3, "dark"): 12.0, (1, 4, "dark"): 10.0, (1, 5, "dark"): 7.0,
    (1, 6, "dark"): 5.0, (1, 7, "dark"): 6.0, (1, 8, "dark"): 11.0,
    (1, 9, "dark"): 11.0, (1, 10, "dark"): 13.0, (1, 11, "dark"): 12.0,
    (1, 12, "dark"): 12.0, (1, 13, "dark"): 14.0, (1, 14, "dark"): 18.0,
    (1, 15, "dark"): 17.0, (1, 16, "dark"): 12.0, (1, 17, "dark"): 5.0,
    (1, 18, "dark"): 17.0, (1, 19, "dark"): 25.0,
    # World 1 Warp
    (1, 0, "warp"): 5.0, (1, 1, "warp"): 5.0, (1, 2, "warp"): 5.0,
    (1, 3, "warp"): 5.0, (1, 4, "warp"): 5.0, (1, 5, "warp"): 5.0,
    (1, 6, "warp"): 5.0, (1, 7, "warp"): 5.0, (1, 8, "warp"): 5.0,
    (1, 9, "warp"): 5.0, (1, 10, "warp"): 5.0, (1, 11, "warp"): 5.0,
    # World 2 Light (Hospital)
    (2, 0, "light"): 11.0, (2, 1, "light"): 10.5, (2, 2, "light"): 14.0,
    (2, 3, "light"): 9.5, (2, 4, "light"): 16.0, (2, 5, "light"): 15.0,
    (2, 6, "light"): 19.0, (2, 7, "light"): 25.0, (2, 8, "light"): 11.0,
    (2, 9, "light"): 12.0, (2, 10, "light"): 9.0, (2, 11, "light"): 11.0,
    (2, 12, "light"): 10.0, (2, 13, "light"): 16.0, (2, 14, "light"): 19.0,
    (2, 15, "light"): 15.0, (2, 16, "light"): 14.0, (2, 17, "light"): 16.5,
    (2, 18, "light"): 14.0, (2, 19, "light"): 24.0,
    # World 2 Dark
    (2, 0, "dark"): 17.0, (2, 1, "dark"): 14.0, (2, 2, "dark"): 13.0,
    (2, 3, "dark"): 14.0, (2, 4, "dark"): 20.0, (2, 5, "dark"): 19.0,
    (2, 6, "dark"): 30.0, (2, 7, "dark"): 33.0, (2, 8, "dark"): 14.0,
    (2, 9, "dark"): 13.0, (2, 10, "dark"): 12.5, (2, 11, "dark"): 22.5,
    (2, 12, "dark"): 11.0, (2, 13, "dark"): 31.0, (2, 14, "dark"): 32.0,
    (2, 15, "dark"): 16.0, (2, 16, "dark"): 12.0, (2, 17, "dark"): 17.0,
    (2, 18, "dark"): 26.0, (2, 19, "dark"): 36.0,
    # World 2 Warp
    (2, 0, "warp"): 5.0, (2, 1, "warp"): 5.0, (2, 2, "warp"): 5.0,
    (2, 3, "warp"): 5.0, (2, 4, "warp"): 5.0, (2, 5, "warp"): 5.0,
    (2, 6, "warp"): 5.0, (2, 7, "warp"): 5.0, (2, 8, "warp"): 5.0,
    (2, 9, "warp"): 5.0, (2, 10, "warp"): 5.0, (2, 11, "warp"): 5.0,
    # World 3 Light (Salt Factory)
    (3, 0, "light"): 9.5, (3, 1, "light"): 8.3, (3, 2, "light"): 16.0,
    (3, 3, "light"): 12.0, (3, 4, "light"): 12.2, (3, 5, "light"): 4.5,
    (3, 6, "light"): 12.4, (3, 7, "light"): 8.3, (3, 8, "light"): 12.5,
    (3, 9, "light"): 10.5, (3, 10, "light"): 9.0, (3, 11, "light"): 11.6,
    (3, 12, "light"): 15.8, (3, 13, "light"): 14.8, (3, 14, "light"): 14.8,
    (3, 15, "light"): 14.8, (3, 16, "light"): 10.5, (3, 17, "light"): 17.0,
    (3, 18, "light"): 17.0, (3, 19, "light"): 20.0,
    # World 3 Dark
    (3, 0, "dark"): 23.0, (3, 1, "dark"): 16.0, (3, 2, "dark"): 16.5,
    (3, 3, "dark"): 20.0, (3, 4, "dark"): 28.0, (3, 5, "dark"): 20.0,
    (3, 6, "dark"): 15.5, (3, 7, "dark"): 17.5, (3, 8, "dark"): 21.0,
    (3, 9, "dark"): 18.0, (3, 10, "dark"): 24.0, (3, 11, "dark"): 11.6,
    (3, 12, "dark"): 40.0, (3, 13, "dark"): 18.0, (3, 14, "dark"): 27.0,
    (3, 15, "dark"): 24.0, (3, 16, "dark"): 11.5, (3, 17, "dark"): 17.0,
    (3, 18, "dark"): 17.0, (3, 19, "dark"): 25.5,
    # World 3 Warp
    (3, 0, "warp"): 5.0, (3, 1, "warp"): 5.0, (3, 2, "warp"): 5.0,
    (3, 3, "warp"): 5.0, (3, 4, "warp"): 5.0, (3, 5, "warp"): 5.0,
    (3, 6, "warp"): 5.0, (3, 7, "warp"): 5.0, (3, 8, "warp"): 5.0,
    (3, 9, "warp"): 5.0, (3, 10, "warp"): 5.0, (3, 11, "warp"): 5.0,
    # World 4 Light (Hell)
    (4, 0, "light"): 11.0, (4, 1, "light"): 23.0, (4, 2, "light"): 11.5,
    (4, 3, "light"): 11.5, (4, 4, "light"): 12.0, (4, 5, "light"): 8.0,
    (4, 6, "light"): 17.0, (4, 7, "light"): 16.0, (4, 8, "light"): 6.0,
    (4, 9, "light"): 15.0, (4, 10, "light"): 12.5, (4, 11, "light"): 10.8,
    (4, 12, "light"): 11.5, (4, 13, "light"): 17.5, (4, 14, "light"): 9.0,
    (4, 15, "light"): 12.0, (4, 16, "light"): 12.0, (4, 17, "light"): 24.5,
    (4, 18, "light"): 14.0, (4, 19, "light"): 22.0,
    # World 4 Dark
    (4, 0, "dark"): 19.0, (4, 1, "dark"): 16.5, (4, 2, "dark"): 12.0,
    (4, 3, "dark"): 17.5, (4, 4, "dark"): 14.0, (4, 5, "dark"): 19.0,
    (4, 6, "dark"): 18.0, (4, 7, "dark"): 19.0, (4, 8, "dark"): 10.5,
    (4, 9, "dark"): 17.0, (4, 10, "dark"): 16.5, (4, 11, "dark"): 18.5,
    (4, 12, "dark"): 23.0, (4, 13, "dark"): 20.0, (4, 14, "dark"): 11.0,
    (4, 15, "dark"): 11.5, (4, 16, "dark"): 18.0, (4, 17, "dark"): 29.0,
    (4, 18, "dark"): 14.0, (4, 19, "dark"): 31.0,
    # World 4 Warp
    (4, 0, "warp"): 5.0, (4, 1, "warp"): 5.0, (4, 2, "warp"): 5.0,
    (4, 3, "warp"): 5.0, (4, 4, "warp"): 5.0, (4, 5, "warp"): 5.0,
    (4, 6, "warp"): 5.0, (4, 7, "warp"): 5.0, (4, 8, "warp"): 5.0,
    (4, 9, "warp"): 5.0, (4, 10, "warp"): 5.0, (4, 11, "warp"): 5.0,
    # World 5 Light (Rapture)
    (5, 0, "light"): 22.0, (5, 1, "light"): 13.0, (5, 2, "light"): 18.0,
    (5, 3, "light"): 13.5, (5, 4, "light"): 12.5, (5, 5, "light"): 11.0,
    (5, 6, "light"): 23.0, (5, 7, "light"): 20.0, (5, 8, "light"): 19.5,
    (5, 9, "light"): 15.5, (5, 10, "light"): 18.5, (5, 11, "light"): 16.0,
    (5, 12, "light"): 20.0, (5, 13, "light"): 30.5, (5, 14, "light"): 13.5,
    (5, 15, "light"): 30.0, (5, 16, "light"): 23.0, (5, 17, "light"): 17.0,
    (5, 18, "light"): 29.0, (5, 19, "light"): 32.0,
    # World 5 Dark
    (5, 0, "dark"): 30.0, (5, 1, "dark"): 17.0, (5, 2, "dark"): 35.0,
    (5, 3, "dark"): 27.0, (5, 4, "dark"): 18.0, (5, 5, "dark"): 12.0,
    (5, 6, "dark"): 15.0, (5, 7, "dark"): 26.0, (5, 8, "dark"): 40.0,
    (5, 9, "dark"): 15.0, (5, 10, "dark"): 25.0, (5, 11, "dark"): 26.0,
    (5, 12, "dark"): 25.0, (5, 13, "dark"): 60.0, (5, 14, "dark"): 15.0,
    (5, 15, "dark"): 32.0, (5, 16, "dark"): 27.0, (5, 17, "dark"): 19.0,
    (5, 18, "dark"): 41.0, (5, 19, "dark"): 48.0,
    # World 5 Warp
    (5, 0, "warp"): 5.0, (5, 1, "warp"): 5.0, (5, 2, "warp"): 5.0,
    (5, 3, "warp"): 5.0, (5, 4, "warp"): 5.0, (5, 5, "warp"): 5.0,
    (5, 6, "warp"): 5.0, (5, 7, "warp"): 5.0, (5, 8, "warp"): 5.0,
    (5, 9, "warp"): 5.0, (5, 10, "warp"): 5.0, (5, 11, "warp"): 5.0,
    # World 6 Light (The End)
    (6, 0, "light"): 30.0, (6, 1, "light"): 44.0, (6, 2, "light"): 34.0,
    (6, 3, "light"): 33.0, (6, 4, "light"): 44.0,
    # World 6 Dark
    (6, 0, "dark"): 40.0, (6, 1, "dark"): 50.0, (6, 2, "dark"): 70.0,
    (6, 3, "dark"): 50.0, (6, 4, "dark"): 60.0,
    # World 7 Light (Cotton Alley)
    (7, 0, "light"): 11.0, (7, 1, "light"): 13.0, (7, 2, "light"): 23.0,
    (7, 3, "light"): 26.0, (7, 4, "light"): 30.0, (7, 5, "light"): 7.5,
    (7, 6, "light"): 10.5, (7, 7, "light"): 26.0, (7, 8, "light"): 21.0,
    (7, 9, "light"): 32.0, (7, 10, "light"): 18.0, (7, 11, "light"): 11.6,
    (7, 12, "light"): 22.0, (7, 13, "light"): 40.0, (7, 14, "light"): 24.0,
    (7, 15, "light"): 20.0, (7, 16, "light"): 20.0, (7, 17, "light"): 21.0,
    (7, 18, "light"): 17.0, (7, 19, "light"): 45.0,
    # World 7 Dark
    (7, 0, "dark"): 60.0, (7, 1, "dark"): 60.0, (7, 2, "dark"): 60.0,
    (7, 3, "dark"): 60.0, (7, 4, "dark"): 60.0, (7, 5, "dark"): 60.0,
    (7, 6, "dark"): 60.0, (7, 7, "dark"): 60.0, (7, 8, "dark"): 60.0,
    (7, 9, "dark"): 60.0, (7, 10, "dark"): 60.0, (7, 11, "dark"): 60.0,
    (7, 12, "dark"): 60.0, (7, 13, "dark"): 60.0, (7, 14, "dark"): 60.0,
    (7, 15, "dark"): 60.5, (7, 16, "dark"): 60.5, (7, 17, "dark"): 60.0,
    (7, 18, "dark"): 60.0, (7, 19, "dark"): 60.0,
}

def get_par_time(world, level_0based, region):
    """Get par time for A+ detection. Returns None if not found."""
    return PAR_TIMES.get((world, level_0based, region))

def is_a_plus(time_val, world, level_0based, region):
    """Check if a time qualifies for A+."""
    par = get_par_time(world, level_0based, region)
    if par is None or time_val <= 0:
        return False
    return time_val <= par



# Helper: type_to_region


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



# Achievement location names


# Warp zone milestones
WARP_MILESTONE_NAMES = {
    1:  "Nostalgia (Unlock a retro warp zone)",
    5:  "Living In the Past (Complete 5 retro warp zones)",
    10: "Old School (Complete 10 retro warp zones)",
    20: "Retro Rampage (Complete all retro warp zones)",
}

# World clear achievements
WORLD_CLEAR_NAMES = {
    (6, "light"): "The End (Beat Chapter 6 Light World)",
    (6, "dark"):  "The Real End (Beat Chapter 6 Dark World)",
    (7, "light"): "Suffragette (Beat Chapter 7 Light World)",
    (7, "dark"):  "Seneca Falls (Beat Chapter 7 Dark World)",
}

# Bandage milestone achievements
BANDAGE_MILESTONE_NAMES = {
    10:  "I Have Crabs! (Collect 10 Bandages)",
    30:  "Metalhead (Collect 30 Bandages)",
    50:  "I Smell something Fishy... (Collect 50 Bandages)",
    70:  "MS PAINT RULZ! (Collect 70 Bandages)",
    90:  "Vx6 (Collect 90 Bandages)",
    100: "Accidental Arsonist (Collect 100 Bandages)",
}

# Petaphile achievement (can't be auto-detected from memory)
PETAPHILE_NAME = 'Well look at you! (Type "petaphile" on the character select screen)'


# Speedrun achievement data


# Speedrun achievements: world -> (threshold_seconds, name)
SPEEDRUN_ACHIEVEMENTS = {
    1: (265.0, "Rare (Speedrun The Forest in 265 Seconds)"),
    2: (460.0, "Medium Rare (Speedrun The Hospital in 460 seconds)"),
    3: (515.0, "Medium (Speedrun The Salt Factory in 515 seconds)"),
    4: (500.0, "Medium Well (Speedrun Hell in 500 seconds)"),
    5: (690.0, "Well Done (Speedrun The Rapture in 690 seconds)"),
}


# Deathless achievement data


# Deathless achievements: (world, region) -> name
DEATHLESS_ACHIEVEMENTS = {
    (1, "light"): "Wood Boy (Complete The Forest Light World Deathless)",
    (2, "light"): "Needle Boy (Complete The Hospital Light World Deathless)",
    (3, "light"): "Salt Boy (Complete The Salt Factory Light World Deathless)",
    (4, "light"): "Brimstone Boy (Complete Hell Light World Deathless)",
    (5, "light"): "Maggot Boy (Complete The Rapture Light World Deathless)",
    (6, "light"): "Dead Boy (Complete The End Light World Deathless)",
    (7, "light"): "Girl Boy (Complete The Cotton Alley Light World Deathless)",
    (1, "dark"):  "Squirrel Boy (Complete The Forest Dark World Deathless)",
    (2, "dark"):  "Blood Clot Boy (Complete The Hospital Dark World Deathless)",
    (3, "dark"):  "Missile Boy (Complete The Salt Factory Dark World Deathless)",
    (4, "dark"):  "Demon Boy (Complete Hell Dark World Deathless)",
    (5, "dark"):  "Zombie Boy (Complete The Rapture Dark World Deathless)",
    (6, "dark"):  "Dr. Fetus Boy (Complete The End Dark World Deathless)",
    (7, "dark"):  "Impossible Boy (Complete The Cotton Alley Dark World Deathless)",
}

# Death counter offset from save_ptr
DEATH_COUNT_OFFSET = 0x38AC


# Xmas level data


XMAS_LEVEL_NAMES = {
    1: "Fruit Cake",
    2: "Socks",
    3: "Sweater",
    4: "Underwear",
    5: "Lump of Coal",
}

def xmas_completion_name(level_1based):
    """Location name for xmas level completion."""
    name = XMAS_LEVEL_NAMES.get(level_1based)
    return f"I-{level_1based} {name}" if name else None

def xmas_aplus_name(level_1based):
    """Location name for xmas A+ rank."""
    name = XMAS_LEVEL_NAMES.get(level_1based)
    return f"I-{level_1based} {name} (A+ Rank)" if name else None

def xmas_bandage_name(level_1based):
    """Location name for xmas bandage."""
    name = XMAS_LEVEL_NAMES.get(level_1based)
    return f"I-{level_1based} {name} (Bandage)" if name else None

# Xmas achievements
XMAS_ACHIEVEMENT_NAMES = [
    "The Kids Xmas!",
    "The Golden Gift!",
]

# Xmas world number in game memory (needs verification - likely 0 or 8)
XMAS_WORLD = 0  # TODO: verify from memory research
