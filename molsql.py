import os
import sqlite3
import MolDisplay
import random


element_to_name =  {'H': 'Hydrogen',
    'He': 'Helium',
    'Li': 'Lithium',
    'Be': 'Beryllium',
    'B': 'Boron',
    'C': 'Carbon',
    'N': 'Nitrogen',
    'O': 'Oxygen',
    'F': 'Fluorine',
    'Ne': 'Neon',
    'Na': 'Sodium',
    'Mg': 'Magnesium',
    'Al': 'Aluminum'}

radiuses = (
    10, 15, 20, 25, 30, 35, 40, 45, 50
)
colors = (
    'FFFFFF',
    '808080',
    '0000FF',
    'FF0000',
    '020202',
    '000000',
    '000002',
    '020000',
    '050505',
    '010101',
    '000005',
    '050000',
    '000500'
)

sqlTable_Elements = """Elements (
    ELEMENT_NO      INTEGER         NOT NULL,
    ELEMENT_CODE    VARCHAR(3)      NOT NULL    PRIMARY KEY,
    ELEMENT_NAME    VARCHAR(32)     NOT NULL,
    COLOUR1         CHAR(6)         NOT NULL,
    COLOUR2         CHAR(6)         NOT NULL,
    COLOUR3         CHAR(6)         NOT NULL,
    RADIUS          DECIMAL(3)      NOT NULL
    );"""

sqlTable_Atoms = """Atoms (
    ATOM_ID         INTEGER         NOT NULL    PRIMARY KEY     AUTOINCREMENT,
    ELEMENT_CODE    VARCHAR(3)      NOT NULL,
    X               DECIMAL(7,4)    NOT NULL,
    Y               DECIMAL(7,4)    NOT NULL,
    Z               DECIMAL(7,4)    NOT NULL,
    FOREIGN KEY (ELEMENT_CODE) REFERENCES Elements (ELEMENT_CODE)
    );"""


sqlTable_Bonds = """Bonds (
    BOND_ID         INTEGER         NOT NULL    PRIMARY KEY     AUTOINCREMENT,
    A1              INTEGER         NOT NULL,
    A2              INTEGER         NOT NULL,
    EPAIRS          INTEGER         NOT NULL
    );"""

sqlTable_Molecules = """Molecules (
    MOLECULE_ID     INTEGER         NOT NULL    PRIMARY KEY     AUTOINCREMENT,
    NAME            TEXT            NOT NULL    UNIQUE
    );"""

sqlTable_MoleculeAtom = """MoleculeAtom (
    MOLECULE_ID     INTEGER         NOT NULL,
    ATOM_ID         INTEGER         NOT NULL,
    FOREIGN KEY (MOLECULE_ID)   REFERENCES Molecules (MOLECULE_ID),
    FOREIGN KEY (ATOM_ID)  REFERENCES Atoms (ATOM_ID)
    );"""

sqlTable_MoleculeBond = """MoleculeBond (
    MOLECULE_ID     INTEGER         NOT NULL,
    BOND_ID         INTEGER         NOT NULL,
    FOREIGN KEY (MOLECULE_ID)   REFERENCES Molecules (MOLECULE_ID),
    FOREIGN KEY (BOND_ID)  REFERENCES Bonds (BOND_ID)
    );"""

sqlTables = {"Elements":sqlTable_Elements,
             "Atoms":sqlTable_Atoms,
             "Bonds":sqlTable_Bonds,
             "Molecules":sqlTable_Molecules,
             "MoleculeAtom":sqlTable_MoleculeAtom,
             "MoleculeBond":sqlTable_MoleculeBond
             }

tableNames = (
            "Elements",
            "Atoms",
            "Bonds",
            "Molecules",
            "MoleculeAtom",
            "MoleculeBond"
        )

# conn.execute (sql_Elements_table)


class Table(dict):
    def __init__(self, conn, tableName):
        super().__init__()
        self.tableName = tableName
        self.conn = conn
        cursor = self.conn.cursor()
        # self.cursor.execute(sqlTables[tableName])

        cursor.execute(f"PRAGMA table_info({tableName})")
        # gets list of keys in table

        self.columnNames = [vals[1] for vals in cursor.fetchall() if not (not vals[0] and vals[5])]

        cursor.close()


    def __setitem__(self, key, values):
        if isinstance(values, tuple) or isinstance(values, list):
            # is tuple or list
            for i, colName in enumerate(self.columnNames):
                if key == colName:
                    super().__setitem__(key, values[i])

        else:
            # not tuple or list
            if key in self.columnNames:
                super().__setitem__(key, values)

    def commit(self):
        cursor = self.conn.cursor()
        #  if "AUTOINCREMENT" not in vals[2]
        columns = ", ".join(self.keys())
        vals = ", ".join([f"'{val}'" for val in self.values()])

        cursor.execute(f"INSERT INTO {self.tableName} ({columns}) VALUES ({vals})")
        self.conn.commit()

        cursor.close()


