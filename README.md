# cloudburst

Cloudburst is autodoc for linguists and conlangers. 

The goal is to integrate finite-state linguistic resources with 
tools for structured documentation, letting you do things like:

* Autogenerate annotations (glosses, pronunciations, segmentations, 
  etc) for written linguistic examples.
* Check that human-written annotations match the predictions of 
  a finite-state model.
* Link words or morphemes in examples to appropriate resources,
  like lexical entries or concordances.
* Index words or morphemes, so that a lexical entry can link to
  all examples using the word in question.

It's based on a few open-source tools: Sphinx and Python doctools
for processing markup and autogenerating HTML documentation or 
LaTeX source code, and Pynini and OpenFST for writing linguistic 
resources. Long-term goals include integration with more linguistic 
resource backends (foma, HFST, SFST, xfst... William Whittaker's 
Words?)

These are big goals. Right now this project is a small experiment.
I am learning as I go, using a personal conlang as a test project,
and blogging about it [here](www.velleman.org/cloudburst). 

# Background

In linguistic writing you see a lot of examples like this

       θέλει να
       θέλ-ει   να
       want-3sg that
       'wants to'
    
or sentences like this:

    All the basic forms can be combined with the future 
    particle θα /θa/ (historically a contraction of θέλει 
    να /'θelina/, 'wants to'). 
    
These show a single linguistic *form* (in this case a short phrase in Modern Greek) 
represented at several different *levels* --- written normally as "θέλει να," 
broken into morphemes as "θέλ-ει να," translated morpheme-by-morpheme as "want-3sg that," 
or converted into an IPA pronunciation key as /'θelina/.

Usually, these examples are written and checked by hand. This is a bit like hand-entering
and hand-testing example code in software documentation: it's not especially fast, and it's 
easy to introduce errors. 
