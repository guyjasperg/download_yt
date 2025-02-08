import os
import subprocess
import time
import pychrome
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import messagebox

def check_and_run_chrome():
    if not check_chrome_running():
        launch_chrome_with_debugging()

def check_chrome_running():
    """Checks if a Chrome instance with remote debugging is running."""
    bChromeRunning = False
    try:
        browser = pychrome.Browser()  # Try connecting; if it fails, Chrome isn't running or debugging is off
        browser.list_tab() # close the browser.
        bChromeRunning = True  # Chrome with debugging is running
    except Exception as e:
        print('ERROR: check_chrome_running() ', e)

    print('Chrome Running:', bChromeRunning)
    return bChromeRunning

def launch_chrome_with_debugging(port=9222):
    """Launches Chrome with remote debugging enabled."""
    chrome_executable = None

    # Find Chrome executable (platform-specific)
    if os.name == 'nt':  # Windows
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            # Add more potential paths if needed
        ]
        for path in chrome_paths:
            if os.path.exists(path):
                chrome_executable = path
                break
    elif os.name == 'posix':  # macOS/Linux
        chrome_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",  # macOS
            "/usr/bin/google-chrome",  # Common Linux path
            "/usr/bin/chromium-browser", # Common Linux path
            # Add more potential paths if needed
        ]
        for path in chrome_paths:
            if os.path.exists(path):
                chrome_executable = path
                break

    if not chrome_executable:
        raise Exception("Chrome executable not found. Please specify the path.")

    try:
        subprocess.Popen([
            chrome_executable,
            "--remote-debugging-port=" + str(port),
            "--user-data-dir=./chrome_profile", # Use a specific profile to avoid conflicts
            "--no-first-run", # prevent first run screen
            "--disable-extensions", # prevent extensions from interfering
        ])

        # Give Chrome a little time to start
        time.sleep(2)  # Adjust if needed

        return True

    except FileNotFoundError:
        raise Exception(f"Chrome executable not found at: {chrome_executable}")
    except Exception as e:
        raise Exception(f"Error launching Chrome: {e}")


def test_pychrome():
    print("test_pychrome")
    browser = pychrome.Browser()

    try:
        tabs = browser.list_tab()

        print("Tabs of type 'page':")

        for tab in tabs:
            if tab.type == 'page':
                # Refresh the tab information to get the latest data (including url and title)
                tab_info = browser.new_tab(tab.id)._kwargs # Get the tab information

                # Access tab information
                url = tab_info.get("url")
                title = tab_info.get("title")

                if url:
                    print(f"- {url} (Title: {title})")
                else:
                    print("- URL not found") # Handle the case where url might not be available.

    except Exception as e:
        message = str(e)
        if message.find('Failed to establish a new connection')>=0:
            print("Chrome with debugging not running")
        else:
            print(f"An error occurred: {e}")

def populate_combobox():
    global tab_data  # Access the global tab data
    
    """Populates the Combobox with tab titles."""
    # tab_data = load_tab_data()
    # titles = [tab["title"] for tab in tab_data]
    combobox["values"] = tab_data
    if tab_data:
        combobox.config(state="readonly")
    else:
        combobox.config(state="normal")
    
    if combobox["values"]: # selects the first item if available
        combobox.current(0)
        on_select(None)

def on_select(event):
    """Handles Combobox selection and opens URL."""
    global tab_data
    selected_title = combobox.get()
    print(f"SelectedItem: {selected_title}")

def get_selected():
    selected_title = combobox.get()
    print(f"SelectedItem: {selected_title}")
    root.withdraw()
    messagebox.showinfo('Selected Item', selected_title)
    
combobox = None
tab_data = ["Apple", "Banana","Grapes"]
# tab_data = []

# # Create the main application window
# root = tk.Tk()
# root.title("Tkinter Tab Example")
# # root.configure(bg="#FFFFFF")
# # root.geometry("400x300")

# # Create a style object
# style = ttk.Style()

# # Configure the TNotebook.Tab style to change the tab background color
# style.configure("TNotebook.Tab", background="lightblue", foreground="black")
# style.map("TNotebook.Tab", background=[("selected", "blue")])  # Change color when selected