class Database():
    def __init__(self, reset=False):
        # reset database
        super().__init__()
        if reset and os.path.exists('molecules.db'):
            os.remove('molecules.db')

        self.conn = sqlite3.connect('molecules.db')
        cursor = self.conn.cursor()

        self.tables = {}

        cursor.close()

        self.create_tables()
    
    def create_tables(self):
        for tableName in tableNames:
            cursor = self.conn.cursor()
            self.conn.execute("""CREATE TABLE IF NOT EXISTS """+sqlTables[tableName])
            
            self.conn.commit()
            self.tables[tableName] = Table(self.conn, tableName)
        
        cursor.close()


    def __setitem__(self, tableName, values):
        if tableName not in self.tables:
            return
        
        currTable = self.tables[tableName]


        for i, columnName in enumerate(currTable.columnNames):
            if i < len(values):
                currTable[columnName] = values[i]

        currTable.commit()




    def close(self):
        self.conn.close()



    def add_atom(self, molname, atom):
#         This method should add the attributes of the atom object (class MolDisplay.Atom) to the
# Atoms table, and add an entry into the MoleculeAtom table that links the named molecule to
# the atom entry in the Atoms table.

        cursor = self.conn.cursor()

        if len(cursor.execute(f"SELECT * FROM Molecules WHERE NAME = '{molname}'").fetchall() ) == 0:
            # mol doesn't exist
            return

        self['Atoms'] = ( atom.element, atom.x, atom.y, atom.z)
        # self['MoleculeAtom'] = ( atom.atom.element, atom.atom.x, atom.atom.y, atom.atom.z)

        cursor.execute("SELECT * FROM Atoms ORDER BY ATOM_ID DESC LIMIT 1")
        atomRow = cursor.fetchone()

        cursor.execute(f"SELECT * FROM Molecules WHERE NAME = '{molname}'")
        molRow = cursor.fetchone()

        self['MoleculeAtom'] = (molRow[0], atomRow[0])

        cursor.close()

    def add_bond(self, molname, bond):
#         This method should add the attributes of the bond object (class MolDisplay.Bond) to the
# Bonds table, and add an entry into the MoleculeBond table that links the named molecule to
# the atom entry in the Bonds table.

        cursor = self.conn.cursor()

        if len(cursor.execute(f"SELECT * FROM Molecules WHERE NAME = '{molname}'").fetchall() ) == 0:
            # mol doesn't exist
            return

        self['Bonds'] = ( bond.a1, bond.a2, bond.epairs)
        # self['MoleculeAtom'] = ( atom.atom.element, atom.atom.x, atom.atom.y, atom.atom.z)

        cursor.execute("SELECT * FROM Bonds ORDER BY BOND_ID DESC LIMIT 1")
        bondRow = cursor.fetchone()

        cursor.execute(f"SELECT * FROM Molecules WHERE NAME = '{molname}'")
        molRow = cursor.fetchone()

        self['MoleculeBond'] = (molRow[0], bondRow[0])

        cursor.close()

    def add_molecule(self, name, fp):
