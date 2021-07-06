from functools import reduce
import operator


layouts = {"abc": ("abcdefghij", "klmnopqrst", "uvwxyz.,'-", "abc", "just the alphabet"),
           "qwerty": ("qwertyuiop", "asdfghjkl;", "zxcvbnm,./", "qwerty", "de facto standard (unfortunately)"),
           "dvorak": ("',.pyfgcrl", "aoeuidhtns", ";qjkxbmwvz", "dvorak", "Default Dvorak"),
           "colemak": ("qwfpgjluy;", "arstdhneio", "zxcvbkm,./", "colemak", "OG colemak"),
           "halmak": ("wlrbz;qudj", "shnt,.aeoi", "fmvc/gpxky", "halmak", "AI generated layout"),
           "mtgap": ("ypoujkdlcw", "inea,mhtsr", "qz/.;bfgvx", "mtgap", "ahead of its time"),
           "colemak qix": (";lcmkjfuyq", "arstgpneio", "xwdvzbn/.,", "colemak_qix", "colemak but good or something")}

layout_symbols = {"qwerty":      "`-=[]'\\",
                  "dvorak":      "`[]/=-\\",
                  "colemak":     "`-=[]'\\",
                  "halmak":      "`-=[]'\\",
                  "mtgap":       "`-=[]'\\",
                  "abc":         "`-=[]'\\",
                  "colemak qix": "`=[-]'\\"}


class Keyboard:
    """
    A barebones representation of a keyboard, containing only the 30 main keys.
    """
    def __init__(self, top_row: str,
                 homerow: str,
                 bot_row: str,
                 name=None,
                 description=None):

        self.name = name if name else homerow[:4]
        self.description = description if description else self.name
        self.top_row = top_row
        self.homerow = homerow
        self.bot_row = bot_row
        self.layout  = [list(self.top_row), list(self.homerow), list(self.bot_row)]
        self.fingers = [[self.top_row[0] + self.homerow[0] + self.bot_row[0]],
                        [self.top_row[1] + self.homerow[1] + self.bot_row[1]],
                        [self.top_row[2] + self.homerow[2] + self.bot_row[2]],
                        list(self.top_row[3:5]) + list(self.homerow[3:5]) + list(self.bot_row[3:5]),
                        list(self.top_row[5:7]) + list(self.homerow[5:7]) + list(self.bot_row[5:7]),
                        [self.top_row[7] + self.homerow[7] + self.bot_row[7]],
                        [self.top_row[8] + self.homerow[8] + self.bot_row[8]],
                        [self.top_row[9] + self.homerow[9] + self.bot_row[9]]]

    def __str__(self):
        return (f"{self.name}:\n"
                f"{' '.join(self.top_row[:5])}   {' '.join(self.top_row[5:])}\n"
                f"{' '.join(self.homerow[:5])}   {' '.join(self.homerow[5:])}\n"
                f"{' '.join(self.bot_row[:5])}   {' '.join(self.bot_row[5:])}\n")

    def __repr__(self):
        return (f"Keyboard(\"{self.top_row}\", \"{self.homerow}\", "
                f"\"{self.bot_row}\", \"{self.name}\")")

    def __bytes__(self):
        return bytes(repr(self).encode('utf-8'))

    def __len__(self):
        return 30

    def __iter__(self):
        for key in reduce(operator.iconcat, self.layout):
            yield key


