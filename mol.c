#include "mol.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>


void atomset( atom *a, char element[3], double *x, double *y, double *z ) {
    if (a == NULL) {
        return;
    }
    if (x == NULL || y == NULL || z == NULL) {
        return;
    }

    // copies element,x,y,z into corresponding values into atom struct
    // copies string element into location at atom.element
    strcpy(a->element, element);
    // copies values into locations at atom.(x,y,z)
    a->x = *x;
    a->y = *y;
    a->z = *z;
}

void atomget( atom *a, char element[3], double *x, double *y, double *z ) {
    if (a == NULL) {
        return;
    }
    if (x == NULL || y == NULL || z == NULL) {
        return;
    }

    // copies values in atom to locations pointed to by element, x, y, z
    strcpy(element, a->element);
    *x = a->x;
    *y = a->y;
    *z = a->z;
}

void bondset( bond *b, unsigned short *a1, unsigned short *a2, atom
**atoms, unsigned char *epairs ) {
    if (b == NULL) {
        return;
    }
    if (a1 == NULL || a2 == NULL) {
        return;
    }
    if (atoms == NULL) {
        return;
    }
    if (epairs == NULL) {
        return;
    }
    // copies values a1,a2, atoms, and epairs into corresponding values in bond struct
    b->a1 = *a1;
    b->a2 = *a2;
    b->atoms = *atoms;
    b->epairs = *epairs;
    compute_coords(b);
}

void bondget( bond *b, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs ) {
    if (b == NULL) {
        return;
    }
    if (a1 == NULL || a2 == NULL) {
        return;
    }
    if (atoms == NULL) {
        return;
    }
    if (epairs == NULL) {
        return;
    }
    // copies values from bond into corresponding values a1,a2,epairs, and atoms
    *a1 = b->a1;
    *a2 = b->a2;
    *atoms = b->atoms;
    *epairs = b->epairs;
}

void compute_coords(bond* b) {
    // compute values: z, x1, y1, x2, y2, len, dx, dy based on a1 and a2 in bond
    b->z = average(b->atoms[b->a1].z, b->atoms[b->a2].z);

    b->x1 = b->atoms[b->a1].x;
    b->y1 = b->atoms[b->a1].y;

    b->x2 = b->atoms[b->a2].x;
    b->y2 = b->atoms[b->a2].y;

    b->len = distance(b->atoms[b->a1].x, b->atoms[b->a2].x, b->atoms[b->a1].y, b->atoms[b->a2].y);
    
    b->dx = (b->x2 - b->x1) / b->len;
    b->dy = (b->y2 - b->y1) / b->len;

}

int bond_comp( const void *a, const void *b ) {
    const atom *left = *(const atom **)a;
    const atom *right = *(const atom **)b;
    if (left->z > right->z) {
        return 1;
    } else if (left->z < right->z) {
        return -1;
    } else {
        return 0;
    }
}
// this method is used to sort and compare the bonds


molecule *molmalloc( unsigned short atom_max, unsigned short bond_max ) {
    // returns address of a malloced molecule that is ready to be filled
    // returns NULL if malloc failed
    molecule *newMol = malloc(sizeof(molecule));;
    
    if (newMol == NULL) {
        return NULL;
    }

    newMol->atom_no = 0;
    newMol->atom_max = atom_max;
    newMol->bond_no = 0;
    newMol->bond_max = bond_max;

    newMol->atoms = malloc(sizeof(atom)*atom_max);
    if (newMol->atoms == NULL) {
        printf("Malloc Failed. Terminating Program.\n");
        exit(1);
    }
    newMol->atom_ptrs = malloc(sizeof(atom*)*atom_max);
    if (newMol->atom_ptrs == NULL) {
        printf("Malloc Failed. Terminating Program.\n");
        exit(1);
    }

    newMol->bonds = malloc(sizeof(bond)*bond_max);
    if (newMol->bonds == NULL) {
        printf("Malloc Failed. Terminating Program.\n");
        exit(1);
    }
    newMol->bond_ptrs = malloc(sizeof(bond*)*bond_max);
    if (newMol->bond_ptrs == NULL) {
        printf("Malloc Failed. Terminating Program.\n");
        exit(1);
    }

    return newMol;
}

