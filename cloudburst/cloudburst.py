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

    BASIC INNARDS
   
   Get a consistent approach to building content. 
   Set up the wordlist-generating functions properly, with a class and properties
   instead of just passing a bunch of references around.

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
    app.add_config_value('cloudburst_indexer', defaultdict(str), 'env')
    app.add_config_value('cloudburst_displayer', defaultdict(str), 'env')
    app.add_node(wordlist)
    app.add_node(word,
            html=(visit_word_node, depart_word_node),
            text=(visit_word_node, depart_word_node),
            latex=(visit_word_node, depart_word_node))
    app.add_role('word', word_role)
    app.add_directive('index', IndexDirective)
    app.add_directive('entry', EntryDirective)
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
    env = inliner.document.settings.env
    app = env.app
    displayer = env.config.cloudburst_displayer
    indexer = env.config.cloudburst_indexer or displayer
    if text[0] == '*':
        return nodes.strong(_(text), _(text)), [] #WHY IS THIS NOT WORKING?
    if not hasattr(env, 'cloudburst_tokens_by_heading'):
        env.cloudburst_tokens_by_heading = defaultdict(list)
    out = []
    text = text.split()
    words_to_display = " ".join(displayer[word] for word in text).split()
    words_to_index = " ".join(indexer[word].lower() for word in text).split()
    for display_as, index_as in zip(words_to_display, words_to_index):
        targetid = "word-%d" % env.new_serialno('word')
        targetnode = nodes.target('', '', ids=[targetid])
        wordnode = make_link_to_index(display_as, index_as, app, options)
        env.cloudburst_tokens_by_heading[index_as].append({
            'docname': env.docname,
            'lineno': lineno,
            'wordnode': wordnode.deepcopy(),
            'targetnode': targetnode,
        })
        out.append(targetnode)
        out.append(wordnode)
        out.append(nodes.Text(' ', ' '))
    out.pop()  # Remove final space; Sphinx will handle spacing between this
               # node and the next one (incl punctuation) if we just get out of the way.
    return out, []

def make_link_to_index(text, lemma, app, options):
    return nodes.reference('', text, refid='lexicon-%s' % punycode.punycode_encode(lemma), **options)

class IndexDirective(Directive):
    def run(self):
        return [wordlist('')]

class EntryDirective(Directive):
    has_content = True

    option_spec = {
        'headword': lambda x: x,
        'rel': lambda x: x
    }

    def run(self):
        env = self.state.document.settings.env

        if not hasattr(env, 'cloudburst_entries_by_heading'):
            env.cloudburst_entries_by_heading = {}

        indexword = self.content[0]
        env.cloudburst_entries_by_heading[indexword] = { k: v for (k, v) in self.options.items() }
        env.cloudburst_entries_by_heading[indexword]['docname'] = env.docname,
        env.cloudburst_entries_by_heading[indexword]['definition'] = ' '.join(self.content[2:])
        return []

def purge_words(app, env, docname):
    if hasattr(env, 'cloudburst_tokens_by_heading'):
        lbh = env.cloudburst_tokens_by_heading.items()
    else:
        lbh = []
    for (heading, tokens) in lbh:
        if tokens == []:
            del env.cloudburst_tokens_by_heading[heading]
        else:
            env.cloudburst_tokens_by_heading[heading] = [token
                    for token in tokens
                    if token['docname'] != docname]
    if hasattr(env, 'cloudburst_entries_by_heading'):
        ebh = env.cloudburst_entries_by_heading.items()
    else:
        ebh = []
    for (heading, entry) in ebh:
        if entry['docname'] == docname:
            del env.cloudburst_entries_by_heading[heading]
  
def process_word_nodes(app, doctree, fromdocname):
    # In case there are no lemmas specified in our environment TODO: maybe this should go in an init funciton instead?
    env = app.builder.env
    if not hasattr(env, 'cloudburst_entries_by_heading'):
        env.cloudburst_entries_by_heading = {}
    resolve_lexical_entries(app)
    for node in doctree.traverse(wordlist):
        process_wordlist(app, doctree, fromdocname, node)

def resolve_lexical_entries(app):
    env = app.builder.env
    for (lemma, entry) in env.cloudburst_entries_by_heading .items():
        if 'headword' in entry and 'rel' in entry:
            headwordlemma = entry['headword']
            headwordentry = env.cloudburst_entries_by_heading [headwordlemma]
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
    # TODO: This seems wrong: doesn't generate an anchor properly, for instance.
    for lemma in sorted(env.cloudburst_tokens_by_heading.keys(), key=lambda l: unidecode(l)+l):
        content.append(make_wordlist_entry(app, doctree, fromdocname, lemma))
    node.replace_self(content)

def make_wordlist_entry(app, doctree, fromdocname, lemma, subentry = False):
    env = app.builder.env
    displayer = env.config.cloudburst_displayer
    indexer = env.config.cloudburst_indexer or displayer
    wordtokens = env.cloudburst_tokens_by_heading[lemma]
    para = nodes.paragraph()
    para += nodes.Text(lemma, lemma)
    para += nodes.target('', '', ids=[('lexicon-%s' % punycode.punycode_encode(lemma))])
    if lemma in env.cloudburst_entries_by_heading :
        entry = env.cloudburst_entries_by_heading [lemma]
        if 'headword' in entry and not subentry:
            return nodes.paragraph()
        if 'definition' in entry:
            para += nodes.Text(_(' ' + entry['definition'] + ' '), _(' ' + entry['definition'] + ' '))
        if 'subentries' in entry:
            for (rel, subentrylemma) in entry['subentries']:
                para += nodes.Text(_(rel + ': '))
                para += make_wordlist_entry(app, doctree, fromdocname, subentrylemma, subentry = True)
    for node in make_wordlist_references(app, doctree, fromdocname, lemma, wordtokens):
        para += node
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
