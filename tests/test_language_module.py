import sys, os
sys.path.append(os.path.abspath('extensions'))
import unittest
from language import Level

class LevelTestCase(unittest.TestCase):
  def setUp(self):
    self.a = Level(sigil = "|", name = "root", derivation = None)
    self.b = Level(sigil = "'", name = "child", derivation = "ghjkl")

  def test_add_child(self):
    self.a.add_child(self.b)
    self.assertEqual(self.a.children[0], self.b, "Child not listed in parent.children[]")
    self.assertEqual(self.b.parent, self.a, "Parent not accessible as child.parent")

  def tearDown(self):
    del self.a

if __name__ == '__main__':
  unittest.main()
