import os
from pathlib import Path
import subprocess
import libs.utility as Util
import re
import glob
from decimal import Decimal
import filecmp
import shutil
import platform
import libs.executionSetting  as AxeExecution
class regressObject:
    def __init__(self):
        self.testrun_list = list()
        self.gold_include_list = list()
        self.gold_exclude_list = list()
        self.result_folder_path=""
        self.regress_time_mark=""
        self.num_tests_to_run_in_parallel = 1
        self.incredibuild_enable = False
        self.run_grits = False
        self.run_aubload = False
        self.run_compare = False
        self.run_lily = False
        self.user_id = "default"
        self.project_name =""

class TestYamlInfo:
    def __init__(self):
        self.default_cmdln =""
        self.test_cmdln =""
        self.seed_count = 1


class YamlTestConfig:
    def __init__(self):
        self.Agent = None
        self.SeedCount = None
        self.CommandLine = ''
        self.VirtualPath = None
        self.Products = list()
        self.Name = None
        self.Products = list()
        self.Targets = list()
        self.Tags = list()
        self.Features = list()

    def printInfo(self):
        print("YamlTestConfig:")
        print(" Name = ", self.Name)
        print(" CommandLine = ", self.CommandLine)
        print(" VirtualPath = ", self.VirtualPath)

class YamlConfig:
    def __init__(self):
        self.SchemaVersion = ""
        self.TestFileName = ""
        self.TestFileGuid = ""
        self.NextAutoTestObjectName = ""
        self.DefaultTestConfig = YamlTestConfig()
        self.test_config_list = list()

    def printInfo(self):
        print("YamlConfig:")
        print(" SchemaVersion = ",self.SchemaVersion)
        print(" TestFileName = ", self.TestFileName)
        print(" NextAutoTestObjectName = ", self.NextAutoTestObjectName)
        self.DefaultTestConfig.printInfo()
        if len(self.test_config_list):
            count = len(self.test_config_list)
            print("This test has ", count, " configs")
            for test_config in self.test_config_list:
                test_config.printInfo()

class GritsOption:
    def __init__(self):
        self.suite = ""
        self.default =""
        self.test =''
       


class TestRead: ## note all paths are src paths
    def __init__(self):
        self.valid_test= True
        self.unit_name =""
        self.test_name =""
        self.test_path = ""
        self.p4_test_path =''
        self.gsf_name =""
        self.gsf_path = ""
        self.cfg_name = ""
        self.cfg_path = ""
        self.path_file_path = ""
        self.test_revision = 0
        self.yaml_name = ""
        self.yaml_path = ""
        self.invalid_message = ""
        self.jason_name =""
        self.has_own_folder = True

        self.type = "gsf"
        self.ymal_config = YamlConfig()
        self.config_id = ""
        self.test_file_relative_path_list = list()
        self.test_src_file_paths = list()
        self.seed = "1"
        self.regress_base = ""
        self.test_dist_path =""



    def printInfo(self):
        print("test info:")
        print(" type = ", self.type)
        print(" config_id = ", self.config_id)
        print(" unit_name = ", self.unit_name)
        print(" test_name = ", self.test_name)
        print(" test_path = ", self.test_path)
        print(" gsf_name = ", self.gsf_name)
        print(" gsf_path = ", self.gsf_path)
        print(" yaml_name = ", self.yaml_name)
        print(" yaml_path = ", self.yaml_path)


