# cloudburst

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
represented at several different *levels* --- written normally as `θέλει να`, 
broken into morphemes as `θέλ-ει να`, translated morpheme-by-morpheme as `want-3sg that`, 
converted into an IPA pronunciation key as `/'θelina/`, and so on.

Finite-state morphology tools can automatically generate some of these levels from each other.
(In Greek, if we know the spelling of a word we can easily generate its pronunciation, 
and with a bit more work we can often generate a breakdown and gloss.) But most linguistic
writing is done in environments where each level must be entered and checked by hand. 
Cloudburst is an experiment in changing that by integrating open-source doc writing tools
(Sphinx, Python's doctools, and LaTeX) with open-source finite-state morphology tools
(Pynini and OpenFST).

