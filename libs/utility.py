import shutil
#import distutils.dir_util
import os
import stat
from pathlib import Path
import re
import libs.test as Test
import libs.HTML as HTML
#import HTML
import csv
import platform
#from os import walk
import subprocess
import libs.executionSetting  as AxeExecution
import textwrap
class Utility:
    def __init__(self):
        self.is_win_os = False
        if re.search("windows", platform.system(), re.IGNORECASE):
            self.is_win_os = True
    def deleteOneFolder(self, dirPath):
        try:
            shutil.rmtree(dirPath)
        except OSError as e:
            print("Error: %s - %s." % (e.filename, e.strerror))

    def change_permissions_recursive(self, path, mode):
        for root, dirs, files in os.walk(path, topdown=False):
            for dir in [os.path.join(root, d) for d in dirs]:
                os.chmod(dir, mode)
        for file in [os.path.join(root, f) for f in files]:
            os.chmod(file, mode)

    def IsDirEmpty(self,dirPath):
        is_empty = True
        if os.path.exists(dirPath):
           all_file_paths = self.GetAllFilePathsFromDir(dirPath)
           for file_path in all_file_paths:
               if Path(file_path).is_file():
                   is_empty = False
        else:
            is_empty =  True

        return is_empty

    def copyOneFile(self, filePath, destDir):
        filePath = str(filePath)
        if not Path(filePath).is_file():
            return
        try:
            shutil.copy(filePath, destDir)
        except shutil.SameFileError:
            pass  # Same file, skip silently
        except Exception as e:
            print(f"Copy failed: {e}")  # Optional: log the error

    def CopyMultifiles(self, src_paths:list, dst_path):
        for file_path in src_paths:
            self.copyOneFile(file_path, dst_path)

    def CopyOneFolderByfiles(self, src_path, dst_path, file_only=False):
        if not Path(src_path).is_dir():
            print("==> skipped, folder dose not exist")
            return

        all_files = os.listdir(Path(src_path))

        Path(dst_path).mkdir(parents=True, exist_ok=True)
        for file_name  in all_files:
            file_path = Path(os.path.join(src_path, os.path.basename(file_name)))
            if Path(file_path).is_dir():
                if file_only:
                    continue
                else:
                    new_dst_path = Path(os.path.join(dst_path, os.path.basename(file_name)))
                    self.CopyOneFolderByfiles(file_path,new_dst_path)
            else:
                dst_file_path =  Path(os.path.join(dst_path, file_name))
                if not dst_file_path.is_file():
                   self.copyOneFile(file_path, dst_path)
    def CopyOneFolderByFileRecursively(self,source_folder, destination_folder):
        # Check if the destination folder exists; if not, create it
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)

        # Walk through the source folder
        for root, dirs, files in os.walk(source_folder):
            # For each file in files
            for file in files:
                # Construct the full file path
                file_path = os.path.join(root, file)
                # Construct the destination file path
                destination_file_path = os.path.join(destination_folder, os.path.relpath(file_path, source_folder))
                # Make sure the destination subfolder exists; if not, create it
                destination_subfolder = os.path.dirname(destination_file_path)
                if not os.path.exists(destination_subfolder):
                    os.makedirs(destination_subfolder)
                # Copy the file
                shutil.copy2(file_path, destination_file_path)

    def copyOtherTestFiles(self, src_path, dst_path):
        if not Path(src_path).is_dir():
            print("==> skipped, folder dose not exist")
            return

        all_files = os.listdir(Path(src_path))

        Path(dst_path).mkdir(parents=True, exist_ok=True)
        for file_name  in all_files:
            file_path = Path(os.path.join(src_path, os.path.basename(file_name)))
            if Path(file_path).is_dir():
               continue
            else:
                dst_file_path =  Path(os.path.join(dst_path, file_name))
                if not dst_file_path.is_file():
                    if Path(file_path).suffix == '.gsf' or Path(file_path).suffix == '.yaml':  # testfile
                        continue
                    else:
                        self.copyOneFile(file_path, dst_path)

    def CopyOneFolder(self, src_path, dst_path): #include folders and unit folder
        #dest_path = os.path.normpath(dst_path)
        #est_path = Path(dest_path)
        #dest_path.mkdir(parents=True, exist_ok=True)
        #print("src_path:", src_path)
        #print("dest_path:", dest_path)
        os.makedirs(Path(dst_path), exist_ok=True)
        self.set_permissions(Path(dst_path))
        # print("copying: ", src_path, "to", dst_path)
        try:
            shutil.copytree(src_path, dst_path)
        except:
            print("copy failed, trying another way " + str(src_path))
            folder_name = os.path.basename(src_path)
            dst_path = os.path.join(dst_path,folder_name)
            try:
                self.CopyOneFolderByFileRecursively(src_path, dst_path)
            except:
                print("file exist  " + str(src_path))
        self.set_permissions(Path(dst_path))
        return

    def GetFolderPathsFromDir(self, dirPath):
        all = os.listdir(dirPath)
        all_file_paths = list()
        for file in all:
            # Create full path
            full_path = os.path.join(dirPath, file)
            # If entry is a directory then get the list of files in this directory
            if os.path.isdir(full_path):
                all_file_paths.append(full_path)
        return all_file_paths

    def GetAllFilePathsFromDir(self,dirpath):
        all_file_paths = list()
        for root, dirs, files in os.walk(dirpath):
            for fileName in files:
                all_file_paths.append(os.path.join(dirpath,fileName))
                all_file_paths.append(root.replace(str(dirpath) + "\\", "") + os.sep + fileName)
        return all_file_paths
    def GetAllFileRelativePathsFromDir(self,dirpath):
        all_file_relative_paths = list()
        for root, dirs, files in os.walk(dirpath):
            for fileName in files:
                if self.is_win_os:
                    all_file_relative_paths.append(root.replace(str(dirpath) + "\\", "") + os.sep + fileName)
                else:
                    all_file_relative_paths.append(root.replace(str(dirpath) + "/", "") + os.sep + fileName)

        return all_file_relative_paths

    def GetAllFileNamesFromDir(self,dirPath):
        file_name_list = list()
        for (dirpath, dirnames, filenames) in os.walk(dirPath):
            file_name_list.append(filenames)
        return file_name_list

    def GetAllfolderPathsFromDir(self,dirPath):
        folder_paths_list = list()
        for (dirpath, dirnames, filenames) in os.walk(dirPath):
            folder_paths_list.append(dirpath)
        return folder_paths_list

    def hasDataInFile(self, filePath):
        has_data = False
        if self.isTxtFile(filePath):
            if os.path.getsize(filePath) > 0:
                with open(filePath) as f:
                    alllines = f.readlines()
                for line in alllines:
                    line = line.strip()
                    if not line:
                        continue
                    elif re.search("--", line):
                        continue
                    elif re.search("END", line):
                        break
                    else:
                        has_data = True
                        break

            else:
                has_data = False
        else:
            if os.path.getsize(filePath) > 0:
                has_data = True
        return  has_data

    def isTxtFile(self, filePath):
        file_extension =  Path(filePath).suffix
        is_txt_file = False
        if str(filePath).find(".aub") != -1:
            is_txt_file = False

        if file_extension == ".txt" or file_extension == ".xml" or file_extension == ".lst" or file_extension == ".json" or file_extension == ".rb" or  file_extension == ".log" :
            is_txt_file = True
        elif file_extension == ".in" or file_extension == ".out": #dram data
            is_txt_file = True
        elif file_extension == ".sbf":
            is_txt_file = True
        return is_txt_file

    def GetAllFilePathsFromCurrentDir(self,dirPath, depth=0):
        all_file_paths = list()
        if  os.path.isdir(Path(dirPath)):
            all = os.listdir(dirPath)
        else:
            return all_file_paths

        for file in all:
            # Create full path
            full_path = os.path.join(dirPath, file)
            # If entry is a directory then get the list of files in this directory
            if os.path.isdir(full_path):
                if depth > 0:
                    depth = depth -1
                    self.GetAllFilePathsFromCurrentDir(full_path,depth)
                else:
                    pass
            else:
                all_file_paths.append(full_path)
        return all_file_paths

    def DirHasFiles(self, dirPath, depth=0):
        all_file_paths =  self.GetAllFilePathsFromDir(dirPath)
        if len(all_file_paths) > 0:
            return True
        else:
            return False

    def GetAllFilePathsFromDir(self,dirPath):
        all_file_paths = list()
        if not Path(dirPath).is_dir():
            print("invalid Dir path!")
            return all_file_paths
        all = os.listdir(Path(dirPath))

        for file in all:
            # Create full path
            full_path = os.path.join(dirPath, file)
            # If entry is a directory then get the list of files in this directory
            if os.path.isdir(full_path):
                all_file_paths = all_file_paths + self.GetAllFilePathsFromDir(full_path)
            else:
                all_file_paths.append(full_path)
        return all_file_paths

    def findItemInList(self, item, itemList:list):
        found_item = False
        for one_item in itemList:
            if str(os.path.basename(item)).strip() == str(os.path.basename(one_item)).strip():
                found_item = True
                break
        return found_item

    def writeCmodelDataToFile(self,filePath, testRunList):
        with open(filePath, 'w',newline="\n") as f:
            for test_run in testRunList:
                unit_name = test_run.unit_name
                test_name = test_run.test_name
                test_regress_name = unit_name +"/" +  test_name
                #print("test name = ", test_regress_name)
                f.write(test_regress_name + "\n")

    def writeDataToFile(self, filePath, testRunList):
        with open(filePath, 'w',newline="\n") as f:
            for test_run in testRunList:
                jason_name = '"' + test_run.jason_name + '"'
                f.write(jason_name + ",\n")

    def writeDataToCsvFile(self, filePath, testRunList):
        with open(filePath,'w', newline='') as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow(["Test Name","Unit Name", "Virtual Path", "Total Frames", "Grits Run Time(Min)","AubLoad Run Time(Min)", "Mem PeakWorkingSetSize(MB)", "Mem PeakPagefileUsage(MB)"])
            for test_run in testRunList:
                test_name = test_run.test_name
                unit_name = test_run.unit_name
                virtual_path = test_run.test_result.virtual_path
                total_frames =  test_run.test_result.test_total_frame
                grits_runtime = test_run.test_result.grits_runtime
                run_time_mb = test_run.test_result.test_runtime
                PeakWorkingSetSize = test_run.test_result.PeakWorkingSetSize
                PeakPagefileUsage = test_run.test_result.PeakPagefileUsage
                csv_writer.writerow([test_name, unit_name, virtual_path, total_frames,grits_runtime, run_time_mb,PeakWorkingSetSize,PeakPagefileUsage])

    def writeDataToSummaryHtmlFile(self, title, filePath, resultList, runTime,regressSetting:AxeExecution.RegressSetting=None, axeExecutioncConfig:AxeExecution.ExecutionMethod=None):
        header = '<h1 align="center">' + title + '</h1>'
        total_time = 0
        for result in resultList:
            total_time = total_time + result.regress_time
        runTime = total_time
        total_time_header = '<h2 align="center">' + "Total Run Time: " + str(self.convertSecToHourMinSec(runTime))+ '</h2>'
        if regressSetting !=None:
            summary_tile = regressSetting.name
            summary_header = '<h3 align="left">' + summary_tile + '</h3>'
            summary_table = HTML.Table(
                header_row=['Unit/List/Test Names', 'Total Tests', 'Pass Tests', 'Pass Rates', 'Fail Tests',
                            'Invalid Tests', 'Regress Time'])  # ,  'Report Links'])

        summary_tile = "Summary"
        summary_header = '<h3 align="left">' + summary_tile + '</h3>'
        summary_table = HTML.Table(header_row=['Unit/List/Test Names', 'Total Tests', 'Pass Tests', 'Pass Rates', 'Fail Tests',  'Invalid Tests', 'Regress Time']) #,  'Report Links'])
        overall = "Overall"
        overall_total = 0
        overall_pass = 0
        overall_fail = 0
        overall_invalid = 0
        #overall_goldnize = 0 maybe need it
        for result in resultList:
            unit_name = result.unit_name
            unit_name_cell = HTML.TableCell(unit_name, bgcolor="white", attribs={'align': 'left'})
            total_num = str(result.total_num)
            overall_total = overall_total + result.total_num
            total_num_cell = HTML.TableCell(total_num, bgcolor="white", attribs={'align': 'right'})
            pass_num = str(result.pass_num)
            overall_pass = overall_pass + result.pass_num
            pass_num_cell = HTML.TableCell(pass_num, bgcolor="lime", attribs={'align': 'right'})
            pass_rate = str(result.pass_rate)
            pass_rate_cell = HTML.TableCell(pass_rate, bgcolor="lime", attribs={'align': 'right'})
            fail_num = str(result.fail_num)
            overall_fail = overall_fail + result.fail_num
            fail_num_cell = HTML.TableCell(fail_num, bgcolor="red", attribs={'align': 'right'})
            invalid_num = str(result.invalid_num)
            overall_invalid = overall_invalid + result.invalid_num
            invalid_num_cell = HTML.TableCell(invalid_num, bgcolor="yellow", attribs={'align': 'right'})
            regress_time = self.convertSecToHourMinSec(result.regress_time)
            regress_time_cell = HTML.TableCell(regress_time, bgcolor="white", attribs={'align': 'right'})
            #html_report_path = result.html_report_path
            #html_report_path_cell = HTML.TableCell(html_report_path, bgcolor="white", attribs={'align': 'left'})
            summary_table.rows.append([unit_name_cell, total_num_cell, pass_num_cell,pass_rate_cell,fail_num_cell,invalid_num_cell, regress_time_cell]) #,html_report_path_cell])

        overall_cell = HTML.TableCell(overall, bgcolor="white", attribs={'align': 'center'})
        overall_total_cell = HTML.TableCell(str(overall_total), bgcolor="white", attribs={'align': 'right'})
        overall_pass_cell = HTML.TableCell(str(overall_pass), bgcolor="lime", attribs={'align': 'right'})
        if overall_total != 0:
            overall_pass_rate = '{:.2f} %'.format((float(overall_pass) / float(overall_total)) * 100)
        else:
            overall_pass_rate = 0
        overall_pass_rate_cell = HTML.TableCell(str(overall_pass_rate), bgcolor="lime", attribs={'align': 'right'})
        overall_fail_cell = HTML.TableCell(str(overall_fail), bgcolor="red", attribs={'align': 'right'})
        overall_invalid_cell = HTML.TableCell(str(overall_invalid), bgcolor="yellow", attribs={'align': 'right'})
        overall_regress_time = runTime
        overall_regress_time_cell = HTML.TableCell(str(self.convertSecToHourMinSec(overall_regress_time)), bgcolor="white", attribs={'align': 'right'})
        overall_report_path = filePath
        overall_html_report_path_cell = HTML.TableCell(overall_report_path, bgcolor="white", attribs={'align': 'left'})
        summary_table.rows.append(
            [overall_cell, overall_total_cell, overall_pass_cell, overall_pass_rate_cell, overall_fail_cell, overall_invalid_cell, overall_regress_time_cell])#,overall_html_report_path_cell])

        summary__htmlcode = str(summary_table)

        with open(filePath, 'w') as f:
            f.write(header)
            f.write('<br>')
            f.write(total_time_header)
            f.write(summary_header)
            f.write(summary__htmlcode)

    def hasGoldnizedData(self, testlist):
        results = [False, 0]
        results[0] = False
        results[1] = 0
        for testrun in testlist:
            if testrun.run_gold== "yes":
                results[0] = True
                if testrun.goldnize_status == "SUCCESS":
                    results[1] = results[1] + 1


        return results

    def writeDataNaxeConfigToHtmlFile(self, title, filePath, summary, testDoneList, cmodel=False, isgraphic=False,
                            regressSetting:AxeExecution.RegressSetting=None, axeExecutioncConfiglist:list=None):
        webhead = '<head> <meta http-equiv="refresh" content="10"> </head>'
        header = '<h1 align="center">' + title + '</h1>'
        total_time = summary["regress_time"]
        total_time_string = self.convertSecToHourMinSec(total_time)
        total_time_header = '<h2 align="center">' + "Total Run Time: " + total_time_string + '</h2>'
        lines_space = 5
        gold_result = self.hasGoldnizedData(testDoneList)
        has_gold = gold_result[0]
        total_gold_nized = gold_result[1]
        is_cmodel = cmodel
        is_graphic = isgraphic
        # regress  seetings
        num_of_axe_configs = len(axeExecutioncConfiglist)
        need_axeconfig_col = False
        if num_of_axe_configs > 1:
            need_axeconfig_col = True
        if regressSetting != None:
            regress_tile = regressSetting.name
            regress_header = '<h3 align="left">' + regress_tile + '</h3>'
            regress_table = HTML.Table()

            regress_aubload_path_name = "Aubload Path: "
            regress_aubload_path_name_cell = HTML.TableCell(str(regress_aubload_path_name), attribs={'align': 'right'})
            regress_aubload_path = regressSetting.aubload_path
            regress_aubload_path_cell = HTML.TableCell(str(regress_aubload_path), attribs={'align': 'left'})
            regress_table.rows.append([regress_aubload_path_name_cell, regress_aubload_path_cell])

            regress_aubload_option_name = "Aubload Options: "
            regress_aubload_option_name_cell = HTML.TableCell(str(regress_aubload_option_name),
                                                              attribs={'align': 'right'})
            regress_aubload_option = regressSetting.additional_aubload_options
            regress_aubload_option_cell = HTML.TableCell(str(regress_aubload_option), attribs={'align': 'left'})
            regress_table.rows.append([regress_aubload_option_name_cell, regress_aubload_option_cell])

            regress_grits_path_name = "Grits Path: "
            regress_grits_path_name_cell = HTML.TableCell(str(regress_grits_path_name), attribs={'align': 'right'})
            regress_grits_path = regressSetting.grits_path
            regress_grits_path_cell = HTML.TableCell(str(regress_grits_path), attribs={'align': 'left'})
            regress_table.rows.append([regress_grits_path_name_cell, regress_grits_path_cell])

            regress_grits_option_name = "Grits Options: "
            regress_grits_option_name_cell = HTML.TableCell(str(regress_grits_option_name),
                                                            attribs={'align': 'right'})
            regress_grits_option = regressSetting.additional_grits_options
            regress_grits_option_cell = HTML.TableCell(str(regress_grits_option), attribs={'align': 'left'})
            regress_table.rows.append([regress_grits_option_name_cell, regress_grits_option_cell])

            if regressSetting.total_test_list_path !="":
                regress_total_test_name = "Total Test List File Path: "
                regress_total_test_name_cell = HTML.TableCell(str(regress_total_test_name),
                                                                attribs={'align': 'right'})
                regress_total_test = regressSetting.total_test_list_path
                regress_total_test_cell = HTML.TableCell(str(regress_total_test), attribs={'align': 'left'})
                regress_table.rows.append([regress_total_test_name_cell, regress_total_test_cell])

            if regressSetting.pass_test_list_path !="":
                regress_pass_test_name = "Pass Test List File Path: "
                regress_pass_test_name_cell = HTML.TableCell(str(regress_pass_test_name),
                                                                attribs={'align': 'right'})
                regress_pass_test = regressSetting.pass_test_list_path
                regress_pass_test_cell = HTML.TableCell(str(regress_pass_test), attribs={'align': 'left'})
                regress_table.rows.append([regress_pass_test_name_cell, regress_pass_test_cell])

            if regressSetting.fail_test_list_path != "":
                regress_fail_test_name = "Fail Test List File Path: "
                regress_fail_test_name_cell = HTML.TableCell(str(regress_fail_test_name),
                                                             attribs={'align': 'right'})
                regress_fail_test = regressSetting.fail_test_list_path
                regress_fail_test_cell = HTML.TableCell(str(regress_fail_test), attribs={'align': 'left'})
                regress_table.rows.append([regress_fail_test_name_cell, regress_fail_test_cell])

            if regressSetting.testrun_info_path != "":
                regress_testrun_test_name = "Test Run Info: "
                regress_testrun_test_name_cell = HTML.TableCell(str(regress_testrun_test_name),
                                                             attribs={'align': 'right'})
                regress_testrun_test = regressSetting.testrun_info_path
                regress_testrun_test_cell = HTML.TableCell(str(regress_testrun_test), attribs={'align': 'left'})
                regress_table.rows.append([regress_testrun_test_name_cell, regress_testrun_test_cell])


            regress_start_time_name = "Start Time: "
            regress_start_time_name_cell = HTML.TableCell(str(regress_start_time_name), attribs={'align': 'right'})
            regress_start_time = regressSetting.start_time
            regress_start_time_cell = HTML.TableCell(str(regress_start_time), attribs={'align': 'left'})
            regress_table.rows.append([regress_start_time_name_cell, regress_start_time_cell])

            regress_end_time_name = "End Time: "
            regress_end_time_name_cell = HTML.TableCell(str(regress_end_time_name), attribs={'align': 'right'})
            regress_end_time = regressSetting.end_time
            regress_end_time_cell = HTML.TableCell(str(regress_end_time), attribs={'align': 'left'})
            regress_table.rows.append([regress_end_time_name_cell, regress_end_time_cell])
            regress_htmlcode = str(regress_table)
        axe_htmlcode_list = list()
        for  axeExecutioncConfig in axeExecutioncConfiglist:
            axe_tile = axeExecutioncConfig.name
            axe_header = '<h3 align="left">' + 'Cobalt CI Config: ' + axe_tile + '</h3>'
            axe_htmlcode_list.append(axe_header)
            axe_table = HTML.Table()

            axe_exe_type_name = "Axe Execution Type: "
            axe_exe_type_name_cell = HTML.TableCell(str(axe_exe_type_name),
                                                         attribs={'align': 'right'})
            axe_exe_type_option = axeExecutioncConfig.agent_type
            axe_exe_type_option_cell = HTML.TableCell(str(axe_exe_type_option), attribs={'align': 'left'})
            axe_table.rows.append([axe_exe_type_name_cell, axe_exe_type_option_cell])
            axe_device_option_name = "Device Option: "
            axe_device_option_name_cell = HTML.TableCell(str(axe_device_option_name),
                                                         attribs={'align': 'right'})
            axe_device_option = axeExecutioncConfig.device_option
            axe_device_option_cell = HTML.TableCell(str(axe_device_option), attribs={'align': 'left'})
            axe_table.rows.append([axe_device_option_name_cell, axe_device_option_cell])

            axe_aubload_option_name = "AubLoad Options: "
            axe_aubload_option_name_cell = HTML.TableCell(str(axe_aubload_option_name),
                                                          attribs={'align': 'right'})
            axe_aubload_option = axeExecutioncConfig.fulsim_options
            axe_aubload_option_cell = HTML.TableCell(str(axe_aubload_option), attribs={'align': 'left'})
            axe_table.rows.append([axe_aubload_option_name_cell, axe_aubload_option_cell])

            axe_grits_option_name = "Grits Options: "
            axe_grits_option_name_cell = HTML.TableCell(str(axe_grits_option_name),
                                                        attribs={'align': 'right'})
            axe_grits_option = axeExecutioncConfig.grits_options
            axe_grits_option_cell = HTML.TableCell(str(axe_grits_option), attribs={'align': 'left'})
            axe_table.rows.append([axe_grits_option_name_cell, axe_grits_option_cell])
            if axeExecutioncConfig.agent_type == 'execute -type LilyAgent':
                axe_fulsim_tbx_option_name = "Fulsim TBX Options: "
                axe_fulsim_tbx_option_name_cell = HTML.TableCell(str(axe_fulsim_tbx_option_name),
                                                          attribs={'align': 'right'})
                axe_fulsim_tbx_option = axeExecutioncConfig.FulsimTbxOptions
                axe_fulsim_tbx_option_cell = HTML.TableCell(str(axe_fulsim_tbx_option), attribs={'align': 'left'})
                axe_table.rows.append([axe_fulsim_tbx_option_name_cell, axe_fulsim_tbx_option_cell])
                lilyx_option_name = "LilyX Options: "
                lilyx_option_name_cell = HTML.TableCell(str(lilyx_option_name),
                                                        attribs={'align': 'right'})
                lilyx_option = axeExecutioncConfig.lilyX_options
                lilyx_option_cell = HTML.TableCell(str(lilyx_option), attribs={'align': 'left'})
                axe_table.rows.append([lilyx_option_name_cell, lilyx_option_cell])
                runtest_option_name = "RunTest Options: "
                runtest_option_name_cell = HTML.TableCell(str(runtest_option_name),
                                                        attribs={'align': 'right'})
                runtest_option = axeExecutioncConfig.run_test_options
                runtest_option_cell = HTML.TableCell(str(runtest_option), attribs={'align': 'left'})
                axe_table.rows.append([runtest_option_name_cell, runtest_option_cell])

            axe_htmlcode = str(axe_table)
            axe_htmlcode_list.append(axe_htmlcode)
        # sumary
        summary_tile = "Summary"
        summary_header = '<h3 align="left">' + summary_tile + '</h3>'
        if has_gold:
            summary_table = HTML.Table(
                header_row=['Total Tests', 'Done Tests', 'Pass Tests', 'Fail Tests', 'Invalid Tests',
                            'Goldenized Tests'])
        else:
            summary_table = HTML.Table(
                header_row=['Total Tests', 'Done Tests', 'Pass Tests', 'Fail Tests', 'Invalid Tests'])

        total_tests = summary["total_tests"]
        total_tests_cell = HTML.TableCell(str(total_tests), attribs={'align': 'center'})
        done_tests = summary["done_tests"]
        done_tests_cell = HTML.TableCell(str(done_tests), attribs={'align': 'center'})
        pass_tests = summary["pass_tests"]
        pass_tests_cell = HTML.TableCell(str(pass_tests), bgcolor='lime', attribs={'align': 'center'})
        fail_tests = summary["fail_tests"]
        fail_tests_cell = HTML.TableCell(str(fail_tests), bgcolor='red', attribs={'align': 'center'})
        invalid_tests = summary["invalid_tests"]

        invalid_tests_cell = HTML.TableCell(str(invalid_tests), bgcolor='yellow', attribs={'align': 'center'})

        goldnized_tests_cell = HTML.TableCell(str(total_gold_nized), bgcolor='lime', attribs={'align': 'center'})
        if has_gold:
            summary_table.rows.append(
                [total_tests_cell, done_tests_cell, pass_tests_cell, fail_tests_cell, invalid_tests_cell,
                 goldnized_tests_cell])
        else:
            summary_table.rows.append(
                [total_tests_cell, done_tests_cell, pass_tests_cell, fail_tests_cell, invalid_tests_cell])

        total_pct = 100
        total_pct_cell = HTML.TableCell(str(total_pct) + "%", bgcolor='white', attribs={'align': 'center'})
        done_pct = 0.0

        pass_pct = 0.0
        if total_tests != 0:
            pass_pct = (float(pass_tests) / float(total_tests)) * 100
            done_pct = (float(done_tests) / float(total_tests)) * 100

        done_pct = round(done_pct, 2)
        done_pct_cell = HTML.TableCell(str(done_pct) + "%", bgcolor='white', attribs={'align': 'center'})
        pass_pct = round(pass_pct, 2)
        pass_pct_cell = HTML.TableCell(str(pass_pct) + "%", bgcolor='lime', attribs={'align': 'center'})

        fail_pct = 0.0
        if total_tests != 0:
            fail_pct = (float(fail_tests) / float(total_tests)) * 100

        fail_pct = round(fail_pct, 2)
        fail_pct_cell = HTML.TableCell(str(fail_pct) + "%", bgcolor='red', attribs={'align': 'center'})

        invalid_pct = 0.0
        if total_tests != 0:
            invalid_pct = (float(invalid_tests) / float(total_tests)) * 100

        invalid_pct = round(invalid_pct, 2)
        invalid_pct_cell = HTML.TableCell(str(invalid_pct) + "%", bgcolor='yellow', attribs={'align': 'center'})
        if has_gold:
            gold_pct = 0.0
            if total_tests != 0:
                gold_pct = (float(total_gold_nized) / float(total_tests)) * 100
            gold_pct = round(gold_pct, 2)
            gold_pct_cell = HTML.TableCell(str(gold_pct) + "%", bgcolor='lime', attribs={'align': 'center'})

            summary_table.rows.append(
                [total_pct_cell, done_pct_cell, pass_pct_cell, fail_pct_cell, invalid_pct_cell, gold_pct_cell])
        else:
            summary_table.rows.append([total_pct_cell, done_pct_cell, pass_pct_cell, fail_pct_cell, invalid_pct_cell])
        summary_htmlcode = str(summary_table)

        if invalid_tests > 0:
            invalid_header = '<h3 align="left">' + 'Invalid Tests' + '</h3>'
            invalid_table = HTML.Table(header_row=['Test Name', 'Unit Name', 'Reason'])
            invalid_suite_list = summary["invalid_test_list"]
            for test_run in invalid_suite_list:
                test_name = test_run.test_name
                work_path = test_run.test_run_path
                work_path = str(work_path).replace("#", "%23")
                work_path = Path(work_path)
                test_name = HTML.link(test_name, work_path)
                test_name_cell = HTML.TableCell(test_name, bgcolor="white", attribs={'align': 'left'})
                unit_name = test_run.unit_name
                unit_name_cell = HTML.TableCell(unit_name, bgcolor="white", attribs={'align': 'center'})
                invalid_reason = test_run.test_result.invalid_message
                invalid_reason_cell = HTML.TableCell(invalid_reason, bgcolor='yellow', attribs={'align': 'left'})
                invalid_table.rows.append([test_name_cell, unit_name_cell, invalid_reason_cell])
            invalid_htmlcode = str(invalid_table)
        # details
        detail_header = '<h3 align="left">' + 'Details' + '</h3>'
        if has_gold:
            if is_cmodel:
                detail_table = HTML.Table(
                    header_row=['Test Name', 'Unit Name', 'Cmodel Status', 'Compare Status', 'Goldenized Status'])
            else:
                if is_graphic:
                    detail_table = HTML.Table(
                        header_row=['Test Name', 'Unit Name', 'Virtual Path', 'Command Line', 'Grits Status',
                                    'Fulsim Status', 'Lily Status', 'Goldenized Status'])
                else:
                    if need_axeconfig_col:
                        detail_table = HTML.Table(
                            header_row=['Test Name', 'Unit Name', 'Virtual Path', 'Axe Configure Name','Command Line', 'Grits Status',
                                        'Fulsim Status', 'Compare Status', 'Goldnized Satus'])
                    else:
                        detail_table = HTML.Table(
                        header_row=['Test Name', 'Unit Name', 'Virtual Path', 'Command Line', 'Grits Status',
                                    'Fulsim Status', 'Compare Status', 'Goldnized Satus'])
        else:
            if is_cmodel:
                detail_table = HTML.Table(header_row=['Test Name', 'Unit Name', 'Cmodel Status', 'Compare Status'])
            else:
                if is_graphic:
                    if need_axeconfig_col:
                        detail_table = HTML.Table(
                            header_row=['Test Name', 'Unit Name', 'Virtual Path', 'Axe Configure Name', 'Command Line', 'Grits Status',
                                        'Fulsim Status', 'Lily Status'])
                    else:
                        detail_table = HTML.Table(
                            header_row=['Test Name', 'Unit Name', 'Virtual Path', 'Command Line', 'Grits Status',
                                        'Fulsim Status', 'Lily Status'])

                else:
                    if need_axeconfig_col:
                        detail_table = HTML.Table(
                        header_row=['Test Name', 'Unit Name', 'Virtual Path',  'Axe Configure Name','Command Line', 'Grits Status',
                                    'Fulsim Status', 'Compare Status'])
                    else:
                        detail_table = HTML.Table(
                            header_row=['Test Name', 'Unit Name', 'Virtual Path', 'Command Line', 'Grits Status',
                                        'Fulsim Status', 'Compare Status'])

        for test_run in testDoneList:
            if not test_run.valid_test:
                continue
            test_name = test_run.test_name
            work_path = test_run.test_run_path
            work_path = str(work_path).replace("#", "%23")
            work_path = Path(work_path)
            test_name = HTML.link(test_name, work_path)
            test_name_cell = HTML.TableCell(test_name, bgcolor="white", attribs={'align': 'left'})
            unit_name = test_run.unit_name
            unit_name_cell = HTML.TableCell(unit_name, bgcolor="white", attribs={'align': 'center'})
            virtual_path = test_run.test_result.virtual_path
            virtual_path_cell = HTML.TableCell(virtual_path, bgcolor="white", attribs={'align': 'left'})
            axe_config_name = test_run.axe_execution_method.name
            axe_config_cell = HTML.TableCell(axe_config_name, bgcolor="white", attribs={'align': 'left'})

            command_line = test_run.yaml_cmdline
            command_line_cell = HTML.TableCell(command_line, bgcolor="white", attribs={'align': 'left'})

            grits_status = test_run.test_result.grits_compile_status
            color = "white"
            if grits_status == "PASS":
                color = "lime"
            elif grits_status == "FAIL":
                color = "red"
            elif grits_status == "WARN":
                color = "yellow"
            grits_file = test_run.test_result.grits_compile_file
            grits_file = str(grits_file).replace("#", "%23")
            grits_file = Path(grits_file)
            grits_status = HTML.link(grits_status, grits_file)
            grits_status_cell = HTML.TableCell(grits_status, bgcolor=color, attribs={'align': 'center'})

            fulsim_status = test_run.test_result.fulsim_compile_status
            color = "white"
            if fulsim_status == "PASS":
                color = "lime"
            elif fulsim_status == "FAIL":
                color = "red"
            elif fulsim_status == "WARN":
                color = "yellow"
            fulsim_file = test_run.test_result.fulsim_compile_file
            fulsim_file = str(fulsim_file).replace("#", "%23")
            fulsim_file = Path(fulsim_file)
            fulsim_status = HTML.link(fulsim_status, fulsim_file)
            fulsim_status_cell = HTML.TableCell(fulsim_status, bgcolor=color, attribs={'align': 'center'})

            compare_status = test_run.test_result.compare_status
            if is_graphic:
                compare_status = test_run.test_result.lily_compile_status
            color = "white"
            if compare_status == "PASS":
                color = "lime"
            elif compare_status == "FAIL":
                color = "red"
            elif compare_status == "WARN":
                color = "yellow"
            compare_file = test_run.test_result.compare_file
            if is_graphic:
                compare_file = test_run.test_result.lily_compile_file
            compare_file = str(compare_file).replace("#", "%23")
            compare_file = Path(compare_file)
            compare_status = HTML.link(compare_status, compare_file)
            compare_status_cell = HTML.TableCell(compare_status, bgcolor=color, attribs={'align': 'center'})

            if has_gold:
                goldnize_status = test_run.goldnize_status
                color = "white"
                if goldnize_status == "SUCCESS":
                    color = "lime"
                elif goldnize_status == "EMPTY":
                    color = "yellow"
                elif goldnize_status == "FAIL":
                    color = "red"

                gold_path = test_run.goldenized_test_gold_path
                gold_path = str(gold_path).replace("#", "%23")
                gold_path = Path(gold_path)
                gold_status = HTML.link(goldnize_status, gold_path)
                gold_status_cell = HTML.TableCell(gold_status, bgcolor=color, attribs={'align': 'center'})
            if has_gold:
                if cmodel:
                    detail_table.rows.append(
                        [test_name_cell, unit_name_cell, fulsim_status_cell, compare_status_cell, gold_status_cell])
                else:
                    if need_axeconfig_col:
                        detail_table.rows.append(
                            [test_name_cell, unit_name_cell, virtual_path_cell, axe_config_cell, command_line_cell, grits_status_cell, fulsim_status_cell,
                             compare_status_cell, gold_status_cell])
                    else:
                        detail_table.rows.append(
                        [test_name_cell, unit_name_cell, virtual_path_cell,command_line_cell, grits_status_cell, fulsim_status_cell,
                         compare_status_cell, gold_status_cell])
            else:
                if cmodel:
                    detail_table.rows.append([test_name_cell, unit_name_cell, fulsim_status_cell, compare_status_cell])
                else:
                    if need_axeconfig_col:
                        detail_table.rows.append(
                            [test_name_cell, unit_name_cell, virtual_path_cell,axe_config_cell, command_line_cell, grits_status_cell,
                             fulsim_status_cell, compare_status_cell])
                    else:
                        detail_table.rows.append(
                        [test_name_cell, unit_name_cell, virtual_path_cell, command_line_cell, grits_status_cell,
                         fulsim_status_cell, compare_status_cell])

        detail_htmlcode = str(detail_table)
        try:
            with open(filePath, 'w') as f:
                if done_pct != 100:
                    f.write(webhead)
                f.write(header)
                f.write('<br>')
                f.write(total_time_header)
                # add blank lines
                for i in range(lines_space):
                    f.write('<br>')
                if regressSetting != None:
                    f.write(regress_header)
                    f.write(regress_htmlcode)

                for axe_htmlcode in axe_htmlcode_list:
                    f.write(axe_htmlcode)

                f.write(summary_header)
                f.write(summary_htmlcode)
                for i in range(2):
                    f.write('<br>')
                if invalid_tests > 0:
                    f.write(invalid_header)
                    f.write(invalid_htmlcode)
                f.write(detail_header)
                f.write(detail_htmlcode)
            return ("write to file successfuly:" + str(filePath))
        except Exception as e:
            print(e)
            return e

    def writeDataToHtmlFile(self, title, filePath, summary, testDoneList, cmodel=False, isgraphic=False,regressSetting:AxeExecution.RegressSetting=None, axeExecutioncConfig:AxeExecution.ExecutionMethod=None):
        webhead ='<head> <meta http-equiv="refresh" content="10"> </head>'
        header = '<h1 align="center">' + title + '</h1>'
        total_time = summary["regress_time"]
        total_time_string = self.convertSecToHourMinSec(total_time)
        total_time_header = '<h2 align="center">' + "Total Run Time: "+ total_time_string + '</h2>'
        lines_space = 5
        gold_result = self.hasGoldnizedData(testDoneList)
        has_gold = gold_result[0]
        total_gold_nized = gold_result[1]
        is_cmodel = cmodel
        is_graphic = isgraphic
        #regress  seetings
        if regressSetting !=None:
            regress_tile = regressSetting.name
            regress_header = '<h3 align="left">' + regress_tile + '</h3>'
            regress_table = HTML.Table()
            
            regress_aubload_path_name = "Aubload Path: "
            regress_aubload_path_name_cell =  HTML.TableCell(str(regress_aubload_path_name),attribs={'align': 'right'})
            regress_aubload_path = regressSetting.aubload_path
            regress_aubload_path_cell = HTML.TableCell(str(regress_aubload_path), attribs={'align': 'left'})
            regress_table.rows.append([regress_aubload_path_name_cell,regress_aubload_path_cell])

            regress_aubload_option_name = "Aubload Options: "
            regress_aubload_option_name_cell = HTML.TableCell(str(regress_aubload_option_name), attribs={'align': 'right'})
            regress_aubload_option  = regressSetting.additional_aubload_options
            regress_aubload_option_cell = HTML.TableCell(str(regress_aubload_option), attribs={'align': 'left'})
            regress_table.rows.append([regress_aubload_option_name_cell, regress_aubload_option_cell])

            regress_grits_path_name = "Grits Path: "
            regress_grits_path_name_cell = HTML.TableCell(str(regress_grits_path_name), attribs={'align': 'right'})
            regress_grits_path = regressSetting.grits_path
            regress_grits_path_cell = HTML.TableCell(str(regress_grits_path), attribs={'align': 'left'})
            regress_table.rows.append([regress_grits_path_name_cell, regress_grits_path_cell])

            regress_grits_option_name = "Grits Options: "
            regress_grits_option_name_cell = HTML.TableCell(str(regress_grits_option_name),
                                                              attribs={'align': 'right'})
            regress_grits_option = regressSetting.additional_grits_options
            regress_grits_option_cell = HTML.TableCell(str(regress_grits_option), attribs={'align': 'left'})
            regress_table.rows.append([regress_grits_option_name_cell, regress_grits_option_cell])

            regress_start_time_name = "Start Time: "
            regress_start_time_name_cell = HTML.TableCell(str(regress_start_time_name), attribs={'align': 'right'})
            regress_start_time = regressSetting.start_time
            regress_start_time_cell = HTML.TableCell(str(regress_start_time), attribs={'align': 'left'})
            regress_table.rows.append([regress_start_time_name_cell, regress_start_time_cell])
            
            regress_end_time_name = "End Time: "
            regress_end_time_name_cell = HTML.TableCell(str(regress_end_time_name), attribs={'align': 'right'})
            regress_end_time = regressSetting.end_time
            regress_end_time_cell = HTML.TableCell(str(regress_end_time), attribs={'align': 'left'})
            regress_table.rows.append([regress_end_time_name_cell, regress_end_time_cell])
            regress_htmlcode = str(regress_table)

        if axeExecutioncConfig != None:
            axe_tile = axeExecutioncConfig.name
            axe_header = '<h3 align="left">' + axe_tile + '</h3>'
            axe_table = HTML.Table()

            axe_device_option_name = "Device Option: "
            axe_device_option_name_cell = HTML.TableCell(str(axe_device_option_name),
                                                          attribs={'align': 'right'})
            axe_device_option = axeExecutioncConfig.device_option
            axe_device_option_cell = HTML.TableCell(str(axe_device_option), attribs={'align': 'left'})
            axe_table.rows.append([axe_device_option_name_cell, axe_device_option_cell])
           
            axe_aubload_option_name = "Fulsim Options: "
            axe_aubload_option_name_cell = HTML.TableCell(str(axe_aubload_option_name),
                                                              attribs={'align': 'right'})
            axe_aubload_option = axeExecutioncConfig.fulsim_options
            axe_aubload_option_cell = HTML.TableCell(str(axe_aubload_option), attribs={'align': 'left'})
            axe_table.rows.append([axe_aubload_option_name_cell, axe_aubload_option_cell])

          

            axe_grits_option_name = "Grits Options: "
            axe_grits_option_name_cell = HTML.TableCell(str(axe_grits_option_name),
                                                            attribs={'align': 'right'})
            axe_grits_option = axeExecutioncConfig.grits_options
            axe_grits_option_cell = HTML.TableCell(str(axe_grits_option), attribs={'align': 'left'})
            axe_table.rows.append([axe_grits_option_name_cell, axe_grits_option_cell])

            axe_htmlcode = str(axe_table)
        #sumary
        summary_tile = "Summary"
        summary_header = '<h3 align="left">' + summary_tile + '</h3>'
        if has_gold:
            summary_table = HTML.Table(header_row=['Total Tests', 'Done Tests', 'Pass Tests', 'Fail Tests', 'Invalid Tests', 'Goldnized Tests'])
        else:
            summary_table = HTML.Table(header_row=['Total Tests', 'Done Tests', 'Pass Tests', 'Fail Tests', 'Invalid Tests'])

        total_tests = summary["total_tests"]
        total_tests_cell = HTML.TableCell(str(total_tests),attribs={'align': 'center'})
        done_tests = summary["done_tests"]
        done_tests_cell = HTML.TableCell(str(done_tests), attribs={'align': 'center'})
        pass_tests = summary["pass_tests"]
        pass_tests_cell= HTML.TableCell(str(pass_tests), bgcolor='lime', attribs={'align': 'center'})
        fail_tests = summary["fail_tests"]
        fail_tests_cell = HTML.TableCell(str(fail_tests), bgcolor='red', attribs={'align': 'center'})
        invalid_tests = summary["invalid_tests"]

        invalid_tests_cell = HTML.TableCell(str(invalid_tests), bgcolor='yellow', attribs={'align': 'center'})

        goldnized_tests_cell= HTML.TableCell(str(total_gold_nized), bgcolor='lime', attribs={'align': 'center'})
        if has_gold:
            summary_table.rows.append([total_tests_cell,done_tests_cell, pass_tests_cell,fail_tests_cell,invalid_tests_cell,goldnized_tests_cell])
        else:
            summary_table.rows.append([total_tests_cell,done_tests_cell, pass_tests_cell,fail_tests_cell,invalid_tests_cell])

        total_pct = 100
        total_pct_cell = HTML.TableCell(str(total_pct) + "%", bgcolor='white', attribs={'align': 'center'})
        done_pct = 0.0

        pass_pct = 0.0
        if total_tests != 0:
            pass_pct = (float(pass_tests)/float(total_tests))*100
            done_pct = (float(done_tests) / float(total_tests)) * 100

        done_pct = round(done_pct, 2)
        done_pct_cell = HTML.TableCell(str(done_pct) + "%", bgcolor='white', attribs={'align': 'center'})
        pass_pct = round(pass_pct, 2)
        pass_pct_cell = HTML.TableCell(str(pass_pct)+"%", bgcolor='lime', attribs={'align': 'center'})

        fail_pct = 0.0
        if total_tests != 0:
            fail_pct = (float(fail_tests) / float(total_tests)) * 100

        fail_pct = round(fail_pct, 2)
        fail_pct_cell = HTML.TableCell(str(fail_pct) + "%", bgcolor='red', attribs={'align': 'center'})

        invalid_pct = 0.0
        if total_tests != 0:
            invalid_pct = (float(invalid_tests) / float(total_tests)) * 100


        invalid_pct = round(invalid_pct, 2)
        invalid_pct_cell = HTML.TableCell(str(invalid_pct) + "%", bgcolor='yellow', attribs={'align': 'center'})
        if has_gold:
            gold_pct = 0.0
            if total_tests != 0:
                gold_pct = (float(total_gold_nized) / float(total_tests)) * 100
            gold_pct = round(gold_pct, 2)
            gold_pct_cell = HTML.TableCell(str(gold_pct)+"%", bgcolor='lime', attribs={'align': 'center'})

            summary_table.rows.append([total_pct_cell,done_pct_cell, pass_pct_cell, fail_pct_cell, invalid_pct_cell,gold_pct_cell])
        else:
            summary_table.rows.append([total_pct_cell,done_pct_cell, pass_pct_cell, fail_pct_cell, invalid_pct_cell])
        summary_htmlcode = str(summary_table)

        if invalid_tests > 0:
            invalid_header = '<h3 align="left">' + 'Invalid Tests' + '</h3>'
            invalid_table = HTML.Table(header_row=['Test Name', 'Unit Name', 'Reason'])
            invalid_suite_list = summary["invalid_test_list"]
            for test_run in invalid_suite_list:
                test_name = test_run.test_name
                work_path = test_run.test_run_path
                work_path = str(work_path).replace("#", "%23")
                work_path = Path(work_path)
                test_name = HTML.link(test_name, work_path)
                test_name_cell = HTML.TableCell(test_name, bgcolor="white", attribs={'align': 'left'})
                unit_name = test_run.unit_name
                unit_name_cell = HTML.TableCell(unit_name, bgcolor="white", attribs={'align': 'center'})
                invalid_reason = test_run.test_result.invalid_message
                invalid_reason_cell = HTML.TableCell(invalid_reason, bgcolor='yellow', attribs={'align': 'left'})
                invalid_table.rows.append([test_name_cell, unit_name_cell, invalid_reason_cell])
            invalid_htmlcode = str(invalid_table)
        #details
        detail_header = '<h3 align="left">' + 'Details' + '</h3>'
        if has_gold:
            if is_cmodel:
                detail_table = HTML.Table(header_row=['Test Name', 'Unit Name', 'Cmodel Status', 'Compare Status','Goldnized Satus'])
            else:
                if is_graphic:
                    detail_table = HTML.Table(header_row=['Test Name', 'Unit Name', 'Virtual Path','Command Line','Grits Status', 'Fulsim Status', 'Lily Status','Goldnized Satus'])
                else:
                    detail_table = HTML.Table(header_row=['Test Name', 'Unit Name', 'Virtual Path','Command Line','Grits Status', 'Fulsim Status', 'Compare Status','Goldnized Satus'])
        else:
            if is_cmodel:
                detail_table = HTML.Table(header_row=['Test Name', 'Unit Name', 'Cmodel Status', 'Compare Status'])
            else:
                if is_graphic:
                    detail_table = HTML.Table(header_row=['Test Name', 'Unit Name', 'Virtual Path','Command Line','Grits Status', 'Fulsim Status', 'Lily Status'])
                else:
                    detail_table = HTML.Table(header_row=['Test Name', 'Unit Name', 'Virtual Path','Command Line','Grits Status', 'Fulsim Status', 'Compare Status'])

        for test_run in testDoneList:
            if not test_run.valid_test:
                continue
            test_name = test_run.test_name
            work_path = test_run.test_run_path
            work_path = str(work_path).replace("#","%23")
            work_path = Path(work_path)
            test_name = HTML.link(test_name,work_path)
            test_name_cell = HTML.TableCell(test_name, bgcolor="white", attribs={'align': 'left'})
            unit_name = test_run.unit_name
            unit_name_cell = HTML.TableCell(unit_name, bgcolor="white", attribs={'align': 'center'})
            virtual_path = test_run.test_result.virtual_path
            virtual_path_cell = HTML.TableCell(virtual_path, bgcolor="white", attribs={'align': 'left'})
            command_line = test_run.yaml_cmdline
            command_line_cell = HTML.TableCell(command_line, bgcolor="white", attribs={'align': 'left'})

            grits_status = test_run.test_result.grits_compile_status
            color = "white"
            if grits_status == "PASS":
                color = "lime"
            elif grits_status == "FAIL":
                color = "red"
            elif grits_status == "WARN":
                color = "yellow"
            grits_file  = test_run.test_result.grits_compile_file
            grits_file = str(grits_file).replace("#", "%23")
            grits_file = Path(grits_file)
            grits_status = HTML.link(grits_status, grits_file)
            grits_status_cell = HTML.TableCell(grits_status, bgcolor=color, attribs={'align': 'center'})

            fulsim_status = test_run.test_result.fulsim_compile_status
            color = "white"
            if fulsim_status == "PASS":
                color = "lime"
            elif fulsim_status == "FAIL":
                color = "red"
            elif fulsim_status == "WARN":
                color = "yellow"
            fulsim_file = test_run.test_result.fulsim_compile_file
            fulsim_file = str(fulsim_file).replace("#", "%23")
            fulsim_file = Path(fulsim_file)
            fulsim_status = HTML.link(fulsim_status, fulsim_file)
            fulsim_status_cell = HTML.TableCell(fulsim_status, bgcolor=color, attribs={'align': 'center'})

            compare_status = test_run.test_result.compare_status
            if is_graphic:
                compare_status = test_run.test_result.lily_compile_status
            color = "white"
            if compare_status == "PASS":
                color = "lime"
            elif compare_status == "FAIL":
                color = "red"
            elif compare_status == "WARN":
                color = "yellow"
            compare_file = test_run.test_result.compare_file
            if is_graphic:
                compare_file = test_run.test_result.lily_compile_file
            compare_file = str(compare_file).replace("#", "%23")
            compare_file = Path(compare_file)
            compare_status = HTML.link(compare_status, compare_file)
            compare_status_cell = HTML.TableCell(compare_status, bgcolor=color, attribs={'align': 'center'})



            if has_gold:
                goldnize_status = test_run.goldnize_status
                color = "white"
                if goldnize_status == "SUCCESS":
                    color = "lime"
                elif goldnize_status == "EMPTY":
                    color = "yellow"
                elif goldnize_status == "FAIL":
                    color = "red"

                gold_path = test_run.goldenized_test_gold_path
                gold_path = str(gold_path).replace("#", "%23")
                gold_path = Path(gold_path)
                gold_status = HTML.link(goldnize_status, gold_path)
                gold_status_cell = HTML.TableCell(gold_status, bgcolor=color, attribs={'align': 'center'})
            if has_gold:
                if cmodel:
                    detail_table.rows.append([test_name_cell, unit_name_cell,fulsim_status_cell,compare_status_cell, gold_status_cell])
                else:
                    detail_table.rows.append([test_name_cell, unit_name_cell,virtual_path_cell, grits_status_cell, fulsim_status_cell,compare_status_cell, gold_status_cell])
            else:
                if cmodel:
                    detail_table.rows.append([test_name_cell, unit_name_cell,fulsim_status_cell,compare_status_cell])
                else:
                    detail_table.rows.append([test_name_cell, unit_name_cell,virtual_path_cell, command_line_cell, grits_status_cell, fulsim_status_cell,compare_status_cell])


        detail_htmlcode = str(detail_table)
        with open(filePath, 'w') as f:
            if done_pct != 100:
                f.write(webhead)
            f.write(header)
            f.write('<br>')
            f.write(total_time_header)
            # add blank lines
            for i in range(lines_space):
                f.write('<br>')
            if regressSetting != None:
                f.write(regress_header)
                f.write(regress_htmlcode)

            if axeExecutioncConfig != None:
                f.write(axe_header)
                f.write(axe_htmlcode)
                
            f.write(summary_header)
            f.write(summary_htmlcode)
            for i in range(2):
                f.write('<br>')
            if invalid_tests > 0:
                f.write(invalid_header)
                f.write(invalid_htmlcode)
            f.write(detail_header)
            f.write(detail_htmlcode)

    def readTestFromList(self,listFilePath):
        test_suite_list = list()
        with open(listFilePath) as f:
            list_data = f.readlines()
        for test_item in list_data:
            print("test_item:", test_item)
            test_gsf_revision = None
            unit_name = None
            search_result = re.search(r"(\w*)/basic", str(test_item))
            if search_result:
                unit_name = search_result.group(1)
            search_result = re.search(r"basic/(.*)", str(test_item))
            if search_result:
                test_gsf_revision = search_result.group(1)
            if test_gsf_revision == None or unit_name == None:
                continue
            test_name = test_gsf_revision.split("/")[0]
            gsf_revision = test_gsf_revision.split("/")[1]
            gsf_revision = gsf_revision.replace("\",", "")

            # test_path = os.path.join(self.test_base, unit_name)
            # test_path = os.path.join(test_path, "basic")
            # test_path = os.path.join(test_path, test_name_revision)
            # print("test_path:", test_path)
            gsf_name = gsf_revision.split("#0")[0]
            print("gsf_revision:", gsf_revision)
            print("gsf_name:", gsf_name)
            test_revision = None

            if gsf_revision.split("#0")[1]:
                test_revision = gsf_revision.split("#0")[1]

            if test_revision == None:
                test_revision = "#0"

            test_run = Test.TestSuite()
            test_run.unit_name = unit_name
            test_run.test_name = test_name
            test_run.gsf_name = gsf_name
            test_run.test_revision = test_revision

            test_suite_list.append(test_run)
        return test_suite_list

    def convertSecToHourMinSec(self,seconds):
        #seconds = seconds % (24 * 3600)
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        return "%d:%02d:%02d" % (hour, minutes, seconds)

    def regularExpressHit(self, filePath, regExressList):
        hit = False
        for one_reg_expression in regExressList:
            if re.search(one_reg_expression, filePath,re.IGNORECASE):
                #print(filePath, 'hit', one_reg_expression)
                hit =True
                break
        #if not hit:
            #print(filePath, 'did not hit', one_reg_expression)
        return hit
    def getSubfolderPathFromDir(self, dirPath):
        subfolder_path_list = list()
        for it in os.scandir(dirPath):
            if it.is_dir():
                subfolder_path_list.append(it.path)
        return subfolder_path_list

    def getItemList(self, itemString:str):
        itemlist = list();
        itemArray = list()
        itemString = itemString.replace(";", ",")

        if re.search(",", itemString):
            itemArray = itemString.split(",")
        else:
            itemArray.append(itemString)

        for item in itemArray:
            item = str(item).strip()
            if item != None and item !="" and not str(item).startswith("#", 0, 1):
                self.addUniquePath(item,itemlist)
        itemlist.reverse()
        return itemlist

    def addUniquePath(self, path, pathList:list):
        if len(pathList) ==0:
            pathList.append(path)
        else:
            unique = True
            for one_path in pathList:
                if one_path == path:
                    unique = False
                    break
            if unique:
                pathList.append(path)



    def getItemList(self, itemString:str):
        itemlist = list();
        itemArray = list()
        itemString = itemString.replace(";", ",")

        if re.search(",", itemString):
            itemArray = itemString.split(",")
        else:
            itemArray.append(itemString)

        for item in itemArray:
            item = str(item).strip()
            if item != None and item !="" and not str(item).startswith("#", 0, 1):
                self.addUniquePath(item,itemlist)
        itemlist.reverse()
        return itemlist

    def set_permissions_recursive(self, directory, mode):
        for root, dirs, files in os.walk(directory):
            for d in dirs:
                dir_path = os.path.join(root, d)
                chomd_cmd = "chmod 775 " + str(dir_path)
                subprocess.run(chomd_cmd, shell=True)

            for f in files:
                f_path = os.path.join(root, f)
                chomd_cmd = "chmod 775 " + str(f_path)
                subprocess.run(chomd_cmd, shell=True)

    def set_permissions(self, directory):
        chomd_cmd = "chmod -R  775 " + str(directory)
        print("chomd_cmd:", chomd_cmd)
        subprocess.run(chomd_cmd, shell=True)

    def findMatchFile(self, fileName, dirPath):
        fileName = os.path.basename(fileName)
        allsplits = str(fileName).split(".")
        allfiles = self.GetAllFilePathsFromCurrentDir(dirPath)
        for onefile in allfiles:
            filefind = True
            for onesplit in allsplits:
                if str(onefile).find(onesplit)!=-1:
                    if Path(onefile).suffix == Path(fileName).suffix:
                        filefind = True
                        break
                    else:
                        filefind = False
                else:
                    filefind = False
            if filefind:
                return onefile
        return None

    def get_file_extension(self,filename):
        """
        Get the file extension from a given filename.

        Parameters:
        filename (str): The name of the file.

        Returns:
        str: The file extension or an empty string if there is no extension.
        """
        _, extension = os.path.splitext(filename)
        return extension

    def wrap(self,string, max_width):
        return textwrap.wrap(string, max_width)

    def get_most_left_parent_path(self, file_path):
        """
        Returns the most left parent path of the given file path.

        Parameters:
        file_path (str): The path to the file.

        Returns:
        str: The most left parent path of the file path.
        """
        # Normalize the path to remove any redundant separators or up-level references
        normalized_path = os.path.normpath(file_path)

        # Split the path into components
        path_components = normalized_path.split(os.sep)

        # Return the first non-empty component after the root
        if len(path_components) > 1:
            return os.sep + path_components[1]
        else:
            return os.sep

    def has_files(self, directory_path):
        """
        Check if the given directory contains any files.

        Parameters:
        directory_path (str): The path to the directory to check.

        Returns:
        bool: True if the directory contains files, False otherwise.
        """
        try:
            # List all entries in the directory
            entries = os.listdir(directory_path)

            # Check if any entry is a file
            for entry in entries:
                entry_path = os.path.join(directory_path, entry)
                if os.path.isfile(entry_path):
                    return True

            # If no files are found, return False
            return False

        except FileNotFoundError:
            print(f"The directory '{directory_path}' does not exist.")
            return False
        except PermissionError:
            print(f"Permission denied to access the directory '{directory_path}'.")
            return False

    def get_os_info(self):
        os_type = platform.system()
        os_version = platform.version()
        return os_type, os_version

    def is_sles15(self):
        try:
            with open('/etc/os-release', 'r') as file:
                os_info = file.read()

            if 'SUSE Linux Enterprise Server' in os_info:
                if 'VERSION="12' in os_info:
                    return False
                elif 'VERSION="15' in os_info:
                    return True
                else:
                    return False
            else:
                return False
        except FileNotFoundError:
            return False

    def get_linux_version(self):
        try:
            with open('/etc/os-release', 'r') as file:
                os_info = file.read()

            if 'SUSE Linux Enterprise Server' in os_info:
                if 'VERSION="12' in os_info:
                    return "Sles 12"
                elif 'VERSION="15' in os_info:
                    return "Sles 15"
                else:
                    return "Unknown linux version"
            else:
                return "Unknown linux version"
        except FileNotFoundError:
            return "Unknown linux version"

    def get_windows_version(self):
        if platform.system() != 'Windows':
            return "Not a Windows system"

        version = platform.version()
        major, minor, build = map(int, version.split('.'))

        if major == 10:
            if build >= 22000:
                return "Windows 11"
            else:
                return "Windows 10"
        else:
            return "Unknown Windows version"