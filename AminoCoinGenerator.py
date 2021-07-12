import amino
import pyfiglet
import json
import time
from os import path
from coingeneratorconfig import coingeneratorfunctions
from concurrent.futures import ThreadPoolExecutor
from colorama import init, Fore, Back, Style
init()
print(Fore.GREEN + Style.NORMAL)
print("""Script by Lil Zevi
Github : https://github.com/LilZevi""")
print(pyfiglet.figlet_format("aminocoingenerator", font="rectangles"))
THIS_FOLDER = path.dirname(path.abspath(__file__))
emails = path.join(THIS_FOLDER, 'emails.txt')
deviceIdfile = path.join(THIS_FOLDER, "device")
emails = open(emails, "r")
print("""[1] Generate Coins
[2] Transfer Coins of All Accounts""")
theselect = input("Type the Number >> ")
	
	
def coinsgenerator(sub_client : amino.SubClient):
	generatingcoins = {"start": int(time.time()), "end": int(time.time()) +300}
	return generatingcoins

def sendingprocces(sub_client : amino.SubClient):
	thetimer = [coinsgenerator(sub_client) for _ in range(50)]
	sub_client.send_active_obj(timers=thetimer)
	print(f"Generating coins in {email}")

def coinsgeneratingproccess(client: amino.Client, email : str, password : str, comid: str):
	try:
		sendingprocces(sub_client)
	except:
		return

def lottery():
	try:
		sub_client.lottery()
		print(f"{email} Played The Lottery")
	except amino.lib.util.exceptions.AlreadyPlayedLottery:
		print(f"{email} Already Played Lottery")
		return

#coins transfer functions
def coinstransfer():
    client = amino.Client()
    password = input("Password for all accounts >> ")
    thebloglink = input("Blog Link >> ")
    theblog = client.get_from_code(thebloglink)
    blogid = client.get_from_code(str(thebloglink.split('/')[-1])).objectId
    thecommunityid = theblog.path[1:theblog.path.index('/')]
    for line in emails:
    	email = line.strip()
    	coingeneratorfunctions.login(client = client, email = email, password = password)
    	sub_client = amino.SubClient(comId=thecommunityid, profile=client.profile)
    	try:
    	   	coins = int(client.get_wallet_info().totalCoins)
    	   	print(f"{email} have {coins} coins")
    	   	if coins != 0:
    	   	   sub_client.send_coins(coins=coins, blogId=blogid)
    	   	   print(f"{email} Transfered {coins} coins")
    	except amino.lib.util.exceptions.NotEnoughCoins:
    	   	print(f"{email} Not Enough Coins")
    	   	return
    	except amino.lib.util.exceptions.InvalidRequest:
    	   	print("InvalidRequest")
    	   	return
    	except amino.lib.util.exceptions.YouAreBanned:
    	   	print(f"{email} This Account Banned")
    	   	return
    	except amino.lib.util.exceptions.InvalidSession:
    	   	print(f"{email} InvalidSession")
    	   	return
    	except:
    		return

if theselect == "1":
    client = amino.Client()
    password = input("Password for all accounts >> ")
    communitylink = input("Community Link >> ")
    communityinfo = client.get_from_code(communitylink)
    communityid = communityinfo.path[1:communityinfo.path.index('/')]

    for line in emails:
        email = line.strip()
        device = coingeneratorfunctions.deviceIdgenerator()
        thedevicejs = {
        "device_id": f"{device}",
        "device_id_sig": "Aa0ZDPOEgjt1EhyVYyZ5FgSZSqJt",
        "user_agent": "Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-G973N Build/beyond1qlteue-user 5; com.narvii.amino.master/3.4.33562)"
        }
        deviceIdfile = open('device.json', "w")
        json.dump(thedevicejs, deviceIdfile)
        deviceIdfile.close()
        coingeneratorfunctions.login(client = client, email = email, password = password)
        sub_client = amino.SubClient(comId=communityid, profile = client.profile)
        lottery()
        for i in range(20):
            with ThreadPoolExecutor(max_workers=150) as executor:
                 _ = [executor.submit(coinsgeneratingproccess, client, email, password, communityid)]

elif theselect == "2":
	coinstransfer()
