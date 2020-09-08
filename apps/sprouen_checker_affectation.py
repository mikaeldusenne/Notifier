import subprocess
from subprocess import PIPE
from NotifierMailer import bs_extractor, run, sendmail, alert, composemail
from datetime import datetime
url = "https://www.cngsante.fr/chiron/celine/affect/norm/024451"

# EMAILS = ','.join(["mikaeldusenne@gmail.com", "mikael.dusenne@chu-rouen.fr", "stefan.darmoni@chu-rouen.fr", "Jacques.Benichou@chu-rouen.fr", "T.Pressat@chu-rouen.fr", "Clement.Massonnaud@chu-rouen.fr"])
emails = "mikaeldusenne@gmail.com mikael.dusenne@chu-rouen.fr".replace(' ', ',')
save_file = '/home/mika/.perso/sprouen_checker_affect.pkl'
cumul_file = '/home/mika/.perso/sprouen_checker_cumul_affect.csv'


def extractf(url=url):
    def f(html):
        h, *t = html.find('table').find_all("tr")[5:]
        columns = [e.text for e in h.find_all("td")]
        rows = [[ee.text for ee in e.find_all("td")] for e in t]
        # print(f"{str(datetime.now())}: {available} postes libres.")
        return [dict(status=status, etudiant=etudiant, voeu=voeu) for *j, status, etudiant, voeu in rows if etudiant != ""]
    return bs_extractor(url, f)


def predicate(new, old):
    def n_first_choice(l):
        return len([e['etudiant'] for e in l if e['voeu']=='1'])
    def n_voeu_definitif(l):
        return len([e['etudiant'] for e in l if e['status']=='affecté'])
    return old is None or (n_voeu_definitif(new) > n_voeu_definitif(old))
    

def tag(t, **kwargs):
    def f(e):
        kvs = " ".join([ f'{k}="{v}"' for k, v in kwargs.items() ])
        return f"<{t} {kvs}>{e}</{t}>"
    return f

tr = tag("tr")
th = tag("th", style="padding:0 1em;")
td = tag("td")
table = tag("table")
tbody = tag("tbody")

def make_table(l):
    def totag(ll, tag=td):
        return "\n".join([tag(e) for e in ll])
    return table("\n".join([tr(e) for e in [totag(l[0].keys(), th)]+[totag(ee.values()) for ee in l]]))


def makemail(new, old):
    s = f"""
Quelqu'un a choisi **Santé Publique** à Rouen!<br>

----

cf https://www.cngsante.fr/chiron/celine/affect/norm/024451 pour plus d'informations.

{make_table(new)}
"""
    return composemail("Quelqu'un a choisi Rouen!", s, html=True)


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
                alert("Céline notification!")
            ],
            always=[
                lambda new, old: append_to_file(cumul_file, f"{datetime.now()},{len(new)}\n")
            ]
        ),
        predicate=predicate,
    )
