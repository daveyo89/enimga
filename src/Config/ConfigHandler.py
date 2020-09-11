import glob
import os
import sys
import yaml
from cryptography.fernet import Fernet


class ConfigHandler:
    def __init__(self):
        self.project_path = sys.path[0]

    def check_existing_config(self):
        os.makedirs(f"{self.project_path}/config", exist_ok=True)
        os.chdir(f"{self.project_path}/config")
        files = glob.glob("*.yaml")

        if not files:
            return self.create_credentials()
        else:
            return self.read_yml(files[0])

    def generate_key(self):
        key = Fernet.generate_key()
        with open(".secret.key", "wb") as key_file:
            key_file.write(key)

    def load_key(self):
        return open(".secret.key", "rb").read()

    def encrypt_message(self, message):
        key = self.load_key()
        encoded_message = message.encode()
        f = Fernet(key)
        encrypted_message = f.encrypt(encoded_message)

        return encrypted_message

    def create_credentials(self):
        self.generate_key()

        username = input("Username: ")
        password = self.encrypt_message(input("Password: "))

        with open(f"{username}.yaml", 'w') as f:
            yaml.safe_dump({"username": username, "pass": password}, f, sort_keys=False)

        return {"username": username, "pass": password}

    def read_yml(self, file):
        with open(file, 'r') as f:
            return yaml.safe_load(f)

    def decrypt_message(self, encrypted_message):
        key = self.load_key()
        f = Fernet(key)

        return f.decrypt(encrypted_message).decode()

    def get_stored_contacts(self):
        os.makedirs(f"{self.project_path}/config", exist_ok=True)
        try:
            contacts = self.read_yml(f"{self.project_path}/config/contacts.yaml")
            if not contacts:
                return list()
            else:
                return contacts

        except Exception:
            return []

    def store_contact(self, contact):
        os.makedirs(f"{self.project_path}/config", exist_ok=True)
        if not os.path.isfile(f"{self.project_path}/config/contacts.yaml"):
            with open(f"{self.project_path}/config/contacts.yaml", 'w', encoding='utf-8'):
                contacts = [contact]
        else:
            contacts = self.get_stored_contacts()
            print(contacts)
            contacts.append(contact)

        with open(f"{self.project_path}/config/contacts.yaml", 'w', encoding='utf-8') as f:
            yaml.safe_dump(contacts, f, sort_keys=False)

        return 0
