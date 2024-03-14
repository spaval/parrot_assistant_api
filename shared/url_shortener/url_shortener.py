import pyshorteners

def short(url: str):
    shortener = pyshorteners.Shortener()
    short_url = shortener.dagd.short(url)
    return short_url