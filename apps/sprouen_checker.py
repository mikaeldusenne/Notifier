from NotifierMailer import bs_extractor, run, sendmail, composemail, alert
from datetime import datetime
url = "https://www.cngsante.fr/chiron/celine/affect/norm/024451"

# EMAILS = ','.join(["mikaeldusenne@gmail.com", "mikael.dusenne@chu-rouen.fr", "stefan.darmoni@chu-rouen.fr", "Jacques.Benichou@chu-rouen.fr", "T.Pressat@chu-rouen.fr", "Clement.Massonnaud@chu-rouen.fr"])
emails = "mikaeldusenne@gmail.com mikael.dusenne@chu-rouen.fr".replace(' ', ',')
# save_file = '/home/mika/.perso/sprouen_checker.pkl'
# cumul_file = '/home/mika/.perso/sprouen_checker_cumul.csv'

# name = "sprouen_checker"

def extractf(url=url):
    def f(html):
        print(html)
        h, *t = html.find('table').find_all("tr")[5:]
        columns = [e.text for e in h.find_all("td")]
        rows = [[ee.text for ee in e.find_all("td")] for e in t]
        ans = [dict(statut=status, etudiant=etudiant, voeu=voeu) for *j, status, etudiant, voeu in rows if etudiant != ""]
        print(ans)
        return ans
    return bs_extractor(url, f)


def predicate(new, old):
    return old is None or len(new) > len(old)


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


def write_file(p, mode, e):
    with open(p, mode) as f:
        f.write(e)


def append_file(p, e):
    return write_file(p, "a", e)


if __name__ == "__main__":
    run(
        extractf=extractf,
        actions=dict(
            predicate_true=[
                sendmail(emails, makemail),
                alert(lambda new, old: dict(title="Céline notification!", content=f"{make_table(new)}"))
            ]
            # always=[
            #     lambda new, old: append_to_file(cumul_file, f"{datetime.now()},{len(new)}\n")
            # ]
        ),
        predicate=predicate,
    )
