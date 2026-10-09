"""
Digital Wedding Invitation + Online RSVP
Run:  python app.py   ->  open http://127.0.0.1:8000
Admin: http://127.0.0.1:8000/admin
Personal link for a guest: http://127.0.0.1:8000/?to=Karim%20Family
"""
import csv
import hmac
import io
import os
import sqlite3
from datetime import datetime
from functools import wraps

from flask import (Flask, Response, flash, g, jsonify, redirect,
                   render_template, request, session, url_for)

import config

BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE, "wedding.db")

app = Flask(__name__)
app.secret_key = config.SECRET_KEY


# ---------------------------------------------------------------- database
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    with sqlite3.connect(DB_PATH) as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS rsvp (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            attending TEXT NOT NULL,
            guests INTEGER DEFAULT 1,
            events TEXT,
            meal TEXT,
            message TEXT,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS wish (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            message TEXT NOT NULL,
            approved INTEGER DEFAULT 1,
            created_at TEXT NOT NULL
        );
        """)


def photos():
    folder = os.path.join(BASE, "static", "photos")
    exts = (".jpg", ".jpeg", ".png", ".webp", ".gif")
    try:
        featured = set(getattr(config, "FEATURED_PHOTOS", []))
        return sorted(f for f in os.listdir(folder)
                      if f.lower().endswith(exts) and f not in featured)
    except FileNotFoundError:
        return []


def has_music():
    return os.path.exists(os.path.join(BASE, "static", "music", "song.mp3"))


# ---------------------------------------------------------------- public
@app.route("/")
def home():
    guest = request.args.get("to", "").strip()[:60]
    wishes = get_db().execute(
        "SELECT name, message, created_at FROM wish WHERE approved=1 "
        "ORDER BY id DESC LIMIT 30").fetchall()
    return render_template("index.html", c=config, guest=guest,
                           wishes=wishes, photos=photos(),
                           music=has_music())


@app.post("/rsvp")
def rsvp():
    f = request.form
    name = f.get("name", "").strip()[:100]
    attending = f.get("attending", "")
    if not name or attending not in ("yes", "no"):
        return jsonify(ok=False, error="Add your name and choose whether you can attend."), 400
    try:
        guests = int(f.get("guests", 1))
    except ValueError:
        guests = 1
    guests = max(1, min(guests, config.MAX_GUESTS_PER_RSVP)) if attending == "yes" else 0
    valid_keys = {e["key"] for e in config.EVENTS}
    events = ",".join(k for k in f.getlist("events") if k in valid_keys)
    message = f.get("message", "").strip()[:600]
    db = get_db()
    db.execute(
        "INSERT INTO rsvp (name, phone, email, attending, guests, events, meal, message, created_at) "
        "VALUES (?,?,?,?,?,?,?,?,?)",
        (name, f.get("phone", "").strip()[:30], f.get("email", "").strip()[:100],
         attending, guests, events, f.get("meal", "")[:30], message,
         datetime.now().isoformat(timespec="seconds")))
    if message:
        db.execute("INSERT INTO wish (name, message, created_at) VALUES (?,?,?)",
                   (name, message, datetime.now().isoformat(timespec="seconds")))
    db.commit()
    return jsonify(ok=True, attending=attending, name=name.split()[0])


@app.post("/wish")
def wish():
    name = request.form.get("name", "").strip()[:60]
    message = request.form.get("message", "").strip()[:400]
    if not name or not message:
        return jsonify(ok=False, error="Add your name and a few words."), 400
    db = get_db()
    db.execute("INSERT INTO wish (name, message, created_at) VALUES (?,?,?)",
               (name, message, datetime.now().isoformat(timespec="seconds")))
    db.commit()
    return jsonify(ok=True, name=name, message=message)


@app.get("/calendar/<key>.ics")
def calendar(key):
    ev = next((e for e in config.EVENTS if e["key"] == key), None)
    if not ev:
        return "Event not found", 404

    def fmt(s):
        return datetime.fromisoformat(s).strftime("%Y%m%dT%H%M%S")

    ics = "\r\n".join([
        "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Wedding//Invite//EN",
        "BEGIN:VEVENT",
        f"UID:{key}-{config.NAME_1}-{config.NAME_2}@wedding",
        f"DTSTAMP:{datetime.now().strftime('%Y%m%dT%H%M%S')}",
        f"DTSTART:{fmt(ev['start'])}", f"DTEND:{fmt(ev['end'])}",
        f"SUMMARY:{ev['name']} – {config.NAME_1} & {config.NAME_2}",
        "LOCATION:" + ", ".join(x for x in (ev["venue"], ev["address"]) if x),
        f"DESCRIPTION:Dress code: {ev['dress']}" if ev["dress"] else "DESCRIPTION:",
        "END:VEVENT", "END:VCALENDAR", ""])
    return Response(ics, mimetype="text/calendar",
                    headers={"Content-Disposition": f"attachment; filename={key}.ics"})


# ---------------------------------------------------------------- admin
def admin_required(fn):
    @wraps(fn)
    def wrapper(*a, **kw):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        return fn(*a, **kw)
    return wrapper


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        given = request.form.get("password", "")
        if config.ADMIN_PASSWORD and hmac.compare_digest(given, config.ADMIN_PASSWORD):
            session["admin"] = True
            return redirect(url_for("admin"))
        flash("That password is incorrect.")
    return render_template("login.html", c=config)


@app.get("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("home"))


@app.get("/admin")
@admin_required
def admin():
    db = get_db()
    rows = db.execute("SELECT * FROM rsvp ORDER BY id DESC").fetchall()
    wishes = db.execute("SELECT * FROM wish ORDER BY id DESC").fetchall()
    yes = [r for r in rows if r["attending"] == "yes"]
    per_event = {e["key"]: 0 for e in config.EVENTS}
    for r in yes:
        for k in (r["events"] or "").split(","):
            if k in per_event:
                per_event[k] += r["guests"]
    stats = {
        "responses": len(rows),
        "yes": len(yes),
        "no": len(rows) - len(yes),
        "guests": sum(r["guests"] for r in yes),
        "per_event": per_event,
    }
    names = {e["key"]: e["name"] for e in config.EVENTS}
    return render_template("admin.html", c=config, rows=rows, wishes=wishes,
                           stats=stats, names=names)


@app.post("/admin/rsvp/<int:rid>/delete")
@admin_required
def delete_rsvp(rid):
    db = get_db()
    db.execute("DELETE FROM rsvp WHERE id=?", (rid,))
    db.commit()
    return redirect(url_for("admin"))


@app.post("/admin/wish/<int:wid>/toggle")
@admin_required
def toggle_wish(wid):
    db = get_db()
    db.execute("UPDATE wish SET approved = 1 - approved WHERE id=?", (wid,))
    db.commit()
    return redirect(url_for("admin") + "#wishes")


@app.get("/admin/export.csv")
@admin_required
def export_csv():
    rows = get_db().execute("SELECT * FROM rsvp ORDER BY id").fetchall()
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["Name", "Phone", "Email", "Attending", "Guests", "Events",
                "Meal", "Message", "Submitted"])
    for r in rows:
        w.writerow([r["name"], r["phone"], r["email"], r["attending"], r["guests"],
                    r["events"], r["meal"], r["message"], r["created_at"]])
    return Response("\ufeff" + buf.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=rsvp_list.csv"})


init_db()

if __name__ == "__main__":
    # host="0.0.0.0" lets phones on the same Wi-Fi open it via your PC's IP
    # port 5000 is taken by AirPlay Receiver on macOS, so default to 8000
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), debug=True)
