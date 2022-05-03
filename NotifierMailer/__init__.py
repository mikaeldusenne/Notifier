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
import webbrowser

import traceback

from dotenv import load_dotenv


load_dotenv("./.env")

logging.getLogger().setLevel(logging.INFO)

def get_pcss_output(c):
    if type(c) == str:
        c=c.split(' ')
    logging.info(c)
    return subprocess.run(c, capture_output=True).stdout.decode().strip()

os.environ['DISPLAY']=':0.0'
os.environ['DBUS_SESSION_BUS_ADDRESS']=get_pcss_output("$HOME/bin/get-dbus")



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
    p = subprocess.Popen(['$HOME/.local/bin/mredact'], 
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


def sendmail(emails, makemail):
    def f(new, old):
        strcontent = makemail(new, old)
        p = Popen(['sendmail', '-f', os.environ["NOTIFIER_MAIL_FROM"], '-t', emails],
                  stdin=PIPE)
        p.communicate(input = str.encode(strcontent))
    return f


def alert(genf, sound="Purr", action=None):
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
            e = [
                    "$HOME/bin/notification",
                    f"{c['title']}",
                    f"{c['content']}"
            ]
            if action is not None:
                e = e+["-A", "a,a"]
            
            commands = [
                f"$HOME/bin/play_sound {sound}".split(' '),
                e]
            
        ans = [get_pcss_output(c) for c in commands][-1]
        print(f"{ans=}")
        if action is not None and ans != "1":
            action(new, old)
        return ans
    return f


def load_old(save_file, default=None):
    try: 
        with open(save_file, 'rb') as f:
            return pickle.load(f, encoding="utf-8")
    except Exception as e:
        print(f"no 'old' file (at {save_file})")
        return default


def browse(f):
    def g(new, old):
        webbrowser.open(f(new, old))
    return g


def save_value(val, dest):
    # os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, 'wb') as f:
        pickle.dump(val, f)


def bs_extractor(url, f):
    return f(BeautifulSoup(requests.get(url).content, 'html.parser'))


def json_extractor(url, f):
    return f(json.loads(requests.get(url).content))


def get_state_path():
    return join(dirname(__file__), "state", basename(argv[0]).replace(".py", ""))


def run(extractf, predicate, actions):
    save_dest = get_state_path()
    save_file = join(save_dest, "last.pkl")
    os.makedirs(save_dest, exist_ok=True)
    old = load_old(save_file)
    
    new = extractf()
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
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        run()
    else:
        while True:
            run()
            timer(5)
