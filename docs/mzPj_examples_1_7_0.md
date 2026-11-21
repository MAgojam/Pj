# Pj 1.7.0 example verification

Verified on 21 November 2026 against the current Python runner and bundled resources.
77 public Python scripts were executed in separate processes with the declared
Data Library datasets or simulated fixtures. Service examples were supplied with
their prerequisite Service script. Script 68 wrote only to a temporary directory.
The local, excluded development example 52 is not part of this public audit.

System Python: 77 passed. Embedded Python: 73 passed; scripts 06, 11, 24 and 39
reported their expected optional-package requirements in this interpreter. These
scripts remain usable with an appropriately equipped System Python. No package
was installed into jamovi's Python.

Both language editions of the library manual passed their 13 existing guided
recipes, catalog/version coverage and all 26 Rust API references. The three new
chapter 9 code blocks in each language also executed without errors. The interaction
chapter directs readers to the complete executable lesson 79; its own commented
real-data call is a template, not a supplied dataset.

This checks Python execution and result generation, not every browser interaction
or desktop export. Windows and WSL2 visual acceptance of the new graphics was
separately supplied by the maintainer. No new macOS desktop visual acceptance is
claimed. Scripts requiring a Data Library document retain that prerequisite.
