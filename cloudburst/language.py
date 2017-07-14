""" Language, Level, and Form objects
"""
from typing import Iterable, List, Set
from warnings import warn
import pynini
from pynini import acceptor as a

def apply_down(transducer: pynini.Fst,
               string: str) -> str:
    """Mimics xfst/foma-style apply down"""
    return (a(string)*transducer).project(True).stringify().decode()

def apply_up(transducer: pynini.Fst,
             string: str) -> List[str]:
    """Mimics xfst/foma-style apply up"""
    return [t.decode() for t, _, _ in
            pynini.shortestpath((transducer*a(string)).project(False),
                                nshortest=5).paths()]

# TODO: determine what a reasonable way to set nshortest is.
# TODO: it feels like a wart that these are outside the Level class. Possibly
# they should be turned into to_roots and from_root methods or some such.

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
        self.fmt = lambda x: x
        if parent:
            self.language = parent.language
            self.parent = parent
        else:
            self.language = self
            self.parent = None
        self.converters = {self: derivation.copy().project(project_output=True)}

    def __call__(self, content: str) -> 'Form':
        values = self.possible_roots(content)
        if not values:
            raise InconsistentForm
        return Form(values=values, levels_to_show=[self])

    def possible_roots(self, content: str) -> List[str]:
        """Convert the specified form from this level to the root level."""
        return apply_up(self.language.converters[self], content)

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

class Form(object):
    """ A linguistic form. """
    def __init__(self,
                 levels_to_show: List[Level],
                 values: Iterable[str]) -> None:
        self.levels_to_show = levels_to_show
        self.values = set(values)

    def __invert__(self) -> 'Form':
        return Form(levels_to_show=[], values=self.values)

    def __and__(self, other) -> 'Form':
        return Form(levels_to_show=(self.levels_to_show + other.levels_to_show),
                    values=(self.values & other.values))

    def __repr__(self) -> str:
        renderings = self.at_levels(self.levels_to_show)
        self._issue_ambiguity_warnings(renderings)
        return ", ".join([" ".join(rendering) for rendering in renderings])

    def __eq__(self, other) -> bool:
        return self.values == other.values

    def _issue_ambiguity_warnings(self, renderings) -> None:
        """ Issue warnings for several kinds of ambiguity. """
        if len(renderings) > 1:
            warn("Rendering a form that is ambiguous at the requested level",
                 SurfaceAmbiguityWarning)
        elif len(self.values) > 1:
            warn("Rendering a form that is ambiguous at the root level, but"
                 "not at the requested level",
                 UnderlyingAmbiguityWarning)

    def is_ambiguous(self) -> bool:
        """ True if this Form is ambiguous --- i.e., if it is consistent with
        multiple underlying root representations. """
        return len(self.values) > 1

    def at_level(self, level: Level) -> Set[List[str]]:
        """ The set of renderings of this form at a given level. """
        return self.at_levels([level])

    def at_levels(self, levels: Iterable[Level]) -> Set[List[str]]:
        """ The set of *lists* of renderings of this form at a given *list* of
        levels."""
        out = set()
        for value in self.values:
            item = []
            for level in levels:
                converter = level.language.converters[level]
                item.append(level.fmt(apply_down(converter, value)))
            out.add(item)
        return out








class Error(Exception):
    """ Generic error for this module. """
    pass

class SurfaceAmbiguityWarning(Error):
    """ A rendering has been requested of a Form that is ambiguous at some of
    the requested Levels. """
    pass

class UnderlyingAmbiguityWarning(Error):
    """ A rendering has been requested of a Form that is ambiguous at the root
    Level, but not at any of the requested Levels. """
    pass

class InconsistentForm(Error):
    """ Attempting to create a form that can't meet all the specified criteria.
    """
