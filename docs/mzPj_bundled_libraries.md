# Python libraries supplied by Pj

> **Pj 1.6.1 / jamovi 28.18 (18 November 2026).** The minimum is now
> jamovi 28.18.0, inclusive. The official runtime includes the native SVG
> document-save fix. Earlier advisories below describe the affected 28.17
> baseline. The separate Office aspect-ratio and Rj resize limitations remain;
> see the [1.6.1 release notes](mzPj_release_1_6_1.md).


## Current library manual

Read the [English manual](mzPj_libraries_manual.md) or
[Italian manual](mzPj_libraries_manual_it.md), also available in DOCX/PDF under
`docs/manuals`. They cover all eleven pure-Python libraries and the26 native
statistical APIs with worked examples. Pj1.6.0 declares minApp jamovi28.17.0.

Native pj_stats_rust1.1.0 adds repeated-measures models, documented in the
[RM guide](mzPj_repeated_measures.md). Windows x64 and Linux x64 are built/tested;
macOS Intel/Apple Silicon are configured in GitHub Actions and await their jobs.
The native package selects a platform/architecture subdirectory. It is separate
from the source-only Python archive; no binary is relabelled for another OS.

Pj 1.4.0 additionally bundles Plotly 7.1.0, Narwhals 2.26.0 and
Packaging 26.3. See the [Plotly guide](mzPj_plotly.md) for activation, dependency
source handling and the `mzpjShowPlotly()` result helper. Earlier 1.3.x JMO
files contain the original eight-library bundle.

Version 1.2.0 supplies eight source-only libraries with the module. No pip,
network access or changes to jamovi's Python installation are required when
running a script. Both jamovi Python and System Python can use these copies.
The bundled-library feature requires Python 3.10 or newer; a previous System
Python can still run other Pj code but cannot activate this bundle.

## Activate a library

```python
sp = mzpjUseLibrary('sympy')
x = sp.Symbol('x')
print(sp.integrate(x**2, (x, 0, 1)))
```

The helper returns the imported module. Activation also supports normal imports:

```python
mzpjUseLibrary('sympy')
from sympy import Symbol, diff
```

Use import names (`more_itertools`) or distribution names (`more-itertools`).
Names are case-insensitive. Activating SymPy also activates mpmath; activating
Jinja2 also activates MarkupSafe. Other libraries are not activated implicitly.
Call the helper in the service script or editor before importing that library.
Pj executes the service script first, then editor code in the same namespace.

## Included versions

| Import name | Version | Required bundled dependency |
|---|---|---|
| sympy | 1.14.0 | mpmath |
| mpmath | 1.3.0 | None |
| jinja2 | 3.1.6 | markupsafe |
| markupsafe | 3.0.3 | None |
| tabulate | 0.10.0 | None |
| uncertainties | 3.2.3 | None |
| simpy | 4.1.1 | None |
| more_itertools | 10.8.0 | None |
| plotly | 7.1.0 | narwhals, packaging |
| narwhals | 2.26.0 | None |
| packaging | 26.3 | None |

These are pinned, tested versions, not a promise to track every upstream release.
Optional features can require additional libraries or external programs. In
particular, uncertainty array operations can use NumPy; SymPy's plotting and
code-generation features may need additional dependencies. Supplying SymPy
does not supply matplotlib, pandas, a compiler or a LaTeX installation.

## Inspect availability

```python
mzpjShowTable(mzpjListLibraries(), name='libraries', title='Pj libraries')
```

Each record contains `Library`, `Version`, `Dependencies`, `Available` and
`Active`. Version describes the supplied copy. `Available` reports whether
the private cache was prepared; `Active` means the supplied module has been
imported in this execution. Listing does not import the eleven libraries.
The Show Python info report also displays a separate bundled-library section.

## Choose an independently installed version

```python
sp = mzpjUseLibrary('sympy', source='system')
```

`source='bundled'` is the default. `source='system'` means the selected
interpreter's ordinary import environment, including when jamovi Python is
selected; it does not switch interpreters. The package must already be installed.
Use normal `import` statements when no explicit Pj source selection is needed.

Pj does not silently replace an already imported module with another version.
Conflicting source selections produce an error explaining that source selection
must precede imports. Edit the order and Run again: each execution starts a new
Python process. This also applies to dependencies shared by two libraries.
Pj does not add its whole cache to sys.path: its import finder handles only
libraries explicitly activated through the helper and their required dependencies.

