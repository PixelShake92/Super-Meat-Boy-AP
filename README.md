# 🥩 Super Meat Boy — Archipelago Randomizer

A full [Archipelago](https://archipelago.gg) multiworld randomizer for **Super Meat Boy** (PC/Steam).

Shuffle level access, boss keys, characters, bandages, warp zones, and more across your multiworld. Race through randomized worlds while trading items with friends playing completely different games.

---

## Features

- **Full chapter randomizer** — World access is gated by Chapter Keys received from the multiworld
- **Boss key system** — Collect boss keys to unlock boss fights, with configurable requirements
- **Dark world integration** — A+ Rank items unlock dark world counterparts of each level
- **Bandage checks** — Bandage collectibles become location checks sent to the multiworld
- **Warp zone support** — All warp zones (including character warps and dark warps) are tracked
- **Achievement locations** — World clears, speedrun times, and deathless runs as optional checks
- **Character shuffle** — Meat Boy, Bandage Girl, and unlockable characters distributed through the pool
- **Multiple goal options** — Beat Larries, clear the light world, conquer the dark world, and more
- **Boss token gating** — Optional progressive boss access tokens
- **Real-time detection** — Level completions, A+ grades, bandages, and boss defeats detected instantly during gameplay

---

## Quick Start

1. **Install the APWorld** — Copy `super_meat_boy.apworld` to your Archipelago `custom_worlds` folder
2. **Back up your saves** — Copy `savegame.dat` from the Super Meat Boy `UserData` folder
3. **Start a fresh save** in Super Meat Boy
4. **Run the client** — Launch `SMB_Archipelago_Client.exe`
5. **Connect** to your Archipelago server and play!

For detailed instructions, see the [Setup Guide](SETUP_GUIDE.md).

---

## Downloads

Grab the latest release from the [Releases](../../releases) page:

- `SMB_Archipelago_Client.exe` — Standalone client (no Python required)
- `super_meat_boy.apworld` — Archipelago world package
- `smb_apworld_data.py` — Game data module (bundled with client, also available separately)

---

## How It Works

The client reads Super Meat Boy's memory in real-time to detect player progress and communicates with the Archipelago server to send and receive items.

**Sending checks:**
- Completing a level (light or dark)
- Collecting a bandage
- Achieving an A+ grade
- Beating a boss
- Completing a warp zone
- World clears, speedruns, and deathless achievements

**Receiving items:**
- Chapter Keys (unlock world access)
- Boss Keys (unlock boss fights)
- A+ Rank items (unlock dark world levels)
- Characters (Meat Boy, Bandage Girl, etc.)
- Boss Tokens (optional progressive boss gating)
- Bandages (granted in-game for milestone tracking)

---

## Configuration

Customise your experience through YAML options:

| Option | Description | Default |
|--------|-------------|---------|
| `goal` | Win condition | Beat Larries |
| `dark_world` | Include dark world levels | Off |
| `bandages` | Include bandage collectibles | Off |
| `boss_req` | Boss keys needed per boss | 17 |
| `boss_tokens` | Enable progressive boss tokens | Off |
| `achievements` | Include world clears and challenges | Off |
| `deathless` | Include deathless run achievements | Off |
| `speedrun` | Include speedrun achievements | Off |

---

## Requirements

- **Super Meat Boy** (Steam, PC)
- **Archipelago** v0.6.4 or later
- **Windows** (memory reading requires Windows)

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Game not detected | Make sure SMB is running, click Refresh |
| Client won't launch | Run as Administrator |
| Checks not sending | Return to level select — the client sweeps on map screen |
| Dark levels not appearing | You need the A+ Rank item from the multiworld |
| Boss door locked | Check your boss key count in the client log |
| Stuck with no available checks | Check with other players — you may need items from them |

See the [Setup Guide](SETUP_GUIDE.md) for more details.

---

## Building from Source

If you want to run from source instead of the exe:

```bash
pip install pymem websockets
python smb_ap_client.py
```

To build the standalone exe:

```bash
pip install pyinstaller
pyinstaller smb_ap_client.spec
```

---

## Credits

- **Super Meat Boy** by Team Meat
- **Archipelago** multiworld framework — [archipelago.gg](https://archipelago.gg)

This project is not affiliated with or endorsed by Team Meat. Super Meat Boy is a trademark of Team Meat.

This is a fan-made tool for use with the Archipelago multiworld randomizer framework.
