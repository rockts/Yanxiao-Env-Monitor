#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time # For the indicator file
from pathlib import Path # For the indicator file

# --- Create a launch.py startup indicator file ---
launch_indicator_path = Path(__file__).resolve().parent / "launch_py_started.txt"
try:
    with open(launch_indicator_path, "w") as f:
        f.write(f"launch.py script started at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    # This print might not be visible in the user's VSCode terminal
    print(f"launch.py startup indicator file created at: {launch_indicator_path}") 
except Exception as e:
    # This print might not be visible either
    print(f"Failed to create launch.py startup indicator file: {e}")
# --- End launch.py startup indicator ---

"""
智慧校园环境监测系统 - 启动器
提供统一的命令行界面启动各种模式
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
import datetime

# --- Start of script ---
timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
print(f"[{timestamp}] launch.py: Script started.", flush=True)
print(f"[{timestamp}] launch.py: Python Executable: {sys.executable}", flush=True)
print(f"[{timestamp}] launch.py: Python Version: {sys.version}", flush=True)
print(f"[{timestamp}] launch.py: Current Working Directory: {os.getcwd()}", flush=True)
print(f"[{timestamp}] launch.py: __file__: {__file__}", flush=True)
print(f"[{timestamp}] launch.py: sys.argv: {sys.argv}", flush=True)

# Attempt to create indicator in /tmp first
tmp_indicator_file = Path(f"/tmp/launch_py_started_vscode_{timestamp.replace(':', '-').replace(' ', '_')}.txt")
try:
    print(f"[{timestamp}] launch.py: Attempting to create TMP indicator: {tmp_indicator_file}", flush=True)
    with open(tmp_indicator_file, "w") as f:
        f.write(f"launch.py started at {timestamp} from {os.getcwd()}\n")
        f.write(f"Python executable: {sys.executable}\n")
        f.write(f"Python version: {sys.version}\n")
        f.write(f"sys.path: {sys.path}\n")
        f.write(f"__file__: {__file__}\n")
        f.write(f"sys.argv: {sys.argv}\n")
    print(f"[{timestamp}] launch.py: Successfully created TMP indicator: {tmp_indicator_file}", flush=True)
except Exception as e_tmp:
    print(f"[{timestamp}] launch.py: ERROR creating TMP indicator '{tmp_indicator_file}': {e_tmp}", flush=True)
    sys.stderr.write(f"[{timestamp}] launch.py: STDERR ERROR creating TMP indicator '{tmp_indicator_file}': {e_tmp}\n")
    sys.stderr.flush()

# Attempt to create indicator in project directory
try:
    PROJECT_ROOT = Path(__file__).resolve().parent
    project_indicator_file = PROJECT_ROOT / f"launch_py_started_project_{timestamp.replace(':', '-').replace(' ', '_')}.txt"
    print(f"[{timestamp}] launch.py: Attempting to create PROJECT indicator: {project_indicator_file}", flush=True)
    with open(project_indicator_file, "w") as f:
        f.write(f"launch.py started at {timestamp} from {os.getcwd()}\n")
        f.write(f"Python executable: {sys.executable}\n")
        f.write(f"Python version: {sys.version}\n")
        f.write(f"sys.path: {sys.path}\n")
        f.write(f"__file__: {__file__}\n")
        f.write(f"sys.argv: {sys.argv}\n")
    print(f"[{timestamp}] launch.py: Successfully created PROJECT indicator: {project_indicator_file}", flush=True)
except Exception as e_proj:
    print(f"[{timestamp}] launch.py: ERROR creating PROJECT indicator '{project_indicator_file}': {e_proj}", flush=True)
    sys.stderr.write(f"[{timestamp}] launch.py: STDERR ERROR creating PROJECT indicator '{e_proj}\n")
    sys.stderr.flush()

print(f"[{timestamp}] launch.py: Script finished.", flush=True)

# --- Simplified execution for debugging ---
# PROJECT_ROOT = Path(__file__).resolve().parent
# indicator_file = PROJECT_ROOT / "launch_py_started.txt"
# timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#
# try:
#    print(f"[{timestamp}] launch.py: Attempting to create indicator file: {indicator_file}")
#    with open(indicator_file, "w") as f:
#        f.write(f"launch.py started at {timestamp} from {Path.cwd()}\n")
#        f.write(f"Python executable: {sys.executable}\n")
#        f.write(f"sys.path: {sys.path}\n")
#    print(f"[{timestamp}] launch.py: Successfully created indicator file: {indicator_file}")
# except Exception as e:
#    print(f"[{timestamp}] launch.py: Error creating indicator file '{indicator_file}': {e}")
#    # Try creating in /tmp as a fallback for permission issues
#    try:
#        tmp_indicator_file = Path("/tmp/launch_py_started_fallback.txt")
#        print(f"[{timestamp}] launch.py: Attempting to create fallback indicator file: {tmp_indicator_file}")
#        with open(tmp_indicator_file, "w") as f:
#            f.write(f"launch.py started (fallback) at {timestamp} from {Path.cwd()}\n")
#            f.write(f"Python executable: {sys.executable}\n")
#            f.write(f"sys.path: {sys.path}\n")
#        print(f"[{timestamp}] launch.py: Successfully created fallback indicator file: {tmp_indicator_file}")
#    except Exception as e_tmp:
#        print(f"[{timestamp}] launch.py: Error creating fallback indicator file '{tmp_indicator_file}': {e_tmp}")
#
# print(f"[{timestamp}] launch.py: Simplified execution finished.")
# --- End of simplified execution ---

# Original code commented out for now:
#
# # Determine Project Root and add to PYTHONPATH
# # PROJECT_ROOT = Path(__file__).resolve().parent
# # SRC_PATH = PROJECT_ROOT / "src"
# #
# # # Add project root and src to sys.path for subprocess and current process
# # if str(PROJECT_ROOT) not in sys.path:
# #     sys.path.insert(0, str(PROJECT_ROOT))
# # if str(SRC_PATH) not in sys.path:
# #     sys.path.insert(0, str(SRC_PATH))
# #
# # # Update PYTHONPATH for subprocesses
# # current_pythonpath = os.environ.get('PYTHONPATH', '')
# # pythonpath_dirs = [str(PROJECT_ROOT), str(SRC_PATH)]
# # for p_dir in pythonpath_dirs:
# #     if p_dir not in current_pythonpath.split(os.pathsep):
# #         current_pythonpath = f"{p_dir}{os.pathsep}{current_pythonpath}"
# # os.environ['PYTHONPATH'] = current_pythonpath
# #
# # print(f"launch.py: Initial sys.path: {sys.path}")
# # print(f"launch.py: PYTHONPATH set to: {os.environ['PYTHONPATH']}")
# #
# # # Attempt to create a startup indicator file for launch.py itself
# # launch_indicator_file = PROJECT_ROOT / "launch_py_started.txt"
# # try:
# #     with open(launch_indicator_file, "w") as f:
# #         f.write(f"launch.py started at {datetime.datetime.now().isoformat()}\n")
# #         f.write(f"PROJECT_ROOT: {PROJECT_ROOT}\n")
# #         f.write(f"SRC_PATH: {SRC_PATH}\n")
# #         f.write(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not Set')}\n")
# #     print(f"launch.py: Created indicator file {launch_indicator_file}")
# # except Exception as e_launch_init:
# #     print(f"launch.py: Failed to create indicator file {launch_indicator_file}: {e_launch_init}")
#
#
# def get_python_path():
#     # ... (rest of the original file commented out) ...
#     # Prefer python3 if available
#     for cmd in ["python3", "python"]:
#         try:
#             # Check if the command exists and is executable
#             path = subprocess.check_output(["which", cmd], text=True).strip()
#             # Additionally, verify it's a Python interpreter (basic check)
#             version_output = subprocess.check_output([path, "--version"], text=True, stderr=subprocess.STDOUT)
#             if "Python" in version_output:
#                 print(f"launch.py: Using Python interpreter at {path}")
#                 return path
#         except (subprocess.CalledProcessError, FileNotFoundError):
#             continue
#     print("launch.py: Warning: Neither 'python3' nor 'python' found or validated. Falling back to sys.executable.")
#     return sys.executable # Fallback to current interpreter
#
# def run_dashboard(args):
#     python_executable = get_python_path()
#     main_script_path = SRC_PATH / "main_dashboard.py"
#     cmd = [python_executable, str(main_script_path)]
#
#     if args.simple:
#         cmd.append("--simple")
#     if args.full:
#         cmd.append("--full")
#     if args.simulate:
#         cmd.append("--simulate")
#     if args.local_mqtt:
#         cmd.append("--local-mqtt")
#     if args.debug:
#         cmd.append("--debug")
#
#     print(f"launch.py: Running command: {' '.join(cmd)}")
#     print(f"launch.py: Working directory: {PROJECT_ROOT}")
#     print(f"launch.py: PYTHONPATH for subprocess: {os.environ.get('PYTHONPATH')}")
#
#     try:
#         # Force foreground execution for debugging
#         # Use Popen for more control if needed, but run should suffice for now
#         process = subprocess.run(cmd, cwd=PROJECT_ROOT, check=False, text=True, # Set check=False to see output even on error
#                                  capture_output=True, env=os.environ.copy())
#
#         print("launch.py: Subprocess stdout:")
#         print(process.stdout if process.stdout else "<No stdout>")
#         print("launch.py: Subprocess stderr:")
#         print(process.stderr if process.stderr else "<No stderr>")
#
#         if process.returncode != 0:
#             print(f"launch.py: Subprocess failed with return code {process.returncode}")
#         else:
#             print("launch.py: Subprocess completed successfully.")
#
#     except FileNotFoundError:
#         print(f"launch.py: Error: The script {main_script_path} or python interpreter {python_executable} was not found.")
#         print(f"launch.py: Please ensure '{python_executable}' is a valid Python command and '{main_script_path}' exists.")
#     except subprocess.CalledProcessError as e:
#         print(f"launch.py: Subprocess execution failed: {e}")
#         print("launch.py: stdout from failed process:", e.stdout)
#         print("launch.py: stderr from failed process:", e.stderr)
#     except Exception as e:
#         print(f"launch.py: An unexpected error occurred while trying to run the dashboard: {e}")
#
# if __name__ == "__main__":
#     # parser = argparse.ArgumentParser(description="Launch the Smart Campus Environmental Monitoring Dashboard.")
#     # mode_group = parser.add_mutually_exclusive_group(required=False) # Made it not required for now
#     # mode_group.add_argument("--simple", action="store_true", help="Run the simple dashboard.")
#     # mode_group.add_argument("--full", action="store_true", help="Run the full-featured dashboard.")
#     #
#     # parser.add_argument("--simulate", action="store_true", help="Use simulated sensor data.")
#     # parser.add_argument("--local-mqtt", action="store_true", help="Use local MQTT broker settings from config.")
#     # parser.add_argument("--debug", action="store_true", help="Enable debug mode (more verbose logging).")
#     #
#     # args = parser.parse_args()
#     #
#     # # Default to simple if no mode is specified
#     # if not args.simple and not args.full:
#     #     print("launch.py: No dashboard mode specified, defaulting to --simple.")
#     #     args.simple = True
#     #
#     # print(f"launch.py: Parsed arguments: {args}")
#     # run_dashboard(args)
#     pass # Do nothing for now with the simplified version
