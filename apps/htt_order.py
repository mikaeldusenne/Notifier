from NotifierMailer import run, sendmail, composemail, alert, browse
from NotifierMailer.helpers import *
import NotifierMailer as nm
from sys import argv
from pprint import pprint, pformat


import requests

url = "https://api.lulu.com/graphql/"

order_number="EUR-XXXXXX"
email="my_email@mail.com"

def make_order_query(order_number, email):
    return {"operationName":"orderLookup","variables":{"orderNumber": order_number,"email": email},"query":"fragment Discount on Discount {\n  type\n  discount {\n    amount\n    currency\n    __typename\n  }\n  __typename\n}\n\nfragment Order on Order {\n  id\n  referenceNo\n  status\n  hasLineItemError\n  contactEmail\n  dateCreated\n  trackingUrl\n  carrierName\n  amount {\n    amount\n    currency\n    __typename\n  }\n  payment {\n    creditCardNumber\n    creditCardCompany\n    cardHolderName\n    __typename\n  }\n  shippingAmount {\n    amount\n    currency\n    __typename\n  }\n  shippingMethod {\n    name\n    traceable\n    minDispatchDate\n    minDeliveryDate\n    maxDispatchDate\n    maxDeliveryDate\n    __typename\n  }\n  shippingAddress {\n    name\n    addressLine1\n    addressLine2\n    city\n    postalCode\n    phone\n    __typename\n  }\n  billingAddress {\n    name\n    addressLine1\n    addressLine2\n    city\n    postalCode\n    phone\n    __typename\n  }\n  lineItems {\n    id\n    quantity\n    status\n    downloadUrl\n    unitAmount {\n      currency\n      amount\n      __typename\n    }\n    totalAmount {\n      currency\n      amount\n      __typename\n    }\n    discounts {\n      ...Discount\n      __typename\n    }\n    product {\n      id\n      name\n      type\n      thumbnailUrl\n      canonicalUrlSlug\n      isbn\n      version\n      contributors {\n        name\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  canBeCanceled\n  itemsNetSubtotalWithDiscounts {\n    amount\n    currency\n    __typename\n  }\n  shippingAndHandlingAmount {\n    amount\n    currency\n    __typename\n  }\n  totalTax {\n    amount\n    currency\n    __typename\n  }\n  __typename\n}\n\nquery orderLookup($email: String!, $orderNumber: String!) {\n  orderLookup(email: $email, orderNumber: $orderNumber) {\n    id\n    ...Order\n    __typename\n  }\n}\n"}

# browseurl = "https://ethgasstation.info/"
browseurl = f"https://www.lulu.com/orders/{order_number}"


def extractf(old=None):
    j = requests.post(url, json=make_order_query(order_number, email)).json()
    # pprint(j)
    return j["data"]["orderLookup"]

predicate = lambda new, old: new != old

def simplify(d):
    keys = "trackingUrl status".split()
    return {
        k: v for k, v in d.items()
        if k in keys # and v is not None
    }

alert_fn = alert(
    lambda new, old: dict(title="HOTT Order", content='\n'+'\n'.join([f"{k}: {v}" for k, v in simplify(new).items()])),
    action=browse(lambda new, old: browseurl)
)

def makemail(new, old):
    s = f"""
HOTT order update!<br>

----

visit {browseurl} for more details.

{pformat(simplify(new))}

----

{pformat(new)}
"""
    return composemail("HOTT order update!", s, html=True)



if __name__ == "__main__":
    emails = 'recipient_1@mail.com'
    args = dict(
        extractf=extractf,
        predicate=predicate,
        actions=dict(predicate_true=[
            # sendmail(emails, makemail),
            alert_fn,
        ])
    )
        
    run(**args)
