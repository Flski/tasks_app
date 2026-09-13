import os


directory_path = os.path.abspath(os.path.dirname(__file__))

database_file_path = "sqlite:///" + os.path.join(directory_path, "database_file.db")

templates_path = os.path.join(directory_path, "templates")

secret_key = "15d40f4e36ee46dc47ca8f7fed026053701c45d2a7e21bea4d164c9e99aa5e44cbb79f2128f7a9d48dbd75fe2d4b2f0b2a0" \
"7c48c8e4a8627fae557fbb840cd24dcfa4f7b806c81d885523529361e465ef5dd3d94c48db99c0a4b7d0587f7131c59168a505342fbb1ce"
