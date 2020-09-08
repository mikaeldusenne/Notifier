from NotifierMailer import bs_extractor, run, sendmail, alert
from datetime import datetime
import json
import requests

url = "https://www.curve.fi/raw-stats/apys.json"

emails = "mikaeldusenne@gmail.com".replace(' ', ',')
save_file = '/dev/null'
cumul_file = '/home/mika/.perso/curvefi.csv'

def extractf(url=url):
    return json.loads(requests.get(url).content)["apy"]["day"]["y"]

def predicate(new, old):
    return new < 0.01

def append_to_file(p, e):
    with open(p, "a") as f:
        f.write(e)

if __name__ == "__main__":
    run(
        save_file = save_file,
        extractf=extractf,
        actions=dict(
            predicate_true=[
                sendmail(emails, makemail),
                alert("CurfeFi!")
            ],
            always=[
                lambda new, old: append_to_file(cumul_file, f"{datetime.now()},{new}\n")
            ]
        ),
        predicate=predicate,
    )