class AnsiKeyboard(Keyboard):
    """
    Ansi version of a keyboard
    Inherits:
        the Keyboard class

    Attributes:
        top_row (str):     A string of length 10 representing the top row of the keyboard, without symbols.
        homerow (str):     A string of length 10 representing the homerow of the keyboard, without symbols.
        bot_row (str):     A string of length 10 representing the bot row of the keyboard.
        name=None:         If not given, will be klc_files from the first 4 keys on the homerow.
        description=None:       A description of the current layout. If not given, defaults to self.name.
        symbols="*******": A string of length 7 representing all 7 symbol keys, from right->left and top->bottom.
        nums="1234567890": A string of length 10 representing what are on qwerty the number positions.
    """
    def __init__(self, top_row: str,
                 homerow: str,
                 bot_row: str,
                 name=None,
                 description=None,
                 symbols="*******",
                 nums="1234567890"):
        super().__init__(top_row, homerow, bot_row, name, description)
        self.symbols = "*******" if len(symbols) != 7 else symbols
        self.wide_symbols = list(self.symbols)
        self.nums = nums
        self.wide_nums = list(nums)

    def __str__(self):
        return (f"{self.name}:\n"
                f"{self.wide_symbols[0]} {' '.join(self.wide_nums)} {' '.join(self.wide_symbols[1:3])} BSP\n"
                f"TB {' '.join(self.top_row)} {' '.join(self.wide_symbols[3:5])} {self.wide_symbols[6]*2}\n"
                f"CPS {' '.join(self.homerow)} {self.wide_symbols[5]} ENT\n"
                f"SHFT {' '.join(self.bot_row)} SHFT\n")

    def __repr__(self):
        return (f"AnsiKeyboard(\"{self.top_row}\", \"{self.homerow}\", \"{self.bot_row}\", "
                f"\"{self.symbols}\", \"{self.name}\", \"{self.nums}\")")

    def mod_wide(self):
        """widemods the keyboard in place
        NOTE: leaves self.layout and self.symbols untouched
        """
        self.wide_symbols = (self.symbols[0] + self.nums[-2:] + self.top_row[-1] +
                             self.symbols[4] + self.homerow[-1] + self.symbols[6])
        self.wide_nums = self.nums[:5] + self.symbols[1:3] + self.nums[-5:-2]
        self.top_row = self.top_row[:5] + self.symbols[3] + self.top_row[-5:-1]
        self.homerow = self.homerow[:5] + self.symbols[5] + self.homerow[-5:-1]
        self.bot_row = self.bot_row[:5] + self.bot_row[-1] + self.bot_row[-5:-1]


class IsoKeyboard(AnsiKeyboard):
    """Iso version of a keyboard
    Inherits:
        the AnsiKeyboard class

    Attributes:
        top_row (str):     A string of length 10 representing the top row of the keyboard, without symbols.
        homerow (str):     A string of length 10 representing the homerow of the keyboard, without symbols.
        bot_row (str):     A string of length 10 representing the bot row of the keyboard.
        name=None:         If not given, will be klc_files from the first 4 keys on the homerow.
        description=None:  A description of the current layout. If not given, defaults to self.name.
        symbols="*******": A string of length 7 representing all 7 symbol keys, from right->left and top->bottom.
        nums="1234567890": A string of length 10 representing what are on qwerty the number positions.
        iso_key="*":     : A character representing the key that distinguishes iso keyboards in the bottom left.
                           If not given, defaults to the 6th symbol given, which is '\' on qwerty."""
    def __init__(self, top_row: str,
                 homerow: str,
                 bot_row: str,
                 name=None,
                 description=None,
                 symbols="*******",
                 nums="1234567890",
                 iso_key=None):
        super().__init__(top_row, homerow, bot_row, name, description, symbols, nums)
        self.iso_key = iso_key if iso_key else self.symbols[6]

    def __str__(self):
        return (f"{self.name}:\n"
                f"{self.wide_symbols[0]} {' '.join(self.nums)} {' '.join(self.wide_symbols[1:3])} BSP\n"
                f"TB {' '.join(self.top_row)} {' '.join(self.wide_symbols[3:5])} EN\n"
                f"CPS {' '.join(self.homerow)} {' '.join(self.wide_symbols[5:])} N\n"
                f"SF {self.iso_key} {' '.join(self.bot_row)} SHFT\n")

    def __repr__(self):
        return (f"IsoKeyboard(\"{self.top_row}\", \"{self.homerow}\", \"{self.bot_row}\", "
                f"\"{self.symbols}\", \"{self.name}\", \"{self.nums}\", \"{self.iso_key}\")")

    def mod_angle(self):
        self.bot_row, self.iso_key = self.bot_row[1:5] + self.iso_key + self.bot_row[5:], self.bot_row[0]
