import subprocess
from subprocess import PIPE
from datetime import datetime

from NotifierMailer import bs_extractor, run, sendmail, alert, composemail
import NotifierMailer as nm

from apps.sprouen_checker import makemail, extractf, make_table, url, emails


def predicate(new, old):
    def voeu_definitif(l):
        return len([e['etudiant'] for e in l if e['statut']=='affecté'])
    return old is None or (voeu_definitif(new) > voeu_definitif(old))


if __name__ == "__main__":
    run(
        extractf=extractf,
        actions=dict(
            predicate_true=[
                sendmail(emails, makemail),
                alert(lambda new, old: dict(title="Céline notification!", content=f"{make_table(new)}"),
                      "pokecenter",
                      nm.browse(lambda new, old: url))
            ]
        ),
        predicate=predicate
    ) 
