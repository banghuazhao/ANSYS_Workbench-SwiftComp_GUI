import os
import shutil

import utilities
import sg_filesystem

# add this block for message box
import clr
clr.AddReference("Ans.UI.Toolkit")
clr.AddReference("Ans.UI.Toolkit.Base")
import Ansys.UI.Toolkit



def noSwiftCompExe(ExtAPI):
    '''check whether there is no SwiftComp executable. if no, return True'''

    def which(program):
        def is_exe(fpath):
            return os.path.isfile(fpath)
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return True
        return False

    if not which("SwiftComp.exe"):
        message = "\n".join([
                  "Can't find SwiftComp.exe!",
                  "Please go to https://analyswift.com/software-trial/ to request SwiftComp from AnalySwift LLC.",
                  "Then follow the Installation Manual to install SwiftComp in your local machine."])
        Ansys.UI.Toolkit.MessageBox.Show(message)
        return True

    return False


def homNotSuccessful(ExtAPI, sc_hom_stdout):
    '''Check whether the homogenization is not successful or not. If not, return True'''

    SGFileSystem = sg_filesystem.SGFileSystem(ExtAPI)

    user_dir_files = os.listdir(SGFileSystem.user_dir)

    # check license issue
    if 'license' in sc_hom_stdout.split():
        message = "\n".join([
                  "Cannot open license file!",
                  "Please check the ouput:",
                  sc_hom_stdout])
        Ansys.UI.Toolkit.MessageBox.Show(message)
        return True

    # Check success. if no successfully!, error
    if 'successfully!' not in sc_hom_stdout.split():
        message = "\n".join([
                  "Homogenization failed!",
                  "Please check the ouput:",
                  sc_hom_stdout])
        Ansys.UI.Toolkit.MessageBox.Show(message)
        return True

    # Check *.k file
    if SGFileSystem.file_name_sc_k in user_dir_files:
        with open(SGFileSystem.dir_file_name_sc_k, 'r') as f:
            k_f = f.read()
        if len(k_f) == 0:  # if *.k is empty, error
            message = "\n".join([
                        "The *.k file is empty!",
                        "Please check the ouput:",
                        sc_hom_stdout])
            Ansys.UI.Toolkit.MessageBox.Show(message)
        return False
    else:  # if no *.k file, error
        message = "\n".join([
                  "Can not find the *.k file!",
                  "Please check the ouput:",
                  sc_hom_stdout])
        Ansys.UI.Toolkit.MessageBox.Show(message)
        return True

    return False


def noSCFile(ExtAPI):
    '''whether there is no *.sc file or not. If no, return True'''

    SGFileSystem = sg_filesystem.SGFileSystem(ExtAPI)

    user_dir_files = os.listdir(SGFileSystem.user_dir)

    # check *.sc file
    if SGFileSystem.file_name_sc in user_dir_files:
        with open(SGFileSystem.dir_file_name_sc) as f:
            u_f = f.read()
        if len(u_f) == 0:  # *.sc file is empty
            message = "\n".join([
                      "The *.sc file is empty!",
                      "Please check and conduct homogenization again!"])
            Ansys.UI.Toolkit.MessageBox.Show(message)
            return True
    else:  # no *.sc file
        message = "\n".join([
                  "Cannot find *.sc file!",
                  "Please check and conduct homogenization again!"])
        Ansys.UI.Toolkit.MessageBox.Show(message)
        return True

    return False


def noKFile(ExtAPI):
    '''whether there is no *.k file or not. If no, return True'''

    SGFileSystem = sg_filesystem.SGFileSystem(ExtAPI)

    user_dir_files = os.listdir(SGFileSystem.user_dir)

    # check *.k file
    if SGFileSystem.file_name_sc_k in user_dir_files:
        with open(SGFileSystem.dir_file_name_sc) as f:
            u_f = f.read()
        if len(u_f) == 0:  # *.k file is empty
            message = "\n".join([
                      "The *.k file is empty!",
                      "Please check and conduct homogenization again!"])
            Ansys.UI.Toolkit.MessageBox.Show(message)
            return True
    else:  # no *.k file
        message = "\n".join([
                  "Cannot find *.k file!",
                  "Please check and conduct homogenization again!"])
        Ansys.UI.Toolkit.MessageBox.Show(message)
        return True

    return False


