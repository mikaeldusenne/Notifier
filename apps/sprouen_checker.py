from datetime import datetime

from NotifierMailer import bs_extractor, run, sendmail, composemail, alert
from NotifierMailer.helpers import make_table

url = "https://www.cngsante.fr/chiron/celine/affect/norm/024451"
emails = ','.join(["recipient_1@mail.com", "recipient_2@mail.com"])

def extractf(url=url):
    def f(html):
        h, *t = html.find('table').find_all("tr")[5:]
        columns = [e.text for e in h.find_all("td")]
        rows = [[ee.text for ee in e.find_all("td")] for e in t]
        ans = [dict(statut=status, etudiant=etudiant, voeu=voeu) for *j, status, etudiant, voeu in rows if etudiant != ""]
        print(ans)
        return ans
    return bs_extractor(url, f)


def predicate(new, old):
    return old is None or len(new) > len(old)


def makemail(new, old):
    s = f"""
Someont chose **Public Health** In Rouen!<br>

----

cf https://www.cngsante.fr/chiron/celine/affect/norm/024451 for more details.

{make_table(new)}
"""
    return composemail("Someone chose Rouen!", s, html=True)



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
