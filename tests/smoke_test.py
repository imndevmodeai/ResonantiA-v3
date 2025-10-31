import unittest
from Three_PointO_ArchE.resonantia_maestro import ResonantiaMaestro

class SmokeTest(unittest.TestCase):
    def test_import_maestro(self):
        self.assertTrue(callable(ResonantiaMaestro))

if __name__ == '__main__':
    unittest.main()
