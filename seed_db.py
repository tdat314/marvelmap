import sqlite3, time

con = sqlite3.connect("ttk.db")
con.executescript(open("schema.sql").read())

# Ensure baseline rows
con.execute("INSERT OR IGNORE INTO rep_global(id,score) VALUES(1,0)")
now = int(time.time())
con.execute("""INSERT OR IGNORE INTO global_timer(id,label,ticks,max_ticks,note,updated_at)
               VALUES(1,'ADVENT',0,6,'',?)""", (now,))

# Regions
regions = [
  ("north-america","",960,512, 0.07,0.38,0.40,0.65),
  ("south-america","",960,512, 0.20,0.60,0.40,0.92),
  ("europe","",960,512, 0.45,0.32,0.60,0.48),
  ("africa","",960,512, 0.46,0.48,0.63,0.78),
  ("east-asia","",960,512, 0.67,0.33,0.85,0.60),
  ("oceania","",960,512, 0.80,0.65,0.95,0.90),
]
for r in regions:
    con.execute("""INSERT OR IGNORE INTO regions(name,img,w,h,x0,y0,x1,y1)
                   VALUES(?,?,?,?,?,?,?,?)""", r)

# Example missions
missions = [
 ("Grand Central Singularity","cosmic,investigate,europe,standard","open","standard","Europe",
  "A shimmering distortion opens above a central transport hub.",
  "A.I.M. field-tests a micro-singularity; Boss enters on Beat 3.",
  0.48,0.35, now,now),
 ("Dockside Heist","tech,heist,north-america,easy","scheduled","easy","North America",
  "Masked crew moving Stark crates at night. Intercept quietly.",
  "Hydra front; elite tech jams powers; cranes as hazards.",
  0.28,0.54, now,now)
]
con.executemany("""INSERT INTO missions
 (title,tags,status,difficulty,region_hint,brief,dossier,x,y,created_at,updated_at)
 VALUES (?,?,?,?,?,?,?,?,?,?,?)""", missions)

con.commit()
con.close()
print("DB seeded: ttk.db")