# # Create a Notebook (tabbed interface)
# notebook = ttk.Notebook(root)
# # notebook.configure(bg="#FFFFFF")
# notebook.pack(fill="both", expand=True)

# # Tab 1: Frame and Widgets
# tab1 = ttk.Frame(notebook)
# notebook.add(tab1, text="Tab 1")

# frame_poToken = tk.Frame(tab1)
# frame_poToken.configure(bg="#FFFFFF")
# frame_poToken.pack(padx=10, pady=10)

# # add visitor, poToken
# lbl_visitor = tk.Label(frame_poToken, text="visitor")
# lbl_visitor.configure(bg="#FFFFFF")
# lbl_visitor.grid(row=0,column=0)

# txt_visitor = tk.Entry(frame_poToken, width=55)
# txt_visitor.grid(row=0,column=1, columnspan=3)

# lbl_poToken = tk.Label(frame_poToken, text="poToken")
# lbl_poToken.grid(row=1,column=0)

# txt_poToken = tk.Entry(frame_poToken, width=55)
# txt_poToken.grid(row=1,column=1, columnspan=3)

# # Tab 2: Frame and Widgets
# tab2 = ttk.Frame(notebook)
# notebook.add(tab2, text="Tab 2")

# frame = tk.Frame(tab2)
# frame.configure(bg="#FFFFFF")
# frame.pack(padx=5, pady=10)

# # Label and Entry for the YouTube URL
# url_label = tk.Label(frame, text="YouTube URL:")
# url_label.grid(row=0, column=0, padx=2, pady=5)

# txturl = tk.Entry(frame, width=50)
# txturl.grid(row=0, column=1, padx=2, pady=5)

# # Button to start the download
# download_button = tk.Button(frame, text="Download", command='')
# download_button.grid(row=0, column=2, padx=2, pady=5)

# # Multiline Textbox for progress updates

# txtLogs = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=20)
# txtLogs.grid(row=1, column=0, columnspan=3, pady=5)
# txtLogs.configure(state=tk.DISABLED)

# # Frame for buttons below the logs
# frame_btn = tk.Frame(tab2, bg="#FFFFFF")
# frame_btn.pack(pady=(5, 10))  # Add padding: 10px top, 20px bottom

# # Add empty columns on both sides to center the buttons
# frame_btn.grid_columnconfigure(0, weight=1)  # Empty column on the left
# frame_btn.grid_columnconfigure(3, weight=1)  # Empty column on the right

# btnListFiles = tk.Button(frame_btn, text="Downloaded Files", command='')
# btnListFiles.grid(row=0, column=1)
# # btnListFiles.pack(side=tk.TOP, anchor=tk.CENTER)  # Center the button

# btn_clear_logs = tk.Button(frame_btn, text="Clear Logs", command='')
# btn_clear_logs.grid(row=0, column=2)

# # label2 = tk.Label(tab2, text="This is Tab 2", font=("Arial", 14))
# # label2.pack(pady=20)

# # entry2 = tk.Entry(tab2, width=30)
# # entry2.pack(pady=10)

# # button2 = tk.Button(tab2, text="Submit (Tab 2)", command=lambda: print(f"Entered: {entry2.get()}"))
# # button2.pack()

# # Tab 3: Frame and Widgets
# tab3 = ttk.Frame(notebook)
# notebook.add(tab3, text="Tab 3")

# # Create an HtmlFrame widget
# label3 = tk.Label(tab3, text="This is Tab 3", font=("Arial", 14))
# label3.pack(pady=20)

# text3 = tk.Text(tab3, height=5, width=40)
# text3.pack()

# combobox = ttk.Combobox(tab3)
# combobox.pack(pady=20)

# btn_get_selected = tk.Button(tab3, text="Get Selected", command=get_selected)
# btn_get_selected.pack(pady=10)

# root.after(0, test_pychrome)

# # Run the application
# root.mainloop()

# **********************************
# Create the main application window
# **********************************
root = tk.Tk()
root.title("YouTube Video Downloader")
# root.geometry("700x400")
root.configure(bg="#FFFFFF")

frame_poToken = tk.Frame()
frame_poToken.configure(bg="#FFFFFF")
frame_poToken.grid(row=0, column=0, sticky=tk.EW, padx=10, pady=10)  # Use grid!
root.grid_columnconfigure(1, weight=1) # Make column 1 expand horizontally

