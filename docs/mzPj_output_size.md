# Output size protection (Pj 1.4.0)

Available in Pj 1.4.0 or newer.

jamovi's engine transport has a 4 MiB message limit in the source reviewed for
this update. This applies to the complete analysis response, not each plot.
Several individually small results can exceed it together.

Pj uses a conservative 3 MiB budget for the aggregate Python result payload and
its native result representation. Tables can grow when converted to native
results. A final 3.5 MiB check on the serialized Pj/Pjp analysis response also
accounts for options, editor code and state. These margins are intentional;
they are not configurable from scripts.

When the result budget is exceeded, Pj/Pjp replace the computed output with an
English information panel explaining the size and suggesting remedies. The
oversized result is not truncated silently. Reduce displayed rows, figures or
console text, or load large JavaScript libraries as module resources instead
of embedding them repeatedly. Python comments normally do not become results;
they contribute when code is echoed, and script/editor state can also contribute
to the complete response. Keep useful comments and required license notices.

The final response check uses jmvcore's compact error-analysis fallback if the
whole message is still too large. This is a last barrier, including exceptional
states; the normal result-budget failure uses the information panel.

After a rejection, edit the script and run again. This is a transport guard,
not a memory quota or a sandbox: Python still constructs its output before the
checks run. Saving, image rendering and exports have their own limitations.

## Service API

`mzPjServiceInfo()$result_budget_bytes` exposes the result budget. Oversized
`mzPjRunPython()` responses raise `mzPjServiceError` with `kind = 'result_size'`,
`bytes`, `stage`, `details` and module-generated `help_html`. No partial result
list is returned. The preflight includes conversion to native results in a
temporary group, without changing the caller's dataset or results.

Calling modules must handle this condition and still check their complete
response: Pj cannot measure unrelated results or options added by another
module. Do not concatenate raw user input into diagnostic HTML.

## Manual check

Load `pjscript/60_output_size_limit.py` with the protection preview installed.
No dataset is required; either Python can be selected. With
`EXCEED_LIMIT = True`, two HTML objects exceed 4 MiB together. Expect a compact
size-information panel and a responsive application. Change the flag to `False`
and run again: a normal recovery table and text should appear.
