"""DUMMY demo data (mixed herd). Replace with real data from your Mianwali farm interviews later."""
import random
from datetime import date, timedelta
import db, service
from blockchain import Chain
from livestock import MILK_SPECIES, DEFAULT_MILK_RATE

HERD = [  # tag, name, species, breed, age_months, weight_kg, shed
    ("BF-001","Lali","Buffalo","Nili-Ravi",54,610,"Dairy Shed A"), ("BF-002","Moti","Buffalo","Nili-Ravi",48,590,"Dairy Shed A"),
    ("BF-003","Kali","Buffalo","Kundi",60,640,"Dairy Shed A"), ("BF-004","Sohni","Buffalo","Nili-Ravi",44,580,"Dairy Shed A"),
    ("CW-001","Chitti","Cow","Sahiwal",40,420,"Dairy Shed A"), ("CW-002","Rani","Cow","Sahiwal",30,380,"Dairy Shed A"),
    ("CW-003","Gulabo","Cow","Cholistani",36,390,"Dairy Shed A"),
    ("BL-001","Sheru","Bull","Sahiwal",48,680,"Breeding Pen"), ("CF-001","Bholi","Calf","Cross-bred",6,110,"Dairy Shed A"),
    ("GT-001","Mithi","Goat","Beetal",24,48,"Goat Shed B"), ("GT-002","Heera","Goat","Beetal",30,52,"Goat Shed B"),
    ("GT-003","Noori","Goat","Dera Din Panah",20,42,"Goat Shed B"), ("GT-004","Chandni","Goat","Beetal",26,46,"Goat Shed B"),
    ("GT-005","Badal","Goat","Teddy",14,34,"Goat Shed B"),
    ("SH-001","Moongi","Sheep","Kajli",22,55,"Sheep Shed C"), ("SH-002","Dhola","Sheep","Lohi",28,62,"Sheep Shed C"),
    ("SH-003","Phuli","Sheep","Thalli",18,44,"Sheep Shed C"), ("SH-004","Jugnu","Sheep","Kajli",16,48,"Sheep Shed C"),
]
BASE = {"Buffalo": 9, "Cow": 11, "Goat": 1.9}

def seed(chain=None):
    db.init()
    if db.q("SELECT COUNT(*) n FROM animals")[0]["n"] > 0:
        return
    chain = chain or Chain()
    random.seed(7)
    today = date.today()
    for tag, name, sp, br, age, w, shed in HERD:
        db.run("INSERT INTO animals(tag,name,species,breed,age_months,weight_kg,owner,created,shed) VALUES(?,?,?,?,?,?,?,?,?)",
               (tag, name, sp, br, age, w, "Demo Farm Owner", str(today - timedelta(days=200)), shed))
        service.add_record(chain, tag, "REGISTRATION", today - timedelta(days=200), f"{sp} {br}, {age} months, {w} kg, {shed}", "Demo Farm Owner")
        vaccine = "PPR vaccine, batch PPR-2026-B" if sp in ("Goat", "Sheep") else "FMD vaccine, batch FMD-2026-A"
        service.add_record(chain, tag, "VACCINATION", today - timedelta(days=60), vaccine, "Dr. Demo Vet",
                           next_due=today + timedelta(days=random.randint(-5, 120)))
    service.add_record(chain, "CW-001", "TREATMENT", today - timedelta(days=20), "Mastitis, antibiotic course 5 days", "Dr. Demo Vet")
    service.add_record(chain, "GT-002", "CHECKUP", today - timedelta(days=12), "Routine checkup, healthy", "Dr. Demo Vet")
    for d in range(30):
        day = str(today - timedelta(days=d)); revenue = 0
        for tag, _, sp, *_ in HERD:
            if sp in MILK_SPECIES:
                lit = round(BASE[sp] + random.uniform(-1.5, 2.0) * (0.2 if sp == "Goat" else 1), 1)
                db.run("INSERT INTO milk(tag,day,liters) VALUES(?,?,?)", (tag, day, lit))
                revenue += lit * DEFAULT_MILK_RATE[sp]
        db.run("INSERT INTO expenses(day,category,amount,tag,note) VALUES(?,?,?,?,?)", (day, "Feed", random.randint(8500, 10500), None, "daily fodder and feed"))
        db.run("INSERT INTO income(day,source,amount,tag) VALUES(?,?,?,?)", (day, "Milk sale", round(revenue * 0.97), None))
    db.run("INSERT INTO expenses(day,category,amount,tag,note) VALUES(?,?,?,?,?)", (str(today - timedelta(days=20)), "Medicine", 3500, "CW-001", "mastitis treatment"))
    db.run("INSERT INTO expenses(day,category,amount,tag,note) VALUES(?,?,?,?,?)", (str(today - timedelta(days=10)), "Labour", 30000, None, "monthly wages"))
