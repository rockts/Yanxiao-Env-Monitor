import datetime
import os
print(f"Simple test script started at {datetime.datetime.now()}")
print(f"Current working directory: {os.getcwd()}")
print(f"Python executable: {os.sys.executable}")
try:
    with open("/Users/rockts/SynologyDrive/Drive/Yanxiao-Env-Monitor/dashboard/simple_test_output.txt", "w") as f:
        f.write(f"Simple test script executed at {datetime.datetime.now()}\n")
    print("Successfully wrote to simple_test_output.txt")
except Exception as e:
    print(f"Error writing to file: {e}")
print("Simple test script finished.")
