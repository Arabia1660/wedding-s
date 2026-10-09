# Digital Wedding Invitation + Online RSVP (Python / Flask)

## Run it (one environment)
```bash
python -m venv venv
# Windows:  venv\Scripts\activate      Mac/Linux:  source venv/bin/activate
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:8000

## Customize
Edit **config.py** only: names, date, card wording, events, venues, story, contacts.
- Invitation card: `static/invitation-card.jpg` is shown on the page, offered as a download, and used as the link preview image.
- Photos: drop images into `static/photos/` — they show up in the gallery automatically.
  The four couple illustrations are cut out of their black backgrounds (`static/decor/couple-*.webp`) and placed
  around the page instead; they're listed in `FEATURED_PHOTOS` in config.py so they don't repeat in the gallery.
- Music: put an mp3 at `static/music/song.mp3` — a music button appears and starts when the envelope opens.

## Personal invite links
`http://YOUR-SITE/?to=Karim%20Family` → the envelope says "A personal invitation for Karim Family" and the RSVP name is pre-filled.

## Admin dashboard
http://127.0.0.1:8000/admin

The admin password is kept out of git. Create `local_settings.py` next to `app.py`:
```python
ADMIN_PASSWORD = "your-password"
SECRET_KEY = "any-long-random-text"
```
or set the `ADMIN_PASSWORD` and `SECRET_KEY` environment variables on your host.
Guest totals, per-event headcount, search, delete, hide/show wishes, and CSV export (opens in Excel).

## Share with guests on your Wi-Fi
The app listens on 0.0.0.0, so phones on the same network can open `http://YOUR-PC-IP:8000`.
To put it online, deploy to PythonAnywhere, Render, or Railway (set `debug=False` first).
