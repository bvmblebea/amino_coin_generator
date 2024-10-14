from src import utils
from src import configs
from tabulate import tabulate

print("""
  ___  ___  ________ _   _ _____ _____ _____ _____ _   _ 
 / _ \ |  \/  |_   _| \ | |  _  /  __ \  _  |_   _| \ | |
/ /_\ \| .  . | | | |  \| | | | | /  \/ | | | | | |  \| |
|  _  || |\/| | | | | . ` | | | | |   | | | | | | | . ` |
| | | || |  | |_| |_| |\  \ \_/ / \__/\ \_/ /_| |_| |\  | Creator: https://github.com/bvmblebea
\_| |_/\_|  |_/\___/\_| \_/\___/ \____/\___/ \___/\_| \_/                               
 _____  _____ _   _  ___________  ___ _____ ___________  
|  __ \|  ___| \ | ||  ___| ___ \/ _ \_   _|  _  | ___ \ 
| |  \/| |__ |  \| || |__ | |_/ / /_\ \| | | | | | |_/ / 
| | __ |  __|| . ` ||  __||    /|  _  || | | | | |    /  
| |_\ \| |___| |\  || |___| |\ \| | | || | \ \_/ / |\ \  
 \____/\____/\_| \_/\____/\_| \_\_| |_/\_/  \___/\_| \_|                                                
""")
print(tabulate(configs.MAIN_MENU, tablefmt="psql"))
select = int(input("[Select]::: "))
if select == 1:
	utils.start_generator()
elif select == 2:
	utils.transfer_coins()
