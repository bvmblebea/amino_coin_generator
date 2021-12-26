from pyfiglet import figlet_format
from sty import fg; print(fg(33))
from coin_generator_configs import main_functions
print("""Script by deluvsushi
Github : https://github.com/deluvsushi""")
print(figlet_format("aminocoingenerator", font="graffiti", width=64))
main_functions.main()
