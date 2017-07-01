import hfst
from typing import Union, Optional

class Level:
  """A level of representation for language forms.

  Note: In almost all cases, :obj:`Level` objects should be created by the 
  :function:`Language.addlevel` function, and not using the :function:`Level()`
  constructor directly.

  Attributes:
      name (str): 
        A valid Python identifier naming the level. Level names must be unique
        per language.
      sigil (str): 
        A sigil that surrounds markup text meant to be interpreted as a form at
        this level.
      children (:obj:`list` of :obj:`Level`): 
        A list of levels that are defined in terms of this one.
      parent (:obj:`Level` or None): 
        The parent level that this one is defined in terms of; `None` if this is the
        root level of its language.
      pathto (:obj:`dict` of :obj:`list` of :obj:`transducer`):
        If thislevel and otherlevel are levels in the same language, 
        thislevel.pathto["otherlevel]" is a path from thislevel to otherlevel running
        through the root node of the language.
  """

  def __init__(self, 
              sigil: str,
              name: str,
              derivation: Optional[str]) -> None:
    self.sigil = sigil
    self.name = name
    self.children = []
    self.parent = None
    self.pathto = {}

  def __repr__(self):
    return "%s (sigil %s)" % (self.name, self.sigil)

  def addchild(self, 
               child: 'Level') -> None:
    """Add the specified node as a child of this one. Does not create paths between
    the new child and any other node --- that is handled by the :obj:`Language` object
    this node and its new child belong to."""
    child.parent = self
    self.children.append(child)

  def walk(node) -> None:
    """Breadth-first traversal of this level and its children.

    Yields:
      :obj:`Level`: The next level in the breadth-first traversal."""
    yield node
    for child in node.children:
      for n in child.walk():
        yield n

  def walkwithdepth(node, level = 0) -> None:
    """Breadth-first traversal of this level and its children, keeping track of the
    depth within the tree.

    Yields:
      (:obj:`Level`, int): The next level in the breadth-first traversal and
      its depth."""
    yield (node, level)
    for child in node.children:
      for n in child.walkwithdepth(level+1):
        yield n

class Language:
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
    self.__dict__ = { rootname: rootlevel }
    self.__root = rootlevel
    self.__sigils = [rootsigil]
    self.__levels = [rootlevel]
    self.__rootname = rootname

  def __repr__(self):
    return ("Language with these levels:\n" +
        "\n".join(
          [((depth * " ") + level.__repr__()) for (level,depth) in self.root.walkwithdepth()]))

  def addlevel(self, 
               sigil       : str, 
               name        : str,
               parent      : Level,
               derivation  : str) -> None:
    if sigil in self.__sigils:
      raise ValueError("Sigil %s already in use in this language." % sigil)
    self.__sigils.append(sigil)
    newlevel = Level(sigil = sigil, name = name, derivation = derivation)
    parent.addchild(newlevel)
    self.__dict__[name] = newlevel
    self.__makepathsfor(newlevel)
    self.__levels.append(newlevel)

  def __makepathsfor(self, newlevel: Level) -> None:
    ascent = self.__pathupfrom(newlevel)
    descent = self.__pathdownto(newlevel)
    for level in self.__root.walk():
      level.pathto[newlevel.name] = self.__pathupfrom(level) + self.__pathdownto(newlevel)
      newlevel.pathto[level.name] = self.__pathupfrom(newlevel) + self.__pathdownto(level)

  def __pathupfrom(self, level: Level) -> None:
    path = []
    while level != self.__root:
      path.append({ "lo": level,
                    "hi": level.parent })
      level = level.parent
    return path

  def __pathdownto(self, level: Level) -> None:
    return list(reversed(self.__pathupfrom(level)))
