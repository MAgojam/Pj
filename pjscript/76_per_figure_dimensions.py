# Pj/Pjp 1.6.2: individual Image and Svg sizes.
# Embedded or System Python; no dataset or optional package required.
# Uses the Pj 1.6.2 helpers mzpjShowImage(..., width=, height=) and mzpjShowSvg().
with open(mzpjResourcePath('mzPj_icon_python.png'), 'rb') as source:
    png = source.read()

# No local dimensions: follows the global popup defaults.
mzpjShowImage(png, name='global_image', title='Image: global popup dimensions')
# Local dimensions override the global defaults for this result only.
mzpjShowImage(png, name='local_image', title='Image: 400 x 300', width=400, height=300)
# One local dimension preserves the original PNG proportions.
mzpjShowImage(png, name='ratio_image', title='Image: width 320, original ratio', width=320)

svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 200"><rect width="400" height="200" fill="#eef3f9"/><path d="M40 160 L130 90 L220 120 L350 35" fill="none" stroke="#3e6da9" stroke-width="5"/><text x="40" y="190" font-size="16">Illustrative SVG profile</text></svg>'
mzpjShowSvg(svg, name='local_svg', title='Svg: 640 x 320', width=640, height=320)
mzpjShowSvg(svg, name='ratio_svg', title='Svg: width 480, viewBox ratio', width=480)
