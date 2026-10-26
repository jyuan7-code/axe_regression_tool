import argparse
import os.path
import pickle
import time
import platform
from pathlib import Path
import sys
import re
import threading
if re.search("windows", platform.system(), re.IGNORECASE):
    import psutil

import platform
#from selenium import webdriver
from multiprocessing import Manager, Pool

import signal
import libs.test as Test
import libs.utility as Util
import random
util_tool = Util.Utility()
global pool
pool = None
is_win_os = False
if re.search("windows", platform.system(), re.IGNORECASE):
    is_win_os = True
    python_exe = "python"
else:
    python_exe = "python3"
def addUniqueRequiredFolder( folderList, folderName):
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


def runOneTest(testRun, test_done_list, message, gold_include_name_list, gold_exclude_name_list, result_folder_path,
               runtime_stamp):

    print("Start to run test " + testRun.test_name)

    if testRun.valid_test:
        test_runner = Test.TestRunner()
        test_runner.gold_include_name_list = gold_include_name_list
        test_runner.gold_exclude_name_list = gold_exclude_name_list
        test_runner.run(testRun)

    test_done_list.append(testRun)
    unitname = testRun.unit_name
    unitname = str(unitname).replace("\\", "_")
    unitname = str(unitname).replace("/", "_")
    seed = random.randint(2, 0xffffffff)
    donetime_in_second = time.time()
    testrun_object_name = runtime_stamp + "_" + str(testRun.test_name)[0:5] + "_" + str(seed) + str(
        round(donetime_in_second))[-2:] + ".testrun"

    try:
        testrun_object_name = os.path.join(result_folder_path, testrun_object_name)
        print("Writing test run  to ", testrun_object_name, end='')

        # Use a more robust pickle approach
        import io
        buffer = io.BytesIO()
        pickle.dump(testRun, buffer, protocol=pickle.HIGHEST_PROTOCOL)  # Fixed: use buffer instead of object_file
        buffer.seek(0)

        with open(testrun_object_name, 'wb') as object_file:
            object_file.write(buffer.getvalue())
        buffer.close()

        print("==> done")
    except Exception as e:
        print(f"Error writing pickle file: {e}")
        # Fallback: try direct pickle
        try:
            with open(testrun_object_name, 'wb') as object_file:
                pickle.dump(testRun, object_file, protocol=pickle.HIGHEST_PROTOCOL)
            print("==> done (fallback)")
        except Exception as e2:
            print(f"Fallback also failed: {e2}")
def stopAllRun(signum, frame):
    if pool !=None:
        try:
            pool.terminate()
            pool.join()
            print("Stopped all test runs !!!")
        except:
            print("An exception occurred from pool")
        print("Stopped all test runs !!!")
        time.sleep(2)
def linuxMemoryUsage():
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
                memory_info = {"total_memory": total_memory, "used_memory": used_memory, "free_memory": free_memory}

    return memory_info
def get_memory_usage_percent() -> float:
    """
        Checks the current system virtual memory usage.

        Returns:
        float: Total system memory usage as a percentage (0.0 to 100.0).
        """
    if is_win_os:
        # psutil.virtual_memory() returns a named tuple containing total, available, percent, used, and free memory.
        memory_info = psutil.virtual_memory()
        return memory_info.percent
    else:
        memory_info = linuxMemoryUsage()
        total_memory = memory_info["total_memory"]
        used_memory = memory_info["used_memory"]
        percent = round(int(used_memory) / int(total_memory) * 100, 2)
        return percent
