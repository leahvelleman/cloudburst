""" Language, Level, and Form objects
"""
import pynini
from pynini import union as u
from pynini import transducer as t
from pynini import acceptor as a

def apply_down(transducer: pynini.Fst,
               string: str) -> str:
    """Mimics xfst/foma-style apply down"""
    return (a(string)*transducer).project(True).stringify().decode()

def apply_up(transducer: pynini.Fst,
             string: str) -> str:
    """Mimics xfst/foma-style apply up"""
    return (transducer*a(string)).project(False).stringify().decode()

class Level(object):
    """A level of representation for language forms.

    Note: In almost all cases, :obj:`Level` objects should be created by the
    :function:`Language.add_level` function, and not using the
    :function:`Level()` constructor directly.

    Attributes:
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

    def __init__(self,
                 derivation: pynini.Fst,
                 parent: 'Level' = None) -> None:
        self.children = []
        self.derivation = derivation
        if parent:
            self.language = parent.language
            self.parent = parent
        else:
            self.language = self
            self.parent = None
        self.converters = {self: derivation.copy().project(project_output=True)}


    def add_child(self,
                  derivation: pynini.Fst) -> None:
        """Add the specified node as a child of mine, and set up converters
        between it and all the nodes I can convert to or from."""
        child = Level(parent=self,
                      derivation=derivation)
        self.children.append(child)
        self.__connect_child(child)
        return child

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

    In Cloudburst a language is made up of one or more levels of
    representation.  Forms that are identical at the root level are treated as
    identical for other purposes.
    """

    def __init__(self,
                 root_lexicon: pynini.Fst) -> None:
        if isinstance(root_lexicon, str):
            root_lexicon = pynini.acceptor(root_lexicon)
        self.sigma_star = root_lexicon.closure()
        super().__init__(derivation=root_lexicon, parent=None)






class Error(Exception):
    """ Generic error for this module. """
    pass

if __name__ == "__main__":
    l = Language(u(*"cat fox".split())+
                 u(*"[+Sg] [+Pl]".split()))
    b = l.add_child(pynini.cdrewrite(t("cat[+Pl]", "cats"),"","",l.sigma_star) *
                    pynini.cdrewrite(t("fox[+Pl]", "foxes"),"","",l.sigma_star))

    print((a("fox[+Pl]")* l.converters[b]).stringify())
