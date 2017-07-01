""" Language, Level, and Form objects
"""
from typing import Optional

class Level(object):
    """A level of representation for language forms.

    Note: In almost all cases, :obj:`Level` objects should be created by the
    :function:`Language.add_level` function, and not using the :function:`Level()`
    constructor directly.

    Attributes:
        name: A valid Python identifier naming the level. Level names must be unique
          per language.
        sigil: A sigil that surrounds markup text meant to be interpreted as a form at
          this level.
        children: A list of levels that are defined in terms of this one.
        parent : The parent level that this one is defined in terms of; `None` if this is the
          root level of its language.
        pathto : If thislevel and otherlevel are levels in the same language,
          thislevel.pathto["otherlevel]" is a path from thislevel to otherlevel running
          through the root node of the language.
    """

    def __init__(self,
                 name: str,
                 sigil: str,
                 derivation: Optional[str]) -> None:
        self.sigil = sigil
        self.name = name
        self.children = []
        self.parent = None
        self.pathto = {}
        self.derivation = derivation

    def __repr__(self):
        return "%s (sigil %s)" % (self.name, self.sigil)

    def add_child(self, child: 'Level') -> None:
        """Add the specified node as a child of this one. Does not create paths between
        the new child and any other node --- that is handled by the :obj:`Language` object
        this node and its new child belong to."""
        child.parent = self
        self.children.append(child)

    def walk(self) -> None:
        """Breadth-first traversal of this level and its children.

        Yields:
            :obj:`Level`: The next level in the breadth-first traversal."""
        yield self
        for child in self.children:
            for node in child.walk():
                yield node

    def walk_with_depth(self, level: int = 0) -> None:
        """Breadth-first traversal of this level and its children, keeping track of the
        depth within the tree.

        Yields: The next level in the breadth-first traversal and its depth."""
        yield (self, level)
        for child in self.children:
            for (childnode, childlevel) in child.walk_with_depth(level+1):
                yield (childnode, childlevel)

class Language(object):
    """ A language.

    In Cloudburst a language is made up of one or more levels of representation,
    each with a unique name and sigil and with a set of transducers linking it to
    other levels in the same language. Every language has a `root` level of
    representation. Forms that are identical at the root level are treated as
    identical for other purposes.

    If `lang` is a language and `lev` is the name of a level belonging to it
    then `lang.<lev>` is a reference to the named level. `lang.root` is always
    a reference to the root level of `lang`."""

    def __init__(self,
                 rootsigil: str = "|",
                 rootname: str = "root") -> None:
        rootlevel = Level(rootsigil, rootname, None)
        self.__dict__ = {rootname: rootlevel}
        self.__root = rootlevel
        self.__sigils = [rootsigil]
        self.__levels = [rootlevel]
        self.__rootname = rootname

    def __repr__(self):
        return ("Language with these levels:\n" +
                "\n".join(
                    [((depth * " ") + level.__repr__())
                     for (level, depth)
                     in self.__root.walk_with_depth()]))

    def add_level(self,
                  name: str,
                  sigil: str,
                  parent: Level,
                  derivation: str) -> None:
        """ Add a level of representation to the language. """
        if sigil in self.__sigils:
            raise Error("Sigil %s already in use in this language." % sigil)
        self.__sigils.append(sigil)
        newlevel = Level(sigil=sigil, name=name, derivation=derivation)
        parent.add_child(newlevel)
        self.__dict__[name] = newlevel
        self.__makepathsfor(newlevel)
        self.__levels.append(newlevel)

    def think(self):
        """ foo """
        pass

    def __makepathsfor(self, newlevel: Level) -> None:
        for level in self.__root.walk():
            level.pathto[newlevel.name] = (self.__pathupfrom(level)
                                           + self.__pathdownto(newlevel))
            newlevel.pathto[level.name] = (self.__pathupfrom(newlevel)
                                           + self.__pathdownto(level))

    def __pathupfrom(self, level: Level) -> None:
        path = []
        while level != self.__root:
            path.append({"lo": level,
                         "hi": level.parent})
            level = level.parent
        return path

    def __pathdownto(self, level: Level) -> None:
        return list(reversed(self.__pathupfrom(level)))


class Error(Exception):
    """ Generic error for this module. """
    pass