def main():
    if 'pathlib._local' not in sys.modules:
        import pathlib
        sys.modules['pathlib._local'] = pathlib


    parser = argparse.ArgumentParser()
    parser.add_argument('--filepath', type=str, required=True)

    args = parser.parse_args()
    filepath = args.filepath

    with open(Path(filepath), 'rb') as runtest_list_file:
        regress_object = pickle.load(runtest_list_file)

    if regress_object == None:
        print("Failed to get regress object")
        return

    run_test_list = regress_object.testrun_list
    total_test = len(run_test_list)
    gold_include_list  = regress_object.gold_include_list
    gold_exclude_list  = regress_object.gold_exclude_list
    result_folder_path = regress_object.result_folder_path
    runtime_stamp = regress_object.regress_time_mark
    regress_name = regress_object.regress_name
    num_tests_to_run_in_parallel = regress_object.num_tests_to_run_in_parallel

    incredibuild_enable = False
    if incredibuild_enable: # incredibulild or netbatch
        testread_base = os.path.join(os.path.dirname(Path(filepath)), "testreads")
        Path(testread_base).mkdir(parents=True, exist_ok=True)

        current_path = os.getcwd() # script base path
        script_path = os.path.join(current_path,"runOneTestRun.py")
        if is_win_os:
            processed_test = 1
            command_line_list = list()
            while len(run_test_list) > 0:
                test_run = run_test_list.pop()
                test_run.return_path = os.path.dirname(Path(filepath))
                test_run.gold_include_list =gold_include_list
                test_run.gold_exclude_list =gold_exclude_list
                test_run.time_stamp = regress_object.regress_time_mark
                test_run.run_in_remote = True
                testrun_object_name = runtime_stamp + "_" + str(test_run.unit_name) + "_" + str(test_run.test_name) + ".testread"
                testrun_object_name = os.path.join(testread_base, testrun_object_name)

                print("(" + str(processed_test) + "/" + str(total_test) + ")" + " Writing one test run for incredibuild to read to ", testrun_object_name, end='')
                with open(testrun_object_name, 'wb') as object_file:
                    pickle.dump(test_run, object_file, protocol=pickle.HIGHEST_PROTOCOL)
                command_line = str(python_exe) + " " + str(script_path)+ " " + "--filepath"+ " " +str(testrun_object_name)
                command_line_list.append(command_line)
                processed_test = processed_test + 1
                print("==> done")
             #write bat file
            command_file = runtime_stamp + "_" + "commandlines.txt"
            command_file_path = os.path.join(testread_base,command_file)
            runtest_bat_file = runtime_stamp + "_" + "runtest.bat"
            runtest_bat_file_path  =  os.path.join(testread_base,runtest_bat_file)
            incredibuild_group = regress_object.user_id + regress_object.regress_time_mark
            with open(command_file_path, 'w') as f:
                while len(command_line_list) > 0:
                    command_line = command_line_list.pop()
                    f.write(command_line+"\n")

            with open(runtest_bat_file_path, 'w') as f:
                if regress_object.run_grits:
                    line1= "xgSubmit /GROUP=" + "'" + incredibuild_group + "'" + "  /allowremote=off /wait /commandfile " +  command_file_path
                else:
                    line1= "xgSubmit /GROUP=" + "'" + incredibuild_group + "'" + "  /allowremote=off /wait /commandfile " +  command_file_path
                f.write(line1+"\n")

                line2= "xgWait /silent /GROUP=" + "'" + incredibuild_group + "'"
                f.write(line2+"\n")

            incredibuild_exe = r"c:\Program Files (x86)\IncrediBuild\xgConsole.exe"
            incredibuild_exe = r"c:\Program Files (x86)\IncrediBuild\IbConsole.exe"

            if Path(incredibuild_exe).is_file():
                incredibuild_exe = '"'+ incredibuild_exe + '"'
            else:
                incredibuild_exe = "xgConsole.exe"
            openmonitor = r"/openmonitor"
            profile = r"/profile=runtestprofile.xml"
            extra = r"/silent /showagent /AvoidLocal=on /nologo /no_dotnet_virt "
            maxcpus = r"/maxcpus=100"
            title = "'" + regress_name + "'"
            title =  "/title=" + title
            #subprocess.Popen([str(incredibuild_exe), runtest_bat_file_path, openmonitor, profile, extra, maxcpus, title])
            command_line  = incredibuild_exe + " " + runtest_bat_file_path + " " + openmonitor + " " + profile + " " + extra + " " + maxcpus + " " + title
            print("cmmand line:", command_line)
            os.system(command_line)
        else: # netbatch
            netbatch_pool	= "sc_normal2" # from TargetEnvironments.json
            netbatch_slot	= "/VPG/All-VPG/SWD/AXE/user"
            nbSecondsPerJob = 60*60
            nbSuspendLimit 			= 40
            nbSuspendRetries 		= 3 # number of times to re-submit a netbatch job if it was resubmitted due to @NbSuspendLimit
            nbRetries               = 2
            nbAttempts              = "--autoreq \"attempts=" + str(nbRetries) +":NBErr\""
            nbConstrain				= "--job-constraints \"wtime>" + str(nbSecondsPerJob)  + ":kill\""	# kill the job if the wall clock time exceeds @NbTime_SecondsPerJob seconds
            nb_mem_class = "SLES12SP5&&2C&&4G&&tFDS>5000"
            nb_cmd_prefix = "/nfs/site/disks/ec_netbatch/install/8.5.1_0966_10/bin/nbq" +  " -c " + '"'+str(nb_mem_class) + '"' + " -Q " + netbatch_slot + " -P " + netbatch_pool + " " +   nbConstrain + " " + \
                            nbAttempts + " -R " + str(nbSuspendLimit) + " -# " + str(nbSuspendRetries) + " "
            processed_test = 1
            while len(run_test_list) > 0:
                test_run = run_test_list.pop()
                test_run.return_path = os.path.dirname(Path(filepath))
                test_run.gold_include_list =gold_include_list
                test_run.gold_exclude_list =gold_exclude_list
                test_run.time_stamp = regress_object.regress_time_mark
                test_run.run_in_remote = True
                testrun_object_name = runtime_stamp + "_" + str(test_run.unit_name) + "_" + str(test_run.test_name) + ".testread"
                testrun_object_name = os.path.join(testread_base, testrun_object_name)

                print("(" + str(processed_test) + "/" + str(total_test) + ")" + " Uploading to netbatch ", testrun_object_name, end='')
                with open(testrun_object_name, 'wb') as object_file:
                    pickle.dump(test_run, object_file, protocol=pickle.HIGHEST_PROTOCOL)
                job_cmd = str(python_exe) + " " + str(script_path)+ " " + "--filepath"+ " " +str(testrun_object_name)
                nb_cmd = nb_cmd_prefix  + job_cmd
                print("(" + str(processed_test) + "/" + str(total_test) + "): ",  nb_cmd)
                os.system(nb_cmd)
    else: # multiprocess
        manager = Manager()
        test_done_list = manager.list()
        global pool
        pool = Pool(processes=num_tests_to_run_in_parallel)
        # Keep track of active tasks: { async_result: (start_time, test_name_string) }
        active_tasks = {}
        tasks_lock = threading.Lock()
        processed = 0
        # Configure your timeout threshold here (e.g., 60 min)
        TEST_TIMEOUT_SECONDS = 60*60

        def monitor_timeouts(tasks, timeout_limit):
            """Background thread that continuously checks for hung processes."""
            while True:
                time.sleep(1)  # Check every second
                with tasks_lock:
                    # If the pool is closed and no tasks are left, exit the thread
                    if not tasks and pool._state != 0:  # 0 is RUN state
                        break

                    now = time.time()
                    to_remove = []

                    for async_result, (start_time, test_info) in list(tasks.items()):
                        if async_result.ready():
                            # Task completed normally, remove from tracking
                            to_remove.append(async_result)
                        elif (now - start_time) > timeout_limit:
                            print(f"\n⚠️ WARNING: {test_info} exceeded time limit of {timeout_limit}s!")
                            # Unfortunately, we cannot terminate a single pool worker thread/process directly
                            # from the master process without killing the whole pool.
                            #
                            # To handle this cleanly:
                            # Option A: Mark it as timed out in your tracking system
                            to_remove.append(async_result)

                    for item in to_remove:
                        tasks.pop(item, None)

        # Start the background timeout monitor
        monitor_thread = threading.Thread(
            target=monitor_timeouts,
            args=(active_tasks, TEST_TIMEOUT_SECONDS),
            daemon=True
        )
        monitor_thread.start()
        while len(run_test_list) > 0:
            test_run = run_test_list.pop()
            while (get_memory_usage_percent() > 80):
                print("Warning: memory usage percentage is high (",get_memory_usage_percent(),"%)")
                print("Waiting for 5 second... ")
                time.sleep(5)
            processed = processed + 1
            message = "(" + str(processed) + "/" + str(
                total_test) + ")processing test: " + test_run.unit_name + "/" + test_run.test_name
            print(message)
            result = pool.apply_async(runOneTest, args=(test_run,test_done_list, message, gold_include_list, gold_exclude_list,result_folder_path,runtime_stamp))
            with tasks_lock:
                active_tasks[result] = (time.time(), f"{test_run.unit_name}/{test_run.test_name}")
            signal.signal(signal.SIGTERM,stopAllRun)

            time.sleep(1)
        pool.close()
    #self.after(500, self.updateRegress)
        pool.join()


if __name__ == "__main__":
    main()



