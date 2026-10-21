"""Shared constants for LivestockChain."""
SPECIES = ["Cow", "Buffalo", "Goat", "Sheep", "Bull", "Calf"]
MILK_SPECIES = ["Cow", "Buffalo", "Goat"]          # species that have milk tracking
PLURAL = {"Cow": "Cows", "Buffalo": "Buffaloes", "Goat": "Goats", "Sheep": "Sheep", "Bull": "Bulls", "Calf": "Calves"}
TAG_PREFIX = {"Cow": "CW", "Buffalo": "BF", "Goat": "GT", "Sheep": "SH", "Bull": "BL", "Calf": "CF"}
DEFAULT_MILK_RATE = {"Cow": 120.0, "Buffalo": 150.0, "Goat": 200.0}   # Rs per litre, editable assumptions
