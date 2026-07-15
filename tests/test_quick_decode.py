from __future__ import annotations

import unittest
import binascii

from scripts.quick_decode import (
    atbash,
    autokey_plaintext,
    character_profile,
    decode_alternating_run_lengths,
    decode_base32,
    decode_base85,
    decode_morse,
    decode_multitap_pairs,
    decode_uu_line,
    gronsfeld,
    hex_atbash,
    match_historical_passcode,
    keyboard_shift,
    vigenere,
    xor_hex_with_text,
)


class QuickDecodeTests(unittest.TestCase):
    def test_atbash_archive_example(self):
        self.assertEqual(atbash("cbt33nzplgl878iw"), "xyg33makoto878rd")

    def test_hex_atbash_preserves_case_family(self):
        self.assertEqual(hex_atbash("0aF7"), "f5A8")

    def test_base32_and_base85(self):
        self.assertEqual(decode_base32("JBSWY3DP"), "Hello")
        self.assertEqual(decode_base85("NM&qnZy;B1a%^NF"), "Hello World!")

    def test_morse_symbol_swap_is_simultaneous(self):
        self.assertEqual(decode_morse("--- ..-", dot="-", dash="."), "SG")

    def test_gronsfeld_archive_example(self):
        self.assertEqual(gronsfeld("IcBtTpWsHuFlbNC2", "1984"), "HtTpSgOoGlXhaEU2")

    def test_multitap_press_key_order(self):
        self.assertEqual(decode_multitap_pairs("15 28 38"), "juv")

    def test_alternating_run_lengths(self):
        self.assertEqual(decode_alternating_run_lengths("1151"), "A")

    def test_character_profile(self):
        profile = character_profile("Ab3!")
        self.assertEqual(profile["class_pattern"], "Aa9!")
        self.assertEqual(profile["digits"], 1)
        self.assertEqual(profile["symbols"], 1)

    def test_historical_format_is_labeled(self):
        matches = match_historical_passcode("xyg33makoto878rd")
        self.assertEqual(matches[0]["source"], "investigation_2016")
        self.assertEqual(matches[0]["parts"]["keyword"], "makoto")

    def test_full_keyboard_mirror_archive_rule(self):
        self.assertEqual(keyboard_shift("1qaz", "mirror"), "0p;/")

    def test_vigenere_standard_example(self):
        self.assertEqual(vigenere("LXFOPVEFRNHR", "LEMON"), "ATTACKATDAWN")

    def test_plaintext_autokey_standard_example(self):
        self.assertEqual(autokey_plaintext("QNXEPVYTWTWP", "QUEENLY"), "ATTACKATDAWN")

    def test_uu_line_and_xor(self):
        encoded = binascii.b2a_uu(b"Cat").decode("ascii").rstrip("\n")
        self.assertEqual(decode_uu_line(encoded), "Cat")
        self.assertEqual(xor_hex_with_text("0928", "A"), "Hi")


if __name__ == "__main__":
    unittest.main()
