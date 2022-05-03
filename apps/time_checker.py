from NotifierMailer import json_extractor, run, sendmail, alert, composemail, browse
import NotifierMailer as nm
from datetime import datetime
import json

url = "http://worldtimeapi.org/api/timezone/Europe/Paris"
emails = "mikaeldusenne@gmail.com".replace(' ', ',')


extractf = lambda: json_extractor(url, lambda j: j["utc_datetime"])

predicate = lambda new, old: new != old


def makemail(new, old):
    return composemail("The time changed!", f"""* test
----
<i>{new}</i>
""", html=True)


if __name__ == "__main__":
    run(
        extractf=extractf,
        actions=dict(
            predicate_true=[
                sendmail(emails, makemail),
                alert(
                    lambda new, old: dict(title="Time Notification", content=f"It's time! {new}"),
                    action=nm.browse(lambda *e: 'https://time.is/')
                )
            ]
        ),
        predicate=predicate,
    )
