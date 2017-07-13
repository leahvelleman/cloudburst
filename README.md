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

* Auto-generate representations from document markup: write 
  ` ``spelling("θέλει να") >> pronunciation`` ` in your reStructuredText 
  source to get `θέλει να /'θelina/` in your HTML or PDF output.
* Auto-check representations from document markup: write
  ` ``spelling("θέλει να") & pronunciation(/'θelina/)`` ` in your reST
  source to get the same output but also trigger an error message if the
  pronunciation you typed is not the one your model generates.
* Present representations with supplemental information: click on
  the word `θέλει` in your browser and get a dictionary entry, found
  under the headword `θέλω`.
