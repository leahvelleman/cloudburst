""" Language, Level, and Form objects
"""

class ClrstTransducer(object):
    """A stub class standing in for transducers between levels of
    representation."""
    def __init__(self,
                 source_code: str) -> None:
        self.source_code = source_code

    def __repr__(self) -> str:
        return self.source_code

    def invert(self) -> 'ClrstTransducer':
        """If I'm a transducer from A to B, make a transducer from B to A.
        Currently (ha ha, funny) represented by reversing my 'source code'."""
        return ClrstTransducer(source_code=self.source_code[::-1])

    def think(self):
        "do a think"
        pass

    def __mul__(self, other: 'ClrstTransducer') -> 'ClrstTransducer':
        return ClrstTransducer(source_code=(self.source_code +
                                            other.source_code))


class Level(object):
    """A level of representation for language forms.

    Note: In almost all cases, :obj:`Level` objects should be created by the
    :function:`Language.add_level` function, and not using the
    :function:`Level()` constructor directly.

    Attributes:
        name: A valid Python identifier naming the level. Level names must be
            unique per language.
        sigil: A sigil that surrounds markup text meant to be interpreted as a
            form at this level.
        children: A list of levels that are defined in terms of this one.
        parent: The parent level that this one is defined in terms of; `None`
            if this is the root level of its language.
        converters: If thislevel and otherlevel are levels in the same language,
            ``thislevel.converters[otherlevel]`` is a path from thislevel to
            otherlevel running through the root node of the language.
        language: Language this level belongs to.
    """

    def __init__(self,
                 name: str,
                 sigil: str,
                 language: 'Language') -> None:
        if language.has_sigil(sigil):
            raise Error("Sigil %s in use in language %s" % (sigil, language))
        if language.has_name(name):
            raise Error("Level name %s in use or reserved in language %s" %
                        (name, language))
        self.name = name
        self.sigil = sigil
        self.language = language

        self.children = []
        self.parent = None
        self.converters = {self: ClrstTransducer("0")}

        language.register_level(level=self, name=name, sigil=sigil)

    def __repr__(self):
        return "%s (sigil %s)" % (self.name, self.sigil)

    def __call__(self, text):
        if not self.parent:
            raise Error("Level %s called before being connected to a language."
                        % self.name)
        return text

    def add_child(self,
                  name: str,
                  sigil: str,
                  derivation: ClrstTransducer) -> None:
        """Add the specified node as a child of mine, and set up converters
        between it and all the nodes I can convert to or from."""
        child = Level(name=name, sigil=sigil, language=self.language)
        child.parent = self
        self.children.append(child)
        for target in list(self.converters):
            target.converters[child] = (target.converters[self] * derivation)
            child.converters[target] = (derivation.invert() *
                                        self.converters[target])

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

class Language(object):
    """ A language.

    In Cloudburst a language is made up of one or more levels of representation,
    each with a unique name and sigil and with a set of transducers linking it to
    other levels in the same language. Every language has a `root` level of
    representation. Forms that are identical at the root level are treated as
    identical for other purposes.

    If `lang` is a language and `lev` is the name of a level belonging to it
    then `lang.<lev>` is a reference to the named level. `lang.root` is always
    a reference to the root level of `lang`.
    """

    def __init__(self,
                 rootname: str = "root",
                 rootsigil: str = "|") -> None:
        self.sigils = []
        self.levels = []
        self.rootname = rootname
        rootlevel = Level(name=rootname, sigil=rootsigil, language=self)
        self.rootlevel = rootlevel

    def __repr__(self):
        return ("Language with these levels:\n" +
                "\n".join(
                    [((depth * " ") + level.__repr__())
                     for (level, depth)
                     in self.rootlevel.walk_with_depth()]))

    def register_level(self, level: Level, name: str, sigil: str) -> None:
        """ Called by a newly created level to inform the language of its
        name and sigil."""
        self.levels.append(level)
        self.sigils.append(sigil)
        self.__dict__[name] = level


    def has_sigil(self, sigil: str):
        """ Is `sigil` already in use as a sigil in this language? """
        return sigil in self.sigils

    def has_name(self, name: str):
        """ Is `name` already in use in this language, either as a level name
        or as the name of a built-in property or method? """
        return name in dir(self)

class Error(Exception):
    """ Generic error for this module. """
    pass

"""
o = skoa.orthography("xetliqɨna")
p = skoa.orthography.converters[skoa.pronunciation](x)
p = o.convert_to(skoa.pronunciation)   # Should be a synonym

# This should do the same as the above, though "with" isn't the right keyword.
with skoa:
    o = orthography("xetlɨqɨnə")
    p = orthography.converters[pronunciation](x)
    p = o.convert_to(pronunciation)
"""