def dehomNotSuccessful(ExtAPI, sc_dehom_stdout):
    '''Check whether the dehomogenization is not successful or not. If not, return True'''

    SGFileSystem = sg_filesystem.SGFileSystem(ExtAPI)

    user_dir_files = os.listdir(SGFileSystem.user_dir)

    # Check success
    if 'successfully!' not in sc_dehom_stdout.split():  # dehomogenization failed!
        message = "\n".join([
                  "Dehomogenization failed!",
                  "Please check the output:",
                  sc_dehom_stdout])
        Ansys.UI.Toolkit.MessageBox.Show(message)
        return True

    # Check *.u file
    if SGFileSystem.file_name_sc_u in user_dir_files:
        with open(SGFileSystem.dir_file_name_sc_u) as f:
            u_f = f.read()

        if len(u_f) == 0:  # *.u file is empty
            message = "\n".join([
                      "The *.u file is empty!",
                      "Please check the output:",
                      sc_dehom_stdout])
            Ansys.UI.Toolkit.MessageBox.Show(message)
            return True
    else:  # no *.u file
        message = "\n".join([
                  "Cannot find the *.u file!",
                  "Please check the output:",
                  sc_dehom_stdout])
        Ansys.UI.Toolkit.MessageBox.Show(message)
        return True

    # Check *.sn file
    if SGFileSystem.file_name_sc_sn in user_dir_files:
        with open(SGFileSystem.dir_file_name_sc_u) as f:
            u_sn = f.read()

        if len(u_sn) == 0:  # *.sn file is empty
            message = "\n".join([
                      "The *.sn file is empty!",
                      "Please check the output:",
                      sc_dehom_stdout])
            Ansys.UI.Toolkit.MessageBox.Show(message)
            return True
    else:  # no *.sn file
        message = "\n".join([
                  "Cannot find the *.sn file!",
                  "Please check the output:",
                  sc_dehom_stdout])
        Ansys.UI.Toolkit.MessageBox.Show(message)
        return True

    return False


# Check *.u and *.sn file
def noUSNFile(ExtAPI):
    '''Check whether there are *.u and *.sn files. If not, return True'''

    SGFileSystem = sg_filesystem.SGFileSystem(ExtAPI)

    user_dir_files = os.listdir(SGFileSystem.user_dir)

    # Check *.u file
    if SGFileSystem.file_name_sc_u in user_dir_files:
        u_f = open(SGFileSystem.dir_file_name_sc_u).read()
        if len(u_f) == 0:  # *.u file is empty
            message = "\n".join([
                      "The *.u file is empty!",
                      "Please check and conduct dehomogenization again!"])
            Ansys.UI.Toolkit.MessageBox.Show(message)
            return False
    else:  # no *.u file
        message = "\n".join([
                  "Can not find the *.u file!",
                  "Please check and conduct dehomogenization again!"])
        Ansys.UI.Toolkit.MessageBox.Show(message)
        return False

    # Check *.sn file
    if SGFileSystem.file_name_sc_sn in user_dir_files:
        u_sn = open(SGFileSystem.dir_file_name_sc_sn).read()
        if len(u_sn) == 0:  # *.sn file is empty
            message = "\n".join([
                      "The *.sn file is empty!",
                      "Please check and conduct dehomogenization again!"])
            Ansys.UI.Toolkit.MessageBox.Show(message)
            return False
    else:  # no *.sn file
        message = "\n".join([
                  "Can not find the *.sn file!",
                  "Please check and conduct dehomogenization again!"])
        Ansys.UI.Toolkit.MessageBox.Show(message)
        return False

    return True


def failureNotSuccessful(ExtAPI, sc_failure_stdout):
    '''Check whether the failure analysis is not successful or not. If not, return True'''

    SGFileSystem = sg_filesystem.SGFileSystem(ExtAPI)

    user_dir_files = os.listdir(SGFileSystem.user_dir)

    # check license issue
    if 'license' in sc_failure_stdout.split():
        message = "\n".join([
                  "Cannot open license file!",
                  "Please check the ouput:",
                  sc_failure_stdout])
        Ansys.UI.Toolkit.MessageBox.Show(message)
        return True

    # Check success. if no successfully!, error
    if 'successfully!' not in sc_failure_stdout.split():
        message = "\n".join([
                  "Failure Analysis failed!",
                  "Please check the ouput:",
                  sc_failure_stdout])
        Ansys.UI.Toolkit.MessageBox.Show(message)
        return True

    return False
