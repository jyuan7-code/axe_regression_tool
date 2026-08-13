
import os
import re
import platform
import subprocess
import time

import libs.utility as Util
from pathlib import Path

class P4Wrapper:
    def __init__(self, userName, isGraphic=False):
        #self.port ="ssl:p4proxy.devtools.intel.com:5110"
        #self.port ="ssl:p4proxy-vpg-sc1.devtools.intel.com:5110"
        self.port ="ssl:fmyperf7111.fm.intel.com:5110"
        #ssl:p4proxy-vpg-sc1.devtools.intel.com:5110
        self.p4_repo_base = "//gen12_fulsim_test_depot/tests"
        self.p4_branches = list()
        if isGraphic:
            self.p4_repo_base = "//genGraphics/validation/tests"
            self.p4_branches = ["branches","Compute_dev","Content_DevBranch","dev","DG2_ReleaseBranch","display_gen10","display_gen11","Gen12LP_ReleaseBranch",
                                "Gen8_MaintenanceBranch","Gen9_MaintenanceBranch","KBL_ReleaseBranch","MTL_ARL_ReleaseBranch","PerfXe_Main",
                                "PerfXe_MTL","PerfXe_PVC","PVC_A-Step_ReleaseBranch","PVC_ReleaseBranch","Xe2_ReleaseBranch","Xe3_ReleaseBranch"]

        self.p4_unit_list = list()
        self.utility = Util.Utility()
        self.user_name = userName
        self.windows_password = ""

        if re.search("windows", platform.system(), re.IGNORECASE):
            self.is_win_os = True
            self.p4_exe = 'p4'
            #set up port
            # set up user
            #set up password
            #p4 set P4USER=jyuan7
            #p4 set P4PORT=ssl:p4proxy-vpg-sc1.devtools.intel.com:5110
            #p4 set P4PASSWD=best6one^

        else:
            self.is_win_os = False
            #self.p4_exe = '/usr/intel/pkgs/p4/2019.1/bin/p4'
            self.p4_exe = '/usr/intel/pkgs/p4/2023.1/bin/p4'
    def getPassWord(self, passWord):
        self.windows_password = passWord
        #print("p4 windows password:", self.windows_password)
    def checkWindowsPassWordInlinux(self, passWord):
        self.getPassWord(passWord)
        self.setEnvirement()
        good_password = True
        cmd = self.p4_exe + " " + "info"
        print("run cmd: ", cmd)
        result = os.popen(cmd)
        lines = result.readlines()
        result.close()
        print("len", len(lines))
        for line in lines:
            print("p4 info:", line)
            if str(line).find("Connect to server failed") != -1:

                good_password =False
                break
        print("good password: ", good_password)
        return good_password

    def setEnvirement(self):
        # set up user
        print("Setting P4 ...")
        cmd = self.p4_exe + " set P4USER=" + str(self.user_name)
        print(cmd)
        result = os.popen(cmd)
        result.close()
        #set up port
        cmd = self.p4_exe + " set P4PORT=" + str(self.port)
        print(cmd)
        result = os.popen(cmd)
        result.close()


    def getUnitList(self):
        if len(self.p4_unit_list) == 0:
            #cmd = self.p4_exe + " -u "  + self.user_name  + " -p " + self.port + " dirs " + '"' + self.p4_repo_base  +"/*" + '"'
            cmd = self.p4_exe + " dirs " + '"' + self.p4_repo_base  +"/*" + '"'
            print("cmd: ", cmd)
            result = os.popen(cmd)
            lines = result.readlines()
            result.close()
            for line in lines:
                unit_name = str(line).replace(self.p4_repo_base,"")
                unit_name = unit_name.replace("/","")
                unit_name = unit_name.strip()
                #print(unit_name)
                self.p4_unit_list.append(unit_name)
        return self.p4_unit_list

    def checkName(self,name):
        dir_name = os.path.dirname(name)
        base_name = os.path.basename(name)
        if dir_name != '':
            cmd = self.p4_exe + " dirs " + '"' + self.p4_repo_base  +"/" + dir_name + "/*" + '"'
        else:
            cmd = self.p4_exe + " dirs " + '"' + self.p4_repo_base  + "/*" + '"'

        print("cmd: ", cmd)
        result = os.popen(cmd)
        lines = result.readlines()
        result.close()
        has_name = False
        for line in lines:
            if base_name in line:
                has_name = True
                break
        return has_name


    def isValidUnit(self,unitName):
        print("P4 checking if", unitName, "isvalid ...",end="")
        #cmd = self.p4_exe  + " -u "  + self.user_name + " -p " + self.port + " dirs " + '"' + self.p4_repo_base + "/"  +unitName + '"'

        cmd = self.p4_exe  + " dirs " + '"' + self.p4_repo_base + "/"  +unitName + '"'
        result = os.popen(cmd)
        print("cmd: ", cmd)
        lines = result.readlines()
        result.close()
        valid = True
        for line in lines:
            if str(line).find("no such") != -1:
                valid = False
        print(str(valid))
        return valid

    def fileExist(self, fileP4Path):
        print("P4 checking if", fileP4Path, "exists ...")
        # cmd = self.p4_exe  + " -u "  + self.user_name + " -p " + self.port + " dirs " + '"' + self.p4_repo_base + "/"  +unitName + '"'
        fileP4Path = str(fileP4Path).replace("#","%23")
        cmd = self.p4_exe + " dirs " + '"' + fileP4Path + '"'
        result = os.popen(cmd)
        print("cmd: ", cmd)
        lines = result.readlines()
        result.close()
        valid = True
        if len(lines) < 1:
            valid = False
        else:
            for line in lines:
                if str(line).find("no such") != -1:
                    valid = False
        print(str(valid))
        return valid

    def isValidUnitGold(self,unitName):
        print("P4 checking if", unitName, "gold is valid ...",end="")
        #cmd = self.p4_exe  + " -u "  + self.user_name + " -p " + self.port + " dirs " + '"' + self.p4_repo_base + "/"  +unitName + "/gold"  +'"'
        cmd = self.p4_exe  + " dirs " + '"' + self.p4_repo_base + "/"  +unitName + "/gold"  +'"'
        print("cmd: ", cmd)
        result = os.popen(cmd)
        lines = result.readlines()
        result.close()
        valid = True
        for line in lines:
            if str(line).find("no such") != -1:
                valid = False
        print(str(valid))
        return valid

    def isValidUnitTest(self,unitName, relativePath):
        print("P4 checking if", unitName, "/"+ str(relativePath), "is valid ...",end="")
        #cmd = self.p4_exe  + " -u "  + self.user_name + " -p " + self.port + " dirs " + '"' + self.p4_repo_base + "/"  +unitName + "/" + str(relativePath)   +'"'
        cmd = self.p4_exe  + " dirs " + '"' + self.p4_repo_base + "/"  +unitName + "/" + str(relativePath)   +'"'
        print(cmd)
        result = os.popen(cmd)
        lines = result.readlines()
        result.close()

        valid = True
        for line in lines:
            if str(line).find("no such") != -1:
                valid = False
        print(str(valid))
        return valid

    def copyOneFile(self, p4_file_path, targetPath, revision=0):
        test_revision = ""
        if revision!=0 and revision!='0':
            test_revision = "@" + str(revision).strip()
        file_name = os.path.basename(p4_file_path)
        print()
        print("P4 copying", p4_file_path, " tests to", targetPath, test_revision, "...")

        p4_path = '"' + p4_file_path +  test_revision + '"'
        targetPath = '"'+ str(targetPath) + "/" + file_name + '"'
        cmd = self.p4_exe  + " print -o " +" " + targetPath +" -k " +   p4_path
        cmd = cmd.replace("\\","/")

        print(cmd,end="")

        #result = subprocess.call(cmd)
        result = os.popen(cmd)
        result.close()

        print(" ==>done ")
        return cmd
    def createRepopath(self,folderPath, targetPath,revision):
        print("P4 createRepopath start ...")
        repopath = os.path.join(targetPath, "repopath.txt")
        with open(repopath, 'w') as f:
            fPath = str(folderPath).replace("\\", "/")
            p4path = "P4PATH=\"" + str(self.port) + fPath
            if (revision != 0 and revision != '0'):
                p4path = p4path + "@" + str(revision)
            p4path = p4path + "\""
            print("write to repopath.txt: " + p4path)
            f.write(p4path)

    def copyOnefolder(self, folderPath, targetPath, revision, createRepoPath=False):
        #create repopath.txt
        #e.g P4PATH="ssl:p4proxy-vpg-sc1.devtools.intel.com:5110//gen12_fulsim_test_depot/tests/BCS/basic/bcs_vfumd_regaccess_lrr@335631"
        os.makedirs(targetPath, exist_ok=True)

        info =""
        #print("self.is_win_os:", self.is_win_os)
        if not  Path(str(targetPath)).is_dir():
            Path(str(targetPath)).mkdir(parents=True, exist_ok=True)
        folderPath = str(folderPath).replace("#", "%23")
        test_revision = ""

        if revision!=0 and revision!='0':
            test_revision = "@" + str(revision).strip()

        p4_path = '"' + str(os.path.join(folderPath, "..."))  + test_revision + '"'

        p4targetPath = '"'+ str(os.path.join(targetPath, "..."))  + '"'
        cmd = self.p4_exe  + " print -o " +" " + p4targetPath +" -k " +   p4_path
        cmd = cmd.replace("\\","/")
        print("P4 cmd:", cmd)
        #print(cmd,end="")
        info = str(cmd)

        #result = subprocess.call(cmd)
        result = os.popen(cmd)
        result.close()
        self.replace_encoded_hash_in_filenames(targetPath)
        #print(" ==>done ")
        info = info + (" ==>done ")
        return info

    def copyOtherTestFiles(self, folderPath, targetPath, revision=0):
        test_revision = ""
        if revision != 0 and revision != '0':
            test_revision = "@" + str(revision).strip()

        p4_path = '"' + str(os.path.join(folderPath, "*")) + test_revision + '"'
        cmd = self.p4_exe + " files " + p4_path
        cmd = cmd.replace("\\", "/")
        print(cmd, end="")
        result = os.popen(cmd)
        alllines = result.readlines()
        result.close()
        for line in alllines:
            search_result =  re.search(r"(.+)#", str(line))
            if search_result:
                src_file = search_result.group(1)
                if Path(src_file).suffix == '.gsf' or  Path(src_file).suffix == '.yaml' :  #testfile
                    continue
                else:
                    self.copyOneFile(src_file,targetPath,revision)
            else:
                print("get nothing!")


    def copyUnitFolder(self, unitName, targetPath, revision=0):
        path = os.path.join(targetPath,unitName)
        if revision == 0 or revision == '0':
            test_revision = ""
        else:
            test_revision = "@" + str(revision).strip()

        if  self.utility.IsDirEmpty(path) and  self.isValidUnit(unitName):
            print("P4 copying", unitName, " tests to", "...",end="")
            #cmd = self.p4_exe  + " -u "  + self.user_name +  " -p " + self.port + " print -o " + '"'+ str(targetPath) + "/" + unitName + "/..." + '"'+" " + '"' + self.p4_repo_base + "/"  +unitName +  "/..." + '"'
            cmd = self.p4_exe  + " print -o " + '"'+ str(targetPath) + "/" + unitName + "/..." + '"'+" " + '-k "' + self.p4_repo_base + "/"  +unitName +  "/..."  + test_revision + '"'
            cmd = cmd.replace("\\","/")

            print(cmd)

            #result = subprocess.call(cmd)
            result = os.popen(cmd)
            result.close()
            self.replace_encoded_hash_in_filenames(path)
        print(" ==>done ")

    def copyOneTestWithTwoTry(self,unitName, testRlativePath, targetPath, revision=0, byforce=False):
        copy_sucess = self.copyOneTest(unitName, testRlativePath, targetPath, revision, byforce)
        if not copy_sucess:
            time.sleep(0.05)
            copy_sucess = self.copyOneTest(unitName, testRlativePath, targetPath, revision, byforce)
        if copy_sucess:
            print("==> Sucess")
        else:
            print("==> Failed")
        return copy_sucess

    def copyOneTest(self,unitName, testRlativePath, targetPath, revision=0, byforce=False):
        path = os.path.join(targetPath,unitName)
        path = os.path.join(path,testRlativePath)
        path = str(path).replace("\\", "/")
        copy_success = False

        if revision == 0 or revision == '0' :
            test_revision = ""
        else:
            test_revision = "@" + str(revision).strip()

        force_copy = self.utility.IsDirEmpty(path) and self.isValidUnitTest(unitName, testRlativePath)
        if byforce:
            force_copy = True

        if force_copy:
            #print("P4 copying", unitName,"/", targetPath, "...",end="")
            #cmd = self.p4_exe + " -u "  + self.user_name + " -p " + self.port + " print -o " + '"'+ str(targetPath) + "/" + unitName + "/" +  str(testRlativePath) + "/..." + '"'+" " \
             # + '"' + self.p4_repo_base + "/"  +unitName + "/" +  str(testRlativePath) +  "/..." + '"'
            cmd = self.p4_exe + " print -o " + '"'+ str(targetPath) + "/" + unitName + "/" +  str(testRlativePath) + "/..."  + '"'+" " \
                  + '-k "' + self.p4_repo_base + "/"  +unitName + "/" +  str(testRlativePath) +  "/..." + test_revision + '"'

            cmd = cmd.replace("\\","/")
            print(cmd)
            #result = subprocess.call(cmd)
            result = os.popen(cmd)
            for line in result:
                if str(line).find("edit change") != -1:
                    copy_success = True
            if copy_success:
                #check if subfolder name has "%23" and replace it with #
                test_folder_path = str(targetPath) + "/" + unitName + "/" +  str(testRlativePath)
                all_subfolder_paths = self.utility.GetAllFilePathsFromDir(test_folder_path)
                for folder_path in all_subfolder_paths:
                    base_name = os.path.basename(folder_path)
                    dir_path = os.path.dirname(folder_path)
                    if str(base_name).find("%23") != -1: #found
                        new_name = base_name.replace("%23", "#")
                        new_path = os.path.join(dir_path, new_name)
                        os.rename(folder_path,new_path)


            #with open(file_path, 'w') as f:
                #for line in result:
                    #f.write(line)
            result.close()
            print(" ==>done: ")

            return  copy_success
        else:
            return True
    def getUnitTestList(self, unitName):
        #cmd = self.p4_exe + " -u "  + self.user_name + " -p " + self.port + " dirs " + '"' + self.p4_repo_base + "/"  +unitName + "/basic" + "/*" + '"'
        cmd = self.p4_exe  + " dirs " + '"' + self.p4_repo_base + "/"  +unitName + "/basic" + "/*" + '"'

        print("cmd: ", cmd)
        result = os.popen(cmd)
        lines = result.readlines()
        result.close()
        json_test_list = list()
        for line in lines:
            test = str(line).replace(self.p4_repo_base,"")
            test = test.replace("^/","")
            test = test.strip()
            print("test:", test)
            json_test_list.append(test)

        return json_test_list

    def replace_encoded_hash_in_filenames(self,root_dir):
         """
         Traverse the directory tree starting at root_dir, and replace '%23' with '#' in both file and folder names.

             :param root_dir: The root directory from which to start the search.
             """
         for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
             # Rename files
             for filename in filenames:
                 if '%23' in filename:
                     new_filename = filename.replace('%23', '#')
                     old_filepath = os.path.join(dirpath, filename)
                     new_filepath = os.path.join(dirpath, new_filename)

                     try:
                         os.rename(old_filepath, new_filepath)
                         print(f'Renamed file: {old_filepath} -> {new_filepath}')
                     except Exception as e:
                         print(f'Error renaming file {old_filepath}: {e}')

             # Rename directories
             for dirname in dirnames:
                 if '%23' in dirname:
                     new_dirname = dirname.replace('%23', '#')
                     old_dirpath = os.path.join(dirpath, dirname)
                     new_dirpath = os.path.join(dirpath, new_dirname)

                     try:
                         os.rename(old_dirpath, new_dirpath)
                         print(f'Renamed directory: {old_dirpath} -> {new_dirpath}')
                     except Exception as e:
                         print(f'Error renaming directory {old_dirpath}: {e}')
