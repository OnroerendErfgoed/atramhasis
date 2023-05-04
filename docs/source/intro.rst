.. _introduction:

============
Introduction
============

Atramhasis is an online SKOS editor. It allows a user to create and edit an
online thesaurus or vocabulary adhering to the 
`SKOS specification <skos_spec_>`_ through a simple web interface. This allows
any user with access to a web browser to consult the thesauri and if so wanted,
to edit them.

Atramhasis is also intended to be one of the focal points in a 
:term:`Service Oriented Architecture <SOA>`. It exposes as much of its 
functionalities as possible through :term:`REST` services. Both reading from
and writing to concept schemes is possible with Atramhasis.

Atramhasis tries to stick as closely as possible to the :term:`SKOS` 
specification. Where this was not possible, we tried to follow other standards
such as :term:`SKOS-THES`.

Atramhasis is being developed by the `Flanders Heritage Agency`_, an agency of
the Flemish Government that deals with Archaeology, Monuments and Landscapes.
As such, we mainly intend to use it with vocabularies and thesauri that are
related to cultural heritage. We generally construct our own thesauri, specific
to our own applications, but while always keeping an eye on other thesauri
in the larger field of cultural heritage such as the 
`Art and Architecture Thesaurus`_ (AAT).

If you have questions about the project, want to help out, want to report a
bug or just want to have a conversation with us, please get in touch. For 
general conversations, you can use our 
`Google Group <https://groups.google.com/d/forum/atramhasis>`_. If you have 
encountered a bug in Atramhasis or it's documentation, or if you want to ask
us to consider implementing a feature, feel free to use our 
`issue tracker <http://github.com/OnroerendErfgoed/Atramhasis/issues>`_.

If you are using this software in and want to reference it, please 
cite the following article in the Journal of Open Source Software:

Koen Van Daele, Tinne Cahy, Wim De Clercq, Jonas Geuens, Bram Goessens, Jonathan Piraux, Bart Saelen, Maarten Taeymans, & Cedrik Vanderhaegen, 2023: Atramhasis: an online skos vocabulary editor. *Journal of Open Source Software*, 8(83), p. 5040, `doi:10.21105/joss.05040 <https://doi.org/10.21105/joss.05040>`_. 

.. _skos_spec: http://www.w3.org/TR/skos-reference/
.. _Flanders Heritage Agency: https://www.onroerenderfgoed.be
.. _Art and Architecture Thesaurus: http://vocab.getty.edu/aat
