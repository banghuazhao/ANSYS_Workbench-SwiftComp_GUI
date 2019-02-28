import os


##############################################################################
# Help Button
##############################################################################

def helpAtToolbar(ag):
    # Display user manual file
    install_dir = ExtAPI.ExtensionManager.CurrentExtension.InstallDir
    os.startfile(install_dir + '\\help\\User_Manual.pdf')
