# Pj 1.8.0

Requires jamovi 28.18.0 or later. Choose the JMO for Windows x64, Linux x64,
macOS Intel or macOS Apple Silicon.

## Hospital Barber–Johnson helper

`mzpjShowBarberJohnson` provides TOI–ALOS, TOI–BTO, ordered trajectories and
common-scale ward panels. Raw capacity/occupied bed-days/exits or explicitly
selected indicators are supported, with duration defined per observation.
Reference-period turnover is an explicit rate rescaling, not a forecast.
Users can supply multiple reference thresholds or bands; these are not
universal clinical quality or efficiency classifications. No optional Python
package is required. Script 81 and its synthetic CSV accompany bilingual
manuals covering the data dictionary, formulas and interpretation limits.

## Native result corrections

- Preserve Image resize intent across the desktop INIT/save/RUN cycle.
  Resize only the selected raster without executing Python or replacing
  unrelated figures, native tables or external data.
- Preserve original size coefficients to prevent cumulative scaling.
- Send native PNG captures one at a time, acknowledge replacements and discard
  stale work. Capture failures remain visible and allow recovery.
- Remove clipping constraints from native D3 Svg containers.

On some Linux installations the native Svg/Image handle is at the lower left
and may not respond. Use function `width`/`height`, or Settings when those
arguments are omitted. Explicit dimensions take precedence over Settings.

The Python service API remains version 1. Native pj_stats_rust 1.1.0 binaries
are reused unchanged; Rust sources are maintained separately.

Windows and Ubuntu WSL2 desktop checks cover integrated and System Python.
macOS packages undergo native Actions build and backend checks; these do not
constitute macOS desktop visual acceptance.
