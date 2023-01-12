import subprocess
from os import system
from util.general import getFiles

def stepSelect(dashboard, opt_id):
    files = getFiles(opt_id)
    
    if files["src_files"] != "0":
        opt_delete_src = input("> Existing symlink to source found! Delete it? (y/n) [n]: ")
        opt_delete_src = "n" if opt_delete_src == "" else opt_delete_src
        if opt_delete_src == "y":
            print("Deleting symlink to source...")
            system(f"rm {dashboard.fileSystem.basePath}/source/{opt_id}")
            files = getFiles(opt_id)
    
    if files["src_files"] == "0":
        opt_sel_method = input("> Show selection method? (local) [local]: ")
        opt_sel_method = "local" if opt_sel_method == "" else opt_sel_method
        if opt_sel_method == "local":
            opt_sel_src = subprocess.getoutput("mktemp")
            system(f'ranger --choosedir="{opt_sel_src}" 1>&2')
            opt_sel_src = subprocess.getoutput(f"cat {opt_sel_src}")
            system(f"rm -rf {dashboard.fileSystem.basePath}/source/{opt_id}")
            system(f'ln -sf "{opt_sel_src}" {dashboard.fileSystem.basePath}/source/{opt_id}')
            files = getFiles(opt_id)

    if files["dest_files"] != "0":
        opt_delete_dest = input("> Existing destination files found! Delete them? (y/n) [n]: ")
        opt_delete_dest = "n" if opt_delete_dest == "" else opt_delete_dest
        if opt_delete_dest == "y":
            print("Deleting destination files...")
            system(f"rm -rf {dashboard.fileSystem.basePath}/processed/{opt_id}/*")
            files = getFiles(opt_id)