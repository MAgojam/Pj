# Run in the Pj/Pjp editor, or load as a service script with Browse... and Run.
png_path = mzpjResourcePath('mzPj_icon_python.png')
with open(png_path, "rb") as image_file:
    mzpjShowImage(image_file, name="pj_icon", title="Pj module icon")
