
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


def dict_to_records(d, colnames):
    return [ {c: v for c,v in zip(colnames, kv)} for kv in d.items() ]

def make_table(l):
    def totag(ll, tag=td):
        return "\n".join([tag(e) for e in ll])
    return table("\n".join([tr(e) for e in [totag(l[0].keys(), th)]+[totag(ee.values()) for ee in l]]))

