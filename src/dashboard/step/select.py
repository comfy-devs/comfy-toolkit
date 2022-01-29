import subprocess
from os import system
from util import getColor, getFiles

def stepSelect():
    system("clear")
    print(f'{getColor("gray")}Nyan Anime Toolkit - Select{getColor("reset")}')
    opt_id = input("> Anime ID? (ID from anilist.co): ")
    files = getFiles(opt_id)
    
    if files.get("src_files") != "0":
        opt_delete_src = input("> Existing source files found! Delete them? (y/n) [n]: ")
        opt_delete_src = "n" if opt_delete_src == "" else opt_delete_src
        if opt_delete_src == "y":
            print("Deleting source files...")
            system(f"rm -rf /usr/src/nyananime/src-episodes/{opt_id}/*")
            files = getFiles(opt_id)
    
    if files.get("src_files") == "0":
        opt_sel_method = input("> Anime selection method? (local) [local]: ")
        opt_sel_method = "local" if opt_sel_method == "" else opt_sel_method
        if opt_sel_method == "local":
            opt_sel_src = subprocess.getoutput("mktemp")
            system(f'ranger --choosedir="{src}" 1>&2')
            opt_sel_src = subprocess.getoutput(f"cat {src}")
            system(f"rm -rf /usr/src/nyananime/src-episodes/{opt_id}")
            system(f'ln -sf "{src}" /usr/src/nyananime/src-episodes/{opt_id}')
            files = getFiles(opt_id)

    if files.get("dest_files") != "0":
        opt_delete_dest = input("> Existing destination files found! Delete them? (y/n) [n]: ")
        opt_delete_dest = "n" if opt_delete_dest == "" else opt_delete_dest
        if opt_delete_dest == "y":
            print("Deleting destination files...")
            system(f"rm -rf /usr/src/nyananime/dest-episodes/{opt_id}/*")
            files = getFiles(opt_id)