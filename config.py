import os


directory_path = os.path.abspath(os.path.dirname(__file__))

database_file_path = "sqlite:///" + os.path.join(directory_path, "database_file.db")

templates_path = os.path.join(directory_path, "templates")

secret_key = "f15b70b81d3219216854b3f165229867ee5742c2d88ca580eda8351cfa647150d1c4178025eabc"
"83f9519d4b845ae1d8fe4f9f847833990b37f9895070b5b580da5e44f277b9"
