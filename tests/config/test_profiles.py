import unittest

from src.config._cipher import _Cipher
from src.config.profiles import ProfilesConfig


class TestProfiles(unittest.TestCase):

    def test_profiles(self):
        cipher = _Cipher()

        p = ProfilesConfig({}, cipher)
        p['p1'] = 'sc1'
        p['p2'] = 'sc2'
        pns = []
        for pn in p:
            pns.append(pn)
        self.assertListEqual(['p1', 'p2'], pns)

        td = p.to_dict()
        self.assertEqual(2, len(td))

        p2 = ProfilesConfig(td, cipher)
        for n in p:
            self.assertEqual(p[n], p2[n])
