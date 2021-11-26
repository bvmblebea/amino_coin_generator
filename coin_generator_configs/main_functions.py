import concurrent.futures
from . import menu_configs, autoreg_functions
from time import time
from library import aminoboi
from tabulate import tabulate

accounts = open("emails.txt", "r")
client = aminoboi.Client()

		# -- coin generator functions --


def auth(email: str, password: str):
	try:
		client.auth(email=email, password=password)
		print(f">> Logged in {email}...")
	except Exception as e:
		print(f">> Error in Auth {e}")
        
def coin_generator():
	send_active_object = {"start": int(time()), "end": int(time()) +300}
	return send_active_object

def generator_main_process(ndc_Id: int, email: str):
	timers = [coin_generator() for _ in range(50)]
	client.send_active_object(ndc_Id=ndc_Id, timers=timers)
	print(f">> Generating coins in {email}...")

def generating_process(ndc_Id: int, email: str):
	generator_main_process(ndc_Id=ndc_Id, email=email)

def play_lottery(ndc_Id: int):
	try:
		lottery = client.lottery(ndc_Id=ndc_Id)
		print(f">> Lottery - {lottery['api:message']}")
	except Exception as e:
		print(f">> Error in play lottery - {e}")
		
def watch_ad():
	try:
		watch_ad = client.watch_ad()
		print(f">> Watch Ad - {watch_ad['api:message']}")
	except Exception as e:
		print(f">> Error in watch ad - {e}")
		
		# -- transfer coins and main function for generating coins -- 
		
def transfer_coins():
    password = input("Password For All Accounts >> ")
    link_Info = client.get_from_link(input("Blog Link >> "))["linkInfoV2"]
    ndc_Id = link_Info["extensions"]["linkInfo"]["ndcId"]; blog_Id = link_Info["extensions"]["linkInfo"]["objectId"]
    for line in accounts:
    	email = line.strip(); auth(email=email, password=password)
    	try:
    		total_coins = client.get_wallet_info()["wallet"]["totalCoins"]
    		print(f">> {email} have {total_coins} coins...")
    		if total_coins != 0:
    			transfer = client.send_coins_blog(ndc_Id=ndc_Id, blog_Id=blog_Id, coins=total_coins)
    			print(f">> {email} transfered {total_coins} coins - {transfer['api:message']}...")
    	except Exception as e:
    		print(f">> Error In Transfer Coins - {e}")

def main_process():
    password = input("Password For All Accounts >> ")
    link_Info = client.get_from_link(input("Community Link >> "))
    ndc_Id = link_Info["linkInfoV2"]["extensions"]["community"]["ndcId"]
    for line in accounts:
    	try:
    		email = line.strip(); auth(email=email, password=password)
    		play_lottery(ndc_Id=ndc_Id); watch_ad()
    		with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor: 
    			_ = [executor.submit(generating_process(ndc_Id, email)) for _ in range(20)]
    		print(f"-- Finished Generating Coins In {email}")
    	except Exception as e:
    		print(f">> Error in main process - {e}")

           
		# -- transfer coins and main function for generating coins -- 

def main():
	print(tabulate(menu_configs.main_menu, tablefmt="psql"))
	select = input("Select >> ")
	
	if select == "1":
		main_process()
	
	elif select == "2":
		transfer_coins()
	
	elif select == "3":
		autoreg_functions.auto_register(password=input("Password For All Accounts >> "))
	
