# Run in Pj or Pjp with either Python interpreter. No dataset is required.
# Templates can be edited; autoescape protects text values inserted into HTML.
jinja = mzpjUseLibrary('jinja2')
safe = mzpjUseLibrary('markupsafe')
values = [8, 10, 11, 12, 14]
average = sum(values) / len(values)
template = jinja.Environment(autoescape=True).from_string('''
<section style="font:14px/1.6 sans-serif;max-width:720px;color:#25364a">
  <h3 style="color:#3e6da9">{{ title }}</h3>
  <p>{{ explanation }}</p>
  <div style="display:flex;gap:18px;background:#f0f5fa;padding:14px;border-radius:8px">
    <span><strong>N</strong>: {{ n }}</span>
    <span><strong>Mean</strong>: {{ '%.2f'|format(mean) }}</span>
  </div>
  <ul>{% for value in values %}<li>Observation {{ loop.index }}: {{ value }}</li>{% endfor %}</ul>
</section>''')
mzpjShowHtml(template.render(title='A report created with Jinja2',
    explanation='Text such as <b>example</b> is displayed literally, rather than executed as HTML.',
    n=len(values), mean=average, values=values), name='template_report', title='Template-based report')
print('MarkupSafe escaping:', safe.escape('<script>alert("example")</script>'))
# MarkupSafe escapes text; it is not a sanitizer for arbitrary HTML documents.
