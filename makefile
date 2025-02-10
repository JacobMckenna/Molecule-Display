FLAGS = -Wall -std=c99 -pedantic
CC = clang
PYTHON = python3.12
PYTHON_PATH = /usr/include/$(PYTHON)
PYTHON_LIB = /usr/lib/$(PYTHON)/x86_64-linux-gnu

export LD_LIBRARY_PATH=$(PWD)

all: check-deps _molecule.so libmol.so

check-deps:
	@echo "Checking dependencies..."
	@which clang > /dev/null || (echo "Installing clang..." && sudo apt install -y clang)
	@which swig > /dev/null || (echo "Installing swig..." && sudo apt install -y swig)
	@if [ ! -f $(PYTHON_PATH)/Python.h ]; then \
	  echo "Installing Python development headers..."; \
	  sudo apt install -y python3-dev; \
	fi

_molecule.so: libmol.so molecule_wrap.o
	$(CC) molecule_wrap.o -shared -L. -lmol -L$(PYTHON_LIB) -l$(PYTHON) -o _molecule.so

libmol.so: mol.o
	$(CC) mol.o -shared -o libmol.so



molecule_wrap.c molecule.py: molecule.i
	swig -python molecule.i

mol.o: mol.c mol.h
	$(CC) $(FLAGS) -c -fPIC mol.c -o mol.o

molecule_wrap.o: molecule_wrap.c molecule.py
	$(CC) $(FLAGS) -I $(PYTHON_PATH) -c -fPIC molecule_wrap.c -o molecule_wrap.o


clean:
	rm -f *.o *.so molecule_wrap.c molecule.py
