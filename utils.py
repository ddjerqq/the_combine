import os
import sys
import time


FEGGZ_NFT = """
███████╗ ███████╗  ██████╗   ██████╗  ███████╗    ███╗   ██╗ ███████╗ ████████╗
██╔════╝ ██╔════╝ ██╔════╝  ██╔════╝  ╚══███╔╝    ████╗  ██║ ██╔════╝ ╚══██╔══╝
█████╗   █████╗   ██║  ███╗ ██║  ███╗   ███╔╝     ██╔██╗ ██║ █████╗      ██║   
██╔══╝   ██╔══╝   ██║   ██║ ██║   ██║  ███╔╝      ██║╚██╗██║ ██╔══╝      ██║   
██║      ███████╗ ╚██████╔╝ ╚██████╔╝ ███████╗    ██║ ╚████║ ██║         ██║   
╚═╝      ╚══════╝  ╚═════╝   ╚═════╝  ╚══════╝    ╚═╝  ╚═══╝ ╚═╝         ╚═╝   
"""


def welcome_screen() -> None:
    for char in FEGGZ_NFT:
        if char == "█":
            rgb(char, color="#ff0000", newline=False)
        else:
            rgb(char, newline=False)
    print()


def rgb(text: str, /, color: str | tuple | int = "#ffffff", *, newline: bool = True) -> None:
    """
        print rgb color 🎊 with this
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        \n
        ~~~~~~~~~~~~~~
        Args:
            text  (str): the text you want to print, str() method is automatically called on it
            color (str): #000000 hex representation of color, prefixed with # or not
            color (tuple): (red, green, blue) color tuple
            color (int): 0xff0000 integer representation of hex color.
            newline (bool default False): whether or now you want to print a new line \n
            after you are done printing rgb, you can insert colored text if you set this to false
        \n
        ~~~~~~~~~~~~~~
        Retrurns:
            None
        \n
        ~~~~~~~~~~~~~~
        Example:
            >>> rgb("lorem ipsum", "#ff0000")
            >>> rgb("lorem ipsum", (255, 0, 0))
            >>> rgb("lorem ipsum", 0xff0000)
            >>> rgb("lorem", "#ff0000", newline=False)
            >>> rgb("ipsum", "#00ff00", newline=False)
    """
    if type(color) == str:
        color = tuple(int(color.lstrip("#")[i: i + 2], 16) for i in (0, 2, 4))

    elif type(color) == tuple:
        pass

    elif type(color) == int:
        blue = color % 256
        green = ((color - blue) // 256) % 256
        red = ((color - blue) // 256 ** 2) - green // 256
        color = red, green, blue

    else:
        raise Exception(f"invalid color {color}")

    if sum(color) > 765:
        raise Exception(f"invalid color {color}")

    end = "\n" if newline else ""
    _color = f"\033[38;2;{color[0]};{color[1]};{color[2]}m"
    _end_char = "\033[0m"

    sys.stdout.write(_color + str(text) + _end_char + end)
    sys.stdout.flush()

