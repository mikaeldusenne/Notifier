import sys
import json
from subprocess import Popen, PIPE, STDOUT
import os
from os.path import join, split, dirname, basename
import subprocess
import pickle
import logging

from time import sleep
from bs4 import BeautifulSoup
import requests
from sys import argv
import platform

import traceback

OS = platform.system()

def timer(mins):
    chars = '|/-\\'
    for n in range(mins):
        for k in range(60):
            c = chars[k%len(chars)]
            print(" running again in {} minute{}  {}    ".format( mins-n, 's' if mins-n > 1 else '' , c), end="\r")
            sleep(1)
    print('')


def make_htmail(s):
    p = subprocess.Popen(['/home/mika/.local/bin/mredact'], 
                         stdin=PIPE, stdout=PIPE)
    result, err = p.communicate(input = str.encode(s))
    return result


def composemail(title, content, html=True):
    if html:
        rest = make_htmail(content).decode("utf-8")
    else:
        rest = f"""Content-Type: text/plain; charset=utf-8;

{content}
"""
    return f"""Subject: {title}
{rest}
"""

    
# # def sendmail(emails, subject, body, ct="text/plain; charset=utf-8"):
# def sendmail(emails, makemail):
#     def f(new, old):
#         def g(subject, rest):
#             strcontent = str.encode("\n".join(
#                 [f"Subject: {subject}", rest]
#             ))
            
#             p = Popen(['sendmail', '-t', emails], 
#                       stdin=PIPE)
#             p.communicate(input = strcontent)
#         return g(**makemail(new,old))
#     return f


def sendmail(emails, makemail):
    def f(new, old):
        strcontent = makemail(new, old)
        p = Popen(['sendmail', '-t', emails],
                  stdin=PIPE)
        p.communicate(input = str.encode(strcontent))
    return f


def alert(genf, sound="Purr"):
    def f(new, old):
        c = genf(new, old)
        if OS=='Darwin':
            commands = [
                [
                    "osascript", "-e",
                    f"{c['title']}: {c['content']}"
                ]
            ]
        elif OS=='Linux':
            commands = [
                [
                    "/home/mika/bin/play_sound", sound
                ],
                [
                    "/home/mika/bin/notification",
                    f"{c['title']}",
                    f"{c['content']}"
            ]]
            
        [subprocess.run(c) for c in commands]
    return f


def load_old(save_file, default=None):
    try: 
        with open(save_file, 'rb') as f:
            return pickle.load(f, encoding="utf-8")
    except Exception as e:
        print(e)
        return default


def save_value(val, dest):
    # os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, 'wb') as f:
        pickle.dump(val, f)


def bs_extractor(url, f):
    return f(BeautifulSoup(requests.get(url).content, 'html.parser'))


def json_extractor(url, f):
    return f(json.loads(requests.get(url).content))


def run(extractf, predicate, actions, alert=None):
    save_dest = join(dirname(__file__), "state", basename(argv[0]).replace(".py", ""))
    save_file = join(save_dest, "last.pkl")
    os.makedirs(save_dest, exist_ok=True)
    
    new = extractf()
    old = load_old(save_file)
    save_value(new, save_file)
    def runall(l):
        def tryf(f, *args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as ex:
                print(ex)
                traceback.print_stack()
                raise ex
                return ex
            
        [tryf(f, old=old,new=new) for f in l]
    runall(actions.get("always", []))
    if predicate(new, old):
        logging.error("Triggering stuff!")
        runall(actions.get("predicate_true", []))
    else:
        runall(actions.get("predicate_false", []))


if __name__ == "__main__":
    url = "https://ethgasstation.info/"
    extract = lambda html: int(html.find('div', {'class': "safe_low"}).text.strip())
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        run()
    else:
        while True:
            run()
            timer(5)
