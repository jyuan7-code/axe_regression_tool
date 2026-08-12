import json
from pathlib import Path
import re
import platform
import libs.utility as Util
class ExecutionMethod:
    def __init__(self):
        self.name =""
        self.test_software = "XeSim_XE3PV2"
        self.product_config = ""
        self.device_option = ""
        self.grits_options = ""
        self.fulsim_options= ""
        self.FulsimTbxOptions =""
        self.aubload_options = ""
        self.fulsimtbx_options = ""
        self.run_test_options = ""
        self.lilycompile_options = ""
        self.lilyX_options = ""
        self.target_config = ""
        self.agent_type = 'fulsimagent'
        self.project_id = ''

class RegressSetting:
    def __init__(self):
        self.name ="Regression Settings"
        self.aubload_path = ""
        self.grits_path = ""
        self.additional_grits_options = ""
        self.aubload_path = ""
        self.additional_aubload_options = ""
        self.start_time = ""
        self.end_time=""
        self.lily_path = ""
        self.agent_type='fulsimagent'
        self.pass_test_list_path = ""
        self.fail_test_list_path = ""
        self.total_test_list_path = ""
        self.done_test_list_path = ""
        self.notdone_test_list_path =""
        self.invalid_test_list_path = ""
        self.testrun_info_path = ""
        self.warn_test_list_path = ""