# add visitor, poToken
lbl_visitor = tk.Label(frame_poToken, text="Visitor")
lbl_visitor.grid(row=0,column=0, sticky=tk.W)

txt_visitor = tk.Entry(frame_poToken, width=55)
txt_visitor.grid(row=0,column=1, columnspan=3)

lbl_poToken = tk.Label(frame_poToken, text="poToken")
lbl_poToken.grid(row=1,column=0, sticky=tk.W)

txt_poToken = tk.Entry(frame_poToken, width=55)
txt_poToken.grid(row=1,column=1, columnspan=3)

frame = tk.Frame()
frame.configure(bg="#FFFFFF")
frame.grid(row=1, column=0, padx=5, pady=10, sticky=tk.NSEW)  # Use grid, sticky for resizing

root.grid_rowconfigure(1, weight=1)  # Make row 1 (the frame) expand vertically
root.grid_columnconfigure(0, weight=1) # Make column 0 expand horizontally

# Label and Entry for the YouTube URL
url_label = tk.Label(frame, text="YouTube URL:")
url_label.grid(row=0, column=0, padx=2, pady=5, sticky=tk.W)

cboURL = ttk.Combobox(frame)
cboURL.grid(row=0, column=1, padx=2, pady=5, sticky=tk.EW) # Sticky East-West

# New Button (before download_button)
browse_button = tk.Button(frame, text="...", command=lambda: print("Browse clicked"))  # Add command
browse_button.grid(row=0, column=2, padx=2, pady=5)  # Place before Download

# Button to start the download
download_button = tk.Button(frame, text="Download", command='')
download_button.grid(row=0, column=3, padx=2, pady=5)

frame.grid_rowconfigure(1, weight=1)  # Make row 1 (txtLogs) expand vertically
# frame.grid_columnconfigure(0, weight=1)  # Make column 0 expand horizontally
frame.grid_columnconfigure(1, weight=1)  # Make column 1 expand horizontally
# frame.grid_columnconfigure(2, weight=1)  # Make column 2 expand horizontally

# Multiline Textbox for progress updates
txtLogs = scrolledtext.ScrolledText(frame, wrap=tk.WORD)
txtLogs.grid(row=1, column=0, columnspan=4, pady=5, sticky=tk.NSEW)
txtLogs.configure(state=tk.DISABLED)

# Frame for buttons below the logs
frame_btn = tk.Frame(root, bg="#FFFFFF")
frame_btn.grid(row=2, column=0, sticky=tk.EW, pady=10) # Grid it!
root.grid_rowconfigure(2, weight=0) # Row 2 should not resize
frame_btn.grid_columnconfigure(0, weight=1)  # Empty column on the left
frame_btn.grid_columnconfigure(3, weight=1)  # Empty column on the right

btnListFiles = tk.Button(frame_btn, text="Downloaded Files", command='')
btnListFiles.grid(row=0, column=1, sticky=tk.S)
# btnListFiles.pack(side=tk.TOP, anchor=tk.CENTER)  # Center the button

btn_clear_logs = tk.Button(frame_btn, text="Clear Logs", command=check_and_run_chrome)
btn_clear_logs.grid(row=0, column=2, sticky=tk.S)
# btn_clear_logs.pack(side=tk.TOP, anchor=tk.CENTER)  # Center the button

# Schedule the initialization function to run after the GUI starts
print('Getting poToken...')
download_button.config(state=tk.DISABLED)
# root.after(0, test_pychrome)

root.resizable(width=False, height=False)  # Disable resizing in both directions

def set_background(widget, color, widget_types=(tk.Label, tk.Entry, tk.Button, ttk.Combobox)): # Add Combobox
    if isinstance(widget, widget_types):
        try:
            widget.config(bg=color)  # Try 'bg' first
        except tk.TclError:
            try:
                widget.config(background=color)  # Try 'background' if 'bg' fails
            except tk.TclError:
                pass  # Ignore if neither works (some widgets might not have bg options)
    for child in widget.winfo_children():
        set_background(child, color, widget_types)

set_background(root, "White")

# Run the application
root.mainloop()


# test_pychrome()

