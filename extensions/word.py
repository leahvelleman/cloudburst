"""
# TODO:

  EASY DISPLAY STUFF
   "Back" links from lexicon entries
   
   Permalinks to paragraphs using pilcrow symbol, and give paragraph numbers in the
   lexical index instead of source code line numbers. (Or have a setting for this?)

   Make section permalinks use the section symbol and appear to the left of the
   sec hed.

  MEDIUM DISPLAY STUFF 

   Why aren't starred wordforms getting <em>'d?

   Figure out how to link indexible words to the section where they're defined.



  HARDER STUFF
   Start using pynini for lemmatization, even if all we do is transduce every
   word to itself. 

   Then start getting a bit smarter about lemmatization. If a lex entry lists
   principal parts explicitly, can we link from them to it correctly?

   What would it take to correctly lemmatize words under stress push?

"""

# TODO: Docstrings
# TODO: Can we somehow make this project autodoc itself?
# TODO: Put up at readthedocs.io?

from docutils import nodes
from docutils.parsers.rst import Directive
from sphinx.locale import _
from collections import defaultdict
from encodings import punycode
from unidecode import unidecode

def setup(app):
  app.add_node(wordlist)
  app.add_node(word,
      html=(visit_word_node, depart_word_node),
      text=(visit_word_node, depart_word_node),
      latex=(visit_word_node, depart_word_node))
  app.add_role('word', word_role)
  app.add_directive('wordlist', WordlistDirective)
  app.add_directive('lemma', LemmaDirective)
  app.connect('doctree-resolved', process_word_nodes)
  app.connect('env-purge-doc', purge_words)
  return {'version': '0.1'}

class word(nodes.General, nodes.Element):
  pass

class wordlist(nodes.General, nodes.Element):
  pass

def visit_word_node(self, node):
  self.visit_emphasis(node)

def depart_word_node(self, node):
  self.depart_emphasis(node)

def word_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
  if text[0] == '*':
    return nodes.strong(_(text), _(text)), [] #WHY IS THIS NOT WORKING?
  env = inliner.document.settings.env
  app = env.app
  if not hasattr(env, 'cloudburst_words'):
    env.cloudburst_words = defaultdict(list)
  out = []
  for word in text.split():
    targetid = "word-%d" % env.new_serialno('word')
    targetnode = nodes.target('', '', ids=[targetid])
    lemma = word.lower()
    wordnode = make_lexicon_link(word, lemma, app, options)
    env.cloudburst_words[lemma].append({
      'docname': env.docname,
      'lineno': lineno,
      'wordnode': wordnode.deepcopy(),
      'targetnode': targetnode,
    })
    out.append(targetnode)
    out.append(wordnode)
    out.append(nodes.Text(' '))
  return out, []

def make_lexicon_link(text, lemma, app, options):
  node = nodes.reference('', '', refid='lexicon-%s' % punycode.punycode_encode(lemma), **options)
  innernode = nodes.emphasis(_(text), _(text))
  node.append(innernode)
  return node

class WordlistDirective(Directive):
  def run(self):
    return [wordlist('')]

class LemmaDirective(Directive):
  has_content = True
  option_spec = {
    'headword': lambda x: x,
    'rel': lambda x: x
  }
  def run(self):
    print self.content
    env = self.state.document.settings.env
    if not hasattr(env, 'cloudburst_all_lemmas'):
      env.cloudburst_all_lemmas = {}
    lemma = self.content[0]
    env.cloudburst_all_lemmas[lemma] = { k: v for (k, v) in self.options.iteritems() }
    env.cloudburst_all_lemmas[lemma]['docname'] = env.docname,
    env.cloudburst_all_lemmas[lemma]['definition'] = ' '.join(self.content[2:])
    return []

