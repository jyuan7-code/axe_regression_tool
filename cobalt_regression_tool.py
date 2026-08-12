#!/usr/intel/bin python3.7.4

import json
import copy
import platform
from os.path import abspath
import sys
import re
import os
import signal
import tkinter as tk
import tkinter.filedialog
from tkinter import *
from tkinter import ttk
import argparse
#VNC does not have  PTL module installed
if re.search("windows", platform.system(), re.IGNORECASE):
    from PIL import Image,ImageTk

import stat
v_1= sys.version_info[0]
v_2= sys.version_info[1]
v_3= sys.version_info[2]
global your_version
your_version = str(v_1) + "." + str(v_2) + "." + str(v_3)
#print("The version of python you are using: " + your_version)
#print("file: ", os.path.basename(__file__))


def linuxCheckVersion():
    if not re.search("windows", platform.system(), re.IGNORECASE):
       if v_1 > 3:
           return
       else:
           if v_1 <  3:
               assert(False)
           else:
               if v_2 > 7:
                   return
               else:
                   if v_2 < 7:
                       assert(False)
                   else:
                       if v_3  > 4:
                           return
                       else:
                           if v_3  <  4:
                               assert(False)
                           else:
                               return



try:
    linuxCheckVersion()
except:
    print("You are using python", your_version, ". Please try verson >= 3.7.4 ", os.path.basename(__file__))
    exit(0)

from tkinter import messagebox
from tkinter.messagebox import askyesno
import libs.test as Test
import libs.utility as Util
import libs.p4 as P4
import libs.executionSetting  as AxeExecution
import libs.release as fulsimrelease
from pathlib import Path
import  multiprocessing



import webbrowser
import time
import datetime
import random
import shutil
from tkinter import simpledialog
import math
import pickle
import subprocess

if re.search("windows", platform.system(), re.IGNORECASE):
    import psutil

#thread_pool_executor = futures.ProcessPoolExecutor(max_workers=2 * multiprocessing.cpu_count() + 1)
#thread_pool_executor = futures.ThreadPoolExecutor(max_workers=2 * multiprocessing.cpu_count() + 1)

import getpass

