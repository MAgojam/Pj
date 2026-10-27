# Run in the Pj/Pjp editor, or load as a service script with Service... and Run.
import math
import statistics

summary = []
for variable, values in data.items():
    clean = [value for value in values
             if isinstance(value, (int, float))
             and not isinstance(value, bool) and math.isfinite(value)]
    if clean:
        summary.append({
            "Variable": variable,
            "N": len(clean),
            "Mean": statistics.mean(clean),
            "SD": statistics.stdev(clean) if len(clean) > 1 else None
        })

if summary:
    mzpjShowTable(summary, name="numeric_summary", title="Numeric summary",
                  notes="Only finite numeric values were included.")
else:
    mzpjShowText("No finite numeric values are available.", name="no_numeric_data")
