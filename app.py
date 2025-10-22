import os, sqlite3, json, time
from flask import Flask, render_template, request, redirect, url_for, session, abort

# Optional .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

APP_SECRET = os.getenv("SECRET_KEY", "dev-secret")
GM_PASSWORD = os.getenv("GM_ADMIN_PASSWORD", "changeme")

DB_PATH = "ttk.db"
GLOBAL_IMG = os.getenv("GLOBAL_IMG", "global.jpg")
GLOBAL_W = int(os.getenv("GLOBAL_W", "960"))
GLOBAL_H = int(os.getenv("GLOBAL_H", "512"))

app = Flask(__name__)
app.secret_key = APP_SECRET

# ---------- DB ----------
def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def is_gm():
    return bool(session.get("is_gm"))

def get_timer():
    con = db()
    row = con.execute("SELECT * FROM global_timer WHERE id=1").fetchone()
    con.close()
    if not row:
        return {"label":"ADVENT","ticks":0,"max_ticks":6,"note":"","updated_at":int(time.time())}
    return dict(row)

def fetch_missions(include_gm: bool):
    cols_public = "id,title,tags,status,difficulty,region_hint,brief,x,y,created_at,updated_at"
    cols = cols_public + (",dossier" if include_gm else "")
    con = db()
    rows = [dict(r) for r in con.execute(f"SELECT {cols} FROM missions ORDER BY updated_at DESC")]
    con.close()
    if not include_gm:
        for r in rows:
            r.pop("dossier", None)
    return rows

def fetch_mission(mid: int, include_gm: bool):
    cols_public = "id,title,tags,status,difficulty,region_hint,brief,x,y,created_at,updated_at"
    cols = cols_public + (",dossier" if include_gm else "")
    con = db()
    row = con.execute(f"SELECT {cols} FROM missions WHERE id=?", (mid,)).fetchone()
    con.close()
    if not row:
        return None
    d = dict(row)
    if not include_gm:
        d.pop("dossier", None)
    return d

# Inject GM flag to all templates
@app.context_processor
def inject_is_gm():
    return {"IS_GM": is_gm()}

# ---------- MAP ----------
@app.get("/")
def map_global():
    missions = fetch_missions(include_gm=is_gm())
    con = db()
    regions  = [dict(r) for r in con.execute("SELECT * FROM regions")]
    con.close()
    payload = {
        "global": {"img": GLOBAL_IMG, "w": GLOBAL_W, "h": GLOBAL_H},
        "regions": regions,
        "missions": missions,
        "timer": get_timer()
    }
    return render_template("map.html", view="global", data=json.dumps(payload), timer=get_timer())

@app.get("/region/<name>")
def map_region(name):
    con = db()
    reg = con.execute("SELECT * FROM regions WHERE name=?", (name,)).fetchone()
    if not reg:
        con.close()
        abort(404)
    con.close()
    missions = fetch_missions(include_gm=is_gm())
    payload = {
        "global": {"img": GLOBAL_IMG, "w": GLOBAL_W, "h": GLOBAL_H},
        "region": dict(reg),
        "missions": missions,
        "timer": get_timer()
    }
    return render_template("map.html", view="region", data=json.dumps(payload), timer=get_timer())

# ---------- MISSIONS ----------
@app.get("/missions")
def missions_list():
    con = db()
    rows = [dict(r) for r in con.execute(
        "SELECT id,title,tags,status,difficulty,region_hint,updated_at FROM missions ORDER BY updated_at DESC"
    )]
    con.close()
    return render_template("missions.html", missions=rows)

@app.get("/missions/<int:mid>")
def mission_detail(mid):
    m = fetch_mission(mid, include_gm=is_gm())
    if not m: abort(404)
    return render_template("mission_view.html", m=m)

# Inline update from GM panel on detail page
@app.post("/missions/<int:mid>/edit")
def mission_update(mid):
    if not is_gm(): abort(403)
    f = request.form
    now = int(time.time())
    # Defensive parsing
    def ffloat(k, default):
        try: return float(f.get(k, default))
        except: return default
    fields = {
        "title":       f.get("title","").strip(),
        "tags":        f.get("tags","").strip(),
        "status":      f.get("status","open"),
        "difficulty":  f.get("difficulty","standard"),
        "region_hint": f.get("region_hint","").strip(),
        "brief":       f.get("brief","").strip(),
        "dossier":     f.get("dossier","").strip(),
        "x":           ffloat("x", 0.5),
        "y":           ffloat("y", 0.5),
        "updated_at":  now
    }
    con = db()
    con.execute("""UPDATE missions SET
        title=:title, tags=:tags, status=:status, difficulty=:difficulty,
        region_hint=:region_hint, brief=:brief, dossier=:dossier, x=:x, y=:y, updated_at=:updated_at
        WHERE id=:mid
    """, {**fields, "mid": mid})
    con.commit(); con.close()
    return redirect(url_for("mission_detail", mid=mid))

# ---------- GM AUTH ----------
@app.post("/gm/login")
def gm_login():
    if request.form.get("password") == GM_PASSWORD:
        session["is_gm"] = True
    return redirect(request.referrer or url_for("map_global"))

@app.post("/gm/logout")
def gm_logout():
    session.pop("is_gm", None)
    return redirect(request.referrer or url_for("map_global"))

# ---------- ADVENT TRACKER ----------
@app.post("/timer/inc")
def timer_inc():
    if not is_gm(): abort(403)
    con = db()
    con.execute("UPDATE global_timer SET ticks = MIN(ticks+1, max_ticks), updated_at=? WHERE id=1", (int(time.time()),))
    con.commit(); con.close()
    return redirect(request.referrer or url_for("map_global"))

@app.post("/timer/dec")
def timer_dec():
    if not is_gm(): abort(403)
    con = db()
    con.execute("UPDATE global_timer SET ticks = MAX(ticks-1, 0), updated_at=? WHERE id=1", (int(time.time()),))
    con.commit(); con.close()
    return redirect(request.referrer or url_for("map_global"))

# ---------- DEV ----------
if __name__ == "__main__":
    app.run(debug=True)
