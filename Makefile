PYTHON  := python
APP     := main.py
NAME    := py-geogebra
DISTDIR := dist

.PHONY: build clean run

build:
	pipreqs . --force
	$(PYTHON) -m PyInstaller --onefile --noconsole --noconfirm --add-data "locales:locales" $(APP)

clean:
	rm -rf build $(DISTDIR) *.spec

run: build
	./$(DISTDIR)/main

