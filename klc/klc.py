from keyboards import Keyboard, AnsiKeyboard, IsoKeyboard
from keyboards import layout_symbols
from klc.data import locale_ids, SC, VK, sym_upper, static
from locale import windows_locale


def get_locale_id(language="english", region=None):
    """If the locale id exists, gives it back. If it doesn't, raises a KeyError"""
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


def make_rows_scs(kb, has_symbols: bool):
    """Depending on the kb type, creates rows of scs and keys with or without custom numbers, an iso key or symbols"""
    if type(kb) == Keyboard:
        try:
            symbols = layout_symbols[kb.name]
        except KeyError:
            symbols = layout_symbols["dvorak"]
        if has_symbols:
            rows = ["1234567890", kb.top_row, kb.homerow, kb.bot_row, symbols]
            scs = [SC["nums"], SC["top_row"], SC["homerow"], SC["bot_row"], SC["symbols"]]
            return rows, scs
        else:
            rows = ["1234567890", kb.top_row, kb.homerow, kb.bot_row]
            scs = [SC["nums"], SC["top_row"], SC["homerow"], SC["bot_row"]]
            return rows, scs
    else:
        rows = [kb.nums, kb.top_row, kb.homerow, kb.bot_row,
                kb.symbols if kb.symbols != "*******" else layout_symbols["dvorak"]]
        scs = [SC["nums"], SC["top_row"], SC["homerow"], SC["bot_row"], SC["symbols"]]
        return rows, scs


def get_kc_line(key: str, sc=None):
    """create a line containing sc, vk and key information. The format is as follows:
    <SC> - <VK code> - <has_capital> - <default ascii code> - <capital ascii code> - <ctrl ascii code>.
    Note that the ctrl ascii code is set to be -1 (doesn't exist)."""
    no_cap = key != key.upper()
    hex_def = hex(ord(key))[2:]
    hex_upper = hex(ord(sym_upper[key]))[2:] if not no_cap else hex(ord(key.upper()))[2:]
    if sc:
        return f"{sc}\t{VK[key]}\t{int(no_cap)}\t00{hex_def}\t00{hex_upper}\t-1"
    else:
        return f"{SC[key]}\t{VK[key]}\t{int(no_cap)}\t00{hex_def}\t00{hex_upper}\t-1"


def from_keyboard(kb, language="english", region=None, has_symbols=True):
    """Takes a Keyboard, AnsiKeyboard or IsoKeyboard object and generates a .klc file corresponding to its name.
    If no symbols, numbers or iso keys are present, uses dvorak symbols, 1234567890 numbers and \\\\ by default."""
    assert type(kb) == Keyboard or type(kb) == AnsiKeyboard or type(kb) == IsoKeyboard, "kb should be a Keyboard object"
    locale_id = get_locale_id(language, region)
    locale_name = windows_locale[int(locale_id, 16)]
    description = f"KBD\t{kb.name}\t\"{kb.description}\"\n\nCOPYRIGHT\t\"(c) 2021 OEM\"\n\nCOMPANY\t\"OEM\"\n\n"\
                  f"LOCALENAME\t\"{'-'.join(locale_name.split('_'))}\"\n\nLOCALEID\t\"0000{locale_id}\"\n\nVERSION\t"\
                  f"1.0\n\nSHIFTSTATE\n\n0\t//Column 4\n1\t//Column 5 : Shft\n2\t//Column 6 :       Ctrl\n\nLAYOUT\t\t"\
                  f";an extra \'@\' at the end is a dead key\n\n//SC\tVK_\t\tCap\t0\t1\t2\n//--\t----\t\t----\t----" \
                  f"\t----\t----\n\n"

    kc_lines = []
    for row, sc_row in zip(*make_rows_scs(kb, has_symbols)):
        for key, sc in zip(row, sc_row):
            kc_lines.append(get_kc_line(key, sc))

    if type(kb) == IsoKeyboard:
        kc_lines.append(get_kc_line(kb.iso_key))

    kc_lines.append("39\tSPACE\t0\t0020\t0020\t0020")
    kc_lines.append("53\tDECIMAL\t0\t002e\t002e\t-1")
    key_lines = '\n'.join(kc_lines)

    desc_2 = f"DESCRIPTIONS\n\n{locale_id}\t{region}-{kb.description}" \
             f"\nLANGUAGENAMES\n\n{locale_id}\t{language}\nENDKBD\n"
    with open(f"klc/generated/{kb.name}.klc", "w", encoding='utf-16') as new_klc_file:
        new_klc_file.write(description + key_lines + static + desc_2)
