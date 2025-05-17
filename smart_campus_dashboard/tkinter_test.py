import os
import sys
import tkinter as tk

print(f"Python Executable: {sys.executable}")
print(f"Python Version: {sys.version}")

os.environ['TK_SILENCE_DEPRECATION'] = '1'

print("Attempting to create Tkinter root window (ultra-simplified)...")
try:
    root = tk.Tk()
    # We can get the version here if needed, now that a root window exists
    print(f"Tkinter root window created. Tcl/Tk patchlevel: {root.tk.call('info', 'patchlevel')}")
    root.title("Ultra-Simplified Tkinter Test")

    label = tk.Label(root, text="Hello, Tkinter Again!")
    print("Label created.")
    label.pack()
    print("Label packed.")

    print("Starting mainloop...")
    root.mainloop()
    print("Mainloop finished.")

except tk.TclError as e:
    print(f"Tkinter TclError: {e}")
    print(f"Current TCL_LIBRARY: {os.environ.get('TCL_LIBRARY')}")
    print(f"Current TK_LIBRARY: {os.environ.get('TK_LIBRARY')}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
