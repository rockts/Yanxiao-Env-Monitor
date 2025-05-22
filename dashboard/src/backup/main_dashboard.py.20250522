#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧校园环境监测系统 - 主入口文件
集成所有功能模块的中央控制器
"""

import os
import sys
import argparse
from pathlib import Path
import datetime # Added for timestamping

# --- Simplified execution for debugging ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent # This is dashboard/src, so parent.parent is dashboard/
indicator_file = PROJECT_ROOT / "main_dashboard_py_started.txt"
timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

try:
    print(f"[{timestamp}] main_dashboard.py: Attempting to create indicator file: {indicator_file}")
    with open(indicator_file, "w") as f:
        f.write(f"main_dashboard.py started at {timestamp} from {Path.cwd()}\n")
        f.write(f"Python executable: {sys.executable}\n")
        f.write(f"sys.path: {sys.path}\n")
    print(f"[{timestamp}] main_dashboard.py: Successfully created indicator file: {indicator_file}")
except Exception as e:
    print(f"[{timestamp}] main_dashboard.py: Error creating indicator file '{indicator_file}': {e}")
    # Try creating in /tmp as a fallback for permission issues
    try:
        tmp_indicator_file = Path("/tmp/main_dashboard_py_started_fallback.txt")
        print(f"[{timestamp}] main_dashboard.py: Attempting to create fallback indicator file: {tmp_indicator_file}")
        with open(tmp_indicator_file, "w") as f:
            f.write(f"main_dashboard.py started (fallback) at {timestamp} from {Path.cwd()}\n")
            f.write(f"Python executable: {sys.executable}\n")
            f.write(f"sys.path: {sys.path}\n")
        print(f"[{timestamp}] main_dashboard.py: Successfully created fallback indicator file: {tmp_indicator_file}")
    except Exception as e_tmp:
        print(f"[{timestamp}] main_dashboard.py: Error creating fallback indicator file '{tmp_indicator_file}': {e_tmp}")

print(f"[{timestamp}] main_dashboard.py: Simplified execution finished.")
# --- End of simplified execution ---

# Original code commented out for now:
#
# # Determine Project Root and add src to sys.path if not already there
# # PROJECT_ROOT = Path(__file__).resolve().parent.parent # dashboard/src -> dashboard/
# # SRC_ROOT = Path(__file__).resolve().parent      # dashboard/src
# #
# # if str(SRC_ROOT) not in sys.path:
# #     sys.path.insert(0, str(SRC_ROOT))
# # if str(PROJECT_ROOT) not in sys.path: # Should not be strictly necessary if PYTHONPATH is set by launcher
# #     sys.path.insert(0, str(PROJECT_ROOT))
# #
# # print(f"main_dashboard.py: Running with Python: {sys.executable}")
# # print(f"main_dashboard.py: sys.path: {sys.path}")
# # print(f"main_dashboard.py: Current working directory: {os.getcwd()}")
# # print(f"main_dashboard.py: PROJECT_ROOT: {PROJECT_ROOT}")
# # print(f"main_dashboard.py: SRC_ROOT: {SRC_ROOT}")
# #
# # # Attempt to create a startup indicator file
# # startup_indicator_file = PROJECT_ROOT / "startup_indicator.txt"
# # try:
# #     with open(startup_indicator_file, "w") as f:
# #         f.write(f"main_dashboard.py started at {datetime.datetime.now().isoformat()}\n")
# #         f.write(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not Set')}\n")
# #     print(f"main_dashboard.py: Created indicator file {startup_indicator_file}")
# # except Exception as e_init:
# #     print(f"main_dashboard.py: Failed to create indicator file {startup_indicator_file}: {e_init}")
# #
# # try:
# #     from core.config_manager import ConfigManager
# #     from core.log_manager import LogManager
# #     # Import UI modules after path adjustments and core modules
# #     from ui.simple_dashboard import SimpleDashboard
# #     from ui.dashboard import Dashboard # Assuming full dashboard is named Dashboard
# # except ImportError as e:
# #     print(f"main_dashboard.py: Critical import error: {e}. Check PYTHONPATH and file locations.")
# #     # Create an error indicator file if imports fail
# #     error_indicator_file = PROJECT_ROOT / "startup_error_imports.txt"
# #     try:
# #         with open(error_indicator_file, "w") as f:
# #             f.write(f"main_dashboard.py import error at {datetime.datetime.now().isoformat()}: {e}\n")
# #             f.write(f"sys.path: {sys.path}\n")
# #             f.write(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not Set')}\n")
# #         print(f"main_dashboard.py: Created import error indicator file {error_indicator_file}")
# #     except Exception as e_err_file:
# #         print(f"main_dashboard.py: Failed to create import error indicator file {error_indicator_file}: {e_err_file}")
# #     sys.exit(1)
# #
# # def main():
# #     # ... (rest of the original file commented out) ...
# #     parser = argparse.ArgumentParser(description="Smart Campus Environmental Monitoring Dashboard - Main Application")
# #     mode_group = parser.add_mutually_exclusive_group(required=False)
# #     mode_group.add_argument("--simple", action="store_true", help="Run the simple dashboard.")
# #     mode_group.add_argument("--full", action="store_true", help="Run the full-featured dashboard.")
# #
# #     parser.add_argument("--simulate", action="store_true", help="Use simulated sensor data.")
# #     parser.add_argument("--local-mqtt", action="store_true", help="Use local MQTT broker settings.")
# #     parser.add_argument("--debug", action="store_true", help="Enable debug mode.")
# #
# #     args = parser.parse_args()
# #
# #     # Default to simple if no mode is specified
# #     if not args.simple and not args.full:
# #         print("main_dashboard.py: No dashboard mode specified, defaulting to --simple.")
# #         args.simple = True
# #
# #     # Initialize ConfigManager - it will use the default path within PROJECT_ROOT
# #     # ConfigManager ensures only one instance is created.
# #     config_manager = ConfigManager(project_root=PROJECT_ROOT)
# #     app_config = config_manager.get_all()
# #
# #     if args.debug:
# #         app_config["logging"]["level"] = "DEBUG"
# #         config_manager.save_config(app_config) # Save updated debug level if changed
# #
# #     # Initialize LogManager - it will use paths relative to PROJECT_ROOT
# #     # LogManager ensures only one instance is created.
# #     log_manager = LogManager(project_root=PROJECT_ROOT,
# #                              log_config=app_config.get("logging", {}))
# #     logger = log_manager.get_logger("MainDashboard")
# #
# #     logger.info(f"main_dashboard.py: Application starting with arguments: {args}")
# #     logger.info(f"main_dashboard.py: Effective log level: {app_config.get('logging', {}).get('level', 'INFO')}")
# #     logger.debug(f"main_dashboard.py: Full application configuration: {app_config}")
# #
# #     # Update app_config with runtime arguments
# #     app_config['runtime_args'] = vars(args)
# #
# #     if args.simple:
# #         logger.info("main_dashboard.py: Launching Simple Dashboard.")
# #         # Pass the whole app_config dictionary
# #         dashboard_app = SimpleDashboard(app_config=app_config, project_root_path=PROJECT_ROOT)
# #         dashboard_app.run()
# #     elif args.full:
# #         logger.info("main_dashboard.py: Launching Full Dashboard.")
# #         # dashboard_app = Dashboard(app_config=app_config, project_root_path=PROJECT_ROOT)
# #         # dashboard_app.run()
# #         logger.warning("Full dashboard not yet implemented in main_dashboard.py. Exiting.")
# #     else:
# #         logger.error("main_dashboard.py: No dashboard mode selected. This should not happen if default is set.")
# #         parser.print_help()
# #
# # if __name__ == "__main__":
# #     # main()
# #     pass # Do nothing for now with the simplified version
