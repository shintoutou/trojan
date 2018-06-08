import os

def run(**kwargs) :
    print("[*] In DirLister Module.")
    files = os.listdir(".")
    
    return str(files)