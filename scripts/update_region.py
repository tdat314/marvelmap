# scripts/update_region.py
import sqlite3, sys

DB = "ttk.db"

def update_region(name, img=None, w=None, h=None, x0=None, y0=None, x1=None, y1=None):
    con = sqlite3.connect(DB)
    cur = con.cursor()
    fields, vals = [], []
    for k,v in dict(img=img, w=w, h=h, x0=x0, y0=y0, x1=x1, y1=y1).items():
        if v is not None:
            fields.append(f"{k}=?")
            vals.append(v)
    if not fields:
        print("Nothing to update."); return
    vals.append(name)
    cur.execute(f"UPDATE regions SET {', '.join(fields)} WHERE name=?", vals)
    con.commit()
    print("Rows changed:", con.total_changes)
    print(cur.execute("SELECT name,img,w,h,x0,y0,x1,y1 FROM regions WHERE name=?", (name,)).fetchone())
    con.close()

if __name__ == "__main__":
    # Example usage (edit these)
    update_region(
        name="north-america",
        img="north-america.jpg",
        w=1920, h=1080,
        x0=0.07, y0=0.38, x1=0.40, y1=0.65
    )
