// mol.h file contianing typedefs and function prototypes for mol.c

// typedef strutures:

typedef struct atom
{
char element[3];
double x, y, z;
} atom;
// atom structure containing element string and 3d positional doubles for as x,y,z

typedef struct bond
{
unsigned short a1, a2;
unsigned char epairs;
atom *atoms;
double x1, x2, y1, y2, z, len, dx, dy;
} bond;
// bond structure containing 2 atoms and a small epairs number

typedef struct molecule
{
unsigned short atom_max, atom_no;
atom *atoms, **atom_ptrs;
unsigned short bond_max, bond_no;
bond *bonds, **bond_ptrs;
} molecule;
// molecule structure containing max and number of atoms and bonds, aswell as the array of bonds, atoms, bond_ptrs, and atom_ptrs

typedef double xform_matrix[3][3];
// 3x3 matrix structure

void atomset( atom *a, char element[3], double *x, double *y, double *z );
// copies values element, x, y, z to corresponding values in atom

void atomget( atom *a, char element[3], double *x, double *y, double *z );
// copies values in atom to corresponding values element, x, y, z

void bondset( bond *b, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs );
// copies values a1, a2, epairs to corresponding 

void bondget( bond *b, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs );
// copies values in bond to corresponding values a1, a2, epairs

void compute_coords( bond *b );
// this funciton computes the values: z,x1,y1,x2,y2,len,dx,dy of the bond

int bond_comp( const void *b1, const void *b2 );
// this method is used to sort and compare the bonds

molecule *molmalloc( unsigned short atom_max, unsigned short bond_max );
// returns address of malloced memory large enough for atom_max and bond_max

molecule *molcopy( molecule *src );
// copies the molecule at src and returns a duplicate copied molecule

void molfree( molecule *ptr );
// frees memory associated with ptr

void molappend_atom( molecule *mol, atom *newAtom );
// This function should copy the data pointed to by atom to the first “empty” atom in atoms in the
// molecule pointed to by molecule, and set the first “empty” pointer in atom_ptrs to the same
// atom in the atoms array incrementing the value of atom_no. If atom_no equals atom_max, then
// atom_max must be incremented, and the capacity of the atoms, and atom_ptrs arrays
// increased accordingly. If atom_max was 0, it should be incremented to 1, otherwise it should be
// doubled. Increasing the capacity of atoms, and atom_ptrs should be done using realloc so
// that a larger amount of memory is allocated and the existing data is copied to the new location.
void molappend_bond( molecule *mol, bond *newBond );
// This function should operate like that molappend_atom function, except for bonds.
void molsort( molecule *mol );
// This function should sort the atom_ptrs array in place in order of increasing z value. I.e.
// atom_ptrs[0] should point to the atom that contains the lowest z value and
// atom_ptrs[atom_no-1] should contain the highest z value. It should also sort the bond_ptrs
// array in place in order of increasing “ z value”. Since bonds don’t have a z attribute, their z
// value is assumed to be the average z value of their two atoms. I.e. bond_ptrs[0] should point
// to the bond that has the lowest z value and bond_ptrs[atom_no-1] should contain the highest
// z value.Hint: use qsort.
void xrotation( xform_matrix matrix, unsigned short deg );
// This function will allocate, compute, and return an affine transformation matrix corresponding
// to a rotation of deg degrees around the x-axis. This matrix must be freed by the user when no-
// longer needed.
void yrotation( xform_matrix matrix, unsigned short deg );
// This function will allocate, compute, and return an affine transformation matrix corresponding
// to a rotation of deg degrees around the y-axis. This matrix must be freed by the user when no-
// longer needed.
void zrotation( xform_matrix matrix, unsigned short deg );
// This function will allocate, compute, and return an affine transformation matrix corresponding
// to a rotation of deg degrees around the z-axis. This matrix must be freed by the user when no-
// longer needed.
void mol_xform( molecule *mol, xform_matrix matrix );
// This function will apply the transformation matrix to all the atoms of the molecule by
// performing a vector matrix multiplication on the x, y, z coordinates.
// Your code should malloc only as much memory as required in the function descriptions. All
// malloc return values must be checked before accessing memory. If malloc returns a NULL
// value, the return value of the calling function should also be NULL.

// nightmare mode:
typedef struct rotations
{
    molecule *x[72];
    molecule *y[72];
    molecule *z[72];
} rotations;
// The structure rotations represents the rotations of a given molecule around the x, y and z
// axes in 5 degree increments. I.e. element x[3] of the structure is a pointer to a molecule
// which is equivalent the given molecule rotated by 15 degrees around the x axis.

rotations *spin(molecule *mol);
// This function will allocate memory for a rotations structure, create molecules using molcopy
// applied to the provided mol, and add their pointers to the x, y, and z members of the rotations
// structure. Each molecule will be rotated by an angle equal to 5 times the array index, and it will
// be sorted.

void rotationsfree(rotations *rot);
// This function will free the memory associated with a rotations structure. This includes freeing
// each of the 216 molecules included within the structure in addition to the structure itself.

// ------------------
// self made methods:
// ------------------
int atom_comp(const void *a1, const void *a2);
// this function is used to compare and sort the atoms with qsort in the molsort funciton.
double average(double val1, double val2);
// this function returns the average between two doubles
double distance(double x1, double x2, double y1, double y2);
// this function calcuates the distance between two points
