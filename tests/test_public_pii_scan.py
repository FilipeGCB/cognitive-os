import unittest

from tools.scan_public_pii import PATTERNS


class PublicPIIScanTests(unittest.TestCase):
    def test_hex_integrity_digest_is_not_classified_as_phone(self):
        digest = "4121617146cc38deb1a51fcfc0ac73bbdd277893d87a41c612587ab6d7cb388d"
        self.assertIsNone(PATTERNS["Brazilian phone-like number"].search(digest))

    def test_brazilian_phone_like_number_is_still_detected(self):
        self.assertIsNotNone(PATTERNS["Brazilian phone-like number"].search("+55 (11) 99999-9999"))


if __name__ == "__main__":
    unittest.main()
