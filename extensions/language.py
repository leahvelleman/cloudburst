""" Language, Level, and Form objects
"""
import pynini
from pynini import union as u
from pynini import transducer as t
from pynini import acceptor as a

class Level(object):
    """A level of representation for language forms.

    Note: In almost all cases, :obj:`Level` objects should be created by the
    :function:`Language.add_level` function, and not using the
    :function:`Level()` constructor directly.

    Attributes:
        name: A valid Python identifier naming the level. Level names must be
            unique per language.
        derivation: If this is the root level of its language, a pynini
            acceptor constituting the root lexicon. If this is a child level, a
            pynini transducer deriving representations at this level from
            representations at the parent level.
        parent: The parent level that this one is defined in terms of; `None`
            if this is the root level of its language.
        children: A list of levels that are defined in terms of this one.
        converters: If thislevel and otherlevel are levels in the same language,
            ``thislevel.converters[otherlevel]`` is a path from thislevel to
            otherlevel running through the root node of the language.
        language: Language this level belongs to.
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self,
                 name: str,
                 derivation: pynini.Fst,
                 parent: 'Level' = None) -> None:
        self.name = name
        self.children = []
        self.derivation = derivation
        # TODO: convince self that this derivation isn't getting mutated ever
        # -- it might be useful someday to have the unmutated, uncomposed
        # original on hand.
        if parent:
            self.language = parent.language
            # TODO add test: error or at least warn if the derivation for a
            # child node isn't a transducer
            if self.language.has_name(name):
                raise Error("Level name %s in use or reserved in language %s." %
                            (name, self.language))
            self.parent = parent
            self.language.register_level(self)
        else:
            self.language = self
            self.parent = None
            # TODO add test: error if the "derivation" for a root node isn't an
            # acceptor.
        self.converters = {self: derivation.copy().project(project_output=True)}

    def __repr__(self):
        return self.name

    def add_child(self,
                  name: str,
                  derivation: pynini.Fst) -> None:
        """Add the specified node as a child of mine, and set up converters
        between it and all the nodes I can convert to or from."""
        child = Level(name=name, parent=self,
                      derivation=derivation)
        self.children.append(child)
        self.__connect_child(child)

    def __connect_child(self, child: 'Level') -> None:
        """For every node I can convert to or from, set up converters for the
        specified child node."""
        derivation = child.derivation
        for target in list(self.converters):
            target.converters[child] = pynini.compose(
                target.converters[self], derivation)
            child.converters[target] = pynini.compose(
                derivation.copy().invert(), self.converters[target])

    def walk(self) -> None:
        """Breadth-first traversal of this level and its children.

        Yields:
            :obj:`Level`: The next level in the breadth-first traversal."""
        yield self
        for child in self.children:
            for node in child.walk():
                yield node

    def walk_with_depth(self, level: int = 0) -> None:
        """Breadth-first traversal of this level and its children, keeping
        track of the depth within the tree. Used to pretty-print the levels
        that make up a Language.

        Yields: The next level in the breadth-first traversal and its depth."""
        yield (self, level)
        for child in self.children:
            for (childnode, childlevel) in child.walk_with_depth(level+1):
                yield (childnode, childlevel)

    def is_root(self) -> bool:
        """True if this node is a root node."""
        return self.parent is None

class Language(Level):
    """ A language.

    In Cloudburst a language is made up of one or more levels of representation,
    each with a unique name and sigil and with a set of transducers linking it
    to other levels in the same language. Every language has a `root` level of
    representation. Forms that are identical at the root level are treated as
    identical for other purposes.

    If `lang` is a language and `lev` is the name of a level belonging to it
    then `lang.<lev>` is a reference to the named level. `lang.root` is always
    a reference to the root level of `lang`.
    """

    def __init__(self,
                 root_lexicon: pynini.Fst,
                 alphabet: pynini.Fst) -> None:
        if isinstance(root_lexicon, str):
            root_lexicon = pynini.acceptor(root_lexicon)
        if isinstance(alphabet, str):
            alphabet = pynini.acceptor(alphabet)
        self.sigma_star = pynini.union(root_lexicon,
                                       alphabet).closure()
        super().__init__(name="root", derivation=root_lexicon, parent=None)


    def __repr__(self):
        return self.name

    def register_level(self, level: Level) -> None:
        """ Called by a newly created level to inform the language of its
        name and sigil."""
        self.__dict__[level.name] = level


    def has_name(self, name: str):
        """ Is `name` already in use in this language, either as a level name
        or as the name of a built-in property or method? """
        return name in dir(self)


class Error(Exception):
    """ Generic error for this module. """
    pass

if __name__ == "__main__":
    l = Language(root_lexicon=(u(*"cat fox".split())+
                               u(*"[+Sg] [+Pl]".split())),
                 alphabet=u(*"""a b c d e f g h i j k l m n o p q r s
                            t u v w x y z""".split()))
    l.add_child(name="b", derivation=(pynini.cdrewrite(t("cat[+Pl]",
                                                         "cats"),
                                                       "","",l.sigma_star) *
                                      pynini.cdrewrite(t("fox[+Pl]", "foxes"),
                                                       "","",l.sigma_star)))
    l.b.add_child(name="c", derivation=pynini.cdrewrite(t("[+Sg]",
                                                          ""),"","",l.sigma_star))
    print((a("fox[+Pl]")* l.converters[l.b]).stringify())
