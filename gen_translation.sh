xgettext --language=Python --keyword=_ --output=messages.pot py_geogebra/*.py
msgmerge --update locales/sk/LC_MESSAGES/messages.po messages.pot
msgmerge --update locales/en/LC_MESSAGES/messages.po messages.pot
