find py_geogebra -name '*.py' >POTFILES.in
xgettext --language=Python --keyword=_ --files-from=POTFILES.in --output=messages.pot
msgmerge --update locales/sk/LC_MESSAGES/messages.po messages.pot
msgmerge --update locales/en/LC_MESSAGES/messages.po messages.pot
