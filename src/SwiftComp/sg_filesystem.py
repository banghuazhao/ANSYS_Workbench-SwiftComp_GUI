class SGFileSystem(object):
    """SG File System class. store the directory and file name

    Attributes:
    work_dir: Where the solve.out file locate
    user_dir: Where the project_file locate
    file_name, file_name_sc, file_name_sc_k, file_name_sc_glb, 
    file_name_sc_u, file_name_sc_sn, file_name_sc_fi: filenames
    """
    def __init__(self, ExtAPI):
        self.work_dir = ''
        self.user_dir = ''
        self.file_name = ''
        self.file_name_sc = ''
        self.file_name_sc_k = ''
        self.file_name_sc_glb = ''
        self.file_name_sc_u = ''
        self.file_name_sc_sn = ''
        self.file_name_sc_fi = ''
        self.file_name_msh = ''
        self.file_name_geo = ''

        self.getDirectory(ExtAPI)
        self.getFileName()

        self.dir_file_name        = self.user_dir + self.file_name
        self.dir_file_name_sc     = self.user_dir + self.file_name_sc
        self.dir_file_name_sc_k   = self.user_dir + self.file_name_sc_k
        self.dir_file_name_sc_glb = self.user_dir + self.file_name_sc_glb
        self.dir_file_name_sc_u   = self.user_dir + self.file_name_sc_u
        self.dir_file_name_sc_sn  = self.user_dir + self.file_name_sc_sn
        self.dir_file_name_sc_fi  = self.user_dir + self.file_name_sc_fi
        self.dir_file_name_msh    = self.user_dir + self.file_name_msh
        self.dir_file_name_geo    = self.user_dir + self.file_name_geo

    def getDirectory(self, ExtAPI):
        '''Get various directory'''
        # Working directory. There are  2 possibilities:
        # 1:
        # Default: C:\Users\...\AppData\Local\Temp\...\unsaved_project_files\dp0\SYS\MECH\
        # User: ...\file_name\file_name_files_dp0\SYS\MECH\
        # 2:
        # Default: C:\Users\...\AppData\Local\Temp\...\unsaved_project_files\_ProjectScrath\ScrB9C8\
        # User: ...\file_name\_ProjectScrath\ScrB9C8\
        self.work_dir = ExtAPI.DataModel.Project.Model.Analyses[0].WorkingDir

        # Find folder directiory
        work_dir_arr = self.work_dir.split('\\')
        work_dir_len = len(work_dir_arr)

        # 1:
        # Default: ['C:', 'Users', '...', 'AppData', 'Local', 'Temp', '...', 'file_name', 'unsaved_project_files', 'dp0', 'SYS', 'MECH']
        # User: ['...', 'file_name', 'file_name_files', 'dp0', 'SYS', 'MECH']
        # 2:
        # Default: ['C:', 'Users', '...', 'AppData', 'Local', 'Temp', '...', 'file_name', '_ProjectScrath', 'ScrB9C8']
        # User: ['...', 'file_name', '_ProjectScrath', 'ScrB9C8']
        if work_dir_arr[work_dir_len - 2] == 'MECH':  # 1
            self.user_dir = '\\'.join(work_dir_arr[:work_dir_len - 5]) + '\\'
        else:  # 2
            self.user_dir = '\\'.join(work_dir_arr[:work_dir_len - 3]) + '\\'

    def getFileName(self):
        ''' Get various filename'''
        user_dir_len = len(self.user_dir.split('\\'))
        self.file_name = self.user_dir.split('\\')[user_dir_len - 2]
        self.file_name_sc = self.file_name + '.sc'
        self.file_name_sc_k = self.file_name_sc + '.k'
        self.file_name_sc_glb = self.file_name_sc + '.glb'
        self.file_name_sc_u = self.file_name_sc + '.u'
        self.file_name_sc_sn = self.file_name_sc + '.sn'
        self.file_name_sc_fi = self.file_name_sc + '.fi'
        self.file_name_msh = self.file_name + '.msh'
        self.file_name_geo = self.file_name + '.geo'



