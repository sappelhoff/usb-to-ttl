[![Ask Me Anything!](https://img.shields.io/badge/Ask%20me-anything-1abc9c.svg)](https://github.com/sappelhoff/usb-to-ttl/issues/new)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3838692.svg)](https://doi.org/10.5281/zenodo.3838692)
[![Behavior Reseach Methods](https://img.shields.io/badge/Behavior%20Research%20Methods-published-11111.svg)](https://doi.org/10.3758/s13428-021-01571-z)

# USB-to-TTL

This repository contains the source code for the `usb-to-ttl` documentation
page. Please see the [documentation](https://stefanappelhoff.com/usb-to-ttl/).

Or ask a question on the [issues page](https://github.com/sappelhoff/usb-to-ttl/issues/new).

Published with the help of:

 - [Sphinx](https://www.sphinx-doc.org/en/master/)
 - [sphinx-bootstrap-theme](https://github.com/ryan-roemer/sphinx-bootstrap-theme)
 - [CircleCI](https://circleci.com/blog/deploying-documentation-to-github-pages-with-continuous-integration/) (link to build guide)
 - [GitHub Pages](https://pages.github.com/)

# License

[![licensebuttonsby](https://licensebuttons.net/l/by/3.0/88x31.png)](https://creativecommons.org/licenses/by/4.0)

Unless otherwise noted, all contents of this repository that were created by
[Stefan Appelhoff](https://stefanappelhoff.com) and
[Tristan Stenner](https://orcid.org/0000-0002-2428-9051)
are released under the
[CC BY 4.0 license](https://creativecommons.org/licenses/by/4.0).

# Build instructions

To build the documentation page yourself, you need to have
[Python](https://www.python.org/) version 3.4 or higher installed, which
includes the `pip` tool.

1. Navigate to the root of the `usb-to-ttl` directory.
1. From the command line, call `pip install -r requirements` to install
   dependencies.
1. Now navigate to the `docs` directory and call `make html` to build the html
   files.
1. Finally, go to `docs/_build` and open `index.html` to view the documentation

# Build status

Is it green?

[![CircleCI](https://circleci.com/gh/sappelhoff/usb-to-ttl.svg?style=shield)](https://circleci.com/gh/sappelhoff/usb-to-ttl)
