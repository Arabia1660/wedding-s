# ==============================================================
#  EDIT EVERYTHING HERE — this is the only file you need to change
# ==============================================================

BRIDE = "Oishee"
GROOM = "Shanto"
BRIDE_FULL = "Oishee"
GROOM_FULL = "Shanto"
# The order the names appear in everywhere on the site (the card puts Oishee first)
NAME_1, NAME_2 = BRIDE, GROOM

# Main event date/time used for the countdown (24h, local time)
WEDDING_DATETIME = "2026-10-21T13:00:00"
DATE_TEXT = "Wednesday, 21 October 2026"
CITY = "Magura"

# Wording from the invitation card
HEADLINE_TOP = "You are warmly invited to the wedding of"
INVITE_LINE = ("Your gracious presence will make our special day even more "
               "memorable as we begin a new chapter together.")
CLOSING_LINE = "We look forward to sharing this joyful occasion with you."
# The opening animation's headline (recreated from the save-the-date video)
OPENING_LINE = "Finally, the date is out."
# Shown beside the dancing illustration ("Two hearts · one journey")
COUPLE_LINE = ("With grateful hearts and the blessings of our families, we are beginning "
               "our forever — and it would mean the world to have you there.")

HASHTAG = ""         # optional, e.g. "#OisheeWedsShanto"

# Families shown under the invitation — leave "" to hide
BRIDE_PARENTS = ""   # e.g. "Daughter of Mr. & Mrs. ..."
GROOM_PARENTS = ""   # e.g. "Son of Mr. & Mrs. ..."

# Events — add, remove or reorder freely. "key" must be unique, no spaces
# (keep "reception" — RSVPs already saved use it).
# Leave "address", "dress", "map" or "map_embed" as "" to hide them.
EVENTS = [
    {
        "key": "reception",
        "name": "The Wedding",
        "date": "Wednesday, 21 October 2026",
        "time": "1:00 PM",
        "start": "2026-10-21T13:00:00", "end": "2026-10-21T17:00:00",
        "venue": "Fatema Community Center",
        "address": "Magura – Jashore Highway, Magura 7600",
        "dress": "",
        "map": "https://maps.app.goo.gl/xnhGBBxNLYmqngKE9",
        "map_embed": "https://www.google.com/maps?q=Fatema+Community+Centre,+Magura+-+Jashore+Hwy,+Magura+7600&output=embed",
    },
]

# Our story — shown as a timeline. Leave the list empty to hide the section.
# Example: {"year": "2022", "title": "First hello", "text": "Where it all began."},
STORY = []

# Photos: put image files in static/photos/ (jpg/png/webp). They appear in the gallery automatically.
# These four illustrations are already placed around the page as cut-outs (static/decor/couple-*.webp),
# so they are kept out of the gallery.
FEATURED_PHOTOS = [
    "WhatsApp Image 2026-10-10 at 00.20.54.jpeg",       # dancing      -> "Two hearts" section
    "WhatsApp Image 2026-10-10 at 00.20.55 (1).jpeg",   # motorbike    -> countdown
    "WhatsApp Image 2026-10-10 at 00.23.13.jpeg",       # garland      -> the celebration
    "WhatsApp Image 2026-10-10 at 00.20.55.jpeg",       # hand in hand -> footer
]
# Music: plays from the start when a guest taps the envelope (path inside static/).
MUSIC_FILE = "music/jakob_welik-murmures-de-la-seine-411960.mp3"

# Contact people shown in the footer. Leave empty to hide.
# Example: {"name": "Groom's side", "phone": "+880 1700-000000"},
CONTACTS = []

RSVP_DEADLINE = "18 October 2026"
MAX_GUESTS_PER_RSVP = 6

# Admin dashboard at /admin.
# The real password and secret key are NOT stored here (this file is public on GitHub).
# Put them in local_settings.py (ignored by git) or set the ADMIN_PASSWORD / SECRET_KEY
# environment variables on your host. Admin login stays disabled until a password is set.
import os
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")
SECRET_KEY = os.environ.get("SECRET_KEY") or os.urandom(32).hex()
try:
    from local_settings import *  # noqa: F401,F403
except ImportError:
    pass