molecule *molcopy( molecule *src ) {
    // returns NULL if src == NULL
    if (src == NULL) {
        printf("ERROR: attempted to copy a NULL molecule\n");
        return NULL;
    }
    molecule *newMol = molmalloc(src->atom_max,src->bond_max);
    if (newMol == NULL) {
        return NULL;
    }
    
    // copy bonds
    for (int i = 0; i < src->bond_no; i++) {
        molappend_bond(newMol, src->bond_ptrs[i]);
    }
    // copy atoms
    for (int i = 0; i < src->atom_no; i++) {
        molappend_atom(newMol, src->atom_ptrs[i]);
    }
    
    return newMol;
}

void molfree( molecule *ptr ) {
    if (ptr == NULL) {
        printf("ERROR: attempted to free a NULL molecule\n");
        return;
    }
    // free arrays
    free(ptr->atom_ptrs);
    free(ptr->bond_ptrs);
    free(ptr->atoms);
    free(ptr->bonds);

    // free molecule
    free(ptr);
    
}

void molappend_atom( molecule *mol, atom *newAtom) {
    if (mol == NULL) {
        return;
    }
    if (newAtom == NULL) {
        // printf("ERROR: attempted appending a NULL atom\n");
        return;
    }
    
    // while max is less than future atom_no
    while (mol->atom_max < mol->atom_no+1) {
        // increase max and array
        if (mol->atom_max == 0) {
            // 0 so increase by 1
            mol->atom_max = 1;
        } else {
            // not 0 so double size
            mol->atom_max *= 2;
        }

        // TODO remove this line
        // atom* old_root_atom = mol->atoms;

        mol->atoms = realloc(mol->atoms, sizeof(atom)*mol->atom_max);
        mol->atom_ptrs = realloc(mol->atom_ptrs, sizeof(atom*)*mol->atom_max);

        if (mol->atoms == NULL || mol->atom_ptrs == NULL) {
            // realloc failed!
            printf("Realloc failure. Ending Program");
            exit(1);
        }


        // adjust memory adress pointers after realloc
        for (int i = 0; i < mol->atom_no; i++) {
            mol->atom_ptrs[i] = &(mol->atoms[i]);
        }
    }
    // append the atom
    mol->atoms[mol->atom_no] = *newAtom;
    mol->atom_ptrs[mol->atom_no] = &(mol->atoms[mol->atom_no]);

    // increment atom_no
    mol->atom_no++;

}

void molappend_bond( molecule *mol, bond *newBond ) {
    if (mol == NULL) {
        printf("ERROR: attempted appending to a NULL molecule\n");
        return;
    }
    if (newBond == NULL) {
        printf("ERROR: attempted appending a NULL bond\n");
        return;
    }
    
    // while max is less than future atom_no
    while (mol->bond_max < mol->bond_no+1) {
        // increase max and array
        if (mol->bond_max == 0) {
            // 0 so increase by 1
            mol->bond_max = 1;
        } else {
            // not 0 so double size
            mol->bond_max *= 2;
        }
        mol->bonds = realloc(mol->bonds, sizeof(bond)*mol->bond_max);
        mol->bond_ptrs = realloc(mol->bond_ptrs, sizeof(bond*)*mol->bond_max);
        
        if (mol->bonds == NULL || mol->bond_ptrs == NULL) {
            // realloc failed!
            printf("Realloc failure. Ending Program");
            exit(1);
        }

        // adjust memory adress pointers after realloc
        for (int i = 0; i < mol->bond_no; i++) {
            mol->bond_ptrs[i] = &(mol->bonds[i]);
        }
    }
    // append the atom
    mol->bonds[mol->bond_no] = *newBond;
    mol->bond_ptrs[mol->bond_no] = &(mol->bonds[mol->bond_no]);

    // increment atom_no
    mol->bond_no++;
}

int atom_comp(const void *a1, const void *a2) {
    const atom *left = *(const atom **)a1;
    const atom *right = *(const atom **)a2;
    if (left->z > right->z) {
        return 1;
    } else if (left->z < right->z) {
        return -1;
    } else {
        return 0;
    }
}
// comparator function used to compare two atoms in qsort

void molsort( molecule *mol ) {
    if (mol == NULL) {
        return;
    }
    // sort atoms based on z value & sort bonds based on avg z value
    qsort(mol->atom_ptrs, mol->atom_no, sizeof(atom*), atom_comp);
    qsort(mol->bond_ptrs, mol->bond_no, sizeof(bond*), bond_comp);
}
// sorts given molecule's atoms and bonds based on z value

double average(double val1, double val2) {
    return (val1+val2)/2;
}
// this function returns the average between two doubles

double distance(double x1, double x2, double y1, double y2) {
    return sqrt( (x2-x1)*(x2-x1) + (y2-y1)*(y2-y1) );
}
// this function returns the distance between the two points