class ExecutionSetting:
    def __init__(self, isUTP):
        #self.execution_method_list = list()
        self.all_execution_method_list = list()
        self.is_win_os = False
        self.util = Util.Utility()
        if re.search("windows", platform.system(), re.IGNORECASE):
            self.is_win_os = True
        path_list =  self.util.GetAllFilePathsFromDir('./executions/')

        for eachpath in path_list:
            if self.util.get_file_extension(eachpath) != ".json":
               continue
            print("method stage file name: ", eachpath)
            projectID =''
            if eachpath.find("xe3p_v2")!=-1:
                projectID = "nvl"
            elif eachpath.find("ptl")!=-1:
                projectID = "ptl"
            elif eachpath.find("elg")!=-1:
                projectID = "elg"
            elif eachpath.find("mtl")!=-1:
                projectID = "mtl"
            elif eachpath.find("lnl")!=-1:
                projectID = "lnl"
            elif eachpath.find("cri")!=-1:
                projectID = "cri"
            elif eachpath.find("ttl")!=-1:
                projectID = "ttl"
            elif eachpath.find("main")!=-1:
                projectID = "hml"
            elif eachpath.find("fcs") != -1:
                projectID = "fcs"
            elif eachpath.find("cls") != -1:
                projectID = "cls"
            else:
                print("warning! project not supported: ", eachpath)

            self.readAxeExecutionMethodFromJsonFile(eachpath, self.all_execution_method_list, isUTP, projectID)
        print("=====================")
        print("total: ", len(self.all_execution_method_list))



    def addUniqueExcutionMethodList(self,methodList, method:ExecutionMethod()):
        if len(methodList) ==0:
            methodList.append(method)
        else:
            unique = True
            for one_method in methodList:
                if method.name == one_method.name:
                    unique = False
                    break
            if unique:
                methodList.append(method)

    def generateIPExecutionMethodNameList(self, IpName, methodlist:list, ProjectName):
        ip_method_list= list()
        name =""
        if IpName =="Media":
            name = "Media"

        if IpName =="3D":
            name = "3D"
        if IpName == "UTP":
            name = "UTP"
        if IpName == "2D":
            name = "2D"
        if IpName == "Bullseye":
            name = "Bullseye"
        if len(methodlist) <1:
            return ip_method_list
        else:
            if name =='':
                return ip_method_list
            for method in methodlist:
                if name =="":
                    ip_method_list.append(method)
                else:
                    if name !="UTP":
                        if str(method.name).lower().find(name.lower()) != -1 and str(method.name).lower().find('UTP'.lower()) == -1:
                            ip_method_list.append(method)
                    else:
                        if  str(method.name).lower().find(name.lower()) != -1:
                            ip_method_list.append(method)
            return ip_method_list

    def generateProjectExecutionMethodNameList(self, ProjectName, methodlist: list):
        pro_method_list = list()
        if ProjectName=='':
            return methodlist
        if len(methodlist) < 1:
            return methodlist
        else:
            for method in methodlist:
               if method.project_id == ProjectName:
                    pro_method_list.append(method)

            return pro_method_list

    def generateExecutionMethodNameList(self,if2d, if3d, ifmedia, ifutp, ProjectName):
        name_list = list()
        if len(self.all_execution_method_list) < 1:
            return name_list
        else:
            name_list = self.generateProjectExecutionMethodNameList(ProjectName, self.all_execution_method_list)
            if not if2d:
                d2_list = self.generateIPExecutionMethodNameList("2D",name_list,ProjectName)
                for item in d2_list:
                    name_list.remove(item)

            if not if3d:
                d2_list = self.generateIPExecutionMethodNameList("3D", name_list, ProjectName)
                for item in d2_list:
                    name_list.remove(item)
            if not ifmedia:
                d2_list = self.generateIPExecutionMethodNameList("Media", name_list, ProjectName)
                for item in d2_list:
                    name_list.remove(item)
            if not ifutp:
                d2_list = self.generateIPExecutionMethodNameList("UTP", name_list, ProjectName)
                for item in d2_list:
                    name_list.remove(item)
            return name_list

    def getExecutionMethod(self, name, methodList:list):
        method = ExecutionMethod()
        if len(methodList) < 1:
            return method
        for one_method in methodList:
            if one_method.name == name:
                method = one_method
                break
        return method

    def readAxeExecutionMethodFromJsonFile(self, jsonFilePath, executonMethodList: list, forUTP, projectID):
        print("Reading axe execution methods from ", jsonFilePath)
        print("for UTP:",forUTP)
        if not Path(jsonFilePath).is_file():
            return executonMethodList
        with open(jsonFilePath, 'r') as f_in:
            my_data = json.load(f_in)
        execution_methods_array = my_data['executionMethods']
        # print(execution_methods_array)
        total = len(execution_methods_array)
        for method in execution_methods_array:
            new_method = ExecutionMethod()
            new_method.project_id = projectID
            print("-------------------")
            print("name:", method['name'])
            # print("software:", method['software'])
            # print("agentCommandLine:", method['agentCommandLine'])
            new_method.name = method['name']


            new_method.test_software = method['software']
            print("test_software:", method['software'])
            new_method.agent_type = method['agentCommandLine']
            attributes = method['attributes']
            for one_attrib in attributes:
                # print(one_attrib)
                # print(one_attrib['name'], "=", one_attrib['value'])
                if one_attrib['name'] == 'AubloadOptions':
                    new_method.aubload_options = one_attrib['value']
                    print(one_attrib['name'], "=", new_method.aubload_options)
                if one_attrib['name'] == 'DeviceOption':
                    new_method.device_option = one_attrib['value']
                    print(one_attrib['name'], "=", new_method.device_option)
                if one_attrib['name'] == 'FulsimOptions':
                    new_method.fulsim_options = one_attrib['value']
                    print(one_attrib['name'], "=", new_method.fulsim_options)
                if one_attrib['name'] == 'FulsimTbxOptions':
                    new_method.FulsimTbxOptions = one_attrib['value']
                    print(one_attrib['name'], "=", new_method.FulsimTbxOptions)
                if one_attrib['name'] == 'GritsOptions':
                    new_method.grits_options = one_attrib['value']
                    print(one_attrib['name'], "=", new_method.grits_options)
                if one_attrib['name'] == 'RunTestOptions':
                    new_method.run_test_options = one_attrib['value']
                    print(one_attrib['name'], "=", new_method.run_test_options)
                if one_attrib['name'] == 'LilyCompileOptions':
                    new_method.lilycompile_options = one_attrib['value']
                    print(one_attrib['name'], "=", new_method.lilycompile_options)
                if one_attrib['name'] == 'LilyXOptions':
                    new_method.lilyX_options = one_attrib['value']
                    print(one_attrib['name'], "=", new_method.lilyX_options)
                if one_attrib['name'] == 'TargetConfig':
                    new_method.target_config = one_attrib['value']
                    print(one_attrib['name'], "=", new_method.target_config)

            if new_method.run_test_options !="" and new_method.run_test_options.find("bullseye")!=-1:
                if self.is_win_os:
                    continue
            executonMethodList.append(new_method)
            #if new_method.name.find("2D") != -1:
            #    continue
            #if new_method.name.find("UTP") != -1:
            #    if forUTP:
            #        executonMethodList.append(new_method)
            #else:
            #    if not forUTP:
             #       executonMethodList.append(new_method)

        #print("total methods:", total)
        return execution_methods_array