class FulsimRegress(Tk):

    def __init__(self):
        super(FulsimRegress, self).__init__()

        self.script_name = os.path.basename(sys.argv[0])
        self.util = Util.Utility()
        self.config_file = None
        cmdline_run = self.parseCmdline()


        self.release_tool = fulsimrelease.FulsimRelease()
        self.user_id = getpass.getuser()
        self.p4client = P4.P4Wrapper(self.user_id )
        self.p4_test_revision = None
        self.src_path_or_testrevsion = ""
        self.regress_base = "" # has regress result_base and regress_test_base
        self.regress_test_base = ""
        self.regress_result_base = ""
        self.project_name = ""
        self.IP_ID = ""


        self.use_p4 = False
        self.use_incredibuild = False
        self.grits_path = ""
        self.aubload_path = ""
        self.grits_option = "" #global
        self.aubload_option = "" # global
        self.required_folders = list()
        self.gold_required_folders = list()
        self.unit_required_folders = list()
        #self.required_folders.append("include")
        #self.required_folders.append("kernels")
        #self.required_folders.append("lib")
        self.grits_rb_path = None
        self.grits_exe_path = None
        self.aubload_exe_path = None
        self.regress_name = ""
        self.list_paths =list()
        self.exclusive_list_paths =list()
        self.suite_name =""

        self.unit_names = ""
        self.json_tests = ""
        self.processRun_runtime= 0 # for each regress
        self.resetRegression()
        self.is_win_os = False
        self.cur_row = 0
        self.gold_include_name_string = ""
        self.gold_exclude_name_string = ""
        self.entry_include_file_string = None
        self.entry_exclusive_file_string = None
        self.entry_out_binary = None
        self.entry_track_file = None

        self.entry_out_binary = None
        self.entry_track_file = None
        self.entry_gold_base = None
        self.entry_copy_test = None

        self.gold_type = "binary"
        self.binary_gold = False
        self.checker_gold = False
        self.dramout_gold = False
        #self.test_suite_list = list()
        self.test_read_list = list()
        self.test_run_list = list()
        self.exclusive_test_run_list = list()
        self.suite_fail_list = list()
        self.run_unit_list = list()
        self.result_list = list()
        self.exclusive_test_read_list = list()
        self.gold_base = ""
        self.test_list_file_path = ""
        self.exclusive_test_list_file_path = ""
        self.full_path_tests = ""
        self.gold_file_list = list()
        self.need_ckr = "no"
        self.copy_test_forgold = True
        self.num_cores = 1

        self.windows_password = None
        self.win_release_web_response = None

        #self.regress_type = "gritsnaubncompare"
        self.run_grits = False
        self.run_aubload = False
        self.run_compare = False
        # goldnation
        self.goldnize  = "no"
        self.cleanup = False
        self.realtime_report = "no"

        self.stop_regress = False
        self.done_regress = False
        self.require_report = False
        self.config_path =""
        self.is_regression_started = False
        self.start_time = 0
        self.run_time = 0 # total run time
        self.html_report_path = ""
        self.summary_html_report_path =""
        self.gold_binary_exclusive_list = list()
        self.gold_include_name_list = "" # include binary and txt files
        self.gold_exclude_name_list = "" # include binary and txt files
        self.new_window = None
        self.config_folder = ""
        self.grits_release_set = list()
        self.grits_version_load = None
        self.aubload_version_load = None
        self.delay_second = -1
        self.previous_done_tests = 0
        self.previous_not_done_tests = 0
        self.previous_pass_tests = 0
        self.previous_fail_tests = 0
        self.previous_invalid_tests = 0
        self.subprocess = None
        self.best_test_revision = 0
        self.axe_execution = AxeExecution.ExecutionSetting(False)

        self.axe_execution_method_list = list()
        self.regress_settings = AxeExecution.RegressSetting()



        if re.search("windows", platform.system(), re.IGNORECASE):
            self.is_win_os = True
            self.python_exe = "python"
        else:
            self.python_exe = "python3"
        #print("self.is_win_os: ", self.is_win_os )
        self.current_path = os.getcwd() # script path

        self.ckr_folder = os.path.join(self.current_path,"ckrfiles")
        self.bin_folder = os.path.join(self.current_path, "bin")
        self.system_ram = 0
        self.run_units = False
        self.run_test_lists = False
        self.run_abs_path_tests = False
        self.run_unit_tests = False
        self.run_exclusive_lists = False
        self.axe_execution_config_ID_list = list()
        self.axe_grits_options=''
        self.axe_aubload_options=''
        # for whole regressions: unit/json_test/test_list/abs test
        self.total_done_list = list()
        self.total_fail_list = list()
        self.total_pass_list = list()
        self.total_invalid_list = list()
        self.selected_axeconfig_list = list()
        self.beyond_compare = r"C:\Program Files\Beyond Compare 4\BCompare.exe"

        if self.is_win_os:
            if not Path(self.beyond_compare).is_file():
                self.beyond_compare = r"C:\Program Files (x86)\Beyond Compare 3\BCompare.exe"
                if not Path(self.beyond_compare).is_file():
                    messagebox.showwarning("Warning!", "Can not find any beyondcompare")

        self.setGui()
        self.processRun_start_time = time.time()
        self.updateRunTime()

        if cmdline_run:
            self.loadConfigureFile(self.config_file)
            self.runGuiRegress()

    def parseCmdline(self):
        parser = argparse.ArgumentParser(
            description="Parse command line arguments",
            exit_on_error=False  # Prevents sys.exit() on argument errors (Python 3.9+)
        )
        parser.add_argument('--filepath', type=str, required=True,
                            help='Path to the configuration file')

        try:
            args = parser.parse_args()
            self.config_file = args.filepath

            # Check if file exists and is accessible
            if Path(self.config_file).is_file():
                print(f"Configuration file found: {self.config_file}")
                return True
            else:
                print(f"Error: Configuration file not found: {self.config_file}")
                return False

        except argparse.ArgumentError as e:
            print(f"Argument parsing error: {e}")
            return False
        except SystemExit:
            # argparse calls sys.exit() on error, catch it to prevent script crash
            print("Error: Invalid command line arguments")
            parser.print_help()
            return False
        except Exception as e:
            print(f"Unexpected error while parsing command line: {e}")
            return False



    def linuxMemoryUsage(self):
        result = os.popen('free -t -g')
        lines = result.readlines()
        result.close()
        memory_info = {}
        for line in lines:

            if str(line).find("Total:") != -1:
                print("line:", line)
                search_result = re.search(r"Total:\s+(\d+)\s+(\d+)\s+(\d+)", str(line))
                if search_result:
                    total_memory = search_result.group(1)
                    used_memory = search_result.group(2)
                    free_memory = search_result.group(3)
                    memory_info =  {"total_memory": total_memory, "used_memory": used_memory,"free_memory": free_memory}

        return memory_info

    def linuxCpuUsage(self):
        if not re.search("windows", platform.system(), re.IGNORECASE):
            result = os.popen('mpstat')
            lines = result.readlines()
            result.close()

            for line in lines:
                if str(line).find("all") != -1:
                    print("line:", line)
                    search_result = re.search(r"all\s+(\d+\.\d+)\s+", str(line))
                    if search_result:
                        usage = search_result.group(1)
                        return usage
    def gotValidDiskPath(self):
        self.saveGuiOutput()
        if self.regress_base == "":
            disk_path = os.getcwd()
        else:
            disk_path = os.path.normpath(self.regress_base)
            while disk_path != "" and not Path(disk_path).is_dir():
                new_disk_path = os.path.dirname(disk_path)
                if new_disk_path =="" or  new_disk_path == disk_path:
                    break
                else:
                    disk_path = new_disk_path
            if not Path(disk_path).is_dir():
                disk_path = os.getcwd()
        return disk_path

    def checkSystemRam(self):
        if self.is_win_os:
            os_version = self.util.get_windows_version()
            os_info  = "Operation System: "  + os_version
            cpu_core = multiprocessing.cpu_count()
            cpu_usage = psutil.cpu_percent()
            cpu_info = "CPU Info: "  + str(cpu_core) + " cores " +", usage " + str(cpu_usage) +"%"
            mem_info = psutil.virtual_memory()
            total_memory = mem_info[0]
            used_memory = mem_info[3]
            free_memory = mem_info[4]
            total_memory = math.ceil(total_memory/(1024*1024*1024)) #GB
            used_memory = math.ceil(used_memory/(1024*1024*1024)) #GB
            free_memory = math.ceil(free_memory/(1024*1024*1024)) #GB
            usage =  round((used_memory/total_memory) * 100, 2)
            memory_info = "Memory Info: total " + str(total_memory) + "GB, " + "used " + str(used_memory) + "GB, " + "free " + str(free_memory) + "GB, " + "usage " + str(usage) +"%"
            disk_path = self.gotValidDiskPath()

            print("disk path =", disk_path)
            stat = shutil.disk_usage(disk_path)
            total_space = math.ceil(stat.total/(1024*1024*1024))
            used_space = math.ceil(stat.used/(1024*1024*1024))
            free_space = math.ceil(stat.free/(1024*1024*1024))
            usage = round((used_space/total_space) * 100, 2)
            disk_info = "Disk Info: total " + str(total_space) + "GB, " + "used " + str(used_space) + "GB, " + "free " + str(free_space) + "GB, " + "usage " + str(usage) +"%"
            print(os_info)
            print(cpu_info)
            print(memory_info)
            print(disk_info)
            global your_version
        else:
            os_version = self.util.get_linux_version()
            os_info = "Operation System: " + os_version
            memory_info = self.linuxMemoryUsage()
            total_memory = memory_info["total_memory"]
            used_memory = memory_info["used_memory"]
            free_memory = memory_info["free_memory"]
            usage =  round(int(used_memory)/int(total_memory) * 100, 2)
            memory_info = "Memory Info: total " + str(total_memory) + "GB, " + "used " + str(used_memory) + "GB, " + "free " + str(free_memory) + "GB, " + "usage " + str(usage) +"%"

            cpu_core = multiprocessing.cpu_count()
            cpu_usage = self.linuxCpuUsage()
            #cpu_usage = psutil.cpu_percent()
            cpu_info = "CPU Info: "  + str(cpu_core) + " cores " +", usage " + str(cpu_usage) +"%"
            total_memory, used_memory, free_memory = map(int, os.popen('free -t -m').readlines()[-1].split()[1:])
            total_memory = math.ceil(total_memory/(1024*1024*1024)) #GB
            used_memory = math.ceil(used_memory/(1024*1024*1024)) #GB
            free_memory = math.ceil(free_memory/(1024*1024*1024)) #GB
            usage =  round((used_memory/total_memory) * 100, 2)
            #memory_info = "Memory Info: total " + str(total_memory) + "GB, " + "used " + str(used_memory) + "GB, " + "free " + str(free_memory) + "GB, " + "usage " + str(usage) +"%"
            disk_path = self.gotValidDiskPath()
            print("disk path =", disk_path)

            stat = shutil.disk_usage(disk_path)
            total_space = math.ceil(stat.total/(1024*1024*1024))
            used_space = math.ceil(stat.used/(1024*1024*1024))
            free_space = math.ceil(stat.free/(1024*1024*1024))
            usage = round((used_space/total_space) * 100, 2)
            disk_info = "Disk Info: total " + str(total_space) + "GB, " + "used " + str(used_space) + "GB, " + "free " + str(free_space) + "GB, " + "usage " + str(usage) +"%"
            print(os_info)
            print(cpu_info)
            print(memory_info) # not accurate in linux
            print(disk_info)
        messagebox.showinfo("System Information ( provided by Python"+ your_version+ ")" , os_info  + "\n" + cpu_info + "\n" + memory_info + "\n" + disk_info )

    def updateGui(self):
        #self.setCatergoryFrame()
        self.setProjectFrame()
        self.setDeviceOptionGui()
        self.setTestListPathGui()
        self.updateAubLoadPathGui()
        self.updateGritsPathGui()
        self.setAubLoadOptionGui()
        self.setAubLoadPathGui()
        self.setGritsOptionGui()
        self.setGritsPathGui()
        self.setTestSourceGui()
        self.setRegressPathGui()
        #self.setRevsionGui()
        self.setCpuCoreGui()
        self.setRegressGui()
        self.setGoldFrameGui()
        #self.setActionGui()
    def remove_transparency(self, image, background_color=(255, 255, 255)):
        if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
            # Ensure the image has an alpha channel
            image = image.convert("RGBA")
            # Create a new background image with a solid color
            background = Image.new("RGB", image.size, background_color)
            # Composite the transparent image onto the solid background
            background.paste(image, mask=image.split()[-1])  # Use the alpha channel as mask
            return background
        else:
            # If the image doesn't have transparency, return it as-is in RGB mode
            return image.convert("RGB")

    def resource_path(self, relative_path):
        """Get the absolute path to a resource."""
        # When running as a PyInstaller bundle
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        # When running as a script
        return os.path.join(os.path.abspath("."), relative_path)

    def setGui(self):
        icon_path = self.resource_path("./icon/intel.GIF")
        if self.is_win_os:
            original_image = Image.open(icon_path)  # Replace with your image path
            # Remove transparency and fix edges
            fixed_image = self.remove_transparency(original_image)
            # Convert the fixed image to a format Tkinter can use
            resized_image = fixed_image.resize((40, 30))
            self.intel_icon = ImageTk.PhotoImage(resized_image)
            self.iconphoto(True, self.intel_icon)
        # Gui
        self.title("Cobalt Regression & Goldenization Tool Version 10.5  by jin.yuan@intel.com 2020. Welcome:  " + str(self.user_id ) + " !")

        self.minsize(500,600)
        if self.is_win_os:
            self.maxsize(1000,1200)
        else:
            self.maxsize(1000,1200)

        self.catergory_frame = ttk.LabelFrame(self, text="", width=800)
        #self.setCatergoryFrame()
        # Create a style
        bold_font = ("Helvetica", 11, "bold")
        self.style = ttk.Style()
        self.style.configure("Custom.TLabelframe.Label", foreground="blue",font=bold_font)
        self.catergory_frame.pack()
        self.createProjectFrame()
        #self.setProjectFrame()

        self.createTestListPathGui()
        self.setTestListPathGui()

        #self.createAubLoadOptionGui()


        self.createAubLoadPathGui()
        self.setAubLoadOptionGui()
        self.setAubLoadPathGui()

        self.createGritsPathGui()
        self.setGritsOptionGui()
        self.setGritsPathGui()

        self.createTestSourceGui()
        self.setTestSourceGui()

        #self.createRegressPathGui()


        #commented out, due to no very useful
        #self.createRevsionGui()
        #self.setRevsionGui()

        self.createCpuCoreGui()
        self.setCpuCoreGui()



        self.createRegressGui()
        self.setRegressPathGui()
        self.setRegressGui()

        self.action_frame = ttk.LabelFrame(self, text="Run Options",style="Custom.TLabelframe")

        self.setActionGui()
        self.action_frame.pack(fill="x")
        self.runinfo_frame = ttk.LabelFrame(self, text="Run Info",style="Custom.TLabelframe")
        self.setRrunInfoGui()
        self.runinfo_frame.pack(fill="x")
        self.createGoldFrameGui()
        if self.entry_goldnize.get() == 'yes':
           self.setGoldFrameGui()
        #self.enableAllGuiItem(self)


    def setRrunInfoGui(self):
        txt = ""
        self.output_info = Text(self.runinfo_frame, height=5, width=220, font=("Helvetica", 10), foreground='blue')
        self.output_info.grid(row=0, column=1)

        # Make sure countdown labels are properly positioned
        self.countdown_label.grid(row=0, column=4, sticky=W, padx=5)
        self.countdown_timer.grid(row=0, column=5, sticky=W, padx=5)


    def setActionGui(self):
        ttk.Button(self.action_frame, text="Save Configuration",
                       command=self.saveConfigure).grid(row=0, column=1,padx=2)
        ttk.Button(self.action_frame, text="Load Configuration",
                       command=self.loadConfigure).grid(row=0, column=2,padx=2)
        s =ttk.Style()
        s.configure('W.TButton',background='gray',foreground='green', fond=('calibri', 20, 'bold', 'underline'))
        self.run_cancel_button  = ttk.Button(self.action_frame, text="Start", style = 'W.TButton', width=12,
                       command=self.runGuiRegress)
        self.run_cancel_button.grid(row=0, column=3,pady=2, padx=2)
        s1 = ttk.Style()
        s1.configure('E.TButton', background='gray', foreground='red', fond=('calibri', 20, 'bold', 'underline'))
        #ttk.Button(self.action_frame, text = "Stop", width=5, style='E.TButton', command=self.stopRegress).grid(row=0, column=4)

        self.pass_fail_str = StringVar()
        self.pass_fail_str.set("")
        self.status_label = ttk.Label(self.action_frame, textvariable = self.pass_fail_str, width=40, anchor=E, font=("Helvetica", 10), foreground = 'blue')
        #self.current_running_unit['frontground'] = 'blue'
        self.status_label.grid(row=0, column=4)
        self.style =ttk.Style()
        self.style.layout('text.Horizontal.TProgressbar',
                     [('Horizontal.Progressbar.trough',
                       {'children': [('Horizontal.Progressbar.pbar',
                                      {'side': 'left', 'sticky': 'ns'})],
                        'sticky': 'nswe'}),
                      ('Horizontal.Progressbar.label', {'sticky': ''})])
        # set initial text
        self.style.configure('text.Horizontal.TProgressbar', text=' ')
        self.progress_bar = ttk.Progressbar(self.action_frame, style='text.Horizontal.TProgressbar',orient="horizontal", length=300, mode='determinate')
        self.progress_bar.grid(row=0, column=5, pady = 10)
        self.progress_bar['maximum'] = 100
        #for i in range(101):
            #time.sleep(0.01)
            #self.progress_bar['value'] = i
            #self.progress_bar.update()

    def updateOutputBox(self, output_info:str, replaceLastline=False):
        if replaceLastline:
            self.output_info.delete("end-1l","end")
        self.output_info.insert(END,"\n" + str(output_info))

    def updateStatusLabel(self, status_info, replaceLastline=False):
        self.pass_fail_str.set(status_info)

    def updateProgressBar(self,  total, total_done):

        if total != 0:
            self.style.configure('text.Horizontal.TProgressbar',
                        text='{:.2f} %'.format((float(total_done)/float(total))*100))  # update label
        else:
            self.style.configure('text.Horizontal.TProgressbar', text='{:.2f} %'.format(0))  # update label

        if total != 0:
            current_done = (float(total_done) / float(total)) * 100
        else:
            current_done = (float(0)) * 100

        self.progress_bar['value'] = current_done
        self.progress_bar.update()

    def changeGoldBaseLableColor(self, event=None):
        if str(self.entry_gold_base.get()).strip() != "":
            self.gold_base_lbe['foreground'] ='#000'
        else:
            self.gold_base_lbe['foreground'] ='#f00'


    def createGoldFrameGui(self):
        self.gold_frame = ttk.LabelFrame(self, text="Goldenize File Options",style="Custom.TLabelframe")

        self.entry_out_binary = BooleanVar()
        self.entry_track_file = BooleanVar()

        # ckr
        #self.entry_need_ckr = StringVar()
        # gold file type
        gold_row = 0
        # Gold base path
        self.gold_base_lbe = ttk.Label(self.gold_frame, text="Gold Base:", foreground='#f00',  width=40, anchor=CENTER)
        self.gold_base_lbe.grid(row=gold_row, column=0)
        self.entry_gold_base = ttk.Entry(self.gold_frame, width=70)
        self.entry_gold_base.grid(row=gold_row, column=1)
        self.entry_gold_base.bind("<KeyRelease>",self.changeGoldBaseLableColor)
        ttk.Label(self.gold_frame, text="", width=5, anchor=CENTER).grid(row=gold_row, column=2)
        ttk.Button(self.gold_frame, text="Select Gold Base Folder", command=self.selectGoldDir).grid(row=gold_row, column=3)

        # if copy required folders
        #gold_row = gold_row + 1
        self.entry_copy_test = StringVar()
        self.entry_copy_test.set(self.copy_test_forgold)
        #ttk.Label(self.gold_frame, text="Copy Test:", width=30, anchor=CENTER).grid(row=gold_row, column=0)
        copy_frame = ttk.Frame(self.gold_frame)
        ttk.Radiobutton(copy_frame, text="yes", value="yes", variable=self.entry_copy_test).grid(row=0, column=0)
        ttk.Radiobutton(copy_frame, text="no", value="no", variable=self.entry_copy_test).grid(row=0, column=1)
        #copy_frame.grid(row=gold_row, column=1)

        gold_row = gold_row + 1
        # gold file type
        gold_type_frame = ttk.Frame(self.gold_frame)
        self.file_type_lbe = ttk.Label(self.gold_frame, text="File Type:", width=40,foreground='#f00', anchor=CENTER)
        self.file_type_lbe.grid(row=gold_row, column=0)

        self.entry_out_binary.set(False)
        ttk.Checkbutton(gold_type_frame, text="Binary Files", variable=self.entry_out_binary,command=self.addRemoveCheckerFrameGui).grid(row= 1,
                                                                                                   column=0)
        ttk.Checkbutton(gold_type_frame, text="Checker Files",variable=self.entry_track_file, command=self.addRemoveCheckerFrameGui).grid(row=1, column=1)

        gold_type_frame.grid(row=gold_row, column=1)

        self.checker_frame = ttk.Frame(self)
        ttk.Label(self.checker_frame, text="Include Name List: ", width=40, anchor=CENTER).grid(row=0, column=0)
        self.entry_include_file_string =  ttk.Entry(self.checker_frame,width=70)
        self.entry_include_file_string .grid(row=0, column=1)

        ttk.Label(self.checker_frame, text="Exlusive Name List: ", width=40, anchor=CENTER).grid(row=1, column=0)
        self.entry_exclusive_file_string =  ttk.Entry(self.checker_frame,width=70)
        self.entry_exclusive_file_string .grid(row=1, column=1)

    def setGoldFrameGui(self):
        #if self.gold_frame == None:
        if self.goldnize  == "yes":
            #self.gold_frame.pack(fill="x")
            self.addGoldFrameGui()
        else:
            self.removeGoldFrameGui()

        if self.binary_gold == "True":
            self.entry_out_binary.set(True)
            self.file_type_lbe['foreground'] = '#000'
        else:
            self.entry_out_binary.set(False)

        if self.checker_gold == "True":
            self.entry_track_file.set(True)
            self.file_type_lbe['foreground'] = '#000'
            self.checker_frame.pack(fill="x")
        else:
            self.entry_track_file.set(False)
            self.checker_frame.pack_forget()

       # self.entry_need_ckr.set(self.need_ckr)

        self.entry_gold_base.delete(0, 'end')
        self.entry_gold_base.insert(0, self.gold_base)
        self.gold_base_lbe['foreground'] = '#000'
        self.entry_copy_test.set(self.copy_test_forgold)
        self.entry_include_file_string.delete(0, 'end') #for gold
        self.entry_include_file_string.insert(0, self.gold_include_name_string)
        self.entry_exclusive_file_string.delete(0, 'end') #for gold
        self.entry_exclusive_file_string.insert(0, self.gold_exclude_name_string)

        #if self.need_ckr == "yes":
         #   self.showCkrFrame()

    def addRemoveCheckerFrameGui(self):
        if self.entry_track_file.get() or self.entry_out_binary.get() or self.binary_gold or self.checker_gold:
            if self.action_frame != None:
                self.action_frame.pack_forget()
            if self.runinfo_frame != None:
                self.runinfo_frame.pack_forget()
            self.checker_frame.pack(fill="x")
            self.file_type_lbe['foreground'] ='#000'
            self.action_frame.pack(fill="x")
            self.runinfo_frame.pack(fill="x")
        else:
            if self.action_frame != None:
                self.action_frame.pack_forget()
            if self.runinfo_frame != None:
                self.runinfo_frame.pack_forget()
            self.checker_frame.pack_forget()
            self.file_type_lbe['foreground'] ='#f00'
            self.action_frame.pack(fill="x")
            self.runinfo_frame.pack(fill="x")


    def getWindowsPassword(self, message):
        password = None
        #while password == None or  str(password) == "":
        password = simpledialog.askstring(message, "PassWord", show="*")
        password = str(password).strip()
        return password

    def passWordIsOk(self, userId, passWord):
        if self.is_win_os:
            return self.release_tool.check_password(self.entry_project_name.get(),userId,passWord)
        else:
            return self.p4client.checkWindowsPassWordInlinux(passWord)

    def checkWindowPasswordReady(self):
        if self.windows_password == None or self.windows_password == 'None' or str(self.windows_password).strip() == "":
            self.windows_password = self.getWindowsPassword("Windows Password Required")
            if self.windows_password == 'None' or self.windows_password =="":
                self.offical_aubload.set(False)
                self.offical_grits.set(False)
                if not self.is_win_os:
                    self.entry_use_p4.set(False)
                return False

            if self.win_release_web_response == None:
                self.win_release_web_response = self.passWordIsOk(self.user_id, self.windows_password)
            if self.win_release_web_response == 2: #connection is bad
                messagebox.showerror("Fulism Release Page Is Down!", "The website is not responding")
                self.offical_aubload.set(False)
                self.offical_grits.set(False)
                return False
            else: # get right password
                while  self.passWordIsOk(self.user_id, self.windows_password) !=0:
                    if self.windows_password == 'None':
                        self.offical_aubload.set(False)
                        self.offical_grits.set(False)
                        if not self.is_win_os:
                            self.entry_use_p4.set(False)
                        return False
                    self.windows_password = self.getWindowsPassword("Password is not correct, please try again")
        self.release_tool.get_user_info(self.user_id,self.windows_password)
        return True
    def updateAubLoadPathGui(self):
        if self.offical_aubload.get():
            if self.entry_project_name.get() == "":
                messagebox.showerror("Project not set!", "Please set the project")
                self.offical_aubload.set(False)
                return
            if self.is_win_os:
                if not self.checkWindowPasswordReady():
                    return
            self.aubload_path_lable.grid_forget()
            self.entry_aub_path.grid_forget()
            self.aubload_or_lable.grid_forget()
            self.selec_aubload_buttion.grid_forget()

            self.aubload_release_lable.grid(row=1, column=0)
            self.aubload_release_cbox.grid(row=1, column=1)

            #self.aubload_or_lable.grid(row=2, column=2)
            #self.selec_aubload_buttion.grid(row=2,column=3)

            if len(self.grits_release_set) > 0:
                self.aubload_release_set = self.grits_release_set
            else:
                if self.is_win_os:
                    self.aubload_release_set = self.release_tool.get_windows_release_set(self.entry_project_name.get())
                else:
                    self.aubload_release_set = self.release_tool.get_linux_release_set(self.entry_project_name.get())


            total_release = len(self.aubload_release_set)
            self.aubload_release_cbox['values'] = self.aubload_release_set
            if len(self.aubload_release_set) > 0:
                self.aubload_release_cbox.current(0)
            print("total_release:", total_release)
        else:
            self.aubload_release_lable.grid_forget()
            self.aubload_release_cbox.grid_forget()
            self.aubload_path_lable.grid(row=1, column=0)
            self.entry_aub_path.grid(row=1, column=1)
            self.aubload_or_lable.grid(row=1, column=2)
            self.selec_aubload_buttion.grid(row=1,column=3)

    def updateGritsPathGui(self):
        if self.offical_grits.get():
            if self.entry_project_name.get() == "":
                messagebox.showerror("Project not set!", "Please set the project")
                self.offical_grits.set(False)
                return
            if self.is_win_os:
                if not self.checkWindowPasswordReady():
                    return
            self.release_tool.get_user_info(self.user_id,self.windows_password)
            self.grits_path_lable.grid_forget()
            self.entry_grits_path.grid_forget()
            self.grits_or_lable.grid_forget()
            self.selec_grits_buttion.grid_forget()

            self.grits_release_lable.grid(row=1, column=0)
            self.grits_release_cbox.grid(row=1, column=1)



            if len(self.aubload_release_set) > 0:
                self.grits_release_set = self.aubload_release_set
            else:
                if self.is_win_os:
                    temp_list = self.release_tool.get_windows_release_set(self.entry_project_name.get())
                    i = 0
                    for one_release_name in temp_list:
                        i = i + 1
                        if i > 500:
                            break;
                        self.grits_release_set.append(one_release_name)

            total_release = len(self.grits_release_set)
            self.grits_release_cbox['values'] = self.grits_release_set
            if len(self.grits_release_set) > 0:
                self.grits_release_cbox.current(0)
            print("total_release:", total_release)
        else:
            self.grits_release_lable.grid_forget()
            self.grits_release_cbox.grid_forget()
            self.grits_path_lable.grid(row=1, column=0)
            self.entry_grits_path.grid(row=1, column=1)
            self.grits_or_lable.grid(row=1, column=2)
            self.selec_grits_buttion.grid(row=1,column=3)

    def addCpuCoreFrame(self):
        if self.entry_incredibuild.get(): #use incredible, no CPU cores
            self.num_core_label.grid_forget()
            self.cores_cbox.grid_forget()
        else:
            self.num_core_label.grid(row=1, column=0)
            self.cores_cbox.grid(row=1, column=1)

    def addP4orLocalframe(self):
        if self.entry_use_p4.get():
            if False: #not self.is_win_os:
                #if not self.checkWindowPasswordReady():
                messagebox.showinfo("Linux P4 test checkout not stable", "Please choose local test source")
                self.entry_use_p4.set(False)
                self.test_source_label['text'] = "Test Source Path:"
                if str(self.entry_srcpath_or_testrevision.get()).strip() =="":
                    self.test_source_label['foreground'] ='#f00'
                else:
                    self.test_source_label['foreground'] ='#000'
                    self.entry_srcpath_or_testrevision['width'] = 70
                    self.or_lable.grid(row=1, column=2)
                    self.select_source_buttion.grid(row=1,column=3)
                return

            self.test_source_label['text'] = "Test Revision:"
            self.entry_srcpath_or_testrevision['width'] = 20
            self.test_source_label['foreground'] ='#000',
            self.select_source_buttion.grid_forget()
            self.or_lable.grid_forget()

        else:
            self.test_source_label['text'] = "Test Source Path:"
            if str(self.entry_srcpath_or_testrevision.get()).strip() =="":
                #if str(self.entry_unit.get()).strip() !="" and str(self.entry_list.get()).strip() !="" and str(self.entry_test.get()).strip() !="":
                self.test_source_label['foreground'] ='#f00'
            else:
                self.test_source_label['foreground'] ='#000'
            self.entry_srcpath_or_testrevision['width'] = 70
            self.or_lable.grid(row=1, column=2)
            self.select_source_buttion.grid(row=1,column=3)




    def addGoldFrameGui(self):
        n_axe_config = len(self.axe_execution_method_list)
        if n_axe_config > 1 and self.goldnize=='yes':
            messagebox.showwarning("Invalid Choice!", "Please select only ONE  axe configure for goldenization")
            self.entry_goldnize.set("no")
        else:
            if self.action_frame != None:
                self.action_frame.pack_forget()
            if self.runinfo_frame != None:
                self.runinfo_frame.pack_forget()
            self.gold_frame.pack(fill="x")
            self.addRemoveCheckerFrameGui()

    def selectCkrDir(self):
        path = tkinter.filedialog.askdirectory(title="Select ckr base folder")
        path = os.path.normpath(path)
        self.entry_ckr_folder.delete(0, 'end')
        self.entry_ckr_folder.insert(0, path)

    def showCkrFrame(self):
        self.ckr_frame.grid(row=4, column=0,columnspan= 4)

    def removeCkrFrame(self):
        if self.ckr_frame != None:
            self.ckr_frame.grid_forget ()

    def selectGoldDir(self):
        old_dir = self.entry_gold_base.get()
        initial_dir = os.path.dirname(Path(old_dir))
        path = tkinter.filedialog.askdirectory(initialdir= initial_dir, title="Select gold base folder")
        if len(path) > 0:
            self.gold_base_lbe['foreground'] ='#000'
            path = os.path.normpath(path)
            if path == ".":
                path = initial_dir
            self.entry_gold_base.delete(0, 'end')
            self.entry_gold_base.insert(0, path)

    def selectAllAxeExecutionConfig(self):
        self.updateDeviceOption()
        self.device_cbox.selection_set(self.axe_execution_config_ID_list)
    def removeGoldFrameGui(self):
        if self.gold_frame != None:
            self.gold_frame.pack_forget()
            self.checker_frame.pack_forget()

    def changeRegressPathLableColor(self, event=None):
        if str(self.entry_regress_base.get()).strip() != "":
            self.regress_path_lbe['foreground'] ='#000'
        else:
            self.regress_path_lbe['foreground'] ='#f00'

    def createRegressGui(self):
        self.regress_frame = ttk.LabelFrame(self, text="Regress Options",style="Custom.TLabelframe")
        self.entry_regress_type = StringVar()
        self.entry_run_grits = BooleanVar()
        self.entry_run_aubload= BooleanVar()
        self.entry_run_compare = BooleanVar()
        self.entry_cleanup = BooleanVar()
        self.entry_goldnize = StringVar()
        self.entry_realtime_report = StringVar()
        self.delay_hours = DoubleVar()

        countdown_randomseed_frame = ttk.Frame(self.regress_frame)
        rf_row = 0
        self.regress_path_lbe = ttk.Label(self.regress_frame, text="Regress Path:",foreground='#f00', width=40, anchor=CENTER)
        self.regress_path_lbe.grid(row=0, column=0)
        self.entry_regress_base = ttk.Entry(self.regress_frame, width=70)
        self.entry_regress_base.grid(row=0, column=1)
        self.entry_regress_base.bind("<KeyRelease>",self.changeRegressPathLableColor)
        ttk.Button(self.regress_frame, text="Select Regress Folder", command=self.selectRegressDir).grid(row=0,
                                                                                                              column=3)
        ttk.Label(self.regress_frame, text="", width=5, anchor=CENTER).grid(row=0, column=2)
        rf_row += 1
        ttk.Label(self.regress_frame, text="Clean Up Tests:", width=20, anchor=CENTER).grid(row=rf_row, column=0)
        #ttk.Label(self.regress_frame, text="Realtime Report:", width=40, anchor=CENTER).grid(row=3, column=0)
        clean_up_frame = ttk.Frame(self.regress_frame)

        ttk.Radiobutton(clean_up_frame, text="yes", value=True, variable=self.entry_cleanup).grid(row=0, column=1)

        ttk.Radiobutton(clean_up_frame, text="no", value= False, variable=self.entry_cleanup).grid(row=0, column=2)
        #report_frame = ttk.Frame(self.regress_frame)
        #ttk.Radiobutton(report_frame, text="yes", value="yes", variable=self.entry_realtime_report).grid(row=0, column=1)

        #ttk.Radiobutton(report_frame, text="no", value="no", variable=self.entry_realtime_report,).grid(row=0, column=2)
        clean_up_frame.grid(row=rf_row, column=1)
        rf_row += 1
        ttk.Label(countdown_randomseed_frame, text="Num Of Random Seeds:", width=28, anchor=W).grid(row=0, column=0)
        self.entry_random_times = ttk.Entry(countdown_randomseed_frame, width=10)
        self.entry_random_times.grid(row=0, column=1)

        ttk.Label(countdown_randomseed_frame, text="Delay Hours:", width=20, anchor=CENTER).grid(row=0, column=2)
        self.entry_delay_hours = ttk.Entry(countdown_randomseed_frame, width=5)
        self.entry_delay_hours.grid(row=0, column=3)

        # Create countdown labels with proper initial configuration
        self.countdown_label = ttk.Label(countdown_randomseed_frame, text="Idling time:", width=20, anchor=E)
        self.countdown_timer = ttk.Label(countdown_randomseed_frame, text="", width=10, anchor=W)

        self.countdown_label.grid(row=0, column=4, sticky=W, padx=5)
        self.countdown_timer.grid(row=0, column=5, sticky=W, padx=5)

        countdown_randomseed_frame.grid(row=rf_row, column=0, columnspan=3)
        rf_row += 1
        ttk.Label(self.regress_frame, text="Regress Name:", width=40, anchor=CENTER).grid(row=rf_row, column=0)

        # regress name
        self.entry_regress_name = ttk.Entry(self.regress_frame, width=50)
        self.entry_regress_name.grid(row=rf_row, column=1, sticky = W)

        ttk.Label(self.regress_frame, text="", width= 2, anchor=CENTER).grid(row=rf_row, column=2)

        s = ttk.Style()
        s.configure('W.TButton', background='gray', foreground='green', fond=('calibri', 14, 'bold', 'underline'))
        #self.request_one_report_button = ttk.Button(self.regress_frame, text="Request One Report", style='W.TButton',
                 #  command=self.requestOneReport)
       # self.request_one_report_button.grid(row=rf_row, column=3,pady=10, padx=2, sticky=W)
        #row 1
        rf_row +=1
        ttk.Label(self.regress_frame, text="Regress Types:", width=20, anchor=CENTER).grid(row=rf_row, column=0)
        regress_option_frame = ttk.Frame(self.regress_frame)
        self.entry_run_grits.set(True)
        ttk.Checkbutton(regress_option_frame, text="run grits", variable=self.entry_run_grits).grid(row=0, column=0)

        self.entry_run_aubload.set(True)
        ttk.Checkbutton(regress_option_frame, text="run aubload", variable=self.entry_run_aubload).grid(row=0, column=1)

        self.entry_run_compare.set(True)
        ttk.Checkbutton(regress_option_frame, text="compare gold", variable=self.entry_run_compare).grid(row=0, column=2)

        #ttk.Radiobutton(regress_option_frame, text="run grits only", value="gritsonly",
         #               variable=self.entry_regress_type).grid(row=0, column=0)

        #ttk.Radiobutton(regress_option_frame, text="run grits+aubload", value="gritsnaub",
        #                variable=self.entry_regress_type).grid(row=0,
         #                                                     column=1)
        #ttk.Radiobutton(regress_option_frame, text="run grits+aubload+compare", value="gritsnaubncompare",
        #               variable=self.entry_regress_type).grid(row=0,
          #                                                     column=2)
        regress_option_frame.grid(row=rf_row, column=1, columnspan=1)

        rf_row += 1
        ttk.Label(self.regress_frame, text="Goldenize Passing Test:", width=20, anchor=CENTER).grid(row=rf_row, column=0)
        #ttk.Label(self.regress_frame, text="Realtime Report:", width=40, anchor=CENTER).grid(row=3, column=0)
        if_goldize_frame = ttk.Frame(self.regress_frame)

        ttk.Radiobutton(if_goldize_frame, text="yes", value="yes", variable=self.entry_goldnize,
                        command=self.addGoldFrameGui).grid(row=0, column=1)

        ttk.Radiobutton(if_goldize_frame, text="no", value="no", variable=self.entry_goldnize,
                        command=self.removeGoldFrameGui).grid(row=0, column=2)
        #report_frame = ttk.Frame(self.regress_frame)
        #ttk.Radiobutton(report_frame, text="yes", value="yes", variable=self.entry_realtime_report).grid(row=0, column=1)

        #ttk.Radiobutton(report_frame, text="no", value="no", variable=self.entry_realtime_report,).grid(row=0, column=2)
        if_goldize_frame.grid(row=rf_row, column=1)


        #report_frame.grid(row=3, column=1)
        #if self.entry_goldnize.get()== 'yes':

        self.regress_frame.pack(fill="x")


    def setRegressGui(self):
        #self.entry_regress_type.set(self.regress_type)
        self.entry_goldnize.set(self.goldnize )
        self.entry_cleanup.set(self.cleanup)
        if self.run_grits == "True":
            self.entry_run_grits.set(True)
        else:
            self.entry_run_grits.set(False)

        if self.run_aubload == "True":
            self.entry_run_aubload.set(True)
        else:
            self.entry_run_aubload.set(False)

        if self.run_compare == "True":
            self.entry_run_compare.set(True)
        else:
            self.entry_run_compare.set(False)

        self.entry_regress_name.insert(0, self.regress_name)

    def createCpuCoreGui(self):
        self.sytem_frame = ttk.LabelFrame(self, text="CPU Core Options",style="Custom.TLabelframe")
        self.entry_incredibuild = BooleanVar()
        rf_row = 0

        #text_message = "Netbatch:"
        #if self.is_win_os:
            #text_message = "IncrediBuild:"

        #if self.is_win_os:
            #ttk.Label(self.sytem_frame, text= text_message, width=40, anchor=CENTER).grid(row=rf_row, column=0)
            #incredibuild_frame = ttk.Frame(self.sytem_frame)
            #ttk.Radiobutton(incredibuild_frame, text="yes", value=True, variable=self.entry_incredibuild,command=self.addCpuCoreFrame).grid(row=0, column=1)
            #ttk.Radiobutton(incredibuild_frame, text="no", value= False, variable=self.entry_incredibuild,command=self.addCpuCoreFrame).grid(row=0, column=2)
            #incredibuild_frame.grid(row=rf_row, column=1)
        self.cpu_cure_frame = ttk.LabelFrame(self, text="regress")
        ttk.Label(self.sytem_frame, text="", width=10, anchor=CENTER).grid(row=rf_row, column=2)
        system_info_btn = ttk.Button(self.sytem_frame, text="System Information", command=self.checkSystemRam)
        system_info_btn.grid(row=rf_row, column=3)
        #if self.is_win_os:
           # rf_row += 1
        self.cores = IntVar()
        self.maximum_cores = os.cpu_count()
        self.num_core_label = ttk.Label(self.sytem_frame, text="Num Of Cores To Use:", width=40, anchor=CENTER)
        self.num_core_label.grid(row=rf_row, column=0)
        self.num_cores = self.maximum_cores /2 #default set to half of the maximum
        self.cores_set = list(range(1, self.maximum_cores  + 1))
        self.cores_cbox = ttk.Combobox(self.sytem_frame, width=10, values=self.cores_set, textvariable=self.cores)
        self.cores_cbox.grid(row=rf_row, column=1)
        #ttk.Label(self.sytem_frame, text="", width=10, anchor=CENTER).grid(row=rf_row, column=2)

        self.sytem_frame.pack(fill="x")

    def setCpuCoreGui(self):
        if (int(self.num_cores) > int(self.maximum_cores)):
            self.num_cores = self.maximum_cores
        self.cores.set(self.num_cores)
        set_value = int(self.num_cores) -1
        self.cores_cbox.current(set_value)


    def createRevsionGui(self):
        self.revision_frame = ttk.LabelFrame(self, text="fulsim/grits revision")
        ttk.Label(self.revision_frame, text="Fulsim/Grits Revision:", width=40, anchor=CENTER).grid(row=0, column=0)
        self.entry_revision = ttk.Entry(self.revision_frame, width=70)
        self.entry_revision.grid(row=0, column=1)
        self.revision_frame.pack(fill="x")

    def createRegressPathGui(self):
        self.regress_path_frame = ttk.LabelFrame(self, text="regress path", fg='#f00')
        ttk.Label(self.regress_path_frame, text="Regress Path:", width=40, anchor=CENTER).grid(row=0, column=0)
        self.entry_regress_base = ttk.Entry(self.regress_path_frame, width=70)
        self.entry_regress_base.grid(row=0, column=1)
        ttk.Button(self.regress_path_frame, text="Select Regress Folder", command=self.selectRegressDir).grid(row=0,
                                                                                                              column=3)
        ttk.Label(self.regress_path_frame, text="", width=5, anchor=CENTER).grid(row=0, column=2)
        self.regress_path_frame.pack(fill="x")
    def setRegressPathGui(self):
        self.entry_regress_base.insert(0, self.regress_base)
        if str(self.entry_regress_base.get()).strip() != "":
            self.regress_path_lbe['foreground'] = '#000'

    def createTestSourceGui(self):
        self.entry_use_p4 = BooleanVar()
        self.test_src_frame = ttk.LabelFrame(self, text="Test Source Options",style="Custom.TLabelframe")

        ttk.Label(self.test_src_frame, text="Test Source Types:", width=40, anchor=CENTER).grid(row=0, column=0)

        if_p4_frame = ttk.Frame(self.test_src_frame)
        #ttk.Checkbutton(if_p4_frame, text="P4_Repo",variable=self.entry_use_p4, width=10, command=self.addP4orLocalframe).grid(row=0, column=1)
        ttk.Radiobutton(if_p4_frame, text="P4 Test Repo", value=True, variable=self.entry_use_p4, command=self.addP4orLocalframe).grid(row=0, column=1)
        ttk.Radiobutton(if_p4_frame, text="Local Test Repo", value= False, variable=self.entry_use_p4,command=self.addP4orLocalframe).grid(row=0, column=2)

        if_p4_frame.grid(row=0, column=1, columnspan=1)

        #self.password_lable = ttk.Label(self.test_src_frame, text="Windows Password:", width=20, anchor=CENTER)
        #self.entry_password = ttk.Entry(self.test_src_frame,show="*", width=20)
        self.or_lable = ttk.Label(self.test_src_frame, text="", width=5, anchor=CENTER)
        self.select_source_buttion = ttk.Button(self.test_src_frame, text="Select Test Source Folder", command=self.selectSrcDir)

        if self.entry_use_p4.get():
            self.test_source_label = ttk.Label(self.test_src_frame, text="Test Revision:", width=20, anchor=CENTER)
            self.entry_srcpath_or_testrevision = ttk.Entry(self.test_src_frame, width=70)

            self.select_source_buttion.grid_forget()
            self.or_lable.grid_forget()
        else:
            self.test_source_label =ttk.Label(self.test_src_frame, text="Test Source Path:", width=20, anchor=CENTER)
            self.entry_srcpath_or_testrevision = ttk.Entry(self.test_src_frame, width=20)
            self.or_lable.grid(row=1, column=2)
            self.select_source_buttion.grid(row=1,column=3)
        self.entry_srcpath_or_testrevision.bind("<KeyRelease>",self.changeSrcPathLableColor)
        #self.password_lable.grid(row=2, column=0)
        #self.entry_password.grid(row=2, column=1)
        self.test_source_label.grid(row=1, column=0)
        self.entry_srcpath_or_testrevision.grid(row=1, column=1)
        #self.select_source_buttion.configure(state='normal')
        self.test_src_frame.pack(fill="x")

    def changeSrcPathLableColor(self, event=None):
        if not self.use_p4:
            if str(self.entry_srcpath_or_testrevision.get()).strip() != "":
                self.test_source_label['foreground'] ='#000'
            else:
                self.test_source_label['foreground'] ='#f00'


    def setTestSourceGui(self):
        self.entry_srcpath_or_testrevision.insert(0, self.src_path_or_testrevsion)

        if self.use_p4:
            self.entry_use_p4.set(True)
            self.addP4orLocalframe()
        else:
            self.entry_use_p4.set(False)
            self.addP4orLocalframe()

    def changeGritsPathLableColor(self, event=None):
        if str(self.entry_grits_path.get()).strip() != "":
            self.grits_path_lable['foreground'] ='#000'
        else:
            self.grits_path_lable['foreground'] ='#f00'
    def createGritsPathGui(self):
        self.offical_grits = BooleanVar()
        self.grits_frame = ttk.LabelFrame(self, text="Grits Options",style="Custom.TLabelframe")
        grits_release_frame = ttk.Frame(self.grits_frame)
        ttk.Radiobutton(grits_release_frame, text="Official Release", value=True, variable=self.offical_grits, command=self.updateGritsPathGui).grid(row=0, column=1)
        ttk.Radiobutton(grits_release_frame, text="Local Grits Folder", value= False, variable=self.offical_grits, command=self.updateGritsPathGui).grid(row=0, column=2)
        grits_release_frame.grid(row=0, column=1, columnspan=1)

        self.grits_path_lable = ttk.Label(self.grits_frame, text="Grits Path:", foreground='#f00',width=40, anchor=CENTER)
        self.entry_grits_path = ttk.Entry(self.grits_frame, width=70)
        self.entry_grits_path.bind("<KeyRelease>",self.changeGritsPathLableColor)
        self.selec_grits_buttion = ttk.Button(self.grits_frame, text="Select Grits Folder", command=self.selectGritsDir)

        self.grits_or_lable =ttk.Label(self.grits_frame, text="", width=5, anchor=CENTER)


        self.grits_release_lable = ttk.Label(self.grits_frame, text="Choose Release Version", width=40, anchor=CENTER)
        self.grits_release_version = StringVar()
        self.grits_release_cbox = ttk.Combobox(self.grits_frame, width=30, values=self.grits_release_set,
                                        textvariable=self.grits_release_version,
                                        postcommand=self.updateGritsPath)


        self.updateGritsPathGui()
        ttk.Label(self.grits_frame, text="Additional Grits Options:", width=40, anchor=CENTER).grid(row=2, column=0)
        self.entry_grits_option = ttk.Entry(self.grits_frame, width=70)
        self.entry_grits_option.grid(row=2, column=1)

        self.grits_frame.pack(fill="x")



    def setGritsPathGui(self):
        if self.offical_grits.get():
            if self.grits_version_load != None:
                self.grits_release_version.set(self.grits_version_load)
                self.grits_version_load = None
        else:
            self.entry_grits_path.insert(0, self.grits_path)
            if str(self.entry_grits_path.get()).strip() != "":
                self.grits_path_lable['foreground'] = '#000'

    def createGritsOptionGui(self):

        self.grits_option_frame = ttk.LabelFrame(self, text="grits options",style="Custom.TLabelframe")
        ttk.Label(self.grits_option_frame, text="Grits Options:", width=40, anchor=CENTER).grid(row=0, column=0)
        self.entry_grits_option = ttk.Entry(self.grits_option_frame, width=70)
        self.entry_grits_option.grid(row=0, column=1)
        self.grits_option_frame.pack(fill="x")

    def setGritsOptionGui(self):
        self.entry_grits_option.insert(0, self.grits_option)

    def changeAubloadPathLableColor(self, event=None):
        if str(self.entry_aub_path.get()).strip() != "":
            self.aubload_path_lable['foreground'] ='#000'
        else:
            self.aubload_path_lable['foreground'] ='#f00'

    def createAubLoadPathGui(self):
        self.offical_aubload = BooleanVar()
        self.aubload_release_set = list()
        self.aubload_release_version = StringVar()
        self.aubload_frame = ttk.LabelFrame(self, text="Fulsim Options",style="Custom.TLabelframe")
        aubload_release_frame = ttk.Frame(self.aubload_frame)
        self.aubload_release_lable = ttk.Label(self.aubload_frame, text="Choose Release Version", width=40, anchor=CENTER)
        self.aubload_release_cbox = ttk.Combobox(self.aubload_frame, width=30, values=self.aubload_release_set,
                                                 textvariable=self.aubload_release_version)
                                                # postcommand=self.officalAubloadUpdateGritsNregressname)
        self.aubload_release_cbox.bind('<<ComboboxSelected>>',self.aulboadUpdateCallback)

        self.aubload_path_lable = ttk.Label(self.aubload_frame, text="AubLoad Path:",foreground='#f00', width=40, anchor=CENTER)
        self.entry_aub_path = ttk.Entry(self.aubload_frame, width=70)
        self.entry_aub_path.bind("<KeyRelease>",self.changeAubloadPathLableColor)
        self.selec_aubload_buttion = ttk.Button(self.aubload_frame, text="Select AubLoad Folder", command=self.selectAubLoadDir)

        self.aubload_or_lable = ttk.Label(self.aubload_frame, text="", width=5, anchor=CENTER)

        ttk.Radiobutton(aubload_release_frame, text="Official Release", value=True, variable=self.offical_aubload, command=self.updateAubLoadPathGui).grid(row=0, column=1)
        ttk.Radiobutton(aubload_release_frame, text="Local Fulsim Build", value= False, variable=self.offical_aubload, command=self.updateAubLoadPathGui).grid(row=0, column=2)

        aubload_release_frame.grid(row=0, column=1, columnspan=1)
        if self.offical_aubload.get():
            self.officalAubloadUpdateGritsNregressname()
        self.updateAubLoadPathGui()
        ttk.Label(self.aubload_frame, text="Additional AubLoad Options:", width=40, anchor=CENTER).grid(row=2, column=0)
        self.entry_aubload_option = ttk.Entry(self.aubload_frame, width=70)
        self.entry_aubload_option.grid(row=2, column=1)
        self.aubload_frame.pack(fill="x")
        #update regress name
    def aulboadUpdateCallback(self, event=None):
        self.officalAubloadUpdateGritsNregressname()
        if event:
            print('event.widget.get():', event.widget.get())
    def officalAubloadUpdateGritsNregressname(self):
        if self.aubload_release_version.get() != None:
            regress_name = os.path.basename(self.aubload_release_version.get())
            self.entry_regress_name.delete(0, 'end')
            self.entry_regress_name.insert(0, regress_name)
            #update regress path
            current_path = self.entry_regress_base.get()
            current_path = os.path.join(os.path.dirname(current_path),regress_name)
            self.entry_regress_base.delete(0, 'end')
            self.entry_regress_base.insert(0, current_path)
            if self.offical_grits.get():
                self.grits_release_version.set(self.aubload_release_version.get())
            if self.entry_goldnize.get():
                current_path = self.entry_gold_base.get()
                current_path = os.path.join(os.path.dirname(current_path), regress_name)
                self.entry_gold_base.delete(0, 'end')
                self.entry_gold_base.insert(0, current_path)
    def setAubLoadPathGui(self):
        if self.offical_aubload.get():
            if self.aubload_version_load != None:
                self.aubload_release_version.set(self.aubload_version_load)
                self.aubload_version_load = None
        else:
            self.entry_aub_path.insert(0, self.aubload_path)
            if str(self.entry_aub_path.get()) !="":
                self.aubload_path_lable['foreground'] = '#000'


    def setAubLoadOptionGui(self):
        self.entry_aubload_option.insert(0, self.aubload_option)

    def createAubLoadOptionGui(self):
        self.aubload_option_frame = ttk.LabelFrame(self, text="aubLoad options",style="Custom.TLabelframe")
        ttk.Label(self.aubload_option_frame, text="AubLoad Options:", width=40, anchor=CENTER).grid(row=0, column=0)
        self.entry_aubload_option = ttk.Entry(self.aubload_option_frame, width=70)
        self.entry_aubload_option.grid(row=0, column=1)
        self.aubload_option_frame.pack(fill="x")

    def createTestListPathGui(self):
        self.test_list_frame = ttk.LabelFrame(self, text="Test Content Options", style="Custom.TLabelframe")
        self.entry_list = ttk.Entry(self.test_list_frame, width=70)
        ttk.Label(self.test_list_frame, text="Test Json List File Path(s):", width=40, anchor=CENTER).grid(row=0, column=0)

        ttk.Button(self.test_list_frame, text="Select Json List Files", command=self.selectListFile).grid(row=0, column=3)
        ttk.Label(self.test_list_frame, text="",width=5,anchor=CENTER).grid(row=0, column=2)

        # unit
        ttk.Label(self.test_list_frame, text="Unit(s)/Test(s):", width=40, anchor=CENTER).grid(row=1, column=0)
        self.entry_unit = ttk.Entry(self.test_list_frame, width=70)
        # unit test
        ttk.Label(self.test_list_frame, text="Json-Test(s):", width=40, anchor=CENTER).grid(row=2, column=0)
        self.entry_test = ttk.Entry(self.test_list_frame, width=70)
        #single test
        #self.entry_full_path_tests = ttk.Entry(self.test_list_frame, width=70)
        #ttk.Label(self.test_list_frame, text="Test With Abs Path(s):", width=40, anchor=CENTER).grid(row=3, column=0)
        #ttk.Button(self.test_list_frame, text="Choose Test Path(s)", command=self.selectTestPath).grid(row=3, column=3)
        #ttk.Label(self.test_list_frame, text="or", width=10, anchor=CENTER).grid(row=3, column=2)

        #exclusive test list
        self.entry_exclusive_list = ttk.Entry(self.test_list_frame, width=70)
        ttk.Label(self.test_list_frame, text="Exclusive Test Json List File Path(s):", width=40, anchor=CENTER).grid(row=4, column=0)

        ttk.Button(self.test_list_frame, text="Select exclusive Json List File", command=self.selectExclusiveListFile).grid(row=4, column=3)
        ttk.Label(self.test_list_frame, text="", width=5, anchor=CENTER).grid(row=4, column=2)

        self.entry_list.grid(row=0, column=1)
        self.entry_unit.grid(row=1, column=1)
        self.entry_test.grid(row=2, column=1)
        #self.entry_full_path_tests.grid(row=3, column=1)
        self.entry_exclusive_list.grid(row=4, column=1)
        self.test_list_frame.pack(fill="x")

    def setTestListPathGui(self):
        self.entry_list.delete(0, 'end')
        if self.test_list_file_path != None and self.test_list_file_path != "":
            self.entry_list.insert(0,self.test_list_file_path )
        self.entry_exclusive_list.delete(0, 'end')
        self.entry_exclusive_list.insert(0, self.exclusive_test_list_file_path)
        #self.entry_full_path_tests.delete(0, 'end')
        #self.entry_full_path_tests.insert(0, self.full_path_tests)
        self.entry_unit.delete(0, 'end')
        self.entry_unit.insert(0, self.unit_names)
        self.entry_test.delete(0, 'end')
        self.entry_test.insert(0, self.json_tests)


    def setDeviceOptionGui(self):
        self.updateDeviceOption()
    def getReleaseSet(self):
        self.updateDeviceOption()
        self.project_option_lbe['foreground'] = '#000'
        if self.win_release_web_response ==2: # web is down
            return
        if self.is_win_os:
            if self.offical_aubload.get() or  self.offical_grits.get():
                if not self.checkWindowPasswordReady():
                    return
                self.aubload_release_set = self.grits_release_set = self.release_tool.get_windows_release_set(self.entry_project_name.get())
                if self.offical_aubload.get():
                    self.aubload_release_cbox['values'] = self.aubload_release_set
                    if len(self.aubload_release_set):
                        self.aubload_release_cbox.current(0)
                if self.offical_grits.get():
                    self.grits_release_cbox['values'] = self.grits_release_set
                    if len(self.grits_release_set):
                        self.grits_release_cbox.current(0)
        else:
            if self.offical_aubload.get() or  self.offical_grits.get():
                self.aubload_release_set = self.grits_release_set = self.release_tool.get_linux_release_set(self.entry_project_name.get())
                if self.offical_aubload.get():
                    self.aubload_release_cbox['values'] = self.aubload_release_set
                    if len(self.aubload_release_set):
                        self.aubload_release_cbox.current(0)
                if self.offical_grits.get():
                    self.grits_release_cbox['values'] = self.grits_release_set
                    if len(self.grits_release_set):
                        self.grits_release_cbox.current(0)

    def createProjectFrame(self):
        # project
        num_col = 0
        num_row = 0
        self.project_frame = ttk.LabelFrame(self, text="Projects & Device Options",style="Custom.TLabelframe")
        self.entry_2d_ip = BooleanVar()
        self.entry_3d_ip = BooleanVar()
        self.entry_utp_ip = BooleanVar()
        self.entry_media_ip = BooleanVar()
        self.entry_media_ip.set(True)
        self.entry_3d_ip.set(True)
        self.entry_utp_ip.set(True)
        self.entry_2d_ip.set(False)

        self.IP_option_frame = ttk.LabelFrame(self.project_frame)
        self.IP_option_lbe = ttk.Label(self.project_frame, foreground='#000', text="IPs:", width=40,anchor=CENTER)
        self.IP_option_lbe.grid(row=num_row, column=num_col)
        num_col = num_col + 1
        ttk.Checkbutton(self.IP_option_frame, text="Media",  variable=self.entry_media_ip,command=self.updateDeviceOption).grid(row=num_row,column=num_col)
        #ttk.Radiobutton(self.IP_option_frame, text="Media", value="Media", variable=self.entry_IP_ID, command=self.updateDeviceOption).grid(row=num_row,column=num_col)
        num_col = num_col + 1
        ttk.Checkbutton(self.IP_option_frame, text="3D", variable=self.entry_3d_ip,command=self.updateDeviceOption).grid(
            row=num_row, column=num_col)
        num_col = num_col + 1
        ttk.Checkbutton(self.IP_option_frame, text="UTP", variable=self.entry_utp_ip,
                        command=self.updateDeviceOption).grid(row=num_row, column=num_col)
        num_col = num_col + 1
        ttk.Checkbutton(self.IP_option_frame, text="2D", variable=self.entry_2d_ip,
                        command=self.updateDeviceOption).grid(row=num_row, column=num_col)

        #ttk.Radiobutton(self.IP_option_frame, text="3D", value="3D", variable=self.entry_IP_ID, command=self.updateDeviceOption).grid(row=num_row,column=num_col)
        self.IP_option_frame.grid(row=num_row, column=1)

        num_row = num_row + 1
        num_col = 0
        self.entry_project_name = StringVar()
        self.project_option_frame = ttk.LabelFrame(self.project_frame)

        self.project_option_lbe = ttk.Label(self.project_frame,foreground='#f00',  text="Projects:", width=40, anchor=CENTER)
        self.project_option_lbe.grid(row=num_row, column=num_col)
        num_col = num_col + 1
        ttk.Radiobutton(self.project_option_frame, text="MTL", value="mtl", variable=self.entry_project_name,
                        command=self.getReleaseSet).grid(row=0, column=num_col)
        num_col = num_col + 1
        ttk.Radiobutton(self.project_option_frame, text="ELG", value="elg", variable=self.entry_project_name, command=self.getReleaseSet).grid(row=0,
                                                                                                            column=num_col)
        num_col = num_col + 1
        ttk.Radiobutton(self.project_option_frame, text="LNL", value="lnl", variable=self.entry_project_name, command=self.getReleaseSet).grid(row=0,
                                                                                                            column=num_col)
        num_col = num_col + 1
        #ttk.Radiobutton(self.project_option_frame, text="ACMR", value="acmr", variable=self.entry_project_name, command=self.getReleaseSet).grid(row=0,
        #                                                                                                                                   column=num_col)
        #num_col = num_col + 1
        ttk.Radiobutton(self.project_option_frame, text="CLS", value="cls", variable=self.entry_project_name, command=self.getReleaseSet).grid(row=0,
                                                                                                                                              column=num_col)
        num_col = num_col + 1
        ttk.Radiobutton(self.project_option_frame, text="PTL/WCL", value="ptl", variable=self.entry_project_name, command=self.getReleaseSet).grid(row=0,
                                                                                                                                               column=num_col)

        num_col = num_col + 1
        ttk.Radiobutton(self.project_option_frame, text="NVL/Xe3p_V2", value="nvl", variable=self.entry_project_name, command=self.getReleaseSet).grid(row=0,
                                                                                                                                               column=num_col)
        num_col = num_col + 1
        ttk.Radiobutton(self.project_option_frame, text="FCS", value="fcs", variable=self.entry_project_name,
                        command=self.getReleaseSet).grid(row=0, column=num_col)
        num_col = num_col + 1
        ttk.Radiobutton(self.project_option_frame, text="CRI", value="cri", variable=self.entry_project_name,
                        command=self.getReleaseSet).grid(row=0,column=num_col)
        self.project_option_frame.grid(row=num_row, column=1)

        num_col = num_col + 1
        ttk.Radiobutton(self.project_option_frame, text="TTL/Xe4", value="ttl", variable=self.entry_project_name,
                        command=self.getReleaseSet).grid(row=0, column=num_col)
        self.project_option_frame.grid(row=num_row, column=1)
        num_col = num_col + 1
        ttk.Radiobutton(self.project_option_frame, text="HML/Xe4_v2", value="hml", variable=self.entry_project_name,
                        command=self.getReleaseSet).grid(row=0, column=num_col)
        self.project_option_frame.grid(row=num_row, column=1)
        num_row = num_row + 1


        self.device_options_set = self.axe_execution.generateExecutionMethodNameList(self.entry_2d_ip.get(),self.entry_3d_ip.get(),self.entry_media_ip.get(),self.entry_utp_ip.get(), self.project_name)
        self.device_option_lbe = ttk.Label(self.project_frame, text="Axe Execution Stages:", foreground="#f00",width=40, anchor=CENTER)
        self.device_option_lbe.grid(row=num_row, column=0)
        treeview_h = len(self.device_options_set)
        if treeview_h > 5:
            treeview_h = 5
        self.device_cbox = ttk.Treeview(self.project_frame, height=treeview_h,selectmode="extended", show="tree")

        scrollbar = ttk.Scrollbar(self.project_frame,orient=tk.VERTICAL, command=self.device_cbox.yview)
        self.device_cbox.configure(yscrollcommand=scrollbar.set)
        self.device_cbox.grid(padx=3, pady=1, row=num_row, column=1, sticky='news')
        self.device_cbox.bind('<<TreeviewSelect>>', self.selectItem, add=True)
        #self.device_cbox.column("#0", minwidth=0, width=400, stretch=NO)
        scrollbar.grid(row=num_row, column=2,sticky='nws',pady=1)
        for i in self.device_cbox.get_children():
            self.device_cbox.delete(i)

        for item in self.device_options_set:
            #print("Inserting ", item.name )
            self.safeInsert(item)
            #self.device_cbox.focus("'" + item + "'")
            #self.device_cbox.selection_set("'"+item+"'")



        ttk.Button(self.project_frame, text="Select All", command=self.selectAllAxeExecutionConfig).grid(row=num_row,column=4)
        ttk.Label(self.project_frame, text="", width=5, anchor=CENTER).grid(row=num_row, column=3, padx =5)
        self.project_frame.pack(fill="x")
    def safeInsert(self, item):
        try:
            # Check if item already exists
            item_id = "'" + item.name + "'"
            if self.device_cbox.exists(item_id):
                print(f"Duplicated axe execution method: {item.name}")
                return False

            self.device_cbox.insert("", "end", item_id, text=item.name)
            return True

        except AttributeError as e:
            print(f"Item missing 'name' attribute: {e}")
            return False
        except Exception as e:
            print(f"Error inserting axe execution method '{getattr(item, 'name', 'Unknown')}': {e}")
            return False

    def selectItem(self, a):
        self.device_option_lbe['foreground'] = '#000'
        self.axe_execution_method_list.clear()
        ate_config_selections =  self.device_cbox.selection()
        number = len(ate_config_selections)
        if number > 0:
            print("======selected axe configs (total " + str(number) + ")=========")
            for selected_item in ate_config_selections:
                item = self.device_cbox.item(selected_item)
                record = item['text']
                print(record)
                axe_execution_method = self.axe_execution.getExecutionMethod(record, self.device_options_set)
                print("test_software:", axe_execution_method.test_software)
                print("agent type:", axe_execution_method.agent_type)
                print("grits options:", axe_execution_method.grits_options)
                print("fulsim options", axe_execution_method.fulsim_options)
                print("aubload options:", axe_execution_method.aubload_options)
                print("device option:", axe_execution_method.device_option)
                print("---------------------------")
                self.axe_execution_method_list.append(axe_execution_method)
            print("total:" + str(number))

    def setProjectFrame(self):
        self.IP_option_lbe['foreground'] = '#000'
        self.entry_project_name.set(self.project_name)
        self.project_option_lbe['foreground'] = '#000'


    def setCatergoryFrame(self):
        row_id = 0
        col_id = 0
        ttk.Label(self.catergory_frame, text="            Configure Name",  font='times 14', width=40, anchor=W, foreground="blue").grid(row=row_id, column=col_id)
        col_id = col_id  + 1
        ttk.Label(self.catergory_frame, text="Options ",font='times 14', width=30, anchor=W, foreground="blue").grid(row=row_id, column=2)
        row_id = 0
        colcol_id = col_id  + 1
        ttk.Label(self.catergory_frame, text = ' More Options  ',font='times 14', width=20, anchor=W, foreground="blue").grid(row=row_id, column=3)


    def getYamlHeader(self, yamls, yamalConfig):
        for line in yamls:
            if re.search(r"DefaultTestObject:", line):
                break

            search_result = re.search(r"SchemaVersion:\s*(.+)", line)
            if search_result:
                yamalConfig.SchemaVersion = str(search_result.group(1)).strip()
            search_result = re.search(r"TestFileName:\s*(.+)", line)
            if search_result:
                gsf_name = str(search_result.group(1)).strip()
                gsf_name = str(gsf_name).replace("'","")
                gsf_name = str(gsf_name).replace('"', "")
                yamalConfig.TestFileName = gsf_name
            search_result = re.search(r"NextAutoTestObjectName:\s*(.+)", line)
            if search_result:
                yamalConfig.NextAutoTestObjectName = str(search_result.group(1)).strip()


    def getYamlDefaultTestConfig(self, yamls, defaultConfig):
        for line in yamls:
            if re.search(r"TestObjects:", line):
                break
            search_result = re.search(r"Agent:\s*(.+)", line)
            if search_result:
                defaultConfig.Agent = str(search_result.group(1)).strip()

            search_result = re.search(r"VirtualPath:\s*(.+)", line)
            if search_result:
                defaultConfig.VirtualPath = str(search_result.group(1)).strip()

            search_result = re.search(r"CommandLine:\s*(.+)", line)
            if search_result:
                defaultConfig.CommandLine = str(search_result.group(1)).strip()

            search_result = re.search(r"SeedCount:\s*(.+)", line)
            if search_result:
                defaultConfig.SeedCount = str(search_result.group(1)).strip()

    def getYamlTestConfigs(self, yamls, configList):

        start = False

        for line in yamls:
            if re.search(r"TestObjects:", line):
                start = True
            if start:
                if re.search(r"^-", line):
                    test_config = Test.YamlTestConfig()
                search_result = re.search(r"CommandLine:\s*(.+)", line)
                if search_result:
                    test_config.CommandLine = str(search_result.group(1)).strip()

                search_result = re.search(r"VirtualPath:\s*(.+)", line)
                if search_result:
                    test_config.VirtualPath = str(search_result.group(1)).strip()

                search_result = re.search(r"Name:\s*(.+)", line)
                if search_result:
                    test_config.Name = (str(search_result.group(1)).strip()).replace("'", "")
                    test_config.Name = test_config.Name.replace('"', "")
                    configList.append(test_config)
                    test_config = Test.YamlTestConfig()

    def readYamlFile(self, yamlPath, testRead):
        if Path(yamlPath).is_file():
            with open(yamlPath,encoding='utf-8') as f:
                yamls = f.readlines()
                default_config = False
                #test_config = False

            if len(yamls) > 0:
                self.getYamlHeader(yamls, testRead.ymal_config)
                self.getYamlDefaultTestConfig(yamls,testRead.ymal_config.DefaultTestConfig)
                self.getYamlTestConfigs(yamls, testRead.ymal_config.test_config_list)
                #for debug
                #testRead.ymal_config.printInfo()


    def readOneUnit(self, unitName):

        if re.search(r"^#", unitName):
            info = "\t\t==>skipped"
            print(info)
            self.updateOutputBox(info)

        if self.use_p4:
            self.updateProgressBar(1, 0)
            unit_target_path = os.path.join(self.regress_test_base, unitName)
            unit_target_path = str(unit_target_path).replace("\\", "/")
            if self.util.has_files(unit_target_path):
                print("Skipped copying unit over as the target folder is not empty: ",unit_target_path )
            else:
                if self.p4_test_revision == None:
                    self.p4_test_revision = 0
                print(" P4 is  copying unit", unitName, "to ", unit_target_path)
                self.p4client.copyUnitFolder(unitName,self.regress_test_base,self.p4_test_revision)
                print(" P4 is  copying unit", unitName, "to ", unit_target_path, "==> done")

            unit_path = Path(os.path.join(self.regress_test_base, unitName))
        else:
            unit_path = Path(os.path.join(self.src_path_or_testrevsion, unitName))

        #self.suite_name = unitName

        print("Reading", unitName, "tests:", unit_path, "...")
        if not unit_path.is_dir():
            return

        all_file_paths = self.util.GetAllFilePathsFromDir(unit_path)
        all_valid_gsf_file_paths = list()
        for file_path in all_file_paths:
           if Path(file_path).suffix != '.gsf':
               continue

           yaml_path = str(file_path).replace('.gsf','.meta.yaml')
           if not Path(yaml_path).is_file():
               continue
           all_valid_gsf_file_paths.append(file_path)

        total = len(all_valid_gsf_file_paths)
        processed = 0
        if (total > 0):
            print("Reading tests:  ", total)
        else:
            print("no tests ")
            return

        for gsf_path in all_valid_gsf_file_paths:
            processed = processed + 1
            gsf_path = str(gsf_path).replace("\\", "/")
            if not self.use_p4:
                if self.is_win_os:
                    gsf_relative_path =  gsf_path.replace(str(self.src_path_or_testrevsion)+'/',"")
                else:
                    gsf_relative_path = gsf_path.replace(str(self.src_path_or_testrevsion) + '/', "")
            else:
                if self.is_win_os:
                    gsf_relative_path = gsf_path.replace(str(self.regress_test_base) + '/', "")
                else:
                    print("gsf_path:",gsf_path)
                    print("self.regress_test_base:", self.regress_test_base)

                    gsf_relative_path = gsf_path.replace(str(self.regress_test_base) + '/', "")
            json_test='"'+str(gsf_relative_path) +'#-1'+'@0'+'"'
            json_test = str(json_test).replace("\\", "/")
            json_test = str(json_test).replace("'", "")


            output_str = ("(" + str(processed) + "/" + str(total) + ")Reading test: " + json_test)
            print(output_str, end="")
            self.updateOutputBox( output_str)

            self.readOneJsonTest(json_test, self.test_read_list,False, True)
            print(" ==> done")
            #self.updateRunTime()
            status_str = "Reading Json tests: " + str(processed) + "/" + str(total)
            self.updateStatusLabel(status_str)
            self.updateProgressBar(total, processed)

            if self.stop_regress:
                return

    def processRun(self):

        self.regress_settings.additional_aubload_options = self.aubload_option
        self.regress_settings.additional_grits_options = self.grits_option
        self.regress_settings.grits_path = self.grits_path
        self.regress_settings.aubload_path = self.aubload_path

        self.regress_settings.start_time = datetime.datetime.now().strftime("%H:%M %b %d %Y")
        self.regress_settings.end_time =''

        self.processRun_start_time  = t1 = time.time()

        if self.stop_regress:
            return

        if not self.hasTest(self.test_run_list):
            print("There are no tests to run")
            messagebox.showinfo("No test found!", "Please check if tests exist")
            return

        unit_result = Test.UnitResult()
        unit_result.type = self.regress_name

        print("Copying include folders ....")
        t1 = time.time()
        self.copyRequiredFolders()
        print("Copy Include folders time: ", self.util.convertSecToHourMinSec(time.time() - t1))

        print("Copying tests ....")
        t1 = time.time()
        self.copyTests(self.test_run_list)

        copy_time = self.util.convertSecToHourMinSec(time.time() - t1)
        print("Copy test time: ", copy_time)



        time.sleep(0.01)
        self.update()
        if self.stop_regress:
            return



        print("Running tests ....")
        t1 = time.time()
        self.test_run_list.reverse()
        self.runTestObjects(self.test_run_list)


        runtest_time = self.util.convertSecToHourMinSec(time.time() - t1)

        print("Run test time: ",runtest_time )
        self.update()
        if self.stop_regress:
            return

        self.processRun_runtime= time.time() - self.processRun_start_time

        time.sleep(0.01)
        self.update()
        if self.stop_regress:
            return


        unit_result.getSummary(self.regress_summary)
        unit_result.html_report_path = self.html_report_path
        self.result_list.append(unit_result)

    def getParentFolder(self, listPaths:list):
        parent_path = ""
        for one_path in listPaths:
            parent_path = Path(os.path.dirname(one_path))
            if parent_path.is_dir():
                return parent_path

        return parent_path

    def selectListFile(self):

        parent_dir = self.getParentFolder(self.list_paths)
        file_paths = tkinter.filedialog.askopenfilenames(initialdir= parent_dir,title="Select one or more test lists",filetypes=(("all files", "*.*"),("list files", "*list"), ("lst files", "*lst"),  ("txt files", "*.txt")))
        file_path_string = ''
        for file_path in file_paths:
            file_path_string = file_path_string + file_path + ","
        #self.entry_list.delete(0,'end')
        self.entry_list.insert(0, file_path_string)
        self.saveGuiOutput()

    def selectExclusiveListFile(self):

        parent_dir = self.getParentFolder(self.exclusive_list_paths)
        file_paths = tkinter.filedialog.askopenfilenames(initialdir= parent_dir,title="Select a exclusive test list",filetypes=( ("all files", "*.*"), ("list files", "*list"),("lst files", "*lst"),("txt files", "*.txt")))

        file_path_string = ''
        for file_path in file_paths:
            file_path_string = file_path_string + file_path + ","
        self.entry_exclusive_list.insert(0, file_path_string)
        self.saveGuiOutput()

    def selectTestPath(self):

        old_dir = self.entry_full_path_tests.get()
        initial_dir = os.path.dirname(Path(old_dir))
        path = tkinter.filedialog.askdirectory(initialdir=initial_dir, title="Select Test Folder")
        if len(path) > 0:
            path = os.path.normpath(path)
            if path == ".":
                path = initial_dir
            else:
                if initial_dir != None:
                    path = ", " + path
                    self.entry_full_path_tests.insert(0, path)
        self.saveGuiOutput()

    def selectAubLoadDir(self):

        old_dir = self.entry_aub_path.get()
        initial_dir = os.path.dirname(Path(old_dir))
        path = tkinter.filedialog.askdirectory(initialdir= initial_dir,title="Select aubload build folder")

        if len(path) > 0:
            self.aubload_path_lable['foreground'] = '#000'
            path = os.path.normpath(path)
            if path == ".":
                path = initial_dir
            self.entry_aub_path.delete(0, 'end')
            self.entry_aub_path.insert(0, path)
            grits_path = os.path.join(path, "grits")
            grits_path = os.path.normpath(grits_path)

            if os.path.isdir(grits_path):
                self.entry_grits_path.delete(0, 'end')
                self.entry_grits_path.insert(0, grits_path)
                self.changeGritsPathLableColor()
            else:
                grits_path = os.path.join(path, "Grits")
                grits_path = os.path.normpath(grits_path)
                if os.path.isdir(grits_path):
                    self.entry_grits_path.delete(0, 'end')
                    self.entry_grits_path.insert(0, grits_path)
                    self.changeGritsPathLableColor()

            #update regress name
            regress_name = os.path.basename(path)
            self.entry_regress_name.delete(0, 'end')
            self.entry_regress_name.insert(0, regress_name)
            #update regress path
            current_path = self.entry_regress_base.get()
            current_path = os.path.join(os.path.dirname(current_path),regress_name)
            self.entry_regress_base.delete(0, 'end')
            self.entry_regress_base.insert(0, current_path)

            #update gold path
            current_path = self.entry_gold_base.get()
            current_path = os.path.join(os.path.dirname(current_path), regress_name)
            self.entry_gold_base.delete(0, 'end')
            self.entry_gold_base.insert(0, current_path)
        self.saveGuiOutput()
    def selectGritsDir(self):

        old_dir = self.entry_grits_path.get()
        initial_dir = os.path.dirname(Path(old_dir))
        path = tkinter.filedialog.askdirectory(initialdir= initial_dir, title="Select Grits Folder")

        if len(path) > 0:
            self.grits_path_lable['foreground'] = '#000'
            path = os.path.normpath(path)
            if path == ".":
                path = initial_dir
            self.entry_grits_path.delete(0, 'end')
            self.entry_grits_path.insert(0, path)
            self.changeGritsPathLableColor()
        self.saveGuiOutput()
    def selectSrcDir(self):

        old_dir = self.entry_srcpath_or_testrevision.get()
        initial_dir = os.path.dirname(Path(old_dir))
        path = tkinter.filedialog.askdirectory(initialdir= initial_dir, title="Select Test Source Folder")
        if len(path) > 0:
            self.test_source_label['foreground'] ='#000',
            path = os.path.normpath(path)
            if path == ".":
                path = initial_dir
            self.entry_srcpath_or_testrevision.delete(0, 'end')
            self.entry_srcpath_or_testrevision.insert(0, path)
        self.saveGuiOutput()
    def selectRegressDir(self):

        old_dir = self.entry_regress_base.get()
        initial_dir = os.path.dirname(Path(old_dir))
        path = tkinter.filedialog.askdirectory(initialdir= initial_dir, title="Select Regress Folder")
        if len(path) > 0:
            self.regress_path_lbe['foreground'] ='#000'
            path = os.path.normpath(path)
            if path == ".":
                path = initial_dir
            self.entry_regress_base.delete(0, 'end')
            self.entry_regress_base.insert(0, path)
        self.saveGuiOutput()

    def findAllFilesInDir(self, dirPath, filePathList):
        files = os.listdir(dirPath)
        for file in files:
            file_path = os.path.join(dirPath, file)
            if os.path.isdir(file_path):
                if file != "gold":
                    self.findAllFilesInDir(file_path, filePathList)
            elif os.path.isfile(file_path):
                filePathList.append(file_path)


    def getCkrFilePath(self,checkerFileName):
        ckr_path = None
        file_name = str(checkerFileName).replace(".txt", "")
        if len(self.all_ckr_file_paths) > 0:
            for path in self.all_ckr_file_paths:
                if re.search(file_name, path, re.IGNORECASE):
                    ckr_path = path
                    break
        return  ckr_path

    def hasPassTest(self):
        total = len(self.pass_test_suite_list)
        if total == 0:
            return False
        else:
            return True

    def start_countdown_timer(self):
        if self.delay_second > 0:
            self.delay_second -= 1
            time_display = str(self.convert_seconds_left_to_time(self.delay_second))
            print("Regress start in: " + time_display, end='\r')

            # Update the countdown display
            self.countdown_label.config(text="Regress start in:")
            self.countdown_timer.config(text=time_display, font=('Arial', 12), background='black', foreground='red',
                                        anchor=CENTER)

            # Force immediate update of the display
            self.countdown_timer.update()
            self.update_idletasks()

            if self.stop_regress:
                self.countdown_label.config(text="Idling time:")
                self.processRun_start_time = time.time()
                self.countdown_timer.config(text="")
                self.update_idletasks()
                return

            # Schedule next update
            self.after(1000, self.start_countdown_timer)

        elif self.delay_second == 0:
            print("Regress started!")
            self.countdown_label.config(text="Total Run Time:")
            self.countdown_timer.config(text="00:00:00")
            self.update_idletasks()

            # Start the actual regression and runtime timer
            self.is_regression_started = True
            self.processRun_start_time = time.time()  # Reset the start time

            # **FIX: Actually start the regression here**
            self.after(100, self.runRegress)  # Start the regression
            self.after(1000, self.updateRunTime)  # Start the runtime updater

    def convert_seconds_left_to_time(self, delay_second):
        return datetime.timedelta(seconds=delay_second)

    def saveGuiOutput(self):
        if self.offical_aubload.get():
            if self.aubload_release_version.get() is None or self.aubload_release_version.get().strip() == "":
                messagebox.showwarning("Aubload version is not selected!",
                                       "Please check if the AubLoad Version is set correctly")
                return
        if self.offical_grits.get():
            if self.grits_release_version.get() is None or self.grits_release_version.get().strip() == "":
                messagebox.showwarning("Grits version is not selected!",
                                       "Please check if the Grits Version is set correctly")
                return

        self.project_name = self.entry_project_name.get()
        self.device_options_set = self.axe_execution.generateExecutionMethodNameList(self.entry_2d_ip.get(),self.entry_3d_ip.get(),self.entry_media_ip.get(),self.entry_utp_ip.get(), self.project_name)

        self.test_list_file_path = self.entry_list.get()
        self.list_paths = self.getItemList(self.test_list_file_path)
        self.exclusive_test_list_file_path = self.entry_exclusive_list.get()
        #self.full_path_tests = self.entry_full_path_tests.get()
        if not self.offical_aubload.get():
            self.aubload_path = self.entry_aub_path.get()
        if not self.offical_grits.get():
            self.grits_path = self.entry_grits_path.get()
        self.aubload_option = self.entry_aubload_option.get()
        self.grits_option = self.entry_grits_option.get()
        self.unit_names = self.entry_unit.get()
        self.json_tests = self.entry_test.get()
        self.json_tests = self.json_tests.rstrip()
        self.json_tests = re.sub(r'\n', '', self.json_tests )
        self.unit_name_list = self.getItemList(self.unit_names)
        self.json_test_list = self.getItemList(self.json_tests)
        self.src_path_or_testrevsion = self.entry_srcpath_or_testrevision.get()
        if self.src_path_or_testrevsion !="":
            self.test_source_label['foreground'] = '#000'
        self.src_path_or_testrevsion = str(self.src_path_or_testrevsion).strip()
        self.src_path_or_testrevsion = str( self.src_path_or_testrevsion).replace("\\", "/")

        self.use_p4 = self.entry_use_p4.get()
        self.use_incredibuild = self.entry_incredibuild.get()
        if self.use_p4:
            if self.src_path_or_testrevsion != None and self.src_path_or_testrevsion !="":
                test_revision_str = self.src_path_or_testrevsion
                test_revision_str = re.sub(r"\D", "", test_revision_str)
                if str(test_revision_str).isnumeric():
                    self.p4_test_revision = int(test_revision_str)
                else:
                    self.p4_test_revision = None
            else:
                self.p4_test_revision = None


        self.regress_base = self.entry_regress_base.get()
        self.regress_base = str(self.regress_base).strip()
        self.regress_test_base = Path(os.path.join(self.regress_base, "tests"))
        self.regress_test_base = str( self.regress_test_base).replace("\\", "/")
        if  self.entry_include_file_string!=None:
            self.gold_include_name_string = self.entry_include_file_string.get()
        if self.entry_exclusive_file_string != None:
            self.gold_exclude_name_string = self.entry_exclusive_file_string.get()



        regress_name = self.entry_regress_name.get()

        if self.entry_random_times.get() != '':
            self.random_times = int(self.entry_random_times.get())
        else:
            self.random_times = 0

        if self.entry_delay_hours.get() != '':
            self.delay_min = float(self.entry_delay_hours.get()) * 60
        else:
            self.delay_min = 0

        if str(regress_name).strip() !="":
            regress_name = str(regress_name).replace(" ", "_") #replace space with _ to make name recoginzied
            self.regress_name = regress_name
        else:

            self.regress_name = os.path.basename(self.aubload_path)
        #self.device = self.entry_device.get()
        self.test_list_file_path = str(self.test_list_file_path).strip()
        self.exclusive_test_list_file_path = str(self.exclusive_test_list_file_path).strip()
        self.exclusive_list_paths = self.getItemList(self.exclusive_test_list_file_path)
        self.full_path_tests = str(self.full_path_tests).strip()
        self.full_path_list = self.getItemList(self.full_path_tests)
        self.project_name = str(self.project_name).strip()
        self.aubload_path = str(self.aubload_path).strip()
        self.grits_path = str(self.grits_path).strip()
        self.aubload_option = str(self.aubload_option).strip()
        self.grits_option = str(self.grits_option).strip()
        self.unit_names = str(self.unit_names).strip()
        self.gold_include_name_list = str(self.gold_include_name_list).strip()


        #self.regress_type = self.entry_regress_type.get()
        self.run_grits = self.entry_run_grits.get()
        self.run_aubload = self.entry_run_aubload.get()
        self.run_compare = self.entry_run_compare.get()

        self.num_cores = self.cores.get()

        #goldnization
        self.realtime_report = self.entry_realtime_report.get()
        self.goldnize  = self.entry_goldnize.get()
        self.cleanup   = self.entry_cleanup.get()
        if self.entry_out_binary != None:
            self.binary_gold = self.entry_out_binary.get()
        if self.entry_track_file != None:
            self.checker_gold = self.entry_track_file.get()

        if self.entry_gold_base != None:
            self.gold_base = self.entry_gold_base.get()
        if self.entry_copy_test != None:
            self.copy_test_forgold = self.entry_copy_test.get()

        # print os.path.basename(path)  # 'test.txt'
        # print os.path.dirname(path)  # '/test1/test2/test3'
        # print os.path.basename(os.path.dirname(path))  # 'test3'


    def saveConfigure(self):
        self.saveGuiOutput()
        #file_name = tkinter.filedialog.asksaveasfile(initialdir= self.config_folder, mode='w', defaultextension=".cfg",filetypes=(
        #("configure files", "*.cfg"), ("txt files", "*.txt"), ("all files", "*")))
        file_name = tkinter.filedialog.asksaveasfilename(initialdir= self.config_folder, defaultextension=".cfg",title='Save Configure File', filetypes=(("configure files", "*.cfg"), ("txt files", "*.txt"), ("all files", "*")))
        if file_name =="":
            print("Can not be saved")
            return
        f = open(file_name, "w+")
        f.write("IPID:" + self.IP_ID + "\n")
        f.write("ProjectName:" + self.project_name +"\n")
        axe_config_line = "AxeConfigs:"
        for axe_config in self.axe_execution_method_list:
            axe_config_line =axe_config_line+ "'"+ axe_config.name +"'" + ","
        f.write(axe_config_line + "\n")
        f.write("TestListFilePath:" + self.test_list_file_path +"\n")
        f.write("TestExclusiveListFilePath:" + self.exclusive_test_list_file_path + "\n")
        f.write("SingleTestPath:" + self.full_path_tests + "\n")
        f.write("UnitNames:" + self.unit_names + "\n")
        f.write("UnitTestNames:" + self.json_tests + "\n")
        f.write("OfficalAubLoad:" + str(self.offical_aubload.get()) +"\n")
        f.write("AubLoadReleaseVersion:" + str(self.aubload_release_version.get()) +"\n")
        f.write("AubLoadDir:" + self.aubload_path +"\n")
        f.write("GritsReleaseVersion:" + str(self.grits_release_version.get()) +"\n")
        f.write("OfficalGrits:" + str(self.offical_grits.get()) +"\n")
        f.write("GritsDir:" + self.grits_path +"\n")
        f.write("AubLoadOption:" + self.aubload_option +"\n")
        f.write("GritsOption:" + self.grits_option +"\n")
        f.write("UseP4:" + str(self.use_p4) +"\n")
        if self.use_p4 :
            f.write("TestSource:" + self.src_path_or_testrevsion +"\n")
        else:
            f.write("TestRevision:" + self.src_path_or_testrevsion +"\n")
        f.write("RegressPath:" + self.regress_base +"\n")

        f.write("RegressName:" + self.regress_name +"\n")
        f.write("RunGrits:" + str(self.run_grits) + "\n")
        f.write("RunAubLoad:" + str(self.run_aubload) + "\n")
        f.write("RunCompare:" + str(self.run_compare) + "\n")
        #f.write("RegressType:" + self.regress_type + "\n")
        f.write("IfGoldnize:" + self.goldnize  + "\n")
        f.write("Cleanup:" + str(self.cleanup)+ "\n")
        f.write("BinaryGold:" + str(self.binary_gold) + "\n")
        f.write("CheckerGold:" + str(self.checker_gold) + "\n")
        f.write("GoldIncludeName:" + self.gold_include_name_string + "\n")
        f.write("GoldExcludeName:" + self.gold_exclude_name_string + "\n")
        f.write("DramoutGold:" + str(self.dramout_gold)+ "\n")
        f.write("GoldBase:" + self.gold_base + "\n")
        f.write("CopyTest:" +str( self.copy_test_forgold) + "\n")
        f.write("NeedCkr:" + self.need_ckr + "\n")
        f.write("CkrPath:" + self.ckr_folder + "\n")
        f.write("CpuCores:" + str(self.num_cores) + "\n")
        f.close()
        status_str = "regression configure is saved to " + str(os.path.basename(file_name))
        self.updateStatusLabel(status_str)
        self.updateProgressBar(0, 0)

    def loadConfigureFile(self,file_path):
        if file_path == "." or not Path(file_path).is_file():
            return
        self.entry_list.delete(0, 'end')
        self.entry_exclusive_list.delete(0, 'end')
        # self.entry_full_path_tests.delete(0, 'end')
        self.entry_aub_path.delete(0, 'end')
        self.entry_aubload_option.delete(0, 'end')
        self.entry_grits_path.delete(0, 'end')
        self.entry_grits_option.delete(0, 'end')
        self.entry_unit.delete(0, 'end')
        self.entry_test.delete(0, 'end')
        self.entry_srcpath_or_testrevision.delete(0, 'end')
        self.entry_regress_base.delete(0, 'end')
        # self.entry_revision.delete(0, 'end')
        self.entry_regress_name.delete(0, 'end')
        self.entry_gold_base.delete(0, 'end')
        self.entry_include_file_string.delete(0, 'end')
        # below for legacy cfg compatible
        self.offical_aubload.set(False)
        self.offical_grits.set(False)
        with open(file_path, 'r') as f:
            lines = f.readlines()

            for line in lines:

                search_result = re.search(r"ProjectName:(\w*)", str(line))
                if search_result:
                    self.project_name = search_result.group(1)
                    self.entry_project_name.set(self.project_name)

                search_result = re.search(r"AxeConfigs:(.*)", str(line))
                if search_result:
                    allconfigs = search_result.group(1)
                    axeconfiglist = allconfigs.split(",")

                    for config in axeconfiglist:
                        print("axeconfig:", config)

                search_result = re.search(r"TestListFilePath:(.*)", str(line))
                if search_result:
                    self.test_list_file_path = search_result.group(1)

                search_result = re.search(r"TestExclusiveListFilePath:(.*)", str(line))
                if search_result:
                    self.exclusive_test_list_file_path = search_result.group(1)

                search_result = re.search(r"SingleTestPath:(.*)", str(line))
                if search_result:
                    self.full_path_tests = search_result.group(1)

                search_result = re.search(r"AubLoadDir:(.*)", str(line))
                if search_result:
                    self.aubload_path = search_result.group(1)

                search_result = re.search(r"GritsDir:(.*)", str(line))
                if search_result:
                    self.grits_path = search_result.group(1)

                search_result = re.search(r"AubLoadOption:(.*)", str(line))
                if search_result:
                    self.aubload_option = search_result.group(1)

                search_result = re.search(r"GritsOption:(.*)", str(line))
                if search_result:
                    self.grits_option = search_result.group(1)

                search_result = re.search(r"UnitNames:(.*)", str(line))
                if search_result:
                    self.unit_names = search_result.group(1)

                search_result = re.search(r"GoldIncludeName:(.*)", str(line))
                if search_result:
                    self.gold_include_name_string = search_result.group(1)

                search_result = re.search(r"GoldExcludeName:(.*)", str(line))
                if search_result:
                    self.gold_exclude_name_string = search_result.group(1)

                search_result = re.search(r"UnitTestNames:(.*)", str(line))
                if search_result:
                    self.json_tests = search_result.group(1)

                search_result = re.search(r"UseP4:(.*)", str(line))

                if search_result:
                    use_p4 = search_result.group(1)
                    if use_p4 == "True":
                        self.use_p4 = True
                    else:
                        self.use_p4 = False

                search_result = re.search(r"OfficalAubLoad:(.*)", str(line))
                if search_result:
                    offical_aub = search_result.group(1)
                    if offical_aub == "True" and self.win_release_web_response != 2:
                        self.offical_aubload.set(True)
                        if self.is_win_os:
                            self.getReleaseSet()
                    else:
                        self.offical_aubload.set(False)

                search_result = re.search(r"AubLoadReleaseVersion:(.*)", str(line))
                if search_result:
                    self.aubload_version_load = search_result.group(1)

                search_result = re.search(r"OfficalGrits:(.*)", str(line))
                if search_result:
                    official_grits = search_result.group(1)
                    if official_grits == "True" and self.win_release_web_response != 2:
                        self.offical_grits.set(True)
                        if self.is_win_os:
                            self.getReleaseSet()
                    else:
                        self.offical_grits.set(False)

                search_result = re.search(r"GritsReleaseVersion:(.*)", str(line))
                if search_result:
                    self.grits_version_load = search_result.group(1)

                search_result = re.search(r"TestSource:(.*)", str(line))
                if search_result:
                    self.src_path_or_testrevsion = search_result.group(1)
                search_result = re.search(r"TestRevision:(.*)", str(line))
                if search_result:
                    self.src_path_or_testrevsion = search_result.group(1)
                search_result = re.search(r"RegressPath:(.*)", str(line))
                if search_result:
                    self.regress_base = search_result.group(1)

                search_result = re.search(r"FulsimRevision:(.*)", str(line))

                search_result = re.search(r"RegressName:(.*)", str(line))
                if search_result:
                    self.regress_name = search_result.group(1)

                search_result = re.search(r"RunGrits:(.*)", str(line))
                if search_result:
                    self.run_grits = search_result.group(1)

                search_result = re.search(r"RunAubLoad:(.*)", str(line))
                if search_result:
                    self.run_aubload = search_result.group(1)

                search_result = re.search(r"RunCompare:(.*)", str(line))
                if search_result:
                    self.run_compare = search_result.group(1)
                search_result = re.search(r"IfGoldnize:(.*)", str(line))
                if search_result:
                    self.goldnize = search_result.group(1)

                search_result = re.search(r"Cleanup:(.*)", str(line))
                if search_result:
                    cleanup = search_result.group(1)
                    if cleanup == "True":
                        self.cleanup = True
                    else:
                        self.cleanup = False

                search_result = re.search(r"BinaryGold:(.*)", str(line))
                if search_result:
                    self.binary_gold = search_result.group(1)

                search_result = re.search(r"CheckerGold:(.*)", str(line))
                if search_result:
                    self.checker_gold = search_result.group(1)

                search_result = re.search(r"DramoutGold:(.*)", str(line))
                if search_result:
                    self.dramout_gold = search_result.group(1)

                search_result = re.search(r"GoldBase:(.*)", str(line))
                if search_result:
                    self.gold_base = search_result.group(1)

                search_result = re.search(r"CopyTest:(.*)", str(line))
                if search_result:
                    self.copy_test_forgold = search_result.group(1)
                search_result = re.search(r"NeedCkr:(.*)", str(line))
                if search_result:
                    self.need_ckr = search_result.group(1)

                search_result = re.search(r"CpuCores:(.*)", str(line))
                if search_result:
                    self.num_cores = search_result.group(1)

        # print("LoadConfigure called")
        # print("project_name:", project_name)
        # print("device:", device)
        # self.entry_project_name.delete(0, 'end')
        # self.entry_device.
        # print("num_cores:",self.num_cores )
        # print("regress_name:", self.regress_name)
        # print("gold_type:", self.gold_type)
        # self.setGui()
        # self.saveGuiOutput()
        status_str = "Loaded  configure file:  " + str(os.path.basename(file_path))
        self.updateStatusLabel(status_str)
        self.updateOutputBox(status_str)

        self.win_release_web_response = 0  # reset to ok
        self.updateGui()
        self.saveGuiOutput()
        self.updateDeviceOption()
        try:
            self.selected_axeconfig_list = axeconfiglist
            self.device_cbox.selection_set(self.selected_axeconfig_list)
        except  Exception as e:
            print(e)

        self.reset()
    def loadConfigure(self):
        file_path = tkinter.filedialog.askopenfilename(initialdir=self.config_folder, title="Select a configure file", filetypes=(
        ("configure files", "*.cfg"), ("txt files", "*.txt"), ("all files", "*")))

        file_path = Path(str(file_path))
        self.config_folder = Path(os.path.dirname(file_path))
        #print("file_path:", file_path)
        #print("file_path.is_file:", file_path)
        if file_path == "." or not file_path.is_file():
            return
        self.loadConfigureFile(file_path)

    def reset(self):
        self.binary_gold = False
        self.checker_gold = False
        self.dramout_gold = False
        self.goldnize  = "no"
        self.best_test_revision =0

    def updateGritsPath(self):
        pass
    def updateAubLoadpath(self):
        pass


    def updateDeviceOption(self):
        #print("self.project_name", self.project_name.get())
        self.axe_execution_config_ID_list.clear()
        self.project_name = self.entry_project_name.get()

        self.device_options_set = self.axe_execution.generateExecutionMethodNameList(self.entry_2d_ip.get(),self.entry_3d_ip.get(),self.entry_media_ip.get(),self.entry_utp_ip.get(), self.project_name)


        #print("self.device_options_set", self.device_options_set)
        #print("values",self.device_cbox['values'])
        for i in self.device_cbox.get_children():
            self.device_cbox.delete(i)


        for item in self.device_options_set:
            try:
                self.device_cbox.insert("", "end", "'" + item.name + "'", text=item.name)
                self.axe_execution_config_ID_list.append("'" + item.name + "'")
            except:
                print("Duplicated axe execution method : ", item.name)


        #self.device_cbox.focus(itemlist)
        try:
            self.device_cbox.selection_set(self.selected_axeconfig_list)
        except:
            print("Warning: not found")



        num_of_axe_method =  len(self.device_options_set)
        if  num_of_axe_method == 0:
            self.device_cbox['height'] = 5
        elif num_of_axe_method < 5:
            self.device_cbox['height'] = num_of_axe_method
        else:
            self.device_cbox['height'] = 5
        #self.device_cbox.current(0)
        #self.device = self.entry_device.get()
        #self.device = str(self.device).strip()



    def disableAllGuiItem(self, parent):
        for child in parent.winfo_children():
            wtype = child.winfo_class()
            if wtype not in ('Frame', 'Labelframe','TLabelframe','TFrame','TProgressbar'):
                #print("type = ",wtype)
                child.configure(state='disable')
            else:
                self.disableAllGuiItem(child)

    def enableAllGuiItem(self, parent):
        for child in parent.winfo_children():
            wtype = child.winfo_class()
            print(wtype)
            if wtype == 'Treeview':
                pass
            if wtype not in ('Frame', 'Labelframe','TLabelframe','TFrame','TProgressbar','Treeview'):
                child.configure(state='normal')

            else:
                self.enableAllGuiItem(child)
    def validateList(self, listpath):
        if (not Path(listpath).is_file()):
            messagebox.showerror("Invaid List File!", "The Test List Does Not Exist: " + str(listpath))
            self.stop_regress = True

    def validateGold(self):
        if self.goldnize  == "yes":
            self.gold_base = self.entry_gold_base.get()
            if self.gold_base == '':
                messagebox.showerror("Gold Base Is Empty !", "Please provide gold base path")
                self.stop_regress = True
                return
            self.gold_base = Path(self.gold_base)
            if not self.gold_base.is_dir():
                self.gold_base.mkdir(parents=True, exist_ok=True)
            if not Path(self.gold_base).is_dir():
                messagebox.showerror( str(self.gold_base) + " Does Not Exist!", "Please make sure the path exist")
                self.stop_regress = True
                return
            ## check parent


    def valdiateUnitTest(self, unittest):
        test_item = str(unittest).replace("\\", "/")
        test_item = str(unittest).replace("\"", "")
        test_item = re.sub("#.*", '', str(test_item))
        test_item = re.sub("@.*", '', str(test_item))
        test_path = Path(os.path.join(self.src_path_or_testrevsion, test_item))
        if test_path!=None or test_path!='':
            if not self.use_p4 and self.copytest == "yes":
                self.validateTestPath(test_path)
        else:
            messagebox.showerror("Invalid unit test ", "Not a valid uni test: " + str(test_item))
            self.stop_regress = True

    def validateUnitPath(self,unitpath):
        if not Path(unitpath).is_dir():
            unit = os.path.basename(unitpath)
            messagebox.showerror("Invaldi Unit",  str(unit) + " Does Not Exist!")
            self.stop_regress = True
            return

    def validateTestPath(self,testpath):
        if not Path(testpath).is_dir():
            messagebox.showerror("Invalid Test Path!",  str(testpath) + " Does Not Exist!")
            self.stop_regress = True
            return

    def validateTestSource(self):
        if self.use_p4:
            return
        if str(self.src_path_or_testrevsion).strip() =='':
            messagebox.showerror("Invalid Test Source", "please put source path")
            self.stop_regress = True
            return
        if not Path(self.src_path_or_testrevsion).is_dir():
            messagebox.showerror("Invalid Test Source", str(self.src_path_or_testrevsion) + " Does Not Exist!")
            self.stop_regress = True
            return


    def validateAubload(self):
        # check aubload
        if self.run_aubload and not Path(self.aubload_path).is_dir():
            messagebox.showerror("AubLoad Path Error", "AubLoad Path Does Not Exist! Please make sure the path exist")
            self.stop_regress = True
            return
        else:
            if self.run_aubload:
                if self.is_win_os:
                    self.aubload_exe_path = os.path.join(self.aubload_path, "AubLoad.exe")
                else:
                    self.aubload_exe_path = os.path.join(self.aubload_path, "AubLoad")
                if not Path(self.aubload_exe_path).is_file():
                    messagebox.showerror("Can't Find AubLoad !", "Please make sure AubLoad exist")
                    self.stop_regress = True
                    return
                else:
                    if self.entry_project_name.get() == "mtl":  # mtl aubload expec config folder in the aubload path
                        self.config_path = os.path.join(self.aubload_path, "config")
                        if not Path(self.config_path).is_dir():
                            reply = messagebox.askyesno("AubLoad issue", "Missing config folder in AuLoad path,want to fix it?")
                            if reply:
                                parent_folder = os.path.dirname(self.aubload_path)
                                config_path = os.path.join(parent_folder, "config")
                                if Path(config_path).is_dir():
                                    self.util.CopyOneFolder(Path(config_path), Path(self.config_path))
                                    if Path(self.config_path).is_dir():
                                        messagebox.showinfo("Missing config folder in AubLoad Path",
                                                            "This issue is fixed !")
                                    else:
                                        messagebox.showerror("Missing config folder ",
                                                             "Sorry, you have to fix it by yourself!")
                                        return
                                else:
                                    messagebox.showerror("Missing config folder ",
                                                         "Sorry, you have to fix it by yourself!")
                                    return
                            else:
                                return

                        else:
                            pass

        #check grits
    def validateGrits(self):
        if self.run_grits and not Path(self.grits_path).is_dir():
            messagebox.showerror("Grits Path Error", "Grits Path Does Not Exist! Please make sure the path exist")
            self.stop_regress = True
            return
        else:
            if self.run_grits:
                if self.is_win_os:
                    self.grits_exe_path = os.path.join(self.grits_path, "bin/gritsagent.exe")
                else:
                    self.grits_exe_path = os.path.join(self.grits_path, "bin/gritsagent")
                self.grits_rb_path = os.path.join(self.grits_path, "agent/gritsagent.rb")

                if (not Path(self.grits_exe_path).is_file() and (not Path(self.grits_rb_path).is_file())):
                    messagebox.showerror("Can't Find gritsagent !", "Please make sure gritsagent exist")
                    self.stop_regress = True
                    return
                else:
                    parent_folder = os.path.dirname(self.grits_path)


    def validateRegressPath(self):
        if self.regress_base == '':
            messagebox.showerror("Regress Path Is Empty !", "Please provide regress path")
            self.stop_regress = True
            return

    def getItemList(self, itemString):
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

    def addUniquePath(self, path, pathList):
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

    def validateRegress(self):
        if not self.is_win_os:
            if self.entry_project_name.get() == "cri" or self.entry_project_name.get() == "ttl" or self.entry_project_name.get() == "hml":
                if not self.util.is_sles15():
                    messagebox.showwarning("Wrong linux server", "Please run the regression in a Sles 15 server")
                    return
            else:
                if self.util.is_sles15():
                    messagebox.showwarning("Wrong linux server", "Please run the regression in a Sles 12 server")
                    return

        self.validateGrits()
        self.validateAubload()
        self.validateGold()
        n_axe_config = len(self.axe_execution_method_list)
        if n_axe_config ==0:
            messagebox.showerror("Axe Execution Stage Not Chosed !", "Must choose at least one Axe Execution Stage")
            return
        elif n_axe_config > 1 and self.goldnize=='yes':
            messagebox.showwarning("Invalid Choice!", "Please select only ONE  axe configure for goldenization")
            self.entry_goldnize.set("no")
            return

        # validate exclusive list
        if self.exclusive_test_list_file_path != None and self.exclusive_test_list_file_path != "" :
            self.exclusive_list_paths = self.getItemList(self.exclusive_test_list_file_path)
            if len(self.exclusive_list_paths) > 0:
                self.run_exclusive_lists = True

            for listpath in self.exclusive_list_paths:
                self.validateList(listpath)

        # validate list
        self.test_list_file_path = str(self.test_list_file_path).strip()
        if self.test_list_file_path != None and self.test_list_file_path != "":
            self.validateRegressPath()
            self.validateTestSource()
            self.list_paths = self.getItemList(self.test_list_file_path)
            if len(self.list_paths):
                self.run_test_lists = True
            for listpath in self.list_paths:
                self.validateList(listpath)

        # validate units
        self.unit_names = str(self.unit_names).strip()
        if self.unit_names != None and self.unit_names != "":
            self.validateRegressPath()
            self.validateTestSource()
            self.unit_name_list = self.getItemList(self.unit_names )
            if len(self.unit_name_list) > 0:
                self.run_units = True
        # validate unit tests
        self.json_tests = str(self.json_tests).strip()
        if self.json_tests != None and self.json_tests != "":
            self.json_test_list = self.getItemList(self.json_tests)
            self.validateTestSource()
            self.validateRegressPath()
            if len(self.json_test_list) > 0:
                self.run_unit_tests = True
           # if not self.use_p4:
            #    for json_test in self.json_test_list:
             #       self.valdiateUnitTest(json_test)

        # validate path tests
        if self.goldnize == "yes" or self.cleanup:
            if self.is_win_os and self.use_incredibuild:
                messagebox.showwarning("Incedibuild is not good for ","Goldenize or clean up tests" )
        if not self.run_unit_tests and not self.run_test_lists and not self.run_units and not self.run_abs_path_tests:
            messagebox.showerror("No test to run!", "Please make sure you have tests to run")
            self.stop_regress = True
            return
    def runGuiRegress(self):
        self.saveGuiOutput()
        self.output_info.delete("1.0","end")

        if self.offical_aubload.get():
            if self.aubload_release_version.get() is None or self.aubload_release_version.get().strip() == "":
                messagebox.showerror("Release Version Error", "Please select an AubLoad release version")
                return
            if self.is_win_os:
                status_str = "Downloading cobalt release  " + str(self.aubload_release_version.get()) + "..."
                self.updateStatusLabel(status_str)
                self.updateOutputBox(status_str)
                self.updateProgressBar(1, 0)
                self.aubload_path = self.release_tool.download_and_unzip_release(self.aubload_release_version.get(),
                                                                            self.regress_base)
                self.updateProgressBar(1, 1)
                status_str = "Downloading cobalt release  " + str(self.aubload_release_version.get()) + "... done"
                self.updateOutputBox(status_str)
            else:
                self.aubload_path = self.release_tool.get_linux_aubload_path(self.aubload_release_version.get())
        if self.offical_grits.get():
            if self.grits_release_version.get() is None or self.grits_release_version.get().strip() == "":
                messagebox.showerror("Release Version Error", "Please select a Grits release version")
                return
            if self.is_win_os:
                status_str = "Downloading cobalt release  " + str(self.grits_release_version.get())
                self.updateStatusLabel(status_str)
                self.updateOutputBox(status_str)
                self.updateProgressBar(1, 0)
                self.grits_path = os.path.join(
                    self.release_tool.download_and_unzip_release(self.grits_release_version.get(), self.regress_base),
                    "grits")
                self.updateProgressBar(1, 1)
                status_str = "Downloading cobalt release  " + str(self.grits_release_version.get()) + "... done"
                self.updateOutputBox(status_str)
            else:
                self.grits_path = self.release_tool.get_linux_grits_path(self.grits_release_version.get())

        self.run_cancel_button.config(text='Cancel/Pause', command=self.stopRegress, state = "normal")
        #self.request_one_report_button.config(state="normal")
        self.stop_regress = False
        #self.validateRegress()
        if not self.is_win_os:
            self.p4client.getPassWord(self.windows_password)

        if self.stop_regress:
            self.forceStop()
            return
        self.excuteRegress()

    def forceStop(self):
        self.stop_regress = True
        self.is_regression_started = False
        self.enableAllGuiItem(self)
        self.resetRegression()

        # Reset the display
        self.countdown_label.config(text="Idling time:")
        self.processRun_start_time = time.time()
        self.countdown_timer.config(text="")
        self.update_idletasks()

        self.run_cancel_button.config(text='Start', command=self.runGuiRegress, state="normal")


    def windowsKill(self):
        current_id = os.getpid()
        for proc in psutil.process_iter():
            #don't kill itself
            if proc.name().find(self.script_name) != -1:
                continue
            #print(proc.name())
            if proc.name().find("python") != -1 or proc.name().find("ruby") != -1 or proc.name().find("AubLoad") != -1:
                print(proc.name())
                print(proc.username())
                print(f'Killing {proc.name()}')
                if proc.pid != current_id:
                    print("Killing", str(proc.pid), proc.name())
                    try:
                        proc.kill()
                    except  Exception as e:
                        print(e)
    def linuxkill(self):
        current_id = os.getpid()
        names = ["AubLoad", "ruby","python"] #python
        for name in names:
            for line in os.popen("ps axuh | grep " + name + " | grep -v grep"):
                fields = line.split()
                if (fields[0] ==self.user_id):
                   # extracting Process ID from the output
                    pid = fields[1]
                    process_name = fields[10]
                    paramater_name = fields[11]
                    #don't kill itself
                    if paramater_name.find(self.script_name) != -1:
                        continue
                    if int(pid) != current_id:
                        print("Killing", str(pid), process_name)
                        try:
                            os.kill(int(pid), signal.SIGKILL)
                        except  Exception as e:
                            print(e)
        print("Process Successfully terminated")

    def stopRegress(self):
        reply = messagebox.askyesno("Cancel Regression", "Are you sure to cancel regression?")
        if reply:
            self.stop_regress = True
            self.is_regression_started = False

            # Reset the display
            self.countdown_label.config(text="Idling time:")
            self.processRun_start_time = time.time()
            self.countdown_timer.config(text="")
            self.update_idletasks()

            self.run_cancel_button.config(text='Start', command=self.runGuiRegress, state="normal")

            if self.subprocess is not None:
                try:
                    if self.is_win_os:
                        self._kill_process_tree_windows(self.subprocess.pid)
                    else:
                        self._kill_process_tree_linux(self.subprocess.pid)
                except Exception as e:
                    print(f"Error killing process tree: {e}")
                finally:
                    try:
                        self.subprocess.terminate()
                        time.sleep(1)
                        if self.subprocess.poll() is None:
                            self.subprocess.kill()
                    except Exception as e:
                        print(f"Error in final subprocess termination: {e}")
                    self.subprocess = None
        else:
            self.saveGuiOutput()

    def _get_child_pids_linux(self, parent_pid):
        """
        Safely get direct child PIDs of parent_pid on Linux.
        Uses /proc/<pid>/status which has a clearly labeled 'PPid:' field,
        avoiding the parsing pitfalls of /proc/<pid>/stat where process
        names with spaces/brackets cause field index errors.
        """
        children = []
        try:
            for entry in os.listdir('/proc'):
                if not entry.isdigit():
                    continue
                try:
                    status_path = f'/proc/{entry}/status'
                    with open(status_path, 'r') as f:
                        for line in f:
                            if line.startswith('PPid:'):
                                ppid = int(line.split(':')[1].strip())
                                if ppid == parent_pid:
                                    children.append(int(entry))
                                break  # No need to read further lines
                except (IOError, OSError, ValueError):
                    # Process may have exited while we were reading
                    pass
        except Exception as e:
            print(f"Error scanning /proc for children of {parent_pid}: {e}")
        return children

    def _kill_process_tree_linux(self, pid):
        """
        Kill a process and its entire descendant tree on Linux.

        Strategy (in order):
        1. Try killing the process group (pgid) with SIGKILL — this is the
           most reliable way to kill grits/aubload and all their children
           in one shot, since subprocess.Popen launches them in the same
           process group by default.
        2. Walk /proc to find and kill any remaining descendants that may
           have changed their process group.
        3. Kill the root pid itself as a final safety net.
        """

        # --- Step 1: Kill by process group ---
        try:
            pgid = os.getpgid(pid)
            # Only kill the group if it's not our own process group,
            # to avoid accidentally killing the GUI itself.
            if pgid != os.getpgid(os.getpid()):
                print(f"Killing process group: {pgid}")
                os.killpg(pgid, signal.SIGKILL)
                time.sleep(0.5)  # Brief pause to let OS clean up
            else:
                print(f"Subprocess shares our process group ({pgid}), "
                      f"skipping killpg — falling back to tree walk.")
        except ProcessLookupError:
            print(f"Process group for PID {pid} already gone.")
        except Exception as e:
            print(f"killpg failed for PID {pid}: {e}, falling back to tree walk.")

        # --- Step 2: Walk /proc and kill any surviving descendants ---
        def kill_tree_recursive(parent_pid):
            """
            Post-order traversal: kill children before parent to avoid
            orphaning grandchildren.
            """
            children = self._get_child_pids_linux(parent_pid)
            for child_pid in children:
                kill_tree_recursive(child_pid)

            try:
                os.kill(parent_pid, signal.SIGKILL)
                print(f"Killed PID: {parent_pid}")
            except ProcessLookupError:
                pass  # Already dead — this is fine
            except PermissionError:
                print(f"Permission denied killing PID {parent_pid} "
                      f"(not owned by {self.user_id})")
            except Exception as e:
                print(f"Unexpected error killing PID {parent_pid}: {e}")

        try:
            kill_tree_recursive(pid)
        except Exception as e:
            print(f"Error in kill_tree_recursive for PID {pid}: {e}")

        # --- Step 3: Final check — confirm root pid is dead ---
        try:
            os.kill(pid, 0)  # Signal 0 = check existence only, no actual kill
            # If we reach here the process still exists
            print(f"PID {pid} still alive after tree kill, sending SIGKILL directly.")
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            print(f"PID {pid} confirmed dead.")
        except Exception as e:
            print(f"Error in final PID {pid} check: {e}")

    def _kill_process_tree_windows(self, pid):
        """
        Kill a process and all its descendants on Windows using psutil,
        which IS available on Windows per the import guard at the top of
        the file: if re.search("windows", platform.system()): import psutil
        """
        try:
            parent = psutil.Process(pid)
            children = parent.children(recursive=True)

            # Kill children first to avoid orphans
            for child in children:
                try:
                    print(f"Killing child: {child.pid} ({child.name()})")
                    child.kill()
                except psutil.NoSuchProcess:
                    pass
                except Exception as e:
                    print(f"Error killing child {child.pid}: {e}")

            # Kill the parent
            try:
                print(f"Killing parent: {parent.pid} ({parent.name()})")
                parent.kill()
            except psutil.NoSuchProcess:
                pass
            except Exception as e:
                print(f"Error killing parent {pid}: {e}")

            # Wait and force-kill any survivors
            all_procs = children + [parent]
            gone, alive = psutil.wait_procs(all_procs, timeout=3)
            for proc in alive:
                try:
                    print(f"Force killing survivor: {proc.pid}")
                    proc.kill()
                except Exception:
                    pass

        except psutil.NoSuchProcess:
            print(f"PID {pid} already terminated.")
        except Exception as e:
            print(f"Error in _kill_process_tree_windows: {e}")


    def requestOneReport(self):
        if self.stop_regress:
            messagebox.showwarning("No Regress In Progress ! ", "Please wait and check!")
            return
        if self.require_report:
            messagebox.showwarning("Generating one report ! ", "Please wait and check!")
        else:
            self.require_report = True
            messagebox.showinfo("Report Generation","Request is just sent")

    def runRegress(self):
        print("Starting regression ...")
        self.validateRegress()
        #self.updateRunTime()
        self.total_done_list.clear()
        self.total_fail_list.clear()
        self.total_pass_list.clear()
        self.total_invalid_list.clear()
        self.test_run_list.clear()
        self.exclusive_test_run_list.clear()
        self.test_read_list.clear()
        self.exclusive_test_read_list.clear()
        self.regress_day_mark = datetime.datetime.now().strftime("%b-%d-%Y_%H-%M")
        if self.use_p4:
            self.p4client.setEnvirement()
        self.regress_result_base = Path(os.path.join(self.regress_base, "results"))
        self.regress_result_base.mkdir(parents=True, exist_ok=True)

        self.countdown_label.config(text="Total Run Time:")
        self.start_time = time.time()

        if self.goldnize  == "yes":
            self.binary_gold = self.entry_out_binary.get()
            self.checker_gold = self.entry_track_file.get()
            self.gold_base = str(self.gold_base)
            self.copy_test_forgold = self.entry_copy_test.get()
            self.gold_include_name_string =self.entry_include_file_string.get()
            if self.gold_include_name_string != None and self.gold_include_name_string != "" and not str(self.gold_include_name_string).startswith("#"):
                self.gold_include_name_list = self.getItemList(self.gold_include_name_string)

            self.gold_exclude_name_string =self.entry_exclusive_file_string.get()
            if self.gold_exclude_name_string != None and self.gold_exclude_name_string != "" and not str(self.gold_exclude_name_string).startswith("#"):
                self.gold_exclude_name_list = self.getItemList(self.gold_exclude_name_string)

        ############ exclude tests for unit and list run #############

        if self.run_exclusive_lists:
            while len(self.exclusive_list_paths) > 0:
                exclusive_list_path = self.exclusive_list_paths.pop()

                self.readOneTestList(exclusive_list_path,self.exclusive_test_read_list,True)
            self.exclusive_test_list_file_path = None
            self.run_exclusive_lists = False
        ##self.updateRunTime()
        #self.validateAubload()
        #self.validateGrits()
        # unit/basic/test

        ##self.updateRunTime()


        ##self.updateRunTime()
         ############ run units #############

        if self.run_units:
             self.unit_name_list = self.getItemList(self.unit_names)
             total =  len(self.unit_name_list)
             total_done = 0
             while len(self.unit_name_list) > 0:

                 unit = self.unit_name_list.pop()
                 if self.use_p4:
                     self.p4client.setEnvirement()
                 unit = str(unit).strip()
                 unit = unit.replace('\\', '/')
                 if unit == '':
                     print("Skipped Null unit")
                     continue
                 total_done = total_done + 1
                 info_str = ("(" + str(total_done) + "/" + str(total) + ")" + "Reading " + str(unit) + " tests ...." )
                 print(info_str)
                 self.updateOutputBox(info_str)
                 status_str = "Reading unit tests: " + str(total_done) + "/" + str(total)
                 self.updateStatusLabel(status_str)
                 self.updateOutputBox(status_str)
                 self.updateProgressBar(total, total_done)
                 self.readOneUnit(unit)

             self.unit_names = None
             self.run_units = False

        ############ Run List #############

        if  self.run_test_lists:
            while len(self.list_paths):
                listpath =  self.list_paths.pop()
                if self.use_p4:
                    self.p4client.setEnvirement()
                self.readOneTestList(listpath,self.test_read_list )
                list_file_name = os.path.basename(listpath)
                list_file_name = str(list_file_name)[0:50]

                self.regress_categary = list_file_name
                 # self.regress_id = self.regress_name + "_" + self.regress_categary
                #self.processRun()
            self.test_list_file_path = None
            self.run_test_lists = False


        if self.run_unit_tests:
            json_list = self.convertToJasonList(self.json_test_list)
            # Guard against None return value
            if json_list is None:
                json_list = []
            total = len(json_list)
            processed = 0
            while len(json_list) > 0:
                json_test = json_list.pop()
                json_test = str(json_test).replace("\\", "/")
                json_test = str(json_test).replace("'", "")

                json_test = json_test.strip()
                processed = processed + 1
                print("(" + str(processed) + "/" + str(
                    total) + ")Reading test: " + json_test, end="")
                self.readOneJsonTest(json_test, self.test_read_list)


            self.json_tests = None
            self.run_unit_tests = False

        total = len(self.test_read_list)
        print("total read tests: ", total)
        if len(self.test_run_list) > 0 and len(self.exclusive_test_run_list) > 0:
            self.removeExclusiveTest(self.exclusive_test_run_list, self.test_run_list)
        print("total run tests: ", len(self.test_run_list))
        self.processRun()
        self.perRunReset()

        if self.stop_regress:

            messagebox.showinfo("Sorry !", self.regress_name + " regression is stopped")
            self.resetRegression()
            self.focessRegressonDone()

    def focessRegressonDone(self):
        messagebox.showinfo("Regression Done!",
                            self.regress_name + " regression is done, please check " + self.summary_html_report_path)
        self.resetRegression()
        self.is_regression_started = False  # Stop the runtime updater

        # Reset the display
        self.countdown_label.config(text="Idling time:")
        self.processRun_start_time = time.time()
        self.countdown_timer.config(text="")
        self.update_idletasks()

        self.run_cancel_button.config(text='Start', command=self.runGuiRegress, state="normal")
        self.stop_regress = False
        self.done_regress = False


    def readOneJsonTest(self,json_test, readTestList: list, exclusive=False, p4checkedoutdone=False):
        if json_test.count("#") > 1:
            print("\t==> invalid")
            return
        if re.search(r"_axeconfig", json_test):
            print("\t==> invalid")
            return
        json_test = str(json_test).replace("\"", "")
        json_test = str(json_test).replace(",", "")
        json_test = str(json_test).replace("'", "")
        json_test = str(json_test).replace("*", "")
        json_test = json_test.strip()
        if re.search(r"^#", json_test):
            info = "\t\t==>skipped"
            print(info)
            self.updateOutputBox(info)

            return
        if json_test == None or json_test =="":
            return
        config_id = '0'
        search_result = re.search(r"#([a-zA-Z0-9-_.]+)", str(json_test))
        if search_result:
            config_id = search_result.group(1)

        test_revision = 0
        search_result = re.search(r"@(\d+)", str(json_test))
        if search_result:
            test_revision = search_result.group(0)
            test_revision  = str(test_revision).replace("@", "")
        #cfg test
        search_result = re.search(r"\/([a-zA-Z0-9-_.]*cfg)", str(json_test))
        unit_name = os.path.dirname(json_test)
        folder_name = os.path.basename(unit_name)
        cfg_name = ""
        test_type = ""
        test_name = ""
        gsf_name = ""
        if search_result:
            cfg_name = search_result.group(1)
        if cfg_name !="":
            test_name = str(cfg_name).replace(".cfg", "")
            gsf_name = str(cfg_name).replace(".cfg", ".gsf")
            test_type = "cfg"
        else:
            search_result = re.search(r"\/([a-zA-Z0-9-_.]*\.gsf)", str(json_test))
            if search_result:
                gsf_name = search_result.group(1)
                test_type = "gsf"
            if gsf_name!="":
                test_name = str(gsf_name).replace(".gsf", "")



        test_read = Test.TestRead()
        test_read.type = test_type


        if folder_name == test_name:
            unit_name = os.path.dirname(unit_name)
            test_read.has_own_folder = True
        else:
            test_read.has_own_folder = False
        yaml_name = test_name +".meta.yaml"

        test_read.jason_name = json_test
        if self.use_p4 and self.p4_test_revision!=None:
            test_revision = self.p4_test_revision
        if test_revision == None:
            test_revision = 0

        if int(self.best_test_revision) < int(test_revision) and int(test_revision) !=0:
            self.best_test_revision = test_revision
        test_read.jason_name = re.sub(r"@(\d+)","@"+ str( self.best_test_revision), test_read.jason_name)

        test_read.unit_name = unit_name
        test_read.test_name = test_name
        test_read.gsf_name = gsf_name
        test_read.cfg_name = cfg_name
        test_read.yaml_name = yaml_name

        test_read.test_revision = test_revision
        test_read.config_id = config_id
        if self.use_p4:
            test_src_path = Path(os.path.join(self.p4client.p4_repo_base, unit_name))
        else:
            test_src_path = Path(os.path.join(self.src_path_or_testrevsion, unit_name))


        target_path = Path(os.path.join(self.regress_test_base, unit_name))

        if test_read.has_own_folder:
            test_src_path = Path(os.path.join(test_src_path, test_name))
            if config_id == "-1" or config_id == "0":
                target_path = str(Path(os.path.join(target_path, test_name)))
            else:
                target_path = str(Path(os.path.join(target_path, test_name + "#" + config_id)))

        test_read.test_path = test_src_path
        test_read.gsf_path = os.path.join(test_src_path, test_read.gsf_name)
        test_read.gsf_path = test_read.gsf_path.replace("\\", "/")
        test_read.cfg_path = os.path.join(test_src_path, test_read.gsf_name)
        test_read.cfg_path = test_read.gsf_path.replace("\\", "/")
        test_read.yaml_path = os.path.join(test_src_path, test_read.yaml_name)
        test_read.yaml_path = test_read.yaml_path.replace("\\", "/")
        test_read.path_file_path = os.path.join(test_src_path, "path.txt")
        test_read.path_file_path = test_read.path_file_path.replace("\\", "/")


        if self.use_p4:
            if not p4checkedoutdone:
                info = "P4 copying test " + str(target_path)
                print(info)
                self.updateOutputBox(info)
                info = self.p4client.copyOnefolder(test_read.test_path, target_path, test_revision, True)
                print(info)
                self.updateOutputBox(info)
                if self.util.has_files(target_path):
                    test_read.cfg_path = os.path.join(target_path, test_read.cfg_name)
                    test_read.gsf_path = os.path.join(target_path, test_read.gsf_name)
                    test_read.yaml_path = os.path.join(target_path, test_read.yaml_name)
                    test_read.path_file_path = os.path.join(target_path, "path.txt")
                    test_read.test_path = target_path
                else:
                    test_read.valid_test =False
                    test_read.invalid_message = "test not found"
                #test_read.test_path = target_path
            else:
                test_read.gsf_path = test_read.gsf_path.replace(self.p4client.p4_repo_base, self.regress_test_base)
                test_read.gsf_path = test_read.gsf_path.replace(self.p4client.p4_repo_base, self.regress_test_base)
                test_read.yaml_path = test_read.yaml_path.replace(self.p4client.p4_repo_base, self.regress_test_base)
                test_read.path_file_path = test_read.path_file_path.replace(self.p4client.p4_repo_base,
                                                                            self.regress_test_base)
                #test_read.test_path = target_path


            test_read.p4_test_path = test_src_path
            test_read.test_path = target_path
            test_read.test_src_file_paths = self.util.GetAllFilePathsFromCurrentDir(Path(target_path))
            test_read.test_file_relative_path_list = self.util.GetAllFileRelativePathsFromDir(Path(target_path))
        else:
            test_read.test_src_file_paths = self.util.GetAllFilePathsFromCurrentDir(Path(test_src_path))
            test_read.test_file_relative_path_list = self.util.GetAllFileRelativePathsFromDir(Path(test_src_path))


        if test_read.type == 'cfg':
            self.AddDisplayToolsPath()
            self.copyRequiredFolders(False)



        test_read.yaml_path = test_read.yaml_path.replace("\\", "/")
        test_read.gsf_path = test_read.gsf_path.replace("\\", "/")
        test_read.path_file_path = test_read.path_file_path.replace("\\", "/")

        print ("\t\tSetting up test: " + str(test_read.unit_name + '/' + test_read.test_name), "...")
        if exclusive:
            self.setupOneTest(test_read, self.exclusive_test_run_list)
        else:
            self.setupOneTest(test_read, self.test_run_list)
        readTestList.append(test_read)

    def excuteRegress(self):
        self.start_time = time.time()
        self.processRun_start_time = time.time()
        self.run_time = 0
        self.is_regression_started = False  # Will be set to True when regression actually starts

        Path(self.regress_test_base).mkdir(parents=True, exist_ok=True)

        self.pass_fail_str.set("")
        self.progress_bar['value'] = 0
        self.style.configure('text.Horizontal.TProgressbar', text='')

        if self.delay_min > 0:
            self.delay_second = int(self.delay_min * 60)
            print("Delay time: " + str(self.convert_seconds_left_to_time(self.delay_second)))
            self.countdown_label.config(text="Regress start in:")
            self.countdown_timer.config(text=str(self.convert_seconds_left_to_time(self.delay_second)))
            self.update_idletasks()
            self.start_countdown_timer()
        else:
            # No delay, start immediately
            self.is_regression_started = True
            self.countdown_label.config(text="Total Run Time:")
            self.countdown_timer.config(text="00:00:00")
            self.update_idletasks()
            # Start both the regression and the runtime updater
            self.after(100, self.runRegress)
            self.after(1000, self.updateRunTime)

    def convertUnittestsToJasonList(self, testList: list):
        new_list = list()
        for test_item in testList:
            unit_name = None
            config = None
            revison = 0
            test_name = None
            test_item = str(test_item).replace("\\", "/")
            test_item = str(test_item).replace("'", "")
            test_item = str(test_item).replace("\"", "")
            test_item = str(test_item).replace(",", "")
            test_item = test_item.strip()
            unit_name = os.path.dirname(test_item)
            test_name = os.path.basename(test_item)
            #set to -1: run all the configs/names, default name = '0'
            config = "-1"
            json_test = '"' + unit_name + "/" + test_name +"/" + test_name + ".gsf#" + config +"@"+str(revison) +'"'

            new_list.append(json_test)
        return new_list

    def convertRtlListToJasonList(self, testList: list):
        new_list = list()
        for line in testList:
            json_test = None
            config = "0"
            revison = 0
            test_name = None
            if str(line).find("-fid")== -1: #not a fulsim test
                continue
            search_result = re.search(r'-fid\s+"(.+)"', line)
            if search_result:
                json_test = search_result.group(1)

            search_result = re.search(r'#(\w+) ', line)
            if search_result:
                config = search_result.group(1)

            search_result = re.search(r'repo_ver\s+(\d+)', line)
            if search_result:
                revison = search_result.group(1)

            search_result = re.search(r'([a-zA-Z0-9-_.]*)#', line)
            if search_result:
                test_name = search_result.group(1)

            if json_test == None or test_name==None:
                continue

            new_line = '"' + json_test + "/" + test_name + ".gsf#" + config +"@"+revison +'"'
            #print("new_line: ", new_line)
            new_list.append(new_line)
        return new_list

    def convertRtlTestToJsonTest(self, line):
        json_test = None
        config = "0"
        revison = 0
        test_name = None

        search_result = re.search(r'-fid\s+"(.+)"', line)
        if search_result:
            json_test = search_result.group(1)

        search_result = re.search(r'#(\w+) ', line)
        if search_result:
            config = search_result.group(1)

        search_result = re.search(r'repo_ver\s+(\d+)', line)
        if search_result:
            revison = search_result.group(1)

        search_result = re.search(r'([a-zA-Z0-9-_.]*)#', line)
        if search_result:
            test_name = search_result.group(1)
        new_line = '"' + json_test + "/" + test_name + ".gsf#" + config + "@" + str(revison) + '"'
        return new_line
    def convertToJasonList(self, testList: list):
        new_list = list()# check the first line
        if len(testList) ==0:
            print("not test in the list: ", testList)
            return

        if str(testList[0]).find("--") != -1 and str(testList[0]).find("Product") != -1:
            new_list = self.convertRtlListToJasonList(testList)
        elif str(testList[0]).find('"') != -1:
            new_list = testList
        else:
            new_list = self.convertUnittestsToJasonList(testList)

        return new_list

    def readOneAxejsonfile(self, jsonFilePath):
        print("Reading json tests from ", jsonFilePath)
        test_list = list()
        if not Path(jsonFilePath).is_file():
            return
        with open(jsonFilePath, 'r') as f_in:
            my_data = json.load(f_in)
            executionStagelist  = my_data['executionStages']
            print(type(executionStagelist))
            print(len(executionStagelist))
            for oneStage in executionStagelist:
                testsByLocation_list = oneStage['testsByLocation']

                for item in testsByLocation_list:
                    print(type(item))
                    test_list.extend(item['tests'])
        return test_list

    def readOneTestList(self, listFile, testReadList, exclusive=False):
        list_file = str(listFile).strip()
        if re.search(r"^#", list_file):
            info = "\t\t==>skipped"
            print(info)
            self.updateOutputBox(info)
        list_file_name = os.path.basename(list_file)
        list_file_name = str(list_file_name)[0:20]
        list_file_name = list_file_name + "..."
        if list_file == '':
            return

        if (not Path(list_file).is_file()):
            return

        if str(listFile).endswith('.json'):
            list_data = self.readOneAxejsonfile(listFile)
        else:
            with open(list_file, encoding='utf-8') as f:
                list_data = f.readlines()
        total = len(list_data)
        processed = 0
        if (total > 0):
            print("Reading", list_file_name, " tests: ", total, " ...")
        else:
            print("no tests ")
            return

        for json_test in list_data:


            processed = processed + 1
            #skip test with #
            json_test = json_test.strip()
            if "--" in json_test:
                print("Skipped invalid test: ", json_test)
                continue
            if json_test =='' or json_test==None:
                print("Skipped invalid test: ", json_test)
                continue
            x = re.search("^#", json_test)
            info_str = "(" + str(processed) + "/" + str(total) + ")" + "Reading Json test  " + str(json_test)
            if x:
                info_str = info_str + "skipped"
                print(info_str)
                self.updateOutputBox(info_str)
                self.updateProgressBar(total, processed)
                status_str = "Reading Json tests: " + str(processed) + "/" + str(total)
                self.updateStatusLabel(status_str)
                continue
            #check if json_test has .gsf
            #true: json test, false: test folder

            json_test = str(json_test).replace("\\", "/")
            json_test = str(json_test).replace("*", "")
            json_test = str(json_test).replace("'", "")

            json_test = json_test.strip()

            print("(" + str(processed) + "/" + str(total) + ")Reading test: " + json_test + '...')
            if json_test.find(".gsf") != -1:
                self.readOneJsonTest(json_test, testReadList, exclusive)
                status_str = "Reading Json tests: " + str(processed) + "/" + str(total)
                self.updateStatusLabel(status_str)
                self.updateOutputBox(info_str)
                self.updateProgressBar(total, processed)
                if self.stop_regress:
                    return
            else:
                if json_test.find("-fid") != -1 or json_test.find("-cid") != -1:
                    if json_test.find("-cid") != -1:
                        status_str = "Reading rtl tests: " + str(processed) + "/" + str(total) + " skipped: rtl cid test"
                        print(status_str)
                        self.updateStatusLabel(status_str)
                        self.updateOutputBox(info_str)
                        self.updateProgressBar(total, processed)
                    else:
                        json_test = self.convertRtlTestToJsonTest(json_test)
                        status_str = "Converted to json test:  " + json_test
                        print(status_str)
                        self.updateStatusLabel(status_str)
                        self.readOneJsonTest(json_test, testReadList, exclusive)
                        status_str = "Reading rtl tests: " + str(processed) + "/" + str(total)
                        print(status_str)
                        self.updateStatusLabel(status_str)
                        self.updateOutputBox(info_str)
                        self.updateProgressBar(total, processed)
                        if self.stop_regress:
                            return

                else:
                    self.readOneUnit(json_test)
                    status_str = "Reading unit tests: " + str(processed) + "/" + str(total)
                    print(status_str)
                    self.updateStatusLabel(status_str)
                    self.updateOutputBox(info_str)
                    self.updateProgressBar(total, processed)
                    if self.stop_regress:
                        return





    def hasTestRun(self, testRun:Test.TestRun, testRunList:list):
        has_testrun= False
        for testrun in testRunList:
            if testRun.test_run_path == testrun.test_run_path:
                has_testrun = True
                break
        return  has_testrun

    def hasTest(self, list):
        total = len(list)
        if total == 0:
            return False
        else:
            return True
    def removeExclusiveTest(self, exclusiveTestRunList, testRunList):
        if len(exclusiveTestRunList) == 0 or len(testRunList) == 0 :
            return
        for exclusive_test_run in exclusiveTestRunList:
            for test_run in testRunList:
                if exclusive_test_run.unit_name == test_run.unit_name and exclusive_test_run.test_name == test_run.test_name:
                    print("test ", test_run.unit_name, "/", test_run.test_name, " is removed")
                    testRunList.remove(test_run)




    def addUniqueTestRead(self, testReadList, testRead):
        if len(testReadList) == 0:
            testReadList.append(testRead)
            return True
        else:
            unique = True
            for test_read in testReadList:
                if ((test_read.unit_name == testRead.unit_name) and (
                        test_read.test_name == testRead.test_name)):
                    unique = False
                    break
            if unique:
                testReadList.append(testRead)
                return True
            else:
                return False

    def addUniqueRequiredFolder(self, folderList, folderName):
        if len(folderList) == 0:
            folderList.append(folderName)
        else:
            unique = True
            for folder_name in folderList:
                if folderName== folder_name:
                    unique = False
                    break
            if unique:
                folderList.append(folderName)

    def CheckRequiredFolder2(self, working_path, aubloadoptions, required_folder_list: list):
        options = aubloadoptions.split()
        is_include_option = False
        include_options = list()
        for option in options:
            if "-include" in option:
                is_include_option = True
                continue
            elif "+aubload" in option or "+fulsim"  in option:
                is_include_option = False
                continue
            elif "-" in option and (not "include"  in option):
                is_include_option = False
                continue
            if is_include_option:
                include_options.append(option)
        if len(include_options) == 0:
            print("there is no include options")
            return
        os.chdir(working_path)
        for onepath in include_options:
            onepath = str(onepath).replace("\\", "/")
            include_folder_path = abspath(onepath)
            include_folder_path = str(include_folder_path).replace("\\", "/")
            if Path(str(include_folder_path)).is_dir():
                #print("include_folder_path to be added: ", include_folder_path)
                self.addUniqueRequiredFolder(required_folder_list, include_folder_path)
    def AddDisplayToolsPath(self):
        display_tools = 'DISP_tools'
        display_tools_path = os.path.join(self.regress_test_base,display_tools)
        display_tools_path = str(display_tools_path).replace("\\", "/")
        self.addUniqueRequiredFolder(self.required_folders, display_tools_path)
    def CheckRequiredFolder(self, path_file_path, required_folder_list:list, for_gold=False):
        dir_path = os.path.dirname(path_file_path)
        os.chdir(dir_path)
        if Path(path_file_path).is_file():
            with open(path_file_path, encoding='utf-8') as f:
                paths = f.readlines()
                must_included_folder = 'INPUTPATH="../../../include"'
                paths.append(must_included_folder)
                for onepath in paths:
                    onepath.strip()
                    if onepath != None and onepath != "":
                        onepath = str(onepath).replace("\\", "/")
                        search_result = re.search(r'INPUTPATH\s*=\s*"(.+)"', onepath)
                        if search_result:
                            include_folder = str(search_result.group(1)).strip()
                            include_folder_path = abspath(include_folder)
                            # if self.use_p4 and not for_gold:
                            # include_folder_path = str(include_folder_path).replace(str(os.path.join(self.regress_base, "tests")), self.p4client.p4_repo_base)
                            include_folder_path = str(include_folder_path).replace("\\", "/")
                            # print("include_folder_path to be added: ",include_folder_path)
                            self.addUniqueRequiredFolder(required_folder_list, include_folder_path)
        else:  # add "../../../include"'
            include_folder = "../../../include"
            include_folder_path = abspath(include_folder)
            include_folder_path = str(include_folder_path).replace("\\", "/")

            self.addUniqueRequiredFolder(required_folder_list, include_folder_path)



    def CheckRequiredFiles(self, gsf_path):
        required_file_list = list()
        if Path(gsf_path).is_file():
            with open(gsf_path,encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines:
                    search_result = re.search(r'"(.+\.asm)"', line)
                    if search_result:
                        required_file = search_result.group(1)
                        required_file_list.append(required_file)
                    search_result = re.search(r'"(.+\.gsf)"', line)
                    if search_result:
                        required_file = search_result.group(1)
                        required_file_list.append(required_file)
                    search_result = re.search(r'.include\s+"(.+)"', line)
                    if search_result:
                        required_file =  search_result.group(1)
                        required_file_list.append(required_file)

                    search_result = re.search(r'require \s*"(.+)"', line)
                    if search_result:
                        required_file =  search_result.group(1)
                        if  Path(required_file).suffix != '.rb':
                            required_file = required_file + ".rb"
                        required_file_list.append(required_file)

                    search_result = re.search(r':clip\s+=>\s*"(.+)"', line)
                    if search_result:
                        required_file = search_result.group(1)
                        required_file_list.append(required_file)
                    search_result = re.search(r'clipFileName\s+=\s*"(.+)"', line)
                    if search_result:
                        required_file = search_result.group(1)
                        required_file_list.append(required_file)

        return  required_file_list

    def addUniqueUnit(self, unitName):
        if len(self.run_unit_list) == 0:
            self.run_unit_list.append(unitName)
        else:
            unique = True
            for unit_name in self.run_unit_list:
                if unitName== unit_name:
                    unique = False
                    break
            if unique:
                self.run_unit_list.append(unitName)

    def addUniqueTest(self, testRunList, testRun):
        if len(testRunList) == 0:
            testRunList.append(testRun)
        else:
            unique = True
            for test_run in testRunList:
                if testRun.valid_test:
                    if (testRun.test_run_path == test_run.test_run_path) and (testRun.test_name == test_run.test_name):
                        unique = False
                        break
                else:
                    if (testRun.unit_name == test_run.unit_name) and (testRun.test_name == test_run.test_name) and (testRun.config_id == test_run.config_id):
                        unique = False
                        break
            if unique:
                testRunList.append(testRun)

    def copyRequiredFolders(self, forGold=False):
        self.required_folders.extend(self.unit_required_folders)
        required_folders = self.required_folders
        if forGold == True:
            required_folders = self.gold_required_folders

        total = len(required_folders)
        if (total<1):
            print("skipped")
            return
        total_done = 0
        self.updateProgressBar(total, total_done)
        for folder in required_folders:
            time.sleep(0.01)
            self.update()
            if self.stop_regress:
                return
            dest_path = folder

            total_done = total_done + 1
            info_str =""
            status_str = "Copying required folders: " + str(total_done) + "/" + str(total)
            self.updateStatusLabel(status_str)
            self.updateOutputBox(status_str)
            self.updateProgressBar(total, total_done)
            if forGold==True:
                gold_base = str(self.gold_base).replace("\\", "/")
                regress_test_base = str(self.regress_test_base).replace("\\", "/")
                src_path = dest_path.replace(gold_base, regress_test_base)
                info_str = ("(" + str(total_done) + "/" + str(total) + ")" + "P4Copying " + str(src_path) +" to " + str(dest_path) + "...")
                print(info_str)

                self.util.CopyOneFolderByfiles(src_path, dest_path, True)
            else:
                regress_test_base = str(self.regress_test_base).replace("\\", "/")
                if self.use_p4:

                    src_path = dest_path.replace(regress_test_base, self.p4client.p4_repo_base)
                    info_str = ("(" + str(total_done) + "/" + str(total) + ")" + "Copying " + str(
                        src_path) + " to " + str(dest_path) + "...")
                    self.updateProgressBar(total, total_done)
                    if self.util.DirHasFiles(dest_path):
                        if self.is_win_os:
                            info_str = info_str + "skipped"
                            self.updateOutputBox(info_str)
                        else:
                            self.updateOutputBox(info_str)
                            try:
                                info_str = self.p4client.copyOnefolder(src_path, dest_path, self.best_test_revision, True)
                            except Exception as e:
                                info_str = (f'Error copying file {src_path}: {e}')
                    elif self:
                        self.updateOutputBox(info_str)
                        try:
                            info_str = self.p4client.copyOnefolder(src_path, dest_path, self.best_test_revision, True)
                        except Exception as e:
                            info_str = (f'Error copying file {src_path}: {e}')
                    print(info_str)

                else:
                    #dest_path is actully src path.
                    self.updateProgressBar(total, total_done)
                    src_path = dest_path
                    src_path_or_testrevsion =  str(self.src_path_or_testrevsion).replace("\\", "/")
                    dest_path =  str(src_path).replace( src_path_or_testrevsion, str(self.regress_test_base))
                    dest_path = str(dest_path).replace("\\", "/")
                    info_str = ("(" + str(total_done) + "/" + str(total) + ")" + "Copying " + str(
                        src_path) + " to " + str(dest_path) + "...")
                    print(info_str)
                    self.util.CopyOneFolderByfiles(src_path, dest_path, True)
                print(" ==> done")

            self.updateOutputBox(info_str)
            self.updateProgressBar(total, total_done)
        self.required_folders.clear()
            ##self.updateRunTime()

    def copyTests(self, testRunList:list):

        total = len(testRunList)
        processed = 0

        self.updateProgressBar(total, processed)

        print("copyed tests:  ", total)
        if total == 0:
            return

        #num_cores = self.cores.get()
        #always use one core
        processed = 0
        #tests/include folder is always required
        for test_run in testRunList:
            processed = processed + 1

            self.update()
            if self.stop_regress:
                return

            if not test_run.valid_test:
                continue

            info_str = ("(" + str(processed) + "/" + str(total) + ")Copying test: " + str(
                test_run.unit_name) + "/" + str(test_run.test_name) + "_cfg" + str(test_run.config_id) + "...")
            print(info_str)
            self.updateOutputBox(info_str)

            self.copyOneTest(test_run)
            #test_run.fileResolve()


            status_str = "Copying tests: " + str(processed) + "/" + str(total)
            self.updateStatusLabel(status_str)
            self.updateOutputBox(status_str)
            self.updateProgressBar(total, processed)



    def copyOneTest(self,testRun):

        dst_path = testRun.test_run_path
        Path(dst_path).mkdir(parents=True, exist_ok=True)

        print("copying test files: " + str(testRun.test_src_path) + " to " + str(dst_path), end='')
        if not self.util.DirHasFiles(dst_path,0):
            if testRun.has_own_folder:
                self.util.CopyOneFolderByfiles(testRun.test_src_path,dst_path,False)
            else:
                self.util.copyOneFile(testRun.yaml_src_path, dst_path)
                self.util.copyOneFile(testRun.path_src_path, dst_path)
                if testRun.type =="cfg":
                    self.util.copyOneFile(testRun.cfg_src_path, dst_path)
                else:
                    self.util.copyOneFile(testRun.gsf_src_path, dst_path)
            print(" ==> done")
        else:
            print(" ==> skipped")
        if self.run_compare and testRun.has_gold:
            print("copying test gold files: " + str(testRun.gold_src_path) + " to " + str(testRun.gold_work_path), end='')
            if self.use_p4:
                info = self.p4client.copyOnefolder(testRun.gold_src_path,testRun.gold_work_path,testRun.test_revision)
                self.updateOutputBox(info)
            else:
                target_path = os.path.dirname(testRun.gold_work_path)
                self.util.CopyOneFolder(testRun.gold_src_path,target_path)

        #testRun.test_src_file_paths = self.util.GetAllFilePathsFromCurrentDir(Path(dst_path))
        #testRun.test_file_relative_path_list = self.util.GetAllFileRelativePathsFromDir(Path(dst_path))

    def setupTestGoldenizedFolder(self,test_run:Test.TestRun):
        goldenized_test_path = Path(os.path.join(str(self.gold_base), str(test_run.unit_name)))
        if test_run.has_own_folder:
            goldenized_test_path = Path(os.path.join(goldenized_test_path, test_run.default_name))
        test_run.goldenized_test_path = goldenized_test_path
        test_run.goldenized_test_gold_path = os.path.join(test_run.goldenized_test_path, "gold")
        test_run.goldenized_test_gold_path = os.path.join(test_run.goldenized_test_gold_path, test_run.test_name)
        test_run.copy_test = self.copy_test_forgold
        test_run.checker_gold = self.checker_gold
        test_run.dramout_gold = self.dramout_gold
        test_run.binary_gold = self.binary_gold
        test_run.gold_base = self.gold_base
    def setupTestGoldFolder(self,testRun:Test.TestRun):
        test_run = testRun
        test_run.ckr_folder_path = self.ckr_folder
        test_run.need_ckr = self.need_ckr
        test_run.ckr_folder_path = self.ckr_folder
        test_run.has_gold = False
        ### check new gold folder

        if self.use_p4:
            old_gold_base = os.path.dirname(test_run.p4test_src_path)
            new_gold_base = os.path.join(test_run.test_run_path, "gold")
        else:
            old_gold_base = os.path.dirname(test_run.test_src_path)
            new_gold_base = os.path.join(test_run.test_src_path, "gold")
        old_gold_base = os.path.dirname(old_gold_base)
        old_gold_base = os.path.join(old_gold_base, "gold")
        old_gold_base = str(old_gold_base).replace("\\", "/")
        new_gold_base = str(new_gold_base).replace("\\", "/")
        new_gold_folder_path = os.path.join(new_gold_base, test_run.test_name)
        old_gold_folder_path = os.path.join(old_gold_base, test_run.default_name)
        old_gold_folder_path = str(old_gold_folder_path).replace("\\", "/")
        new_gold_folder_path = str(new_gold_folder_path).replace("\\", "/")

        if os.path.isdir(new_gold_folder_path) or (self.use_p4 and self.p4client.fileExist(new_gold_folder_path)):
            test_run.has_gold = True
            test_run.gold_src_path = new_gold_folder_path
            if self.use_p4:
                test_run.gold_work_path = str(new_gold_folder_path).replace(
                    self.p4client.p4_repo_base, str(self.regress_test_base))
            else:
                test_run.gold_work_path = str(new_gold_folder_path).replace(
                    self.src_path_or_testrevsion, str(self.regress_test_base))
            print("gold_work_path: ", test_run.gold_work_path)
        if not test_run.has_gold:
            if os.path.isdir(old_gold_folder_path) or (self.use_p4 and self.p4client.fileExist(old_gold_folder_path)):
                test_run.has_gold = True
                test_run.gold_src_path = old_gold_folder_path
                if self.use_p4:
                    test_run.gold_work_path = str(old_gold_folder_path).replace(
                        self.p4client.p4_repo_base, str(self.regress_test_base))
                else:
                    test_run.gold_work_path = str(old_gold_folder_path).replace(
                        self.src_path_or_testrevsion, str(self.regress_test_base))
                print("gold_work_path: ", test_run.gold_work_path)

        if not test_run.has_old_gold and not test_run.has_gold:
            new_gold_folder_path = new_gold_folder_path + "#" + test_run.config_id
            old_gold_folder_path = old_gold_folder_path + "#" + test_run.config_id
            if os.path.isdir(new_gold_folder_path) or (self.use_p4 and self.p4client.fileExist(new_gold_folder_path)):
                #test_run.has_old_gold = True
                test_run.gold_src_path = new_gold_folder_path
                if self.use_p4:
                    test_run.gold_work_path = str(new_gold_folder_path).replace(
                        self.p4client.p4_repo_base, str(self.regress_test_base))
                else:
                    test_run.gold_work_path = str(new_gold_folder_path).replace(
                        self.src_path_or_testrevsion, str(self.regress_test_base))
            if not test_run.has_old_gold:
                if os.path.isdir(old_gold_folder_path) or (self.use_p4 and self.p4client.fileExist(old_gold_folder_path)):
                    test_run.has_old_gold = True
                    test_run.gold_src_path = old_gold_folder_path
                    if self.use_p4:
                        test_run.gold_work_path = str(old_gold_folder_path).replace(
                            str(self.p4client.p4_repo_base), str(self.regress_test_base))
                    else:
                        test_run.gold_work_path = str(old_gold_folder_path).replace(
                        str(self.src_path_or_testrevsion), str(self.regress_test_base))


            if self.use_p4 and test_run.gold_src_path != "" and test_run.gold_work_path != "":
                self.p4client.copyOnefolder(test_run.gold_src_path,test_run.gold_work_path,self.p4_test_revision)
        print("gold_work_path by setupTestGoldFolder: ", test_run.gold_work_path)
    def configTestRun(self, testRun:Test.TestRun,testRead:Test.TestRead, testRunList, testConfig):
        test_run = testRun

        test_confg = testConfig
        test_run.valid_test = testRead.valid_test
        #test_run.test_file_relative_path_list = testRead.test_file_relative_path_list
        #test_run.test_src_file_paths = testRead.test_src_file_paths
        if not testRead.valid_test:
            test_run.test_result.invalid_message = testRead.invalid_message
        test_run.seed = testRead.seed
        test_run.grits_exe = self.grits_exe_path
        test_run.grits_rb = self.grits_rb_path
        test_run.aubload_exe = self.aubload_exe_path
        test_run.run_grits = self.run_grits

        test_run.run_aubload = self.run_aubload
        test_run.run_compare = self.run_compare
        test_run.time_stamp = "_" + self.regress_day_mark

        test_run.p4test_src_path = testRead.p4_test_path
        test_run.gsf_src_path = testRead.gsf_path
        test_run.cfg_src_path = testRead.cfg_path
        test_run.yaml_src_path = testRead.yaml_path
        test_run.path_src_path =  testRead.path_file_path
        test_run.unit_name = testRead.unit_name

        test_run.run_gold = self.goldnize
        test_run.cleanup = self.cleanup
        test_run.has_own_folder = testRead.has_own_folder
        test_run.test_name = testRead.test_name
        test_run.gsf_name = testRead.gsf_name
        test_run.cfg_name = testRead.cfg_name
        test_run.test_src_file_paths = testRead.test_src_file_paths
        test_run.test_file_relative_path_list = testRead.test_file_relative_path_list

        if test_confg != None:
            test_run.config_id = test_confg.Name
            test_run.jason_name = test_run.jason_name.replace('#-1','#'+ test_confg.Name)
            test_run.test_name = testRead.test_name + "#" + test_confg.Name
            if testRead.ymal_config.TestFileName !='':
                if testRun.type=='cfg':
                    test_run.cfg_name = testRead.ymal_config.TestFileName
                else:
                    test_run.gsf_name = testRead.ymal_config.TestFileName
            else:
                if testRun.type == 'cfg':
                    test_run.cfg_name = testRead.cfg_name
                else:
                    test_run.gsf_name = testRead.gsf_name

        else:
            test_run.test_name = testRead.test_name
            test_run.gsf_name = testRead.gsf_name

        test_run.yaml_name = testRead.yaml_name

        test_run.type = testRead.type
        if not testRead.has_own_folder:
            dst_path = Path(os.path.join(self.regress_test_base, test_run.unit_name))
            test_run.unit_run_path = dst_path
            if test_run.config_id =="0" and int(test_run.seed,0) == 1:
                dst_path = str(dst_path) + "_" + test_run.default_name
            else:
                dst_path = str(dst_path) + "_" + test_run.test_name
            #if test_confg.Name !='0':
            #    dst_path = str(dst_path) + "_" + test_run.test_name + "#" + test_confg.Name
            #else:
            #    dst_path = str(dst_path) + "_" + test_run.test_name
        else:
            dst_path = Path(os.path.join(self.regress_test_base, test_run.unit_name))
            test_run.unit_run_path = dst_path
            if test_run.config_id == "0" and int(test_run.seed,0) == 1:
                dst_path = Path(os.path.join(dst_path, test_run.default_name))
            else:
                dst_path = Path(os.path.join(dst_path, test_run.test_name))

        test_run.test_run_path = dst_path



        if self.run_compare:
            self.setupTestGoldFolder(test_run)
        if self.goldnize == 'yes':
            self.setupTestGoldenizedFolder(test_run)




        if test_confg != None and test_confg.CommandLine != None and test_confg.CommandLine != "":
            test_grits_option = test_run.getGritsOption(test_confg.CommandLine)
            test_auload_option = test_run.getAubLoadOption(test_confg.CommandLine)
            test_run.yaml_cmdline = str(testConfig.CommandLine).replace('"', '')
            test_run.yaml_cmdline = str(test_run.yaml_cmdline).replace("'", '')
        else:
            test_grits_option =  test_run.getGritsOption(testRead.ymal_config.DefaultTestConfig.CommandLine)
            test_auload_option = test_run.getAubLoadOption(testRead.ymal_config.DefaultTestConfig.CommandLine)
            test_run.yaml_cmdline = str(testRead.ymal_config.DefaultTestConfig.CommandLine).replace('"', '')
            test_run.yaml_cmdline = str(test_run.yaml_cmdline).replace("'", '')
        #for 3d tests, include folder
        if  test_auload_option.find("-include")!= -1 and Path(test_run.test_run_path).is_dir():
            self.CheckRequiredFolder2( Path(test_run.test_run_path), test_auload_option,self.required_folders)
            self.CheckRequiredFolder2(Path(test_run.test_run_path), test_auload_option, test_run.test_required_folders)
        self.CheckRequiredFolder(test_run.path_src_path, test_run.test_required_folders)
        self.CheckRequiredFolder(test_run.path_src_path, self.required_folders, False)
        test_run.test_required_files = self.CheckRequiredFiles(test_run.gsf_src_path)
        config_index = 0
        for axeConfig in self.axe_execution_method_list:
            test_run = copy.deepcopy(test_run)
            test_run.axe_execution_method = axeConfig
            config_index =  config_index + 1
            if test_run.type == 'cfg':
                test_run.run_cfg = True
                test_run.disp_tool_base = self.regress_test_base
                test_run.disp_tool_base = str(test_run.disp_tool_base).replace("\\", "/")
                test_run.disp_setup_exe = os.path.join(test_run.disp_tool_base, 'DISP_tools/setup/DispSetup')
                test_run.disp_setup_exe = str(test_run.disp_setup_exe).replace("\\", "/")
                test_run.generateDispOption()
                self.test_runner.runCFG(test_run)
                test_run.run_cfg = False
                test_run.type = 'gsf'
            test_run.dump_path = test_run.test_run_path
            if config_index > 1:
                test_run.test_run_path  =  str(test_run.test_run_path) + "_axeconfig" + str(config_index)
            if len(self.axe_execution_method_list) > 1:
                test_run.file_identifier = str(axeConfig.name).replace(" ", "_")
                test_run.file_identifier = test_run.file_identifier.lower()
            else:
                test_run.file_identifier = ''

            if axeConfig != None:
                suite_grits_option = axeConfig.grits_options + " " + self.grits_option
                suite_aubload_option = axeConfig.fulsim_options + " " + self.aubload_option
            else:
                suite_grits_option = self.grits_option
                suite_aubload_option = self.aubload_option
                # check if there is -s seed  and get the seed
            suit_grits_seed = None
            search_result = re.search(r'-s \s*(\S+)', suite_grits_option)
            if search_result:
                suit_grits_seed = str(search_result.group(1))


            grits_option = test_grits_option  # + " " + default_grits_option
            aubload_options = test_auload_option  # + " " + default_aubload_option
            if grits_option != None:
                if not re.search(r'-s\s*(\S+)', grits_option):
                    grits_option = grits_option + " -s " + str(testRun.seed)
            else:
                grits_option = "-s " + str(testRun.seed)

            if self.random_times == 0:
                if suit_grits_seed != None:
                    grits_option = re.sub(r'-s\s*\S+', '', grits_option)
            else:
                grits_option = re.sub(r'-s\s*\S+', '-s '+  str(testRun.seed), grits_option)

            # test_run.yaml_cmdline = str(testRead.ymal_config.DefaultTestConfig.CommandLine).replace('"','') + " " + str(testConfig.CommandLine).replace('"','')
            test_run.yaml_cmdline = str(test_run.yaml_cmdline).replace('"', '')
            test_run.yaml_cmdline =  str(test_run.yaml_cmdline).replace("'",'')

            grits_option = grits_option + " " + suite_grits_option
            aubload_options = aubload_options + " " + suite_aubload_option
            test_run.grits_option = grits_option + " -device " + test_run.axe_execution_method.device_option
            test_run.aubload_option = aubload_options + " -device " + test_run.axe_execution_method.device_option

            if test_confg != None:
                if test_confg.VirtualPath != None:
                    test_run.test_result.virtual_path = test_confg.VirtualPath
                elif testRead.ymal_config.DefaultTestConfig.VirtualPath != None:
                    test_run.test_result.virtual_path = testRead.ymal_config.DefaultTestConfig.VirtualPath
            else:
                test_run.test_result.virtual_path = "N/A"
            # compare gold
            if test_run.unit_name != None and test_run.test_name != None:
                self.addUniqueTest(testRunList, test_run)
                self.addUniqueUnit(test_run.unit_name)
                print("\t" + test_run.jason_name + " added")
            else:
                print("\t" + test_run.jason_name + " not added")

            if test_run.run_cfg:
                disp_options = " -test " + test_run.default_name + " -proj "
                device  = str(axeConfig.device_option).split("/")[-1]
                proj_name = device.split('.')[0]
                disp_options =  disp_options + proj_name + " -disp_tools " + str(test_run.disp_tool_base) + " -tdir " + str(test_run.test_run_path) + " -fileresolverpath "
                file_resolve_path = os.path.join(test_run.disp_tool_base, "AxeFileResolver")
                disp_options = disp_options + str(file_resolve_path)
                disp_options = disp_options.replace("\\", "/")
                test_run.disp_options = disp_options
                print("disp_options = ",  test_run.disp_options)

        #print("suite_aubload_option = ", suite_aubload_option)
        #print("default_aubload_option = ", default_aubload_option)
        #print("test_aubload_option = ", test_aubload_option)

    def setupOneTest(self,testRead,testRunList):

        if  Path(testRead.yaml_path).is_file():
            print("\t\tReading test yaml file", testRead.yaml_path, "...")
            self.readYamlFile(testRead.yaml_path, testRead)
        else:
            testRead.valid_test = False
            testRead.invalid_message  = "not a yaml test"
        test_run = Test.TestRun(self.use_p4)
        test_run.project_id = self.project_name
        test_run.regress_base = self.regress_base
        test_run.test_revision = testRead.test_revision
        test_run.jason_name = testRead.jason_name
        test_run.unit_name = testRead.unit_name
        test_run.cfg_name = testRead.cfg_name
        test_run.gsf_name = testRead.gsf_name
        test_run.cfg_src_path = testRead.cfg_path
        test_run.gsf_src_path = testRead.gsf_path
        test_run.test_run_path = testRead.test_dist_path
        test_run.test_src_path = testRead.test_path
        test_run.type = testRead.type
        test_run.config_id = testRead.config_id
        test_run.default_name = testRead.test_name


        if not testRead.valid_test:
            test_run.valid_test = testRead.valid_test
            test_run.invalid_message = testRead.invalid_message
            test_run.unit_name = testRead.unit_name
            test_run.default_name =  test_run.test_name = testRead.test_name + "#" + test_run.config_id
            test_run.test_result.invalid_message = testRead.invalid_message
            print(" invalid ",end="")
            self.addUniqueTest(testRunList, test_run)
        else:
            if not (testRead.config_id == None or testRead.config_id == "" or testRead.config_id == "-1"):
                for test_confg in testRead.ymal_config.test_config_list:
                    if testRead.config_id == test_confg.Name:
                        self.configTestRun(test_run, testRead, testRunList, test_confg)
                        if self.random_times  > 0:
                            test_name = testRead.test_name
                            for i in range(self.random_times):
                                seed = random.randint(2, 0xffffffff)
                                seed_hex = hex(seed)
                                testRead.seed = seed_hex
                                testRead.test_name = test_name + "_s" + str(seed_hex)
                                new_test_run = copy.deepcopy(test_run)
                                print(" ==> done")
                                self.configTestRun(new_test_run, testRead, testRunList, test_confg)
            else:
                for test_confg in testRead.ymal_config.test_config_list:
                    new_test_run = copy.deepcopy(test_run)
                    self.configTestRun(new_test_run, testRead, testRunList, test_confg)
                    # print(vars(test_run))
                    # testRunList.append(test_run)
                    if self.random_times  > 0:
                        test_name = testRead.test_name
                        for i in range(self.random_times):
                            seed = random.randint(2, 0xffffffff)
                            seed_hex = hex(seed)
                            testRead.seed = seed_hex
                            testRead.test_name = test_name + "_s" + str(seed_hex)
                            new_test_run = copy.deepcopy(test_run)
                            print(" ==> done")
                            self.configTestRun(new_test_run, testRead, testRunList, test_confg)
                            # replace -s option



    def retrieveTestRunObjects(self, total_test, testrun_object_folder_path, regress_name):
        all_file_paths = self.util.GetAllFilePathsFromDir(testrun_object_folder_path)
        after_time = 15000
        if total_test > 500:
            after_time = 30000
        if total_test > 3000:
            after_time = 60000
        if total_test > 6000:
            after_time = 120000
        num_retrieved = 0
        for file_path in all_file_paths:
            if  Path(file_path).suffix == ".testrun" and str(file_path).find(str(self.regress_day_mark)) != -1:

                with open(Path(file_path), 'rb') as testRunbinary:
                    try:
                        test_run = pickle.load(testRunbinary)
                        num_retrieved = num_retrieved + 1
                        info_str = "(" + str(num_retrieved) + ")Retrieving  test " + str(
                            test_run.test_name + "#" + test_run.config_id) + "..."
                        self.addUniqueTest(self.total_done_list,test_run)
                        if test_run.goldnize_status ==  "SUCCESS":
                            path_file_path = os.path.normpath(
                                Path(os.path.join(test_run.goldenized_test_path, "path.txt")))
                            self.CheckRequiredFolder(path_file_path, self.gold_required_folders,True)
                        grits_status = test_run.test_result.grits_compile_status
                        fulsim_status = test_run.test_result.fulsim_compile_status
                        compare_status = test_run.test_result.compare_status
                        goldnize_status = test_run.goldnize_status
                        info_str = info_str + "done, "

                        if test_run.run_grits:
                            info_str = info_str + " grits: " + grits_status
                        if test_run.run_aubload:
                            info_str = info_str + " fulsim: " + fulsim_status
                        if test_run.run_compare:
                            info_str = info_str + " gold compare: " + compare_status
                        if test_run.run_gold=="yes":
                            info_str = info_str + " goldenize: " + goldnize_status
                        self.updateOutputBox(info_str)

                    except:
                        print("test run object can not be loaded: ", file_path)
                try:
                    os.remove(file_path)
                except:
                    print("test run object can not be deleted: ", file_path)

        if len(self.gold_required_folders)>0 and  self.goldnize  == "yes":
            self.copyRequiredFolders(True)
        total_done = len(self.total_done_list)
        self.updateObjectRegressStatus(self.total,self.total_done_list,regress_name)

        self.updateProgressBar(self.total, total_done)
        if  total_done >= total_test or self.stop_regress:
            self.regress_settings.end_time = datetime.datetime.now().strftime("%H:%M %b %d %Y")
            self.updateObjectRegressStatus(self.total, self.total_done_list, regress_name)

            self.updateProgressBar(self.total, total_done)
            print("Stopping regression....",end="")
            self.updateOutputBox("Regression is done ")
            self.focessRegressonDone()
            print("done!")
            return
        else:
            self.after(after_time, self.retrieveTestRunObjects,total_test, testrun_object_folder_path,regress_name )
    def runIncrediBuildObjects(self,testRunList, unitName=None):
        pass

    def runTestObjects(self,testRunList):
        #write testRunListTo file
        self.test_run_list_done = False
        regress_obj_name = "testRun_list_" + self.regress_day_mark + ".regressobject"
        test_per_core = 3 # for linux
        if self.is_win_os:
            test_per_core = 1

        num_tests_to_run_in_parallel   = self.num_cores*test_per_core

        if self.use_incredibuild:
            if self.is_win_os:
                testrun_object_folder_path = os.path.join(self.regress_result_base,"incredibuild")
            else:
                testrun_object_folder_path = os.path.join(self.regress_result_base,"netbatch")
        else:
            testrun_object_folder_path = os.path.join(self.regress_result_base,"multiprocess")
        Path(testrun_object_folder_path).mkdir(parents=True, exist_ok=True)

        test_run_object_list_path = os.path.join(testrun_object_folder_path,regress_obj_name)
        regress_object = Test.regressObject()
        regress_object.testrun_list.extend(testRunList)
        regress_object.result_folder_path = testrun_object_folder_path
        regress_object.regress_time_mark = self.regress_day_mark
        regress_object.num_tests_to_run_in_parallel = num_tests_to_run_in_parallel
        regress_object.gold_include_list = self.gold_include_name_list
        regress_object.gold_exclude_list = self.gold_exclude_name_list
        regress_object.incredibuild_enable = self.use_incredibuild
        regress_object.regress_name=  self.regress_name
        regress_object.run_grits=  self.run_grits
        regress_object.run_aubload =  self.run_aubload
        regress_object.run_compare =  self.run_compare
        regress_object.user_id = self.user_id

        print("Writing test run list to ", test_run_object_list_path, end='')
        with open(test_run_object_list_path, 'wb') as object_file:
            pickle.dump(regress_object, object_file)
        print("==> done")
        print("Launching regression",end='')
        self.updateOutputBox("Launching regression ...")
        script_path = os.path.join(self.current_path,"runTestRunList.py")
        script_path= str(script_path).replace("\\", "/")
        #script_exe_path = os.path.join(self.current_path,"runTestRunList.exe")

        # use binary in release set
        #if Path(script_exe_path).is_file():
            #script_path = script_exe_path
        print( str(self.python_exe), str(script_path), "--filepath",str(test_run_object_list_path))
        self.subprocess = subprocess.Popen([str(self.python_exe), str(script_path), "--filepath",str(test_run_object_list_path)])

        #subprocess.Popen([str(self.python_exe), str(script_path), "--filepath",str(test_run_object_list_path)],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        #stdout, stderr = run_process.communicate()
       # print("stdout: ", stdout.decode())
        #print("stderr: ", stderr)
        print("==> done")


        self.previous_not_done_tests =  self.total = len(testRunList)
        ## generate total test list file
        list_name = str(self.regress_name) + "_" + self.regress_day_mark + "_" + "total_test.lst"
        self.regress_settings.total_test_list_path = os.path.join(self.regress_result_base, list_name)
        self.populatelistfile(testRunList,self.regress_settings.total_test_list_path)
       # self.generateTestListFile(testRunList,self.regress_name,"total_test.lst")

        if len(self.axe_execution_method_list) <=1:
            html_report_name =  str(self.axe_execution_method_list[0].name).replace(" ","_") + "_" + self.regress_day_mark + "_regress_report.html"
        else:
            html_report_name = self.regress_name  +"_" + self.regress_day_mark + "_regress_report.html"

        self.html_report_path = os.path.join(self.regress_result_base, html_report_name)
        self.updateObjectRegressStatus(self.total,self.total_done_list, self.regress_name) # windows required: make sure the html is created before use webbrowser to open it
        webbrowser.open(self.html_report_path, new=0, autoraise=True)
        self.retrieveTestRunObjects(self.total,testrun_object_folder_path, self.regress_name)


    def updateRunTime(self):
        # Only update if regression is actually running and not stopped
        if hasattr(self, 'processRun_start_time'):
            runtime = time.time() - self.processRun_start_time
            self.run_time = self.util.convertSecToHourMinSec(runtime)

            #self.countdown_label.config(text="Total Run Time:")
            self.countdown_timer.config(
                text=str(self.run_time),
                font=('Arial', 12),
                background='black',
                foreground='red',
                anchor=CENTER
            )
            # Force immediate update
            self.countdown_timer.update()
            self.update_idletasks()

            # Continue updating if regression is still running
            self.after(1000, self.updateRunTime)

    def generateCsvReport(self,testDoneList, unitName):
        #csv_report_name = self.regress_name + "_" + unitName + "_"+ self.regress_day_mark + "_runinfo.csv"
        csv_report_name = self.regress_name + "_" + self.regress_day_mark + "_runinfo.csv"
        self.regress_settings.testrun_info_path = os.path.join(self.regress_result_base, csv_report_name)

        status_str = "Writing passing test information to " + str(self.regress_settings.testrun_info_path)
        print(status_str)
        self.updateOutputBox(status_str)
        aub_pass_test_suite_list = list()
        for test_suite in testDoneList:
            if test_suite.valid_test:
                fulsim_status = test_suite.test_result.fulsim_compile_status
                if fulsim_status == "PASS":
                    aub_pass_test_suite_list.append(test_suite)
        self.util.writeDataToCsvFile(self.regress_settings.testrun_info_path,aub_pass_test_suite_list)

    def generateHtmlReport(self,testDoneList ):
        title = os.path.basename(self.html_report_path)
        status = self.util.writeDataNaxeConfigToHtmlFile(title, self.html_report_path, self.regress_summary,testDoneList,False, False, self.regress_settings,self.axe_execution_method_list)
        self.updateOutputBox(status)

    def generateSuiteFailList(self,regress_name):
        suite_fail_file_name = regress_name  +"_" + self.regress_day_mark + "_fail.lst"
        suite_fail_file_path = os.path.join(self.regress_result_base, suite_fail_file_name)
        print("Writing failing list to ", suite_fail_file_path)
        self.util.writeDataToFile(suite_fail_file_path, self.suite_fail_list)

    def generateDoneTtestList(self, regressName, testDoneList,regress_result_base):
        total_test_name = regressName  + "_total_test.lst"
        total_test_path = os.path.join(regress_result_base, total_test_name)
        print("Writing total test list to ", total_test_path)
        self.util.writeDataToFile(total_test_path, testDoneList)

    def generateTestListFile(self,test_list, unit_name, file_basename, for_allregresses=False):
        if for_allregresses:
            list_name = self.regress_name +   "_" + self.regress_day_mark + "_" + file_basename
        else:
            #regress_id = str(self.regress_name) + "_" + str(unit_name)
            regress_id = str(self.regress_name)
            list_name = regress_id +   "_" + self.regress_day_mark + "_" + file_basename
        list_path = os.path.join(self.regress_result_base, list_name)
        status_str = "Writing test names  to " +  str(list_path)
        print(status_str)
        self.updateOutputBox(status_str)
        self.util.writeDataToFile(list_path, test_list)

    def populatelistfile(self, test_list, file_path):
        status_str = "Writing test names  to " + str(file_path)
        print(status_str)
        self.updateOutputBox(status_str)
        self.util.writeDataToFile(file_path, test_list)


    def updateObjectRegressStatus(self, total_run, done_list, regress_name):
        sorted_done_list = self.generateSummary(total_run, done_list, regress_name)
        self.generateHtmlReport(sorted_done_list)

    def generateSummary(self,total_run, testDoneList, unit_name):
        total_tests = total_run

        total_time = time.time() - self.processRun_start_time

        runtime = self.util.convertSecToHourMinSec(total_time)


        goldnize_tests = 0
        for test_run in testDoneList:
            if test_run.valid_test:
                grits_status = test_run.test_result.grits_compile_status
                fulsim_status = test_run.test_result.fulsim_compile_status
                compare_status = test_run.test_result.compare_status
                goldnize_status = test_run.goldnize_status
                if grits_status != "FAIL" and fulsim_status != "FAIL" and compare_status != "FAIL":
                    self.addUniqueTest(self.total_pass_list, test_run)
                else:
                    self.addUniqueTest(self.total_fail_list, test_run)
                if goldnize_status == "SUCCESS":
                    goldnize_tests = goldnize_tests + 1
            else:
                self.addUniqueTest(self.total_invalid_list,test_run)

        sorted_done_test_list = list() # sort so invalid + fail + pass
        sorted_done_test_list.extend(self.total_invalid_list)
        sorted_done_test_list.extend(self.total_fail_list)
        sorted_done_test_list.extend(self.total_pass_list)

        total_done = len(self.total_done_list)
        total_pass = len(self.total_pass_list)
        total_fail = len(self.total_fail_list)
        total_invalid = len(self.total_invalid_list)
        testNotDoneList = list()
        for test_run in self.test_run_list:
            if self.hasTestRun(test_run, self.total_done_list):
                pass
            else:
                testNotDoneList.append(test_run)
        total_not_done = len(testNotDoneList)
        print()
        sys.stdout.write( str(unit_name) + " overall status: total = " + str(total_tests)+ " total done  = "  + str(total_done) + " pass = " + str(total_pass) + " fail = " +str(total_fail)+ " invalid = " + str(total_invalid) + ", run time = " +str(runtime))
        print()
        status_str = "Overall status:  " + str(total_pass) + "/" + str(total_done) + " pass"
        status_str = status_str + ", " + str(total_done) + "/" + str(self.total) + " done"
        self.updateStatusLabel(status_str)
        self.updateOutputBox(status_str)

        self.regress_summary = {"regress_time": total_time, "total_tests": total_tests,  "done_tests": total_done, "pass_tests": total_pass,
                       "fail_tests": total_fail, "invalid_tests": total_invalid, "invalid_test_list": self.total_invalid_list,
                       "goldnize_tests": goldnize_tests}
        if total_not_done < self.previous_not_done_tests:
            list_name = str(self.regress_name) + "_" + self.regress_day_mark + "_" + "not_done_test.lst"
            self.regress_settings.notdone_test_list_path = os.path.join(self.regress_result_base, list_name)
            self.populatelistfile(testNotDoneList, self.regress_settings.notdone_test_list_path)
            #self.generateTestListFile(testNotDoneList,unit_name,"not_done_test.lst")
            self.previous_not_done_tests = total_not_done
        if total_done > self.previous_done_tests:
            list_name = str(self.regress_name) + "_" + self.regress_day_mark + "_" + "done_test.lst"
            self.regress_settings.done_test_list_path = os.path.join(self.regress_result_base, list_name)
            self.populatelistfile(testDoneList, self.regress_settings.done_test_list_path)
            #self.generateTestListFile(testDoneList,unit_name,"done_test.lst")

            self.previous_done_tests = total_done

        if total_pass > self.previous_pass_tests:
            list_name = str(self.regress_name) + "_" + self.regress_day_mark + "_" + "pass_test.lst"
            self.regress_settings.pass_test_list_path = os.path.join(self.regress_result_base, list_name)
            self.populatelistfile(self.total_pass_list, self.regress_settings.pass_test_list_path)
            #self.generateTestListFile(self.total_pass_list,  unit_name, "pass_test.lst", True)
            self.generateCsvReport(self.total_pass_list,unit_name)

        if total_fail > self.previous_fail_tests:
            list_name = str(self.regress_name) + "_" + self.regress_day_mark + "_" + "fail_test.lst"
            self.regress_settings.fail_test_list_path = os.path.join(self.regress_result_base, list_name)
            self.populatelistfile(self.total_fail_list, self.regress_settings.fail_test_list_path)
            #self.generateTestListFile(self.total_fail_list, unit_name, "fail_test.lst", True)
        if total_invalid > self.previous_invalid_tests:
            list_name = str(self.regress_name) + "_" + self.regress_day_mark + "_" + "invalid_test.lst"
            self.regress_settings.invalid_test_list_path = os.path.join(self.regress_result_base, list_name)
            self.populatelistfile(self.total_invalid_list, self.regress_settings.invalid_test_list_path)
            #self. generateTestListFile(self.total_invalid_list, unit_name, "invalid_test.lst", True)
        print("\nOverall status: total = ", total_tests, "pass = ", total_pass, "fail = ", total_fail, "invalid = ", total_invalid)
        return sorted_done_test_list
    def perRunReset(self):
        self.test_run_list = list()
        self.test_read_list = list()
        self.p4_test_revision = None
        self.best_test_revision = 0

    def resetRegression(self):
        self.perRunReset()
        self.stop_regress = False
        self.regress_name =""

        self.result_list = list()
        self.exclusive_test_read_list = list()
        self.suite_fail_list = list()

        self.full_path_tests = list()
        self.test_list_file_path = None
        self.unit_names = ""
        self.run_time = 0
        self.start_time = time.time()
        self.required_folders.clear()
        self.gold_required_folders.clear()
        self.unit_required_folders.clear()
        self.previous_done_tests = 0
        self.previous_pass_tests = 0
        self.previous_fail_tests = 0
        self.previous_invalid_tests = 0
        self.best_test_revision = 0
        self.run_units = False
        self.run_test_lists = False
        self.run_unit_tests = False



    def updateRegressStatus(self, total_run, done_list):
        total_done = len(done_list)
        while total_done != total_run:
            total_done = len(done_list)

            print(total_done, "/", total_run, " are done")
            time.sleep(1)
        print("the status process is done")
        return



    def confirm(self):
        ans = askyesno(title="Cobalt Regression Tool", message='Do You Want To Exit ?')
        if ans:
            FulsimRegress.destroy(self)


def main():
    fulsim_regress = FulsimRegress()
    fulsim_regress.protocol("WM_DELETE_WINDOW",fulsim_regress.confirm)
    fulsim_regress.mainloop()



if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()