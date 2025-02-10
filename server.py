from http.server import HTTPServer, BaseHTTPRequestHandler
import MolDisplay
import molsql
import cgi

form = cgi.FieldStorage()

db = molsql.Database(reset=False)
MolDisplay.element_name = db.element_name();
MolDisplay.radius = db.radius();
MolDisplay.header = MolDisplay.baseheader + db.radial_gradients();

hostname = "localhost"
port = 59355


class Server(BaseHTTPRequestHandler):
    # selectedMol = None

    def do_GET(self):

        # if self.path == '/':
        html = ""
        html += """
<!DOCTYPE html>
<html>
<head>
    <title>Molecule</title>
    <style>
        body {
            background-color: #f0f0f0;
        }
        .box {
            background-color: black;
            color: white;
            padding: 10px;
            margin: 10px;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <h1>Molecules</h1>
    <div class="box">Upload sdf file to be used as Molecule.</div>
    <form action="/upload" method="post" enctype="multipart/form-data">
        <label for="name">Molecule Name:</label>
        <input type="text" id="name" name="name">
        <input type="file" name="sdf_file">
        <button type="submit">Upload</button>
    </form>
    <div class="box">Select a molecule to be displayed.</div>
    <form action="/molecule" method="post" enctype="multipart/form-data">
        <select name="molecule_list">"""
        for name in db.getMolNames():
            mol = db.load_mol(name)
            mol.sort()
            html += f'<option value="{name}">{name}: ({mol.atom_no}: Atoms, {mol.bond_no}: Bonds)</option>'
        html += """</select>
        <button id="selectButton" type="submit">Display Selected Molecule</button>
    </form> """

        html += """
    <div class="box">Add elements.</div>
    <form action="/add" method="post">
        <label for="number">Element Number:</label>
        <input type="number" id="number" name="number">
        <label for="code">Element Code:</label>
        <input type="text" id="code" name="code">
        <label for="name">Element Name:</label>
        <input type="text" id="name" name="name">
        <label for="color1">Color Value 1:</label>
        <input type="color" id="color1" name="color1">
        <label for="color2">Color Value 2:</label>
        <input type="color" id="color2" name="color2">
        <label for="color3">Color Value 3:</label>
        <input type="color" id="color3" name="color3">
        <label for="radius">Radius:</label>
        <input type="number" id="radius" name="radius">
        <button type="submit">Add</button>
    </form>
    """

        html += """
    <div class="box">Remove elements.</div>
    <button type="submit">Remove</button>
    <label for="name">Element Name:</label>
    <input type="text" id="ELEMENT_NAME" name="ELEMENT_NAME">
</body>
</html>
"""

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(bytes(html, 'utf-8'))

  
    def do_POST(self):

        ctype, pdict = cgi.parse_header(self.headers['content-type'])
        
        
        if self.path == "/molecule":
            
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.readline()
            post_data = self.rfile.readline()
            post_data = self.rfile.readline()
            post_data = self.rfile.readline()
            selected_molecule = post_data.decode('utf-8')
            selected_molecule = selected_molecule.strip()
            mol = db.load_mol(selected_molecule)
            mol.sort()



            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(bytes(f"<p>Number of Atoms: {mol.atom_no}</p>", 'utf-8'))
            self.wfile.write(bytes(f"<p>Number of Bonds: {mol.bond_no}</p>", 'utf-8'))
            svg = mol.svg()
            self.wfile.write(bytes(svg, 'utf-8'))
        
        elif self.path == "/upload":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.readline()
            post_data = self.rfile.readline()
            post_data = self.rfile.readline()
            post_data = self.rfile.readline()
            
            data = post_data.decode('utf-8')
            data = data.split()
            name = data[0]

            post_data = self.rfile.readline()

            post_data = self.rfile.readline()
            data = post_data.decode('utf-8')
            data = data.split()
            filename = data[3].split("=")[1]
            filename = filename.strip('"')

            post_data = self.rfile.readline()
            post_data = self.rfile.readline()

            db.add_molecule(name, open(filename, "r"))


            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            if name in db.getMolNames():
                self.wfile.write(bytes("<!DOCTYPE html><html><head><title>Success!</title></head><body><h1>Success!</h1></body></html>", 'utf-8'))
            else:
                self.wfile.write(bytes("<!DOCTYPE html><html><head><title>Fail!</title></head><body><h1>Fail!</h1></body></html>", 'utf-8'))
            


HTTPServer((hostname, port), Server).server_close()
webServer = HTTPServer((hostname, port), Server)
print("Server started http://%s:%s" % (hostname, port))

try:
    webServer.serve_forever()
except KeyboardInterrupt:
    webServer.server_close()
    print("Server stopped.")
webServer.server_close()
print("Server stopped.")