class TestRun:
    def __init__(self, useP4=None):
        if useP4!=None:
            self.use_p4 = useP4
        self.p4_copied = False
        self.unit_name = None
        self.unit_folder_ready = False
        self.test_name = None # with tag
        self.gsf_name = ""
        self.cfg_name = ""
        self.yaml_name = ""
        self.test_revision =None
        self.test_src_path = None
        self.p4test_src_path = None
        self.test_run_path = None
        self.dump_path =''
        self.test_gold_folder_path = ""
        self.old_gold_path = ""
        self.unit_run_path = None
        self.ckr_folder_path =None
        self.type = "gsf"
        self.grits_option =""
        self.aubload_option = ""
        self.grits_exe = ""  # path

        self.grits_rb = None  # path
        self.lily_exe = None  # path
        self.aubload_exe = None  # path
        self.seed = "1"
        self.grits_option = ""
        self.aubload_option = ""
        self.lily_options =""
        self.exedir_path = None
        self.project_id = "" # for  cmpare gold file
        self.run_grits = False
        self.run_cfg = False
        self.disp_tool_base = ""
        self.disp_setup_exe = None
        self.disp_options = ""

        self.run_aubload = False
        self.run_compare = False
        self.run_lily = False
        self.jason_name =""
        self.has_own_folder = True

        self.has_old_gold = False
        self.need_ckr= False
        self.valid_test= True
        self.test_result = TestResult()
        self.device = ""
        self.device_option =""
        self.config_id = "0"
        self.default_name =""
        #for test goldnization
        self.run_gold = "no" #goldnize test.
        self.goldenize = "no"  # goldnize test.
        self.traditional_goldnize_path = ""
        self.new_gold_path = None
        self.gold_src_path =''
        self.gold_work_path = ''
        self.new_gold_base = None
        self.copy_test = False
        self.binary_gold = False
        self.checker_gold = False
        self.dramout_gold = False
        self.goldnize_status = "N/A"
        self.gold_base = ""
        self.regress_base = ""
        self.test_file_relative_path_list = list()
        self.gold_file_relative_path_list = list()
        self.cleanup = False
        self.return_path = ""
        self.time_stamp = ""
        self.gold_include_name_list = list()
        self.gold_exclude_name_list = list()
        self.run_in_remote = False
        self.test_src_file_paths = list()
        self.gsf_src_path=""
        self.cfg_src_path=""
        self.yaml_src_path=""
        self.path_src_path=''
        self.axe_execution_method = None
        self.yaml_cmdline =''
        self.file_identifier =''
        self.goldenized_test_path =''
        self.goldenized_test_gold_path = ''
        self.beyond_compare=''
        self.test_required_folders = list()
        self.test_required_files = list()
        self.util = Util.Utility()
        self.input_file_ext_list = list()
        self.input_file_ext_list.append('rb')
        self.input_file_ext_list.append('gsf')
        self.input_file_ext_list.append('bin')
        self.input_file_ext_list.append('vc3')
        self.input_file_ext_list.append('264')
        self.input_file_ext_list.append('yu12')
        self.input_file_ext_list.append('av1')
        self.input_file_ext_list.append('yuy2')
        self.input_file_ext_list.append('nv12')
        self.input_file_ext_list.append('par')
        self.input_file_ext_list.append('g7a')
        self.input_file_ext_list.append('g6a')
        self.input_file_ext_list.append('ivf')
        self.input_file_ext_list.append('asm')
        self.input_file_ext_list.append('obj')
        self.input_file_ext_list.append('dat')
        self.input_file_ext_list.append('y210')
        self.input_file_ext_list.append('ayuv')
        self.input_file_ext_list.append('p010')
        self.input_file_ext_list.append('json')


        if re.search("windows", platform.system(), re.IGNORECASE):
            self.is_win_os = True
        else:
            self.is_win_os = False

    def getGritsOption(self, yamlCmdLine):
        line = str(yamlCmdLine)
        line = line.replace("'", "")
        line = line.replace('"', "")

        grits_option = ""
        if line =="":
            return grits_option
        grits_option = ""
        grits_options = list()
        options = line.split()
        is_grits_option = True
        for option in options:
            if "+grits" in option:
                is_grits_option = True
                continue
            elif "+aubload" in option or "+fulsim" in option or "+runsim"  in option:
                is_grits_option = False
                continue
            if is_grits_option:
                grits_options.append(option)

        if len(grits_options) == 0:
            grits_option = ""
            return grits_option

        for option in grits_options:
            grits_option = grits_option + " " + option
        #print("grits_option = ", grits_option)
        return grits_option

    def generateDispOption(self):
        disp_options = " -test " + self.default_name + " -proj "
        device = str(self.axe_execution_method.device_option).split("/")[-1]
        proj_name = device.split('.')[0]
        disp_options = disp_options + proj_name + " -disp_tools " + str(self.disp_tool_base) + " -tdir " + str(
            self.test_run_path) + " -fileresolverpath "
        file_resolve_path = os.path.join(self.disp_tool_base, "AxeFileResolver/AxeFileResolver")
        disp_options = disp_options + str(file_resolve_path)
        disp_options = disp_options.replace("\\", "/")
        self.disp_options = disp_options
        print("disp_options = ", self.disp_options)

    def getAubLoadOption(self, yamlCmdLine):
        line = str(yamlCmdLine)
        line = line.replace("'", "")
        line = line.replace('"', "")
        aubload_option = ""
        if line == "" or ("+aubload" not in line) :
            return aubload_option
        aubload_option = ""
        aubload_options = list()
        options = line.split()
        is_aubload_option = False
        for option in options:
            if "+grits" in option:
                is_aubload_option = False
                continue
            elif "+fulsim" in option:
                is_aubload_option = False
                continue
            elif "+runsim" in option:
                is_aubload_option = False
                continue
            elif "+aubload" in  option:
                is_aubload_option = True
                continue
            if is_aubload_option:
                aubload_options.append(option)

        if len(aubload_options) == 0:
            aubload_option = ""
            return aubload_option

        for option in aubload_options:
            aubload_option = aubload_option + " " + option
        #print("aubload_option = ", aubload_option)

        return aubload_option
    def getFulsimOption(self, yamlCmdLine):
        line = str(yamlCmdLine)
        line = line.replace("'", "")
        line = line.replace('"', "")
        aubload_option = ""
        if line == "" or ("+fulsim" not in line) :
            return aubload_option
        aubload_option = ""
        aubload_options = list()
        options = line.split()
        is_aubload_option = False
        for option in options:
            if "+grits" in option:
                is_aubload_option = False
                continue
            elif "+aubload" in  option:
                is_aubload_option = False
                continue
            elif "+fulsim" in  option:
                is_aubload_option = True
                continue
            if is_aubload_option:
                aubload_options.append(option)

        if len(aubload_options) == 0:
            aubload_option = ""
            return aubload_option

        for option in aubload_options:
            aubload_option = aubload_option + " " + option
        #print("aubload_option = ", aubload_option)

        return aubload_option

    def findProjectSpecificGold(self, gold_file_list: list):
        one_list = list()
        if len(gold_file_list) == 0:
            return one_list

        for one_item in gold_file_list:
            if str(one_item).find("__") != -1:
                if str(one_item).find(str(self.project_id).lower()) !=-1:
                    one_list.append(one_item)
        return one_list
    def fileResolve(self):
        os.chdir(self.test_run_path)
        print("file resolve start ...")
        self.CheckRequiredFiles(self.gsf_name)
        self.CheckRequiredFiles2(self.grits_option)
        self.test_run_path = str(self.test_run_path).replace("\\", "/")
        if  not Path(self.test_run_path).is_dir():
            print("working path does not exist, please create it:",self.test_run_path)
            return
        while len(self.test_required_files) >0:
            onefile = self.test_required_files.pop()
            if str(onefile).find('"') != -1 or str(onefile).find(' ') != -1:
                continue
            onefile_src_path = os.path.join(self.test_src_path,onefile)
            #print("onefile_src_path:", onefile_src_path)
            if Path(str(onefile_src_path)).is_file():
                #print("copying " + str(onefile_src_path) + " to " + self.test_run_path )
                dest_file_path = os.path.join(self.test_run_path,onefile)
                if not Path(str(dest_file_path)).is_file():
                    self.util.copyOneFile(onefile_src_path, self.test_run_path)
                    if Path(str(onefile_src_path)).is_file() and (Path(str(onefile_src_path)).suffix == '.gsf' or Path(str(onefile_src_path)).suffix == '.rb'):
                        self.CheckRequiredFiles(onefile_src_path)
            else:
                os.chdir(Path(self.test_run_path))

                if not Path(onefile).is_file():
                    #print(onefile_src_path)
                    for src_path in self.test_required_folders:
                        onefile_src_path = os.path.join(src_path,onefile)
                        onefile_src_path = onefile_src_path.replace("\\", "/")
                        #print(onefile_src_path)
                        if Path(str(onefile_src_path)).is_file():
                            print("copying " + str(onefile_src_path) + " to " + self.test_run_path )
                            self.util.copyOneFile(onefile_src_path,self.test_run_path)
                            if Path(onefile).is_file() and (Path(onefile).suffix=='.gsf' or Path(onefile).suffix=='.rb'):
                                #if Path(onefile).suffix=='.rb':
                                    #print("reading rb file: ", onefile)
                                self.CheckRequiredFiles(onefile)
        print("file resolve start ....done:")

    def CheckRequiredFiles2(self, commandline):
        for ext in self.input_file_ext_list:
            search_result = re.search(r'([^\s\\]*\.' + ext + ')', commandline)
            if search_result:
                required_file = search_result.group(1)
                self.test_required_files.append(required_file)
        self.test_required_files = list(set(self.test_required_files))
    def CheckRequiredFiles(self, gsf_path):
        required_file_list = list()
        if Path(gsf_path).is_file():
            with open(gsf_path, encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines:
                    for ext in self.input_file_ext_list:
                        search_result = re.search(r'"(.+\.'+ ext +')"', line)
                        if search_result:
                            required_file = search_result.group(1)
                            self.test_required_files.append(required_file)

                    search_result = re.search(r'.include\s+"(.+)"', line)
                    if search_result:
                        required_file = search_result.group(1)
                        self.test_required_files.append(required_file)

                    search_result = re.search(r'require \s*"(.+)"', line)
                    if search_result:
                        required_file = search_result.group(1)
                        if Path(required_file).suffix != '.rb':
                            required_file = required_file + ".rb"
                        self.test_required_files.append(required_file)

                    search_result = re.search(r':clip\s+=>\s*"(.+)"', line)
                    if search_result:
                        required_file = search_result.group(1)
                        self.test_required_files.append(required_file)
        self.test_required_files = list(set(self.test_required_files))


class UnitResult:
    def __init__(self):
        self.type = "gsf" # gsf or cfg
        self.pass_num = 0
        self.fail_num = 0
        self.total_num = 0
        self.pass_rate = 0.0
        self.invalid_num = 0
        self.unit_name =""
        self.regress_time = 0
        self.html_report_path =""

    def getSummary(self, summary):
        self.pass_num = summary["pass_tests"]
        self.fail_num = summary["fail_tests"]
        self.invalid_num = summary["invalid_tests"]
        self.total_num = summary["total_tests"]
        if self.total_num != 0:
            self.pass_rate = '{:.2f} %'.format((float(self.pass_num) / float(self.total_num)) * 100)
        else:
            self.pass_rate = '{:.2f} %'.format(0 * 100)
        self.regress_time = summary["regress_time"]
        utility = Util.Utility()
        #self.regress_time = utility.convertSecToHourMinSec(self.regress_time)

    def printResult(self):
        print(self.unit_name + ": " + "pass= " + str(self.pass_num) + " total_tests= " + str(self.total_num)+ " pass_rate= " + str(self.pass_rate) + " regress_time= " + str(self.regress_time))

class TestResult:
    def __init__(self):
        self.fatal_errors = list()
        self.warns = list()
        self.checker_mismatch = list()
        self.env_errors = list()
        self.grits_errors = list()
        self.fulsim_errors = list()
        self.lily_errors = list()
        self.overall_status = "NOTRUN" # "NOTRUN" "RUN" "DONE"
        self.grits_compile_status = "N/A"
        self.fulsim_compile_status = "N/A"
        self.lily_compile_status = "N/A"
        self.compare_status = "N/A"
        self.test_status = "N/A"
        # aubload run time
        self.test_runtime = 0
        self.grits_runtime = 0
        self.PeakWorkingSetSize = 0
        self.PeakPagefileUsage = 0
        self.grits_compile_file = ''
        self.fulsim_compile_file = ''
        self.lily_compile_file = ''
        self.compare_file = ''
        self.invalid_message = ""
        self.virtual_path =""
        self.test_total_frame = 0

class TestRunInfo:
    def __init__(self):
        self.grits_exe = None #path
        self.grits_rb = None #path
        self.aubload_exe = None #path
        self.seed = 1
        self.grits_option =""
        self.aubload_option = ""
        self.exedir_path = None
        self.run_grits = False
        self.run_aubload = False
        self.run_compare = False


class TestRunner:
    def __init__(self):
        self.path = os.getcwd()
        self.util = Util.Utility()
        self.gold_include_name_list = list()
        self.gold_exclude_name_list = list()
        self.is_win_os = False
        self.project_name = ""
        if re.search("windows", platform.system(), re.IGNORECASE):
            self.is_win_os = True
        self.axe_resolve_files= list()
        self.axe_resolve_files.append("Axe.config")
        self.axe_resolve_files.append("Axe.Credential.dll")
        self.axe_resolve_files.append("AxeCommon.dll")
        self.axe_resolve_files.append("AxeCommonLib")
        self.axe_resolve_files.append("AxeFileResolver")
        self.axe_resolve_files.append("AxeFileResolver.exe")
        self.axe_resolve_files.append("AxeFileResolver.exe.config")
        self.axe_resolve_files.append("AxeMessageBroker.dll")
        self.axe_resolve_files.append("CSharpDotNet4Utilities.dll")
        self.axe_resolve_files.append("CSharpUtilities.dll")
        self.axe_resolve_files.append("Newtonsoft.Json.dll")
        self.axe_resolve_files.append("NLog.dll")
        self.axe_resolve_files.append("Sentry.dll")
        self.axe_resolve_files.append("Sentry.NLog.dll")
        self.axe_resolve_files.append("SharpSvn.dll")
        self.beyond_compare = r'"C:\Program Files\Beyond Compare 4\BCompare.exe"'
        if not  Path(r"C:\Program Files\Beyond Compare 4\BCompare.exe").is_file():
            self.beyond_compare = r'"C:\Program Files (x86)\Beyond Compare 3\BCompare.exe"'

    def run(self,testRun:TestRun):
        try:
            if testRun.run_cfg:
                self.runCFG(testRun)
            if testRun.run_grits and testRun.valid_test:
                self.runGrits(testRun)
            if testRun.run_aubload and testRun.valid_test:
                self.runAubLoad(testRun)
            if testRun.run_lily and testRun.valid_test:
                self.runLily(testRun)

            if testRun.run_compare and testRun.valid_test:
                self.compareWithGold(testRun)
            if testRun.run_gold != "no" and testRun.valid_test:
                self.runGoldnization(testRun)
            if testRun.cleanup and testRun.valid_test:
                self.cleanupTest(testRun)
        except  Exception as e:
                print(e)


    def runATE(self,testRun:TestRun):
        testRun.test_result.fulsim_compile_status = "PASS"
        ate_exe = os.path.normpath(testRun.aubload_exe)
        work_path = os.path.normpath(testRun.test_run_path)
        #aubload_option = testRun.aubload_option
        ate_compile_file = testRun.test_name+".txt"
        testRun.test_result.fulsim_compile_file = os.path.normpath(Path(str(os.path.join(work_path, ate_compile_file))))

        os.chdir(work_path)

        atefile_path_list = list()

        for root, dirs, files in os.walk(work_path):
            for ate_file in files:
                if ate_file.endswith('.ate'):
                    aub_path = os.path.join(work_path, ate_file)
                    atefile_path_list.append(aub_path)

        if len(atefile_path_list) == 0:
            testRun.test_result.fulsim_compile_status = "FAIL"
            testRun.test_result.fulsim_errors.append("ate file does not exist")

            with open(ate_compile_file ,"w") as fw:
                for line in testRun.test_result.fulsim_errors:
                    fw.write(line)
                testRun.test_file_relative_path_list.append(testRun.test_result.fulsim_compile_file)
            return

        atefile_path_list.sort(key=os.path.getctime)
        if len(atefile_path_list) >1:
            print()
            print('Warning: more than one aub file found')
            for ate_file_path in atefile_path_list:
                print(ate_file_path)

        latest_ate_file_path = atefile_path_list[-1]
        latest_ate_name = os.path.basename(latest_ate_file_path)
        ate_cmd = str(os.path.normpath(ate_exe)) + " " + str(latest_ate_name)

        print("ate_cmd: ", ate_cmd)
        print("Running ATE_main at", testRun.test_run_path, end='')
        fout = open(ate_compile_file,"w")
        #ferr = open(fulsim_compile_error_file,"w")
        axe_run = subprocess.run(ate_cmd, shell=True, stdout=fout, stderr=fout, timeout=40*60) #40 minute sec
        fout.close()
        if axe_run.returncode != 0:
            testRun.test_result.fulsim_compile_status = "FAIL"
            testRun.test_result.fulsim_errors.append(axe_run.stderr)
        else:
            testRun.test_result.fulsim_compile_status = "PASS"

        print(" ==>", testRun.test_result.fulsim_compile_status)

    def runCmodel(self,testRun:TestRun):
        if testRun.project_id == "ate":
            self.runATE(testRun)
        else:
            raise("this CModle is not supported")
        if testRun.run_compare:
            self.compareWithGold(testRun)
        if testRun.run_gold != "no" and testRun.valid_test:
            self.runGoldnization(testRun)

    def cleanupTest(self, testRun):
        work_path = testRun.test_run_path
        work_path = os.path.normpath(work_path)
        print("Running test cleaning up at", work_path, end='')
        all_file_relatvie_paths = self.util.GetAllFileRelativePathsFromDir(work_path)
        for file_relative_path in all_file_relatvie_paths:
            file_name = os.path.basename(file_relative_path)
            if not self.util.findItemInList(file_name,testRun.test_file_relative_path_list) and not self.util.findItemInList(file_name,testRun.gold_file_relative_path_list):
                file_path = os.path.join(work_path,file_relative_path)
                if Path(str(file_path)).is_file():
                    try:
                        os.remove(file_path)
                    except:
                        print("Error while deleting file ", file_path)
        # remove empty folders
        all_folder_paths = self.util.GetAllfolderPathsFromDir(work_path)
        for folder_path in all_folder_paths:
            if Path(folder_path).is_dir() and self.util.IsDirEmpty(folder_path):
                try:
                    shutil.rmtree(folder_path)
                except:
                    print("Error while deleting folder ", folder_path)
        print("==> done")


    def runCFG(self, testRun: TestRun):
        work_path = testRun.test_run_path
        work_path = os.path.normpath(work_path)
        gsf_file = testRun.gsf_name
        gsf_path = os.path.join(work_path, gsf_file)
        os.chdir(work_path)
        if Path(gsf_path).is_file():
            print("skipped disp tool, as gsf file exists")
            return

        perf_exe = "/usr/intel/pkgs/perl/5.14.1-threads/bin/perl"
        if self.is_win_os:
            perf_exe = 'perl'
        disp_cmd = perf_exe + " " + testRun.disp_setup_exe + " " +  testRun.disp_options
        disp_out = "disp.out"
        fout = open(disp_out, "w")
        print("working path : ", work_path)
        print("disp_cmd: ", disp_cmd)

        print("Running disp tool at", work_path, end='')
        # ferr = open(grits_compile_file, "w")
        disp_run = subprocess.run(disp_cmd, shell=True, stdout=fout, stderr=fout, timeout=20 * 40)  # 20 min
        fout.close()



    def runGrits(self,testRun:TestRun):
        grits_exe = testRun.grits_exe
        grits_exe = os.path.normpath(grits_exe)
        #print("grits_exe: ", grits_exe)
        grits_rb = testRun.grits_rb
        grits_rb = os.path.normpath(grits_rb)
        work_path = testRun.test_run_path
        work_path = os.path.normpath(work_path)
        #seed = testRun.seed
        grits_option = testRun.grits_option
        gsf_file = testRun.gsf_name
        gsf_path = os.path.join(work_path,gsf_file)
        gsf_path = os.path.normpath(gsf_path)
        testRun.test_result.grits_compile_status = "N/A"
        if testRun.file_identifier!='':
            grits_compile_file = "grits_"+ testRun.file_identifier + testRun.time_stamp + ".out"
        else:
            grits_compile_file = "grits_"+  testRun.time_stamp + ".out"

        os.chdir(work_path)
        if not (Path(gsf_path).is_file()):
            fout = open(grits_compile_file, "w") #testRun.test_result.invalid_message = gsf_file + " does not exist"
            fout.write(gsf_file + " does not exist")
            fout.close()
            testRun.test_result.grits_compile_status = "FAIL"
            testRun.test_result.grits_compile_file =  Path(os.path.join(work_path, grits_compile_file))
            testRun.test_result.grits_compile_file = os.path.normpath(testRun.test_result.grits_compile_file)
            return
        if(Path(grits_rb).is_file()):
            grits_cmd = "ruby " + str(grits_rb) + " " + str(gsf_file) + " " + testRun.grits_option
        elif (Path(grits_exe).is_file()):
            grits_cmd = str(grits_exe) + " " + str(gsf_file)  + " " + testRun.grits_option
        else:
            testRun.test_result.grits_compile_status = "FAIL"
            testRun.test_result.fatal_errors.append("Grits executable file not found")
            return
        if testRun.file_identifier != '':
            grits_cmd =  grits_cmd  +   " -FileIdentifier " + testRun.file_identifier


        print("Running grits at", work_path)
        print("grits_cmd: ", grits_cmd)

        #grits_compile_err_file = "grits.out"
        testRun.test_result.grits_compile_file =  Path(os.path.join(work_path, grits_compile_file))
        testRun.test_result.grits_compile_file = os.path.normpath(testRun.test_result.grits_compile_file)
        fout = open(grits_compile_file, "w")
        #ferr = open(grits_compile_file, "w")
        grits_run = subprocess.run(grits_cmd,shell=True, stdout=fout, stderr=fout, timeout=120*60) #2 hours
        fout.close()
        testRun.test_file_relative_path_list.append(testRun.test_result.grits_compile_file)
        #ferr.close()
        #print("grits_run.returncode", grits_run.returncode)
        #print("grits_run.stdout: ", grits_run.stdout)
        #print("grits_run.stderr: ", grits_run.stderr)
        if grits_run.returncode != 0:
            #testRun.test_result.overall_status = "FAIL"
            testRun.test_result.grits_compile_status = "FAIL"
            testRun.test_result.grits_errors.append(grits_run.stderr)
            #testRun.test_result.fatal_errors.append("grits compile failed")
            #Change to WARN if  grits log has "Test case * generated"
            with open(grits_compile_file,'r') as f:
                grits_data = f.readlines()
                for line in grits_data:
                    if line != None:
                        if "Test case" in line and "generated" in line:
                            testRun.test_result.grits_compile_status = "WARN"
                            break
        else:
            testRun.test_result.grits_compile_status = "PASS"

        if testRun.test_result.grits_compile_status == "PASS" or testRun.test_result.grits_compile_status == "WARN":
            with open(grits_compile_file, 'r') as f:
                grits_data = f.readlines()
            for line in grits_data:
                search_result = re.search(r"Grits TestTime.*\((.*) sec", str(line))
                if search_result:
                    testRun.test_result.grits_runtime = search_result.group(1)
                else:
                    search_result = re.search(r"totaling.*(.*) sec", str(line))
                    if search_result:
                        testRun.test_result.grits_runtime = search_result.group(1)
            testRun.test_result.grits_runtime = Decimal(testRun.test_result.grits_runtime) / 60
            testRun.test_result.grits_runtime = round(testRun.test_result.grits_runtime, 2)

        print(" ==>", testRun.test_result.grits_compile_status)

    def runGoldnization(self, testRun):
        #grit.out and fulsim log file should not be goldnized.
        testRun.test_file_relative_path_list.append(testRun.test_result.grits_compile_file)
        testRun.test_file_relative_path_list.append(testRun.test_result.fulsim_compile_file)
        print("Goldnizing test " + testRun.test_name,end='')
        if testRun.test_result.grits_compile_status == "FAIL" or testRun.test_result.fulsim_compile_status == "FAIL":
            print(" ==> skipped")
            testRun.goldnize_status = "FAIL"
            return


        self.generateOneTestGold(testRun)

    def removeItemFromList(self, excludeList: list, itemList:list):
        new_list = list()
        for item in itemList:
            to_be_removed = False
            for exclude_item in excludeList:
                if str(item).strip() == str(exclude_item).strip():
                    to_be_removed = True
                    break
            if not to_be_removed:
                new_list.append(item)
        return new_list

    def generateOneTestGold(self, testRun:TestRun):
        all_file_paths = self.util.GetAllFilePathsFromDir(testRun.test_run_path)
        test_exist_goldfolder_path = os.path.join(testRun.test_run_path, "gold")
        all_exist_goldfile_paths = list()
        if Path(test_exist_goldfolder_path).is_dir():
            all_exist_goldfile_paths = self.util.GetAllFilePathsFromDir(test_exist_goldfolder_path)

        if len(all_exist_goldfile_paths) > 0:
            all_file_paths = self.removeItemFromList(all_exist_goldfile_paths,all_file_paths) # gold folder files is not genrated by runing the test, should not be goldnized.
        os.chdir(testRun.test_run_path)

        for file_path in all_file_paths:

            if len(self.gold_include_name_list) >0:
                os.chdir(testRun.test_run_path)
                relatvie_file_path = os.path.relpath(file_path)
                if not self.util.regularExpressHit(relatvie_file_path, self.gold_include_name_list):
                    continue
                dir_path = os.path.dirname(relatvie_file_path)
            if len(self.gold_exclude_name_list) >0:
                os.chdir(testRun.test_run_path)
                relatvie_file_path = os.path.relpath(file_path)
                if self.util.regularExpressHit(relatvie_file_path, self.gold_exclude_name_list):
                    continue

            if not self.util.hasDataInFile(file_path):
                continue
            relative_file_path = os.path.relpath(file_path)
            # targ_tradi_gold_file_path  =  os.path.join(testRun.traditional_goldnize_path,relative_file_path)
            # dir_tradi_path = os.path.dirname(targ_tradi_gold_file_path)
            target_path = testRun.goldenized_test_gold_path
            if dir_path !="":
                target_path = os.path.join(target_path,dir_path)
            Path(target_path).mkdir(parents=True, exist_ok=True)
            #Path(dir_tradi_path).mkdir(parents=True, exist_ok=True)
            #self.util.copyOneFile(file_path, dir_tradi_path)
            self.util.copyOneFile(file_path, target_path)

        if testRun.copy_test:
            self.util.CopyMultifiles(testRun.test_src_file_paths, testRun.goldenized_test_path)

        if self.util.DirHasFiles(testRun.goldenized_test_gold_path,2): # and not self.util.IsDirEmpty(testRun.traditional_goldnize_path):
               testRun.goldnize_status = "SUCCESS"
               print("==> ", testRun.goldnize_status )
        else:
            testRun.goldnize_status = "EMPTY"
            print("==> ", testRun.goldnize_status )
    def runLily(self,testRun:TestRun):
        lily_exe = os.path.normpath(testRun.lily_exe)
        work_path = os.path.normpath(testRun.test_run_path)
        lily_compile_file = "lily" + testRun.time_stamp + ".txt"
        testRun.test_result.lily_compile_file = os.path.normpath(Path(os.path.join(work_path, lily_compile_file)))
        print("Running Lily at", testRun.test_run_path)
        os.chdir(work_path)
        gsf_file = testRun.gsf_name

        lily_cmd = str(os.path.normpath(lily_exe)) + " " + str(gsf_file) + " " + testRun.lily_options
        #print("grits_option:", grits_option)
        #print("aubload_optoin:", aubload_optoin)
        #print("fulsim_option:", fulsim_option)
        print("lily commandline:",lily_cmd)
        #print("lily commandline:", lily_cmd, end='')
       # print("lily commandline:")
        testRun.test_result.lily_compile_status = "FAIL"
        fout = open(lily_compile_file,"w")

        lily_run = subprocess.run(lily_cmd,shell=True, stdout=fout, stderr=fout, timeout=20*40) #20 min
        fout.close()
        testRun.test_file_relative_path_list.append(testRun.test_result.lily_compile_file)
        os.chdir(work_path)
        testRun.test_result.lily_compile_status = "FAIL"
        grits_pass = False
        aubload_pass = False
        lilyx_pass = False
        solution_pass = False
        compiler_pass = False
        fulsim_tbx_async_pass = False
        fulsim_tbx_stage_pass = False
        test_pass = False
        grits_warn = False
        with open(lily_compile_file, 'r') as f:
            lily_data = f.readlines()
            for line in lily_data:
                if line.find("Grits") != -1:
                    if line.find("Grits Stage Completed Successfully") != -1:
                        grits_pass = True
                    elif line.find("Grits Warning") != -1:
                        grits_warn = True
                if line.find("AubLoad") != -1 and line.find("AubLoad Stage Completed Successfully") != -1:
                    aubload_pass = True
                if line.find("LilyX") != -1 and line.find("LilyX Stage Completed Successfully") != -1:
                    lilyx_pass = True
                if line.find("Solution Cleaner") != -1 and line.find(
                        "Solution Cleaner Stage Completed Successfully") != -1:
                    solution_pass = True
                if line.find("Compiler") != -1 and line.find("Compiler Stage Completed Successfully") != -1:
                    compiler_pass = True
                if line.find("Fulsim TBX") != -1 and line.find(
                        "Fulsim TBX Async Start Stage Completed Successfully") != -1:
                    fulsim_tbx_async_pass = True
                if line.find("Test") != -1 and line.find("Test Stage Completed Successfully") != -1:
                    test_pass = True
                if line.find("Fulsim TBX") != -1 and line.find("Fulsim TBX Stage Completed Successfully") != -1:
                    fulsim_tbx_stage_pass = True
        if grits_warn:
            if aubload_pass and lilyx_pass and solution_pass and compiler_pass and fulsim_tbx_async_pass and fulsim_tbx_stage_pass and test_pass:
                testRun.test_result.lily_compile_status = "WARN"
        elif grits_pass and aubload_pass and lilyx_pass and solution_pass and compiler_pass and fulsim_tbx_async_pass and fulsim_tbx_stage_pass and test_pass:
            testRun.test_result.lily_compile_status = "PASS"
        else:
            testRun.test_result.lily_compile_status = "FAIL"


        print(" ==>", testRun.test_result.lily_compile_status)




    def runAubLoad(self,testRun):
        if testRun.test_result.grits_compile_status == "FAIL":
            testRun.test_result.fulsim_compile_status = "N/A"
            print("Running AubLoad ==> Skipped"," ==>", testRun.test_result.fulsim_compile_status)
            return

        testRun.test_result.fulsim_compile_status = "PASS"
        aubload_exe = os.path.normpath(testRun.aubload_exe)
        work_path = os.path.normpath(testRun.test_run_path)
        w_option = ''
        test_name = testRun.test_name[:10]
        if testRun.file_identifier != '':
            fulsim_compile_file = test_name + "_" + testRun.file_identifier
            w_option = '-w ' +  testRun.file_identifier
            testRun.dump_path = os.path.join(testRun.test_run_path, testRun.file_identifier)
        else:
            fulsim_compile_file = test_name
            testRun.dump_path =testRun.test_run_path
        fulsim_compile_file = str(fulsim_compile_file).replace('#','_')
        fulsim_compile_file =  fulsim_compile_file + testRun.time_stamp +  ".txt"

        testRun.test_result.fulsim_compile_file = os.path.normpath(Path(os.path.join(work_path, fulsim_compile_file)))

        aub_paths = list()

        for root, dirs, files in os.walk(work_path):
            for aub_file in files:
                if aub_file.endswith('.aub') and str(aub_file).find(testRun.file_identifier)!= -1:
                    aub_path = os.path.join(work_path, aub_file)
                    aub_paths.append(aub_path)

        os.chdir(work_path)

        print("Running AubLoad at", testRun.test_run_path, end='')
        if len(aub_paths) == 0:
            testRun.test_result.fulsim_compile_status = "FAIL"
            testRun.test_result.fulsim_errors.append("Aub file does not exist")
            print(" ==>", testRun.test_result.fulsim_compile_status)
            with open(fulsim_compile_file ,"w") as fw:
                for line in testRun.test_result.fulsim_errors:
                    fw.write(line)
                testRun.test_file_relative_path_list.append(testRun.test_result.fulsim_compile_file)
            return

        aub_paths.sort(key=os.path.getctime)
        if len(aub_paths) >1:
            print()
            print('Warning: more than one aub file found')
            for aub_path in aub_paths:
                print(aub_path)

        latest_aub_path = aub_paths[-1]
        latest_aub_name = os.path.basename(latest_aub_path)

        if w_option != '':
            aub_cmd = str(os.path.normpath(aubload_exe)) + " " + str(latest_aub_name) + " " + testRun.aubload_option + " " + w_option

        else:
            aub_cmd = str(os.path.normpath(aubload_exe)) + " " + str(latest_aub_name) + " " + testRun.aubload_option


        if re.search("sfc", testRun.aubload_option) or re.search("ve", testRun.aubload_option) or re.search("all", testRun.aubload_option):
            Path("fdve").mkdir(parents=True, exist_ok=True)

        print("aub_cmd: ", aub_cmd)

        if testRun.test_result.grits_compile_status == "FAIL":
            testRun.test_result.fulsim_compile_status = "N/A"
            print(" ==> skipped")
            return
        fout = open(fulsim_compile_file,"w")

        aub_run = subprocess.run(aub_cmd, shell=True, stdout=fout, stderr=fout, timeout=120*60) #2 hours
        fout.close()
        testRun.test_file_relative_path_list.append(testRun.test_result.fulsim_compile_file)

        os.chdir(work_path)
        if aub_run.returncode != 0:
            testRun.test_result.fulsim_compile_status = "FAIL"
            testRun.test_result.fulsim_errors.append(aub_run.stderr)
            with open(fulsim_compile_file,'r') as f:
                aub_data = f.readlines()
                for line in aub_data:
                    if line != None:
                        if "Success" in line:
                            testRun.test_result.fulsim_compile_status = "WARN"
        else:
            testRun.test_result.fulsim_compile_status = "PASS"

        if testRun.test_result.fulsim_compile_status == "PASS" or testRun.test_result.fulsim_compile_status == "WARN":
            testRun.test_result.test_runtime = 0
            testRun.test_result.PeakWorkingSetSize = 0
            testRun.test_result.PeakPagefileUsage = 0
            with open(fulsim_compile_file,'r') as f:
                aub_data = f.readlines()
            for aub_line in aub_data:
                search_result = re.search(r"UserTime:\s+(.*) seconds", str(aub_line))
                if search_result:
                    testRun.test_result.test_runtime = search_result.group(1)

                search_result = re.search(r"PeakWorkingSetSize\): (.*)KB", str(aub_line))
                if search_result:
                    testRun.test_result.PeakWorkingSetSize = search_result.group(1)

                search_result = re.search(r"PeakPagefileUsage\): (.*)KB", str(aub_line))
                if search_result:
                    testRun.test_result.PeakPagefileUsage = search_result.group(1)
                #Send Frame # 1 of 3 to Fulsim
                search_result = re.search(r"end Frame #.*of (\d+) to Fulsim", str(aub_line))
                if search_result:
                    testRun.test_result.test_total_frame = search_result.group(1)

            #change to min
            testRun.test_result.test_runtime = Decimal(testRun.test_result.test_runtime)/60
            testRun.test_result.test_runtime = round( testRun.test_result.test_runtime,2)
            #change to MB
            testRun.test_result.PeakWorkingSetSize = Decimal(testRun.test_result.PeakWorkingSetSize) / 1024
            testRun.test_result.PeakWorkingSetSize = round(testRun.test_result.PeakWorkingSetSize, 2)
            testRun.test_result.PeakPagefileUsage = Decimal(testRun.test_result.PeakPagefileUsage) / 1024
            testRun.test_result.PeakPagefileUsage = round(testRun.test_result.PeakPagefileUsage, 2)
        print(" ==>", testRun.test_result.fulsim_compile_status)

    def compareWithGold(self,testRun):
        work_path = testRun.test_run_path
        print("Gold path: ",testRun.gold_work_path)
        print("Test path: ", work_path)
        print("comparing to gold: ", work_path, end ='')

        if testRun.test_result.grits_compile_status == "FAIL" or testRun.test_result.fulsim_compile_status == "FAIL" or not os.path.isdir(testRun.gold_work_path):
            testRun.test_result.compare_status = "N/A"
            print(" ==> skipped")
            return
        if testRun.file_identifier != '':
            compile_file = "compare_result" + "_" + testRun.file_identifier + testRun.time_stamp + ".txt"

        else:
            compile_file = "compare_result"  + testRun.time_stamp + ".txt"
        testRun.test_result.compare_file = os.path.normpath(os.path.join(work_path, compile_file))
        utility = Util.Utility()
        testRun.test_result.compare_status = "PASS"
        os.chdir(testRun.gold_work_path)
        all_gold_file_paths = utility.GetAllFilePathsFromDir(testRun.gold_work_path)
        #all_gold_file_paths = testRun.findProjectSpecificGold(all_gold_file_paths)


        if len(all_gold_file_paths) == 0: # if there is no gold files
            testRun.test_result.compare_status = "N/A"
            print(" ==> skipped")
            return
        else:
            testRun.gold_file_relative_path_list.extend(all_gold_file_paths)

        for gold_path in all_gold_file_paths:
            gold_path = gold_path.replace('\\', '/')
            if str(gold_path).find('__') !=-1:
                continue
            relative_gold_path = os.path.relpath(Path(gold_path))

            if Path(gold_path).suffix == '.swp': # temp file
                continue
            if (Path(gold_path).suffix != '.ckr' and Path(gold_path).suffix != '.tkn'):

                output_file_path = Path(os.path.join(str(testRun.dump_path), str(relative_gold_path)))
                file_name = os.path.basename(output_file_path)
                ckr_file_name = file_name.replace(Path(file_name).suffix, ".ckr")
                ck_file_path = None
                if testRun.ckr_folder_path != None and testRun.ckr_folder_path != "":
                    ck_file_path = os.path.join(testRun.ckr_folder_path, ckr_file_name)
                if os.path.isfile(output_file_path):
                    if ck_file_path != None and os.path.isfile(ck_file_path):
                        self.CompareTwoFile(testRun, gold_path, output_file_path, ck_file_path)
                    else:
                        self.CompareTwoFile(testRun, gold_path, output_file_path, None)
                else:
                    testRun.test_result.compare_status = "FAIL"
                    testRun.test_result.checker_mismatch.append(
                        "Compare error with file not exist: " + str(output_file_path))
            else:
                if Path(gold_path).suffix == '.tkn':
                    with open(testRun.test_result.fulsim_compile_file) as f:
                        aubload_log = f.readlines()
                    with open(gold_path) as f:
                        gold_log = f.readlines()
                    if len(gold_log) > 0 and len(aubload_log) > 0:
                        pass_compare = True
                        for item in gold_log:
                            if not self.util.findItemInList(item,aubload_log):
                                testRun.test_result.compare_status = "FAIL"
                                pass_compare = False
                                break

                        if pass_compare:
                            if self.is_win_os:
                                testRun.test_result.checker_mismatch.append("Match: " + self.beyond_compare + "  "+ str(gold_path) + "  " + str(testRun.test_result.fulsim_compile_file))
                            else:
                                testRun.test_result.checker_mismatch.append("Match: " + 'meld' + "  "+ str(gold_path) + "  " + str(testRun.test_result.fulsim_compile_file))
                        else:
                            if self.is_win_os:
                                testRun.test_result.checker_mismatch.append("Mismatch: " + self.beyond_compare + "  "+ str(gold_path) + "  " + str(testRun.test_result.fulsim_compile_file))
                            else:
                                testRun.test_result.checker_mismatch.append("Mismatch: " + 'meld' + "  "+ str(gold_path) + "  " + str(testRun.test_result.fulsim_compile_file))

                    else:
                        pass

                else:
                    pass
    
        with open(testRun.test_result.compare_file,'w') as f:
            for mismatch in testRun.test_result.checker_mismatch:
                f.write(mismatch+"\n")

        testRun.test_file_relative_path_list.append(testRun.test_result.compare_file)
        print(' ==>', testRun.test_result.compare_status)


    def CompareTwoFile(self,testRun, file1_path, file2_path, ckr_file_path = None ):
        file_compare = "Match"

        # read ckr file
        include_columns = list()
        exclude_columns = list()
        include_rows = list()
        exclude_rows = list()
        if ckr_file_path != None:
            # print("ckr_file_path: ", ckr_file_path)
            # read ckr file
            with open(ckr_file_path) as f:
                lines = f.readlines()
                for line in lines:
                    # print("ckrline:", line)
                    line = line.strip()
                    if re.search("^#", line):
                        continue
                    splits = line.split()
                    if splits[0] == "exlude" or splits[0] == "exclude":  # e.g. exlude col 1
                        if re.search("col", line):
                            exclude_columns = splits[2:]
                        else:
                            exclude_rows = splits[2:]
                        # print("exclude_columns: ", exclude_columns)
                    if splits[0] == "include" or splits[0] == "inlude":  # e.g. include col 8 9 10
                        if re.search("col", line):
                            include_columns = splits[2:]
                        else:
                            include_rows = splits[2:]
                        # print("include_columns: ", include_columns)
        else:
            pass

        # .txt, .in and .out files are plain txt files
        if (Path(file1_path).suffix != '.txt' and Path(file1_path).suffix != '.in' and Path(file1_path).suffix != '.out' and Path(file1_path).suffix != '.md5'):
            #binary file
            with open(file1_path, 'rb') as file1:
                data1 = file1.read()
            with open(file2_path, 'rb') as file2:
                data2 = file2.read()

            if data1 == data2:
                #print("Compare match: ", str(file1_path), str(file2_path))
                pass

            else:
                file_compare = "Mismatch"
                testRun.test_result.compare_status = "FAIL"
        else: # checker file
            fh1 = open(file1_path, "r")
            fh2 = open(file2_path, "r")
            line1s = fh1.readlines()
            line2s = fh2.readlines()
            total1 = len(line1s)
            total2 = len(line2s)
            if total1 != total2:
                file_compare = "Mismatch"
                testRun.test_result.compare_status = "FAIL"
            else:
                for i in range(total1): # 0 based
                    if str(i + 1) in exclude_rows: #exclude_rows is 1 based
                        # print(i, "in exclude: skipped")
                        # raise("stop")
                        continue
                    line1 = line1s[i]
                    line1 = line1.strip()
                    if not line1:
                        continue
                    line2 = line2s[i]
                    line2 = line2.strip()
                    #print("line1: ", line1)
                    #print("line2: ", line2)
                    if re.search("--", line1):
                        #print (" ===> skipped")
                        continue
                    if Path(file1_path).suffix == '.out' or  Path(file1_path).suffix == '.in':  # dram files
                        line1splits = line1.split()
                        line2splits = line2.split()
                        if line1splits[1:] != line2splits[1:]: #only compare data not addresss.
                            file_compare = "Mismatch"
                            testRun.test_result.compare_status = "FAIL"
                            break
                    elif len(exclude_columns) == 0 and len(include_columns) ==0 and len(exclude_rows) == 0 and len(include_rows) ==0 :
                        if line1 == line2:
                            #print(" ===> match")
                            pass
                        else:
                            #print("line1: ", line1)
                            #print("line2: ", line2)
                            #print(" ===> mismatch")
                            file_compare = "Mismatch"
                            testRun.test_result.compare_status = "FAIL"
                            break

                    else:
                        line1splits = line1.split()
                        line2splits = line2.split()
                        #print("line1splits: ", line1splits)
                        #print("line1splits: ", line2splits)
                        for i in range(len(line1splits)):

                            if len(exclude_columns) != 0:
                                # print("exclude_columns: ", exclude_columns)
                                if str(i) in exclude_columns:
                                    # print(i, "in exclude: skipped")
                                    # raise("stop")
                                    #print(i,"column data",line1splits[i], line2splits[i], " == >skipped")
                                    continue
                            if len(include_columns) != 0:
                                # print("include_columns: ", include_columns)
                                if i not in include_columns:
                                    # print(i, " not include: skipped")
                                    continue

                            if line1splits[i] == line2splits[i]:
                                pass
                                # print("column", i,  "match: ", line1, line2)
                            else:
                                file_compare = "Mismatch"
                                testRun.test_result.compare_status = "FAIL"
                                break

            #print(file_compare, file1_path)
            fh1.close()
            fh2.close()

        if file_compare == "Match":
            if self.is_win_os:
                testRun.test_result.checker_mismatch.append("Match: " + self.beyond_compare + "  "+ str(file1_path) + "  " + str(file2_path))
            else:
                testRun.test_result.checker_mismatch.append("Match: " + 'meld' + "  "+ str(file1_path) + "  " + str(file2_path))
        else:
            if self.is_win_os:
                testRun.test_result.checker_mismatch.append("Mismatch: "  + self.beyond_compare+ "  "+ str(file1_path) + "  " + str(file2_path))
            else:
                testRun.test_result.checker_mismatch.append("Mismatch: "  + 'meld' + "  "+ str(file1_path) + "  " + str(file2_path))


class YamlTestRunner(TestRunner):
    pass
