# Pj 1.5.0 — cancellable Python execution

This release improves Python process management while preserving public service
API version 1. Package and platform validation are recorded in the release.

## Why replace `system2()` with `processx`?

The goal is more reliable control of Python execution, especially when another
jamovi module calls Pj as a background service. This service was introduced in
Pj 1.3.0 and was already available in 1.4.0; 1.5.0 strengthens its execution
management while preserving public API version 1. The previous blocking invocation
made it difficult to monitor a running calculation and respond promptly when
the calling analysis requested a restart. A process handle allows Pj to poll
execution, drain diagnostic output and invoke the caller's checkpoint while
Python is still running.

This change supports timely cancellation, explicit exit-status handling and
cleanup of child processes after completion, errors or interruption. It also
provides one elapsed-time budget for the service call, covering both bundled
library preparation and the user's calculation. On Linux, System Python still
runs on the host through Flatpak's supported host-launch mechanism; additional
host lifecycle handling extends these controls across the sandbox boundary.

These are lifecycle and integration improvements, not a claim that `processx`
makes statistical calculations faster. Earlier comparisons also involved
different preparation and graphical workloads, so they do not establish a
general speed advantage over `system2()`. Python calculations and the existing
public service API remain the responsibility of the same Pj interfaces.

## Changes

Python execution now uses `processx` for both editors and the public service,
including bundled-library preparation. A new optional service `checkpoint`
callback lets the calling jamovi analysis request a restart while Python runs.
Restart conditions propagate unchanged. Process trees are cleaned up on failure,
cancellation, timeout and normal return; UTF-8 diagnostics and large stderr
streams are handled without blocking the child process.

`mzPjRunPython(timeout=60L)` now shares one execution budget across library
preparation and the main Python process. Bootstrap timeouts retain
`kind='timeout'`; no later phase starts after the budget has expired.
The editors retain their existing unlimited execution policy.

The Run keyboard hint now occupies a compact footer below the editor, keeping
it visible when a native horizontal scrollbar is present.

System Python on the Linux Flatpak host uses `processx` with
`flatpak-spawn --host --watch-bus` and script input through an open file
descriptor. A standard-library host guard completes descendant cleanup and
acknowledges it to Pj, including when the launcher is terminated. This route
supports the same optional checkpoint and elapsed-time budget. It does not
require installing another Python package or exposing sandbox temp paths.

Public service API version 1 and its result/Output contract remain compatible.
`mzPjServiceInfo()` adds capability metadata. Individual responses identify
their runner and whether a checkpoint was enabled. Existing callers need no
new argument; callers wanting cancellation supply their own analysis checkpoint
and rethrow jamovi's restart condition. See the
[service API guide](mzPj_service_api.md) and complete developer example.

`processx` is declared in Imports and is supplied by supported jamovi runtimes.
No new Python library or statistical method is introduced by this update.
Earlier function handbooks still describe the Python helper interfaces.
