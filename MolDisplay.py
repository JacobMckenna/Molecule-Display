import molecule

baseheader = """<svg version="1.1" width="1000" height="1000" xmlns="http://www.w3.org/2000/svg">"""
footer = """</svg>"""

header = """<svg version="1.1" width="1000" height="1000" xmlns="http://www.w3.org/2000/svg">"""

radius = {}
element_name = {}

offsetx = 500
offsety = 500


class Atom:
    def __init__(self, c_atom):
        self.atom = c_atom
        self.z = c_atom.z

    def __str__(self):
        return self.atom.element +" "+ str(self.atom.x) +" "+ str(self.atom.y) +" "+ str(self.atom.z)

    def svg(self):
        cx = (self.atom.x * 100.0) + offsetx
        cy = (self.atom.y * 100.0) + offsety
        s = element_name[self.atom.element]
        r = radius[self.atom.element]

        string = '  <circle cx="%.2f" cy="%.2f" r="%d" fill="url(#%s)"/>\n' % (cx, cy, r, s)
        return string

class Bond:
    def __init__(self, c_bond):
        self.bond = c_bond
        self.z = c_bond.z
    
    def __str__(self):
        buildString = ""
        buildString += str(self.bond.a1)+" "+str(self.bond.a2)+" "+str(self.bond.epairs)+" "
        buildString += str(self.bond.x1)+" "+str(self.bond.y1)+" "+str(self.bond.x2)+" "+str(self.bond.y2)+" "
        buildString += str(self.bond.len)+" "+str(self.bond.dx)+" "+str(self.bond.dy)

        return buildString

    def svg(self):
        cx1 = (self.bond.x1 * 100.0) + offsetx
        cy1 = (self.bond.y1 * 100.0) + offsety
        cx2 = (self.bond.x2 * 100.0) + offsetx
        cy2 = (self.bond.y2 * 100.0) + offsety

        x1 = cx1 - self.bond.dy*10.0
        y1 = cy1 + self.bond.dx*10.0

        x2 = cx1 + self.bond.dy*10.0
        y2 = cy1 - self.bond.dx*10.0

        x3 = cx2 + self.bond.dy*10.0
        y3 = cy2 - self.bond.dx*10.0

        x4 = cx2 - self.bond.dy*10.0
        y4 = cy2 + self.bond.dx*10.0


        string = '  <polygon points="%.2f,%.2f %.2f,%.2f %.2f,%.2f %.2f,%.2f" fill="green"/>\n' %(x1,y1,x2,y2,x3,y3,x4,y4)
        return string

# molecule struct/class
class Molecule(molecule.molecule):
    def __init__(self):
        super().__init__()
    
    def __str__(self):
        buildString = ""
        buildString += "Atoms:\n"
        for i in range(self.atom_no):
            buildString += str(Atom(self.get_atom(i)))+"\n"
        buildString += "\n"
        
        print("Bonds:\n")
        for i in range(self.bond_no):
            buildString += str(Bond(self.get_bond(i)))+"\n"
        
        return buildString

    # returns svg text to display molecule
    def svg(self):
        buildString = ""
        buildString += header
        # append atoms and bonds in order of increasing z value
        # assume that each array has already been sorted
        a,b = 0,0
        while a < self.atom_no and b < self.bond_no:
            if self.get_atom(a).z < self.get_bond(b).z:
                # append a
                temp = Atom(self.get_atom(a))
                buildString += temp.svg()
                a += 1
            else: # self.get_bond(b).z < self.get_atom(a).z:
                # append b
                temp = Bond(self.get_bond(b))
                buildString += temp.svg()
                b += 1

        if a == self.atom_no:
            # a got max, append the rest of b
            for i in range(b, self.bond_no):
                temp = Bond(self.get_bond(i))
                buildString += temp.svg()

        elif b == self.bond_no:
            # b got max, append the rest of a
            for i in range(a, self.atom_no):
                temp = Atom(self.get_atom(i))
                buildString += temp.svg()
        
        buildString += footer

        return buildString
    
    # parses the file object to fill in the data for the molecule
    def parse(self, file_object):
        try:
            file_object.readline()
            file_object.readline()
            file_object.readline()

            line = file_object.readline()

            line = line.split()
 
            num_atoms = int(line[0])
            num_bonds = int(line[1])


            for i in range(num_atoms):
                # loop through next couple lines which are each atoms
                line = file_object.readline().split()
                self.append_atom(line[3], float(line[0]),float(line[1]),float(line[2]))
            
            for i in range(num_bonds):
                line = file_object.readline().split()
                self.append_bond(int(line[0]),int(line[1]),int(line[2]))

        except:
            print("Error")