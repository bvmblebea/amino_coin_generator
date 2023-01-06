from time import time
from json import load
from time import sleep
from threading import Thread
from tabulate import tabulate
from src.library import amino
from concurrent.futures import ThreadPoolExecutor

accounts = []
with open("accounts.json") as database:
	data = load(database)
	for account in data:
		accounts.append(account)

def login(
		amino: amino.Amino,
		email: str,
		password: str) -> None:
	try:
		print(f"[deviceID]::: {amino.device_id}")
		amino.login(
			email=email,
			password=password,
			socket=False)
		print(f"[Logged in]::: {email}")
	except Exception as e:
		print(f"[Error in login]::: {e}")
        
        
def get_timers() -> dict:
	return {
		"start": int(time()),
		"end": int(time()) + 300
	}

def coin_generator(
		amino: amino.Amino,
		ndc_id: int,
		email: str,
		delay: int) -> None:
	timers = [
		get_timers() for _ in range(50)
	]
	amino.send_active_object(ndc_id=ndc_id, timers=timers)
	print(f"[Generating coins in]::: {email}")

def generate_coins(
		amino: amino.Amino,
		ndc_id: int,
		email: str,
		delay: int) -> None:
	Thread(
		target=coin_generator,
		args=(
			amino.
			ndc_id,
			email,
			delay)
		).start()
	
def play_lottery(
		amino: amino.Amino,
		ndc_id: int) -> None:
	try:
		response = amino.lottery(ndc_id=ndc_id)["api:message"]
		print(f"[Lottery]::: {response}")
	except Exception as e:
		print(f"[Error in play lottery]::: {e}")
		
def watch_ad(amino: amino.Amino) -> None:
	try:
		response = amino.watch_ad()["api:message"]
		print(f"[Watch ad]::: {response}")
	except Exception as e:
		print(f"[Error in watch ad]::: {e}")
		
def transfer_coins() -> None:
	link_info = amino.Amino().get_from_code(
		input("[Blog link]::: "))["linkInfoV2"]["extensions"]["linkInfo"]
	ndc_id = link_info["ndcId"]
	blog_id = link_info["objectId"]
	delay = int(input("[Transfer delay in seconds]::: "))
	for account in accounts:
		amino = amino.Amino()
		email = account["email"]
		password = account["password"]
		try:
			login(
				amino=amino,
				email=email,
				password=password)
			amino.join_community(ndc_id=ndc_id)
			total_coins = amino.get_wallet_info()["wallet"]["totalCoins"]
			print(f"[{email} total coins]::: {total_coins}")
			if total_coins != 0:
				response = amino.send_coins_blog(
					ndc_id=ndc_id,
					blog_Id=blog_id,
					coins=total_coins)["api:message"]
				print(f"[{email} sent]::: {total_coins} coins - {response}")
			elif total_coins > 500:
				total_coins = 500
				response = amino.send_coins_blog(
					ndc_id=ndc_id,
					blog_Id=blog_id,
					coins=total_coins)["api:message"]
				print(f"[{email} sent]::: {total_coins} coins - {response}")
			sleep(delay)
		except Exception as e:
			print(f"[Error in transfer coins]::: {e}")


def main_process() -> None:
	ndc_id = amino.Amino().get_from_code(
		input("[Community link]::: "))["linkInfoV2"]["extensions"]["community"]["ndcId"]
	delay = int(input("[Generation delay in seconds]::: "))
	for account in accounts:
		amino = amino.Amino()
		email = account["email"]
		password = account["password"]
		try:
			login(
				amino=amino,
				email=email,
				password=password)
			watch_ad(amino=amino)
			play_lottery(amino=amino, ndc_id=ndc_id)
			with ThreadPoolExecutor(max_workers=100) as executor: 
				[executor.submit(generate_coins(
						amino, ndc_id, email, delay)) for _ in range(25)]
			sleep(delay)
		except Exception as e:
			print(f"[Error in main process]::: {e}")
