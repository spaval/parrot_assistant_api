import pyshorteners

def short(url: str):
    short_url: str = url

    try:
        shortener = pyshorteners.Shortener()
        short_url = shortener.dagd.short(url)
    except Exception as e:
        pass

    return short_url