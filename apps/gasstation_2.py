from sys import argv
from os import environ
from dotenv import load_dotenv

from NotifierMailer import run, sendmail, composemail, alert, browse
from NotifierMailer.helpers import *
import NotifierMailer as nm


load_dotenv("./.etherscan_credentials.env")


# browseurl = "https://ethgasstation.info/"
browseurl = "https://etherscan.io/gastracker"

url_etherscan = f"https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey={environ['ETHERSCAN_APIKEY']}"

def extractf(old=None):
    return nm.json_extractor(
        url_etherscan,
        lambda e: {
            k: int(e['result'][v])
            for k, v in [
                    ("fast", "FastGasPrice"),
                    ("standard", "ProposeGasPrice"),
                    ("low", "SafeGasPrice"),
            ]
        }
    )

predicate = lambda new, old: new['standard'] <= 60

alert_fn = alert(
    lambda new, old: dict(title="Gas Price", content='\n'+'\n'.join([f"{k}: {v}" for k, v in new.items()])),
    action=browse(lambda new, old: browseurl)
)

def makemail(new, old):
    s = f"""
Gas price is quite low ATM!<br>

----

Check {browseurl} for more infor.

{make_table(dict_to_records(new, ['speed', 'recommanded Gwei price']))}
"""
    return composemail("Low gas price!", s, html=True)



if __name__ == "__main__":
    emails = 'my_email@mail.com'
    # emails = ','.join(['mikaeldusenne@gmail.com', 'clement.massonnaud@gmail.com', 'clarisse.amelot@gmail.com'])
    args = dict(
        extractf=extractf,
        predicate=predicate,
        actions=dict(predicate_true=[
            # sendmail(emails, makemail),
            alert_fn,
        ])
    )
        
    run(**args)