#         This function should create a MolDisplay.Molecule object, call its parse method on fp, add
# an entry to the Molecules table and call add_atom and add_bond on the database for each
# atom and bond returned by the get_atom and get_bond methods of the molecule.

        cursor = self.conn.cursor()
        
        if len(cursor.execute(f"SELECT * FROM Molecules WHERE NAME = '{name}'").fetchall() ) == 1:
            # mol already exists
            print("mol already exists")
            return

        mol = MolDisplay.Molecule()
        mol.parse(fp)

        self.conn.execute('''
            INSERT INTO Molecules (NAME)
            VALUES (?)
        ''', (name,))


        for i in range(mol.atom_no):
            self.add_atom(name, mol.get_atom(i))

        for i in range(mol.bond_no):
            self.add_bond(name, mol.get_bond(i))


        cursor.close()

    def load_mol( self, name ):

        cursor = self.conn.cursor()
        
        # generates list of atom id's
        atomJoin = cursor.execute(
        f"""
        SELECT *
        FROM Molecules
        JOIN MoleculeAtom
        ON Molecules.MOLECULE_ID = MoleculeAtom.MOLECULE_ID
        WHERE Molecules.NAME = '{name}'
        """
        ).fetchall()

        atomIndexs = [vals[3] for vals in atomJoin]

        atoms = cursor.execute(
        f"""
        SELECT *
        FROM Atoms
        WHERE ATOM_ID IN ({",".join(["?"] * len(atomIndexs))})
        """, atomIndexs
        ).fetchall()





        # generates list of bond id's
        bondJoin = cursor.execute(
        f"""
        SELECT *
        FROM Molecules
        JOIN MoleculeBond
        ON Molecules.MOLECULE_ID = MoleculeBond.MOLECULE_ID
        WHERE Molecules.NAME = '{name}'
        """
        ).fetchall()

        bondIndexs = [vals[3] for vals in bondJoin]

        bonds = cursor.execute(
        f"""
        SELECT *
        FROM Bonds
        WHERE BOND_ID IN ({",".join(["?"] * len(bondIndexs))})
        """, bondIndexs
        ).fetchall()

        MolDisplay.element_name = self.element_name()
        MolDisplay.radius = self.radius()
        MolDisplay.header = MolDisplay.baseheader + self.radial_gradients();

        mol = MolDisplay.Molecule()

        for atom in atoms:
            mol.append_atom(atom[1], atom[2], atom[3], atom[4])

        for bond in bonds:
            mol.append_bond(bond[1]-1, bond[2]-1, bond[3])

        return mol
    

    def radius( self ):

        rad = {}
        cursor = self.conn.cursor()
        for element in cursor.execute(f"SELECT * FROM Elements").fetchall():
            rad.update({element[1]: element[6]})

        cursor.close()

        return rad


    def element_name( self ):
        ele_name = {}
        cursor = self.conn.cursor()
        for elementCode in [row[1] for row in cursor.execute("SELECT * FROM Atoms").fetchall()]:
            if elementCode not in [row[1] for row in cursor.execute("SELECT * FROM Elements").fetchall()]:
                self['Elements'] = (random.randint(1,60), elementCode, element_to_name[elementCode], random.choice(colors), random.choice(colors), random.choice(colors), random.choice(radiuses))



        for element in cursor.execute("SELECT * FROM Elements").fetchall():
            ele_name.update({element[1]: element[2]})

        cursor.close()

        return ele_name


    def radial_gradients( self ):
        cursor = self.conn.cursor()
        radialGradientSVG = ""

        for element in cursor.execute("SELECT * FROM Elements").fetchall():

            radialGradientSVG += """
                <radialGradient id="%s" cx="-50%%" cy="-50%%" r="220%%" fx="20%%" fy="20%%">
                    <stop offset="0%%" stop-color="#%s"/>
                    <stop offset="50%%" stop-color="#%s"/>
                    <stop offset="100%%" stop-color="#%s"/>
                </radialGradient>""" % (element[2],element[3],element[4],element[5])

        return radialGradientSVG
    

    def getMolNames(self):
        cursor = self.conn.cursor()

        return [mol[1] for mol in cursor.execute("SELECT * FROM Molecules")]
    
        

        






# if __name__ == "__main__":
#     db = Database(reset=True);
#     db.create_tables();
#     db['Elements'] = ( 1, 'H', 'Hydrogen', 'FFFFFF', '050505', '020202', 25 );
#     db['Elements'] = ( 6, 'C', 'Carbon', '808080', '010101', '000000', 40 );
#     db['Elements'] = ( 7, 'N', 'Nitrogen', '0000FF', '000005', '000002', 40 );
#     db['Elements'] = ( 8, 'O', 'Oxygen', 'FF0000', '050000', '020000', 40 );


#     fp = open( 'water-3D-structure-CT1000292221.sdf' );
#     db.add_molecule( 'Water', fp );
#     # fp = open( 'caffeine-3D-structure-CT1001987571.sdf' );
#     # db.add_molecule( 'Caffeine', fp );
#     # fp = open( 'CID_31260.sdf' );
#     # db.add_molecule( 'Isopentanol', fp );
#     # display tables
#     # print( db.conn.execute( "SELECT * FROM Elements;" ).fetchall() );
#     # print( db.conn.execute( "SELECT * FROM Molecules;" ).fetchall() );
#     # print( db.conn.execute( "SELECT * FROM Atoms;" ).fetchall() );
#     # print( db.conn.execute( "SELECT * FROM Bonds;" ).fetchall() );
#     # print( db.conn.execute( "SELECT * FROM MoleculeAtom;" ).fetchall() );
#     # print( db.conn.execute( "SELECT * FROM MoleculeBond;" ).fetchall() );
#     db.load_mol('Water')


# if __name__ == "__main__":
#     db = Database(reset=False); # or use default

#     MolDisplay.radius = db.radius();
#     MolDisplay.element_name = db.element_name();
#     MolDisplay.header += db.radial_gradients();
#     for molecule in [ 'Water', 'Caffeine', 'Isopentanol' ]:
#         mol = db.load_mol( molecule );
#         mol.sort();
#         fp = open( molecule + ".svg", "w" );
#         fp.write( mol.svg() );
#         fp.close();