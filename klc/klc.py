from keyboards import Keyboard, AnsiKeyboard, IsoKeyboard, layouts
from .data import locale_ids
import locale


def get_locale_id(language="english", region=None):
    if region:
        try:
            return locale_ids[f"{language.lower()} - {region.lower()}"]
        except KeyError:
            print(f"{language} - {region} is not a valid identifier")
    else:
        try:
            return locale_ids[language]
        except KeyError:
            print(f"{language} unfortunately does not exist")


def from_keyboard_ansi(kb: AnsiKeyboard, language="english", region=None):
    assert type(kb) == AnsiKeyboard, "kb should be an AnsiKeyboard object"
    locale_id = "0000{}".format(get_locale_id(language, region))
    locale_name = locale.windows_locale[int(locale_id, 16)]
    print(f"KBD\t{kb.name}\t\"{kb.description}\"\n\nCOPYRIGHT\t\"(c) 2021 OEM\"\n\nCOMPANY\t\"OEM\"\n\n"
          f"LOCALENAME\t\"{locale_name}\"\n\nLOCALEID\t\"{locale_id}\"\n\nVERSION\t1.0\n\nSHIFTSTATE\n\n"
          f"0\t//Column 4\n1\t//Column 5 : Shft\n2\t//Column 6 :       Ctrl\n\nLAYOUT\t\t"
          f";an extra \'@\' at the end is a dead key\n\n//SC\tVK_\t\tCap\t0\t1\t2\n"
          f"//--\t----\t\t----\t----\t----\t----\n\n")
