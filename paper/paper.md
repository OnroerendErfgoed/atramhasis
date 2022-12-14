---
title: 'Atramhasis: A webbased SKOS editor'
tags:
  - Python
  - SKOS
  - thesaurus
  - vocabulary
  - linked data
authors:
  - name: Van Daele, Koen
    orcid: 0000-0002-8153-2978
    corresponding: True
    affiliation: 1
  - name: Geuens, Jonas
    orcid: 0000-0001-8197-5034
    affiliation: 1
  - name: Vanderhaegen, Cedrik
    affiliation: 1
  - name: Goessens, Bram
    affiliation: 1
affiliations:
 - name: Flanders Heritage Agency, Belgium
   index: 1
date: 22 december 2022
bibliography: paper.bib
---

# Summary

Atramhasis is an online SKOS [@skos:2008] editor that allows users 
to create, maintain and consult controlled vocabularies and thesauri according 
to the SKOS standard. These SKOS vocabularies consist of concepts, collections
and their relations. A concept being something a researcher wants to describe and define.
Flanders Heritage is active in the domain of cultural heritage and 
describes concepts such as [Roman period](https://id.erfgoed.net/thesauri/dateringen/1223),
[oppida](https://id.erfgoed.net/thesauri/erfgoedtypes/1052) or 
[archaeological excavations](https://id.erfgoed.net/thesauri/gebeurtenistypes/38).
Similar concepts and collections are grouped in a conceptscheme, eg. the 
conceptscheme of [heritage types](https://id.erfgoed.net/thesauri/erfgoedtypes)
consists of concepts that describes types of heritage, ranging from 
[solitary trees](https://id.erfgoed.net/thesauri/erfgoedtypes/1654) 
over [burial mounds](https://id.erfgoed.net/thesauri/erfgoedtypes/170)
 to [airfields](https://id.erfgoed.net/thesauri/erfgoedtypes/476) 
and [swimming pools](https://id.erfgoed.net/thesauri/erfgoedtypes/949). Concepts 
and collections can be labelled with preferred labels and alternative labels, 
more elaborately described with definitions and notes, and provided with references 
to source material. The concepts can be related, in general or in a hierarchical way 
(broader/narrower), to other concepts and collections in the same vocabulary or 
to concepts in other vocabularies such as the Art and Architecture Thesaurus (AAT) [@aat].

![Airfields described as a SKOS concept.\label{fig:airfields}](atramhasis_screen_airfields.png)

# Statement of need

Atramhasis was written to be a lightweight open source SKOS editor. First and foremost,
we wanted a system that adheres to the SKOS standard, yet is useable for users without
knowledge of SKOS or RDF. For a typical user, it had to feel as if they were consulting 
a normal website, as opposed to a RDF vocabulary since the latter can feel rather daunting 
to non-technical users. This not only applies to users consulting the thesauri, but also 
to those editing them. The editors do not write RDF statements, but edit data in a normal 
web admin interface \autoref{fig:editingairfields}. All mapping to RDF and SKOS is done behind
the scene, invisible to the editors.

![Editing the concept of airfields is simple and straightforward.\label{fig:editingairfields}](atramhasis_screen_edit_airfields.png)

The system was conceived as Flanders Heritage's [central platform](https://thesaurus.onroerenderfgoed.be) 
for publication of internal and regional vocabularies dealing with cultural heritage [@Mortier:2017]. 
The publication website allows humans to browse, search and consult the vocabularies 
online in a user-friendly way. Search results can be downloaded in CSV format for further processing.
Internal and external systems use the webservices provided by Atramhasis 
to consult or download vocabularies. Concept uris are used in indexing data 
in systems such as the [Inventory of Immovable Cultural Heritage](https://inventaris.onroerenderfgoed.be).
This allows users to search those external systems using the provided thesauri \autoref{fig:searchingairfields}.
For a typical end-user the thesauri are presented as dropdown lists or specialised 
widgets that allow navigating the thesaurus from the top concepts along branches to 
the leafs. For most internal operations with the thesaurus, JSON REST services are used because 
they are convenient for web developers to design and develop enterprise IT-systems.
For external uses, publishing of linked data is supported. Individual concepts and
collections can be downloaded as RDF data in Turtle, RDF/XML and JSON/LD format. Entire
conceptschemes can be downloaded in Turtle or RDF/XML format. Finally, an integration with a
Linked Data Fragments server is available that allows quering the server with SPARQL queries
through the Triple Pattern Fragments protocol [@Verborgh:2016].

![Searching for airfields in the Inventory of Immovable Cultural Heritage\label{fig:searchingairfields}](inventaris_screen_search_airfields.png)

An Atramhasis instance can also be connected to external vocabularies and thesauri through 
an interface called a Skosprovider [@skosprovider:2022]. Any thesaurus providing one can 
be used for linking external concepts. Out of the box skosproviders are available for Getty 
vocabularies such as the AAT [@aat] or other Atramhasis instances, but any thesaurus adhering 
to the SKOS standard can be added with a little development work. Connecting an external 
thesaurus opens up the possiblity of interlinking internal and external thesauri, importing 
concepts from such a thesaurus and turning your vocabularies into true linked data. 

# Acknowledgements

As with any long lived project, Atramhasis has benefitted from the input of several colleagues and software developers over the years. While it's impossible to thank them, we do want to thank Bart Saelen, Tinne Cahy and Cedrik Vanderhaegen for much of the original development. A full list of people who contributed over the years can be found on Github. Leen Meganck and Sophie Mortier were responsible for building most of the vocabularies that led to creating the software. Their needs and requirements drove the features of Atramhasis.

# References
