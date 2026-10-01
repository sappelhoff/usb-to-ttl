usb-to-ttl
==========

This website contains supplementary material to the article **"In COM we trust: Feasibility of USB-based event marking"**, by Stefan Appelhoff |ORCID_appelhoff| and Tristan Stenner |ORCID_stenner|.

The article is available with open access from Behavior Research Methods: `doi:10.3758/s13428-021-01571-z <https://doi.org/10.3758/s13428-021-01571-z>`_

Please feel free to open a `new GitHub issue`_ for any questions, suggestions, or comments you might have.

The source for this website is persistently stored on Zenodo (`doi:10.5281/zenodo.3838692 <https://doi.org/10.5281/zenodo.3838692>`_) and can be used to build the website locally (see ``README.md`` file at the root of the archive).

.. |ORCID_appelhoff| image:: _static/orcid_16x16.png
                     :target: https://orcid.org/0000-0001-8002-0877
                     :alt: (ORCID ID Stefan Appelhoff)

.. |ORCID_stenner| image:: _static/orcid_16x16.png
                   :target: https://orcid.org/0000-0002-2428-9051
                   :alt: (ORCID ID Tristan Stenner)

Brief Overview
--------------

A multitude of scientific disciplines employs experimental research involving the presentation of stimuli to research subjects.
Be it displaying a stimulus to a human, applying an electric shock to a rodent, or switching off the lights in a room where an autonomous robot is trying to navigate.
Researchers need to record these events together with other data to make sense of the results.

Traditionally, the `parallel port`_ was the interface of choice for event marking, and a lot of hardware for science experiments depends on this interface.
Yet, the parallel port has been replaced by the universal serial bus (`USB`_) protocol, which means that it is becoming more and more difficult to obtain modern computer hardware that supports a parallel port "out of the box".

Replacements of the parallel port interface are needed to make sure that all the benefits that the parallel port supplied in the past (speed, simplicity, robustness) will be available in the future.

One such replacement is relay output data via USB to a dedicated microcontroller unit (e.g., an `Arduino`_ or a `Teensy`_), which then converts the incoming data into a parallel signal, and sends it on to its destination.

In our article, **"In COM We Trust: Feasibility of USB-Based Event Marking"**, we show the feasibility of such an approach through a direct comparison of USB based event marking with the parallel port.
On this website we showcase supplementary material.

Supplementary Material
----------------------

:ref:`data-and-scripts`
^^^^^^^^^^^^^^^^^^^^^^^

The data used in the article **"In COM we trust: Feasibility of USB-based event marking"** as well as the analysis scripts are supplied.
Additionally, we provide code to reproduce the figures used in the article.

:ref:`diy-instructions`
^^^^^^^^^^^^^^^^^^^^^^^

In this section we supply a shopping list, build instructions, and example firmware to build a simple hardware to mark events from USB to TTL.

:ref:`code-examples`
^^^^^^^^^^^^^^^^^^^^

In this section we provide examples on *how* to mark events from USB to TTL using popular programming languages (e.g., `Python`_).

:ref:`commercial-alternatives`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For convenience we provide a (non-complete) list of commercial alternatives for event marking via USB.

Related articles throughout the Internet
----------------------------------------

Here we list some interesting non-academic sources and further or related readings in no particular order:

- https://medium.com/@tltx/the-void-left-by-the-parallel-port-51eb6c919e8a
- http://psy.swan.ac.uk/staff/freegard/audio%20switch%20report.pdf
- https://dubioussentiments.wordpress.com/2015/05/05/replacing-parallel-port-signaling-with-usb/
- https://computer.howstuffworks.com/parallel-port1.htm
- https://computingforpsychologists.wordpress.com/2011/05/16/ttl-technology-getting-things-talking-to-each-other/
- https://computingforpsychologists.wordpress.com/2012/04/15/how-to-make-your-own-parallel-port-response-boxes/

Acknowledgements
----------------

This project was supported by the `Fellow-Programm Freies Wissen`_ of `Wikimedia Germany`_, the `Stifterverband`_, and the `VolkswagenStiftung`_.

.. _new GitHub issue: https://github.com/sappelhoff/usb-to-ttl/issues/new
.. _parallel port: https://en.wikipedia.org/wiki/Parallel_port
.. _USB: https://en.wikipedia.org/wiki/USB
.. _Arduino: https://www.arduino.cc/
.. _Teensy: https://www.pjrc.com/teensy/
.. _Python: https://www.python.org
.. _Fellow-Programm Freies Wissen: https://de.wikiversity.org/wiki/Wikiversity:Fellow-Programm_Freies_Wissen
.. _Wikimedia Germany: https://www.wikimedia.de/
.. _Stifterverband: https://www.stifterverband.org/
.. _VolkswagenStiftung: https://www.volkswagenstiftung.de/
