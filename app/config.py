import locale

locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

url = "https://myelectricaldata.fr/api"

fail_count = 24

f = open("/app/VERSION", "r")
VERSION = f.read()
f.close()