import pyfiglet
from coin_generator_configs import main_functions
from sty import fg
print(fg(33))
print("""Script by deluvsushi
Github : https://github.com/deluvsushi""")
print(pyfiglet.figlet_format("aminocoingenerator", font="graffiti", width=64))
main_functions.main()
