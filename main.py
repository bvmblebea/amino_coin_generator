from src import utils
from src import configs
from tabulate import tabulate
print("""\033[38;5;45m
Script by deluvsushi
Github : https://github.com/deluvsushi
                     _              _____      _             
     /\             (_)            / ____|    (_)            
    /  \   _ __ ___  _ _ __   ___ | |     ___  _ _ __        
   / /\ \ | '_ ` _ \| | '_ \ / _ \| |    / _ \| | '_ \       
  / ____ \| | | | | | | | | | (_) | |___| (_) | | | | |      
 /_/____\_\_| |_| |_|_|_| |_|\___/ \_____\___/|_|_|_|_|      
  / ____|                         | |           |  _ \       
 | |  __  ___ _ __   ___ _ __ __ _| |_ ___  _ __| |_) | ___  
 | | |_ |/ _ \ '_ \ / _ \ '__/ _` | __/ _ \| '__|  _ < / _ \ 
 | |__| |  __/ | | |  __/ | | (_| | || (_) | |  | |_) | (_) |
  \_____|\___|_| |_|\___|_|  \__,_|\__\___/|_|  |____/ \___/
""")
print(tabulate(configs.MAIN_MENU, tablefmt="psql"))
select = int(input("[Select]::: "))
if select == 1:
	utils.main_process()
	
elif select == 2:
	utils.transfer_coins()
