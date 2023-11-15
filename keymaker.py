from cryptography.fernet import Fernet

key = Fernet.generate_key()
with open("key","wb") as keyFile:
    keyFile.write(key)