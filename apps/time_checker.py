from NotifierMailer import json_extractor, run, sendmail, alert, composemail
from datetime import datetime
import json

url = "http://worldtimeapi.org/api/timezone/Europe/Paris"
emails = "mikaeldusenne@gmail.com".replace(' ', ',')


extractf = lambda url: json_extractor(url, lambda j: j["utc_datetime"])

predicate = lambda new, old: new != old


def makemail(new, old):
    return composemail("L'heure a changé!", f"""* test
----
<i>{new}</i>
""", html=True)


if __name__ == "__main__":
    run(
        extractf=extractf,
        actions=dict(
            predicate_true=[
                sendmail(emails, makemail),
                alert(lambda new, old: dict(title="Time Notification", content=f"il est l'heure! {new}"))
            ]
        ),
        predicate=predicate,
    )