def purge_words(app, env, docname):
  if not hasattr(env, 'cloudburst_words'):
    return
  for (lemma, wordtokens) in env.cloudburst_words.iteritems():
    if env.cloudburst_words[lemma] == []:
      del env.cloudburst_words[lemma]
    else:
      env.cloudburst_words[lemma] = [word 
          for word in env.cloudburst_words[lemma] 
          if word['docname'] != docname]
  env.cloudburst_all_lemmas = {lemma: features 
      for (lemma, features) in env.cloudburst_all_lemmas.iteritems() 
      if features['docname'] != docname}
  
def process_word_nodes(app, doctree, fromdocname):
  resolve_headwords(app)
  print app.builder.env.cloudburst_all_lemmas
  for node in doctree.traverse(wordlist):
    process_wordlist(app, doctree, fromdocname, node)

def resolve_headwords(app):
  env = app.builder.env
  for (lemma, entry) in env.cloudburst_all_lemmas.iteritems():
    if entry.has_key('headword') and entry.has_key('rel'):
      headwordlemma = entry['headword']
      headwordentry = env.cloudburst_all_lemmas[headwordlemma]
      rel = entry['rel']
      if not hasattr(headwordentry, 'subentries'):
        headwordentry['subentries'] = []
      headwordentry['subentries'].append((rel, lemma))

def process_wordlist(app, doctree, fromdocname, node):
  env = app.builder.env
  content = []
  head = nodes.title()
  head.append(nodes.Text("Lexicon", "Lexicon"))
  content.append(head)
  # In case there are no lemmas specified in our environment TODO: maybe this should go in an init funciton instead?
  if not hasattr(env, 'cloudburst_all_lemmas'):
    env.cloudburst_all_lemmas = {}
  # TODO: This seems wrong: doesn't generate an anchor properly, for instance.
  for lemma in sorted(env.cloudburst_words.keys(), key=lambda l: unidecode(l)+l):
    content.append(make_wordlist_entry(app, doctree, fromdocname, lemma))
  node.replace_self(content)

def make_wordlist_entry(app, doctree, fromdocname, lemma, subentry = False):
  env = app.builder.env
  wordtokens = env.cloudburst_words[lemma]
  para = nodes.paragraph()
  para += nodes.Text(lemma, lemma)
  para += nodes.target('', '', ids=[('lexicon-%s' % punycode.punycode_encode(lemma))])
  if env.cloudburst_all_lemmas.has_key(lemma):
    entry = env.cloudburst_all_lemmas[lemma]
    if entry.has_key('headword') and not subentry:
      return nodes.paragraph()
    if entry.has_key('definition'):
      para += nodes.Text(_(' ' + entry['definition'] + ' '), _(' ' + entry['definition'] + ' '))
    for node in make_wordlist_references(app, doctree, fromdocname, lemma, wordtokens):
      para += node
    if entry.has_key('subentries'):
      for (rel, subentrylemma) in entry['subentries']:
        para += nodes.Text(_(rel + ': '))
        para += make_wordlist_entry(app, doctree, fromdocname, subentrylemma, subentry = True)
  return para

def make_wordlist_references(app, doctree, fromdocname, lemma, wordtokens):
  env = app.builder.env
  nodelist = [nodes.Text(" (", " (")]
  first = True
  for wordtoken in wordtokens:
    if first:
      first = False
    else:
      nodelist.append(nodes.Text(", ", ", "))
    filename = env.doc2path(wordtoken['docname'], base=None)
    lineno = wordtoken['lineno']
    newnode = nodes.reference('', '')
    innernode = nodes.emphasis(_(str(lineno)), _(str(lineno)))
    newnode['refdocname'] = wordtoken['docname']
    newnode['refuri'] = app.builder.get_relative_uri(fromdocname, wordtoken['docname']) + '#' + str(wordtoken['targetnode']['ids'][0])
    newnode.append(innernode)
    nodelist.append(newnode)
  nodelist.append(nodes.Text('.)', '.)'))
  return nodelist