void xrotation( xform_matrix matrix, unsigned short deg ) {
    double pi = 3.141593;
    double radian = (double)deg*(pi/180.0);

    matrix[0][0] = 1;    // x1
    matrix[0][1] = 0;           // y1
    matrix[0][2] = 0;    // z1

    matrix[1][0] = 0;            // x2
    matrix[1][1] = cos(radian);            // y2
    matrix[1][2] = -1 * sin(radian);            // z2

    matrix[2][0] = 0;    // x3
    matrix[2][1] = sin(radian);                // y3
    matrix[2][2] = cos(radian);         // z3
}

void yrotation( xform_matrix matrix, unsigned short deg ) {
    double pi = 3.141593;
    double radian = (double)deg*(pi/180.0);

    matrix[0][0] = cos(radian);    // x1
    matrix[0][1] = 0;           // y1
    matrix[0][2] = sin(radian);    // z1

    matrix[1][0] = 0;            // x2
    matrix[1][1] = 1;            // y2
    matrix[1][2] = 0;            // z2

    matrix[2][0] = -1 * sin(radian);    // x3
    matrix[2][1] = 0;                // y3
    matrix[2][2] = cos(radian);         // z3
}

void zrotation( xform_matrix matrix, unsigned short deg ) {
    double pi = 3.141593;
    double radian = (double)deg*(pi/180.0);

    matrix[0][0] = cos(radian);    // x1
    matrix[0][1] = -1 * sin(radian);           // y1
    matrix[0][2] = 0;    // z1

    matrix[1][0] = sin(radian);            // x2
    matrix[1][1] = cos(radian);            // y2
    matrix[1][2] = 0;            // z2

    matrix[2][0] = 0;    // x3
    matrix[2][1] = 0;                // y3
    matrix[2][2] = 1;         // z3
}

void mol_xform( molecule *mol, xform_matrix matrix ) {
    atom* currAtom;
    bond* currBond;
    double currX, currY, currZ;
    for (int i = 0; i < mol->atom_no; i++) {
        // for each atom
        currAtom = mol->atom_ptrs[i];

        // save x,y,z vals
        currX = currAtom->x;
        currY = currAtom->y;
        currZ = currAtom->z;

        // set new x,y,z vals
        currAtom->x = (matrix[0][0]*currX) + (matrix[0][1]*currY) + (matrix[0][2]*currZ);
        currAtom->y = (matrix[1][0]*currX) + (matrix[1][1]*currY) + (matrix[1][2]*currZ);
        currAtom->z = (matrix[2][0]*currX) + (matrix[2][1]*currY) + (matrix[2][2]*currZ);
    }

    for (int i = 0; i < mol->bond_no; i++) {
        // for each bond
        currBond = mol->bond_ptrs[i];

        // compute new coords
        compute_coords(currBond);
    }
}

rotations *spin(molecule *src) {
    if (src == NULL) {
        printf("ERROR: attempted to spin a NULL molecule\n");
        return NULL;
    }
    xform_matrix x_matrix;
    xform_matrix y_matrix;
    xform_matrix z_matrix;

    rotations *newRot = malloc(sizeof(rotations));
    if (newRot == NULL) {
        return NULL;
    }

    for (int i = 0; i < 72; i++) {
        // copy molecules
        newRot->x[i] = molcopy(src);
        if (newRot->x[i] == NULL) {
            return NULL;
        }
        newRot->y[i] = molcopy(src);
        if (newRot->y[i] == NULL) {
            return NULL;
        }
        newRot->z[i] = molcopy(src);
        if (newRot->z[i] == NULL) {
            return NULL;
        }

        // rotate
        xrotation(x_matrix, (unsigned short)(i*5));
        yrotation(y_matrix, (unsigned short)(i*5));
        zrotation(z_matrix, (unsigned short)(i*5));

        // modify molecule
        mol_xform(newRot->x[i], x_matrix);
        mol_xform(newRot->y[i], y_matrix);
        mol_xform(newRot->z[i], z_matrix);

        // sort the molecules individually
        molsort(newRot->x[i]);
        molsort(newRot->y[i]);
        molsort(newRot->z[i]);
    }

    return newRot;
}

void rotationsfree(rotations *rot) {
    if (rot == NULL) {
        printf("ERROR: attempted to free a NULL rotations\n");
        return;
    }
    for (int i = 0; i < 72; i++) {
        molfree(rot->x[i]);
        molfree(rot->y[i]);
        molfree(rot->z[i]);
    }
    free(rot);
}