## Cache, operating systems and performance

The approximately 13.6 MB archive and JSON catalog live in `inst/extdata` and are
included in the JMO. On first use Pj verifies the archive's SHA-256 and extracts
it to a private user cache. The cache is identified by archive digest and Python
major/minor version. Later runs probe the cache without transferring the archive
again. Imports occur only when requested; library startup costs still apply.

Typical cache roots:

- Windows: `%LOCALAPPDATA%/mzPj/python`.
- Linux: `${XDG_CACHE_HOME:-~/.cache}/mzPj/python`.
- macOS: `${XDG_CACHE_HOME:-~/.cache}/mzPj/python` with the current implementation.

Under Flatpak, the host System Python prepares its own host-visible cache using
the existing host-execution bridge. It never tries to import directly from a
sandbox-only `/app` path. The Flatpak host permission is still required; see
[Linux setup](mzPj_linux_system_python.md). The cache mechanism cannot grant it.
The first library preparation can take longer; subsequent runs reuse the cache.
An unavailable cache does not deliberately prevent unrelated Python code from
running; activating a bundled library reports the preparation error.

The archive rejects traversal entries, symbolic links and native extensions;
its compressed and expanded contents are checked before use. The cache is
ordinary code writable by its owner, not a security sandbox for user scripts.
If a cache is damaged, close the running analysis and remove only the affected
digest/version directory, then Run again. Pj does not modify other Python packages.

Windows and Ubuntu WSL are the validation targets. macOS-compatible source
packaging does not constitute a tested macOS release.

## Examples and interpretation

Standalone files in `pjscript` are repository examples, excluded from JMO builds:

- 43: catalog, symbolic and high-precision calculations, console tables.
- 44: Jinja2 HTML report and MarkupSafe escaping.
- 45: uncertainty propagation, including reuse of correlated quantities.
- 46: SimPy waiting-time comparison with a D3 result.
- 47: overlapping windows, batching and distinct permutations.
- 48: all-eight diagnostic checks with bundled-source verification and PASSED/FAILED results.
- 49: symbolic Bernoulli-model standard errors, numerical probabilities and a teaching report.
- 50: Pj paired changes, bootstrap uncertainty and an omnibus permutation comparison.
- 51: Pjp prediction scenarios, covariance-aware intervals, leave-one-out validation and two optional dataset columns.

All seven require no dataset and can be loaded in either editor with either
Python interpreter. Examples 50–51 instead share the Learning Lab dataset and
target Pj and Pjp respectively; their code is also embedded in the fifth Data
Library document. See the [example guide](mzPj_examples.md#learning-lab-two-analyses-on-one-dataset).
Example 45 reports measurement standard uncertainties,
not confidence intervals; first-order propagation can be unsuitable for strong
nonlinearity or large uncertainty. Example 46 is one reproducible simulation
per staffing scenario, not an inferential comparison. Overlapping windows in
example 47 are not independent observations. MarkupSafe escapes text; it is not
a general-purpose sanitizer of arbitrary HTML.
Example 49 uses an exact model standard error, a continuous normal approximation
for a probability, and a first-order delta-method transformed standard error.
It does not run a test on the open dataset.

## Provenance and licenses

`inst/extdata/mzPj_python_libraries.json` records distribution versions, original
wheel filenames and SHA-256 checksums for the original eight packages,
installed-distribution provenance for the Plotly additions, dependencies, license paths and the
resulting archive checksum. Unmodified upstream Python sources and license
notices are preserved inside the archive. Upstream tests, installation records
and command-line entry points are omitted. MarkupSafe's native accelerator is
omitted; its upstream pure-Python fallback is used. No native binary is shipped in that pure-Python archive; native Rust binaries are separate.
Third-party comments are preserved as upstream source, not translated.

Upstream projects: [SymPy](https://www.sympy.org/), [mpmath](https://mpmath.org/),
[Jinja2](https://jinja.palletsprojects.com/), [MarkupSafe](https://markupsafe.palletsprojects.com/),
[tabulate](https://github.com/astanin/python-tabulate),
[uncertainties](https://uncertainties.readthedocs.io/),
[SimPy](https://simpy.readthedocs.io/),
[more-itertools](https://more-itertools.readthedocs.io/).
