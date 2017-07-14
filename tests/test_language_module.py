#pylint: disable=wildcard-import, missing-docstring, attribute-defined-outside-init, unused-wildcard-import
import unittest
from pynini import transducer as t
from pynini import acceptor as a
from pynini import union as u
import pynini
from cloudburst.language import *

chars = ([chr(i) for i in range(1, 91)] + 
         ["\[", "\\", "\]"])

class UtilityTestCase(unittest.TestCase):
    def test_apply(self):
        self.assertEqual(apply_down(t("Foo", "Bar"), "Foo"), "Bar",
                         "apply_down gives unexpected result")
        self.assertEqual(apply_up(t("Foo", "Bar"), "Bar"), ["Foo"],
                         "apply_up gives unexpected result")

class LanguageTestCase(unittest.TestCase):
    def setUp(self):
        self.language = Language(u(a("foo"), a("bar"), a("baz")))

    def test_add_child(self):
        self.level1 = self.language.add_child(u(t("foo", "Foo"),
                                                t("bar", "Bar"),
                                                t("baz", "Baz")))
        self.assertEqual(self.language.children[0],
                         self.level1, "Child not listed in parent.children[]")
        self.assertEqual(self.level1.parent,
                         self.language, "Parent not accessible as child.parent")

    def test_form_equality(self):
        self.form1 = self.language("foo")
        self.form2 = self.language("foo")
        self.assertEqual(self.form1, self.form2,
                         "Forms identical at root level not treated as equal")

    def test_conversion(self):
        self.level1 = self.language.add_child(
            u(t("foo", "Foo"), t("bar", "Bar"), t("baz", "Baz")))
        self.form1 = self.level1("Foo")
        self.form2 = self.language("foo")
        self.assertEqual(self.form1.convert(self.language), self.form2,
                         "Conversion to root level gave unexpected result")
        self.assertEqual(self.form2.convert(self.level1), self.form1,
                         "Conversion from root level gave unexpected result")

    def test_constraint(self):
        self.level1 = self.language.add_child(a("f") + t("o", "a").closure())
        self.form1 = self.level1("faa")
        with self.assertRaises(Error):
            self.form1 = self.level1("faaa")

    def tearDown(self):
        del self.language

class FormTestCase(unittest.TestCase):
    def setUp(self):
        self.lang = Language(u(*chars).closure(0,3))
        self.level1 = self.lang.add_child(
            pynini.cdrewrite(t("O", "o"), "", "", self.lang.sigma_star))
        self.level2 = self.lang.add_child(
            pynini.cdrewrite(t("F", "f"), "", "", self.lang.sigma_star))

    def test_form_creation(self):
        self.form1 = self.level1("Foo")

    def test_impossible_form_creation(self):
        with self.assertRaises(Error):
            self.form1 = self.level1("foo")

    def test_possible_roots(self):
        self.assertEqual(self.level1.possible_roots("Foo"), ["foo"])

    def test_ambiguity(self):
        self.level3 = self.lang.add_child(
            u(t("A", "a"), t("B", "b")))
        self.level4 = self.level3.add_child(
            u(t("a", "a"), t("b", "a")))
        self.assertTrue(self.level4("a").is_ambiguous())
        with self.assertRaises(UnderlyingAmbiguityWarning):
            print(self.level4("A"))
        with self.assertRaises(SurfaceAmbiguityWarning):
            print(~self.level4("A") >> self.level3)

if __name__ == '__main__':
    unittest.main()
