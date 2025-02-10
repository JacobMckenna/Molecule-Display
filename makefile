FLAGS = -Wall -std=c99 -pedantic
CC = clang
PYTHON = /usr/include/python3.7m
PYTHON_LIB = /usr/lib/python3.7/config-3.7m-x86_64-linux-gnu

export LD_LIBRARY_PATH=`pwd`

_molecule.so: libmol.so molecule_wrap.o molecule.py
	$(CC) molecule_wrap.o -dynamiclib -shared -L. -lmol -L$(PYTHON_LIB) -lpython3.7m -o _molecule.so

libmol.so: mol.o
	$(CC) mol.o -shared -o libmol.so

# paths

# all: test1 test2 test3
all: mol.o molecule_wrap.o

molecule_wrap.c molecule.py: molecule.i
	swig3.0 -python molecule.i

mol.o: mol.c mol.h
	$(CC) $(FLAGS) -c -fPIC mol.c -o mol.o

molecule_wrap.o: molecule_wrap.c molecule.py
	$(CC) $(FLAGS) -I $(PYTHON) -c -fPIC molecule_wrap.c -o molecule_wrap.o


clean:
	rm -f *.o *.so
