PYTHON  := python3
APP     := main.py
NAME    := py-geogebra
DISTDIR := dist

.PHONY: build clean run

build:
	$(PYTHON) -m PyInstaller \
	--onefile --noconsole --noconfirm \
	--hidden-import struct --hidden-import _struct --add-data "locales:locales" --name py-geogebra --add-data "resources:resources" --hidden-import=requests --hidden-import=dotenv --hidden-import=libsql_client --hidden-import=requests --hidden-import=flask --hidden-import=threading --add-data ".env:." --add-data "py_geogebra/flask/templates:py_geogebra/flask/templates" \
	--hidden-import=libsql --hidden-import=websockets --collect-all libsql main.py \


clean:
	rm -rf build $(DISTDIR) *.spec

run: build
	./$(DISTDIR)/$(NAME)
