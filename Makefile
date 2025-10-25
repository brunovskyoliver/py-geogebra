PYTHON  := python3
APP     := main.py
NAME    := py-geogebra
DISTDIR := dist

.PHONY: build clean run

build:
	$(PYTHON) -m PyInstaller \
		--onefile \
		--noconsole \
		--noconfirm \
		--name "$(NAME)" \
		--add-data "locales:locales" \
		--add-data "resources:resources" \
		--add-data ".env:." \
		--hidden-import=requests \
		--hidden-import=struct \
		--hidden-import=_struct \
		--hidden-import=dotenv \
		--hidden-import=libsql_client \
		$(APP)

clean:
	rm -rf build $(DISTDIR) *.spec

run: build
	./$(DISTDIR)/$(NAME)

