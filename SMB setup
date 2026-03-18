# Super Meat Boy — Archipelago Setup Guide

Welcome to the Super Meat Boy randomizer for Archipelago! This guide will get you from zero to playing in a few minutes.

---

## What You Need

- **Super Meat Boy** on Steam (PC version)
- **Archipelago** — download from [archipelago.gg](https://archipelago.gg)
- **SMB Archipelago Client** — `SMB_Archipelago_Client.exe` (included in this release)
- **SMB APWorld file** — `super_meat_boy.apworld` (included in this release)

---

## First Time Setup

### 1. Install the APWorld

Copy `super_meat_boy.apworld` into your Archipelago custom worlds folder or double click to install it for you:

```
C:\ProgramData\Archipelago\custom_worlds\
```

If the `custom_worlds` folder doesn't exist, create it.

### 2. Place the Client

Put `SMB_Archipelago_Client.exe` somewhere convenient — the Super Meat Boy game folder works fine:

```
C:\Program Files (x86)\Steam\steamapps\common\Super Meat Boy\
```

### 3. Generate a Game

Open the Archipelago Launcher and click **Generate**. You can use the default settings or customise your YAML — see the Options section below for what's available.

If you're playing multiworld with friends, the host generates the game and gives you the room details.

### 4. Back Up Your Save

The randomizer requires a **fresh save file**, so back up your existing saves first. Super Meat Boy saves are located at:

```
C:\Program Files (x86)\Steam\steamapps\common\Super Meat Boy\UserData\
```

The file you're looking for is `savegame.dat`. Copy it somewhere safe before starting. To restore your original save later, just copy it back.

> **Important:** Each randomizer seed needs its own clean save. Don't reuse saves between different seeds — delete or rename `savegame.dat` and let the game create a new one.

---

## Playing

### 1. Start Super Meat Boy

Launch the game from Steam as normal. **Start a new save file** — the randomizer needs a clean save to work properly.

### 2. Launch the Client

Run `SMB_Archipelago_Client.exe`. It will automatically detect the running game.

### 3. Connect

Enter your server details:

- **Server**: The Archipelago server address (e.g., `archipelago.gg:12345`)
- **Slot Name**: Your player name from the YAML
- **Password**: Only if the room has one

Click **Connect**. The client will sync your progress and you're good to go.

### 4. Play!

The client runs in the background and handles everything automatically:

- **Completing levels** sends checks to the server
- **Collecting bandages** sends checks (if enabled)
- **Getting A+ grades** sends checks and unlocks dark world levels
- **Beating bosses** sends checks and triggers cutscenes
- **Completing warp zones** sends checks
- Items you receive from other players are applied automatically but bandage tracking is still weird. Characters are items in the multi so the bandages don't really matter but it does annoy me. 

---

## YAML Options

Here are the main settings you can tweak in your YAML:

| Option | What It Does |
|--------|-------------|
| `goal` | Win condition — beat Larries, clear light world, clear dark world, etc. |
| `dark_world` | Enables dark world levels as locations (A+ items unlock them) |
| `bandages` | Adds bandage collectibles as location checks |
| `boss_req` | How many boss keys needed to fight each boss (default: 17) |
| `boss_tokens` | Adds boss tokens that gate access to later bosses |
| `achievements` | Adds world clears, speedruns, and deathless runs as checks |

---

## Troubleshooting

**"Game not detected"**
Make sure Super Meat Boy is running before launching the client. Click **Refresh** to re-check.

**Client crashes on launch**
Right-click the exe and run as Administrator. The client needs memory access to the game process.

**Checks not sending**
Return to the level select screen — the client does a full sweep whenever you're on the map. If something was missed during gameplay, this catches it.

**Stuck on a world you can't access**
You need the Chapter Key item for that world. Check with other players or keep clearing your available locations.

**Dark levels not appearing**
You need the corresponding A+ Rank item from the multiworld. Getting an A+ time in-game alone won't unlock the dark version — you need the item.

**Boss door won't open**
You need enough Boss Keys. The client shows your progress (e.g., "Chapter 2 Boss Key (12/17)") in the log.

---

## Tips

- **Check your log.** The client window shows everything — items received, checks sent, and any issues.
- **Connection settings save automatically.** You won't need to re-enter them next time.
- **You can reconnect at any time.** Your progress is tracked server-side. If the client disconnects, just reconnect and it picks up where you left off.
- **New save file each seed.** Don't reuse save files between different randomizer seeds.

---

## Need Help?

Jump into the Archipelago Discord and look for the Super Meat Boy channel. Myself and other players are happy to help!

---

*Now go save Bandage Girl. Or Meat Boy. Or whoever the randomizer decides needs saving.*
