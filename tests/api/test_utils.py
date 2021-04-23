import unittest

from ocdb.api import utils


class TestUtils(unittest.TestCase):
    def test_encrypt(self):
        with self.assertRaises(ValueError) as e:
            # noinspection PyTypeChecker
            utils.encrypt('password', None)

        self.assertEqual('password-key must be set: ocdb conf password-key [key].', str(e.exception))

        res = utils.encrypt('password', 'key1')
        self.assertEqual('fbe24205bf452fe3babc90b2e0446ca44bd287f8c303fc7ad4d298d0616'
                         '953ff418710c70fb9dc4aa26a1d950474679c1967656ffcad7b5c339debb77538e0db', res)


if __name__ == '__main__':
    unittest.main()
