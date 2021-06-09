import amino
import base64
import string
import random
import pyfiglet
import json
import time
from os import path
from hashlib import sha1
from concurrent.futures import ThreadPoolExecutor
from colorama import init, Fore, Back, Style
init()
print(Fore.GREEN)
print(Style.NORMAL)
print("""Script by Lil Zevi
Github : https://github.com/LilZevi""")
print(pyfiglet.figlet_format("AminoCoinGenerator", font="rectangles"))
client = amino.Client()
THIS_FOLDER = path.dirname(path.abspath(__file__))
emails = path.join(THIS_FOLDER, 'emails.txt')
deviceIdfile = path.join(THIS_FOLDER, "device")
emails = open(emails, "r")
password = input("Password for accounts/Пароль для аккаунтов: ")
communitylink = input("Community Link/Ссылка на сообщество: ")
communityinfo = client.get_from_code(communitylink)
thecommunityid = communityinfo.path[1:communityinfo.path.index('/')]

def coinsgenerator(sub_client : amino.SubClient):
	generatingcoins = {"start": int(time.time()), "end": int(time.time()) +300}
	return generatingcoins

def sendingprocces(sub_client : amino.SubClient):
    thetimer = [coinsgenerator(sub_client), coinsgenerator(sub_client), coinsgenerator(sub_client), coinsgenerator(sub_client), coinsgenerator(sub_client), coinsgenerator(sub_client), coinsgenerator(sub_client), coinsgenerator(sub_client), coinsgenerator(sub_client), coinsgenerator(sub_client), coinsgenerator(sub_client), coinsgenerator(sub_client), coinsgenerator(sub_client), coinsgenerator(sub_client), coinsgenerator(sub_client), coinsgenerator(sub_client), coinsgenerator(sub_client), coinsgenerator(sub_client), coinsgenerator(sub_client), coinsgenerator(sub_client), coinsgenerator(sub_client), coinsgenerator(sub_client), coinsgenerator(sub_client), coinsgenerator(sub_client), coinsgenerator(sub_client), coinsgenerator(sub_client), coinsgenerator(sub_client), coinsgenerator(sub_client), coinsgenerator(sub_client), coinsgenerator(sub_client), coinsgenerator(sub_client), coinsgenerator(sub_client), coinsgenerator(sub_client), coinsgenerator(sub_client), coinsgenerator(sub_client), coinsgenerator(sub_client), coinsgenerator(sub_client), coinsgenerator(sub_client), coinsgenerator(sub_client)]
    for j in range(-1430, 1440, 10):
        sub_client.send_active_obj(timers=thetimer, tz=j)
        print(f"Generating coins in {email}")

def lottery():
	try:
		sub_client.lottery()
		print(f"{email} Played The Lottery")
	except amino.lib.util.exceptions.AlreadyPlayedLottery:
		print(f"{email} Already Played Lottery")
		return


def deviceIdgenerator(st : int = 69):
    ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k = st))
    thedevice = '01' + (MetaSpecial := sha1(ran.encode("utf-8"))).hexdigest() + sha1(bytes.fromhex('01') + MetaSpecial.digest() + base64.b64decode("6a8tf0Meh6T4x7b0XvwEt+Xw6k8=")).hexdigest()
    return thedevice

    
def login(client : amino.Client, email : str, password : str):
    try:
        client.login(email=email, password=password)
        print(f"Logged in/Зашли в {email}\n")
    except amino.lib.util.exceptions.YouAreBanned:
        print(f"{email} This Account Banned")
        print(f"{email} Этот Аккаунт Забанили")
        return
    except amino.lib.util.exceptions.VerificationRequired as e:
        print(f"Verification required for {email}")
        print(f"Запрашивается верификация для {email}")
        link = e.args[0]['url']
        print(link)
        input(" > ")
        login(client, email, password)
    except amino.lib.util.exceptions.InvalidPassword:
        print(f"Incorrect password for {email}")
        print(f"Неверный пароль для {email}")
        passx = input("Enter correct password > ")
        login(client, email, passx)
    except amino.lib.util.exceptions.InvalidAccountOrPassword:
        print(f"Incorrect password for {email}")
        print(f"Неверный пароль для {email}")
        passx = input("Enter correct password > ")
        login(client, email, passx)
    except:
        return
        

def coinsgeneratingproccess(client: amino.Client, email : str, password : str, comid: str):
    try:
        sendingprocces(sub_client)
    except:
        return
        

for line in emails:
    email = line.strip()
    communityid = thecommunityid
    device = deviceIdgenerator()
    thedevicejs = {
    "device_id": f"{device}",
    "device_id_sig": "Aa0ZDPOEgjt1EhyVYyZ5FgSZSqJt",
    "user_agent": "Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-G973N Build/beyond1qlteue-user 5; com.narvii.amino.master/3.4.33562)"
    }
    deviceIdfile = open('device.json', "w")
    json.dump(thedevicejs, deviceIdfile)
    deviceIdfile.close()
    client = amino.Client()
    login(client = client, email = email, password = password)
    sub_client = amino.SubClient(comId = communityid, profile = client.profile)
    lottery()
    for _ in range(25):
            with ThreadPoolExecutor(max_workers=150) as executor:
                  _ = [executor.submit(coinsgeneratingproccess, client, email, password, communityid)]
