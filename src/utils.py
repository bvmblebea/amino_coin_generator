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


def login(client: amino.Client, email: str, password: str):
	try:
		print(f"[deviceID]::: {client.device_id}")
		client.login(
			email=email, password=password, socket=False)
		print(f"[Logged in]::: {email}")
	except Exception as e:
		print(f"[Error in login]::: {e}")
        
        
def get_timers():
	return {"start": int(time()), "end": int(time()) + 300}


def coin_generator(client: amino.Client, ndc_id: int, email: str):
	timers = [get_timers() for _ in range(50)]
	client.send_active_object(ndc_id=ndc_id, timers=timers)
	print(f"[Generating coins in]::: {email}")
	sleep(5)


def generate_coins(client: amino.Client, ndc_id: int, email: str):
	Thread(target=coin_generator, args=(client, ndc_id, email)).start()
	
	
def play_lottery(client: amino.Client, ndc_id: int):
	try:
		lottery = client.lottery(ndc_id=ndc_id)["api:message"]
		print(f"[Lottery]::: {lottery}")
	except Exception as e:
		print(f"[Error in play lottery]::: {e}")
		
		
def watch_ad(client: amino.Client):
	try:
		watch_ad = client.watch_ad()["api:message"]
		print(f"[Watch ad]::: {watch_ad}")
	except Exception as e:
		print(f"[Error in watch ad]::: {e}")
		
		
def transfer_coins():
	link_info = amino.Client().get_from_code(
		input("[Blog link]::: "))["linkInfoV2"]["extensions"]["linkInfo"]
	ndc_id = link_Info["ndcId"]
	blog_id = link_Info["objectId"]
	for account in accounts:
		email = account["email"]
		password = account["password"]
		try:
			client = amino.Client()
			login(client=client, email=email, password=password)
			client.join_community(ndc_id=ndc_id)
			total_coins = client.get_wallet_info()["wallet"]["totalCoins"]
			print(f"[{email} total coins]::: {total_coins}")
			if total_coins != 0:
				transfer = client.send_coins_blog(
					ndc_id=ndc_id, blog_Id=blog_id, coins=total_coins)["api:message"]
				print(f"[{email} sent]::: {total_coins} coins - {transfer}")
			elif total_coins > 500:
				total_coins = 500
				transfer = client.send_coins_blog(
					ndc_id=ndc_id, blog_Id=blog_id, coins=total_coins)["api:message"]
				print(f"[{email} sent]::: {total_coins} coins - {transfer}")
		except Exception as e:
			print(f"[Error in transfer coins]::: {e}")


def main_process():
	ndc_id = amino.Client().get_from_code(
		input("[Community link]::: "))["linkInfoV2"]["extensions"]["community"]["ndcId"]
	for account in accounts:
		client = amino.Client()
		email = account["email"]
		password = account["password"]
		try:
			login(client=client, email=email, password=password)
			play_lottery(client=client, ndc_id=ndc_id)
			watch_ad(client=client)
			with ThreadPoolExecutor(max_workers=100) as executor: 
				[executor.submit(generate_coins(client, ndc_id, email)) for _ in range(25)]
		except Exception as e:
			print(f"[Error in main process]::: {e}")
