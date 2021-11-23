import aminofix
import concurrent.futures
from time import time
from . import menu_configs, autoreg_functions
from tabulate import tabulate

accounts = open("emails.txt", "r")
client = aminofix.Client()

		# -- coin generator functions --

def auth(email: str, password: str):
	try:
		client.login(email=email, password=password)
		print(f">> Logged in {email}...")
	except aminofix.lib.util.exceptions.YouAreBanned:
		print(f">> Error - {email} This Account Banned...")
	except aminofix.lib.util.exceptions.VerificationRequired as e:
		print(">> Error - VerificationRequired...")
		verification_link = e.args[0]["url"]
		print(f"Verification Link >> {verification_link}")
		verification = input("Waiting for verification >> ")
	except aminofix.lib.util.exceptions.InvalidPassword:
		print(f">> Error - Incorrect password {email}")
		auth(email=email, password=input("Enter correct password >> "))
	except Exception as e:
		print(f">> Error In Auth - {e}")
        
def coin_generator(sub_client: aminofix.SubClient):
	send_active_object = {"start": int(time()), "end": int(time()) +300}
	return send_active_object

def generator_main_process(sub_client: aminofix.SubClient, email: str):
	timers = [coin_generator(sub_client=sub_client) for _ in range(50)]
	sub_client.send_active_obj(timers=timers)
	print(f">> Generating coins in {email}...")

def generating_process(sub_client: aminofix.SubClient, email: str):
	try:
		generator_main_process(sub_client=sub_client, email=email)
	except Exception as e:
		print(f">> Error in generating process - {e}")

def play_lottery(sub_client: aminofix.SubClient, email: str):
	try:
		sub_client.lottery()
		print(f">> {email} Played The Lottery...")
	except aminofix.lib.util.exceptions.AlreadyPlayedLottery:
		print(f">> Error - {email} Already Played Lottery...")

		# -- transfer coins and main function for generating coins -- 
		
def transfer_coins():
    password = input("Password For All Accounts >> ")
    link_Info = client.get_from_code(input("Blog Link >> "))
    com_Id = link_Info.comId; blog_Id = link_Info.blogId
    for line in accounts:
    	email = line.strip(); auth(email=email, password=password)
    	sub_client = aminofix.SubClient(comId=com_Id, profile=client.profile)
    	try:
    		total_coins = int(client.get_wallet_info().totalCoins())
    		print(f">> {email} have {total_coins} coins...")
    		if coins != 0:
    			sub_client.send_coins(coins=total_coins, blogId=blog_Id)
    			print(f">> {email} transfered {total_coins} coins...")
    	except aminofix.lib.util.exceptions.NotEnoughCoins:
    		print(f">> Error - {email} Not Enough Coins...")
    	except aminofix.lib.util.exceptions.YouAreBanned:
    		print(f">> Error - {email} This Account Banned...")
    	except aminofix.lib.util.exceptions.InvalidSession:
    		print(f">> Error - {email} InvalidSession...")
    	except Exception as e:
    		print(f">> Error In Transfer Coins - {e}")

def main_process():
    password = input("Password For All Accounts >> ")
    link_Info = client.get_from_code(input("Community Link >> "))
    com_Id = link_Info.json["extensions"]["community"]["ndcId"]
    for line in accounts:
    	try:
    		email = line.strip(); auth(email=email, password=password)
    		sub_client = aminofix.SubClient(comId=com_Id, profile=client.profile)
    		play_lottery(sub_client=sub_client, email=email)
    		for i in range(20):
    			with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor: 
    				_ = [executor.submit(generating_process(sub_client, email))]
    	except aminofix.lib.util.exceptions.UserNotMemberOfCommunity:
    		client.join_community(comId=com_Id)
    		return
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
