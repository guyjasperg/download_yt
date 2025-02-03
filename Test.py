import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext

# Create the main application window
root = tk.Tk()
root.title("Tkinter Tab Example")
# root.configure(bg="#FFFFFF")
# root.geometry("400x300")

# Create a style object
style = ttk.Style()

# Configure the TNotebook.Tab style to change the tab background color
style.configure("TNotebook.Tab", background="lightblue", foreground="black")
style.map("TNotebook.Tab", background=[("selected", "blue")])  # Change color when selected

# Create a Notebook (tabbed interface)
notebook = ttk.Notebook(root)
# notebook.configure(bg="#FFFFFF")
notebook.pack(fill="both", expand=True)

# Tab 1: Frame and Widgets
tab1 = ttk.Frame(notebook)
notebook.add(tab1, text="Tab 1")

frame_poToken = tk.Frame(tab1)
frame_poToken.configure(bg="#FFFFFF")
frame_poToken.pack(padx=10, pady=10)

# add visitor, poToken
lbl_visitor = tk.Label(frame_poToken, text="visitor")
lbl_visitor.configure(bg="#FFFFFF")
lbl_visitor.grid(row=0,column=0)

txt_visitor = tk.Entry(frame_poToken, width=55)
txt_visitor.grid(row=0,column=1, columnspan=3)

lbl_poToken = tk.Label(frame_poToken, text="poToken")
lbl_poToken.grid(row=1,column=0)

txt_poToken = tk.Entry(frame_poToken, width=55)
txt_poToken.grid(row=1,column=1, columnspan=3)

# Tab 2: Frame and Widgets
tab2 = ttk.Frame(notebook)
notebook.add(tab2, text="Tab 2")

frame = tk.Frame(tab2)
frame.configure(bg="#FFFFFF")
frame.pack(padx=5, pady=10)

# Label and Entry for the YouTube URL
url_label = tk.Label(frame, text="YouTube URL:")
url_label.grid(row=0, column=0, padx=2, pady=5)

txturl = tk.Entry(frame, width=50)
txturl.grid(row=0, column=1, padx=2, pady=5)

# Button to start the download
download_button = tk.Button(frame, text="Download", command='')
download_button.grid(row=0, column=2, padx=2, pady=5)

# Multiline Textbox for progress updates

txtLogs = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=20)
txtLogs.grid(row=1, column=0, columnspan=3, pady=5)
txtLogs.configure(state=tk.DISABLED)

# Frame for buttons below the logs
frame_btn = tk.Frame(tab2, bg="#FFFFFF")
frame_btn.pack(pady=(5, 10))  # Add padding: 10px top, 20px bottom

# Add empty columns on both sides to center the buttons
frame_btn.grid_columnconfigure(0, weight=1)  # Empty column on the left
frame_btn.grid_columnconfigure(3, weight=1)  # Empty column on the right

btnListFiles = tk.Button(frame_btn, text="Downloaded Files", command='')
btnListFiles.grid(row=0, column=1)
# btnListFiles.pack(side=tk.TOP, anchor=tk.CENTER)  # Center the button

btn_clear_logs = tk.Button(frame_btn, text="Clear Logs", command='')
btn_clear_logs.grid(row=0, column=2)

# label2 = tk.Label(tab2, text="This is Tab 2", font=("Arial", 14))
# label2.pack(pady=20)

# entry2 = tk.Entry(tab2, width=30)
# entry2.pack(pady=10)

# button2 = tk.Button(tab2, text="Submit (Tab 2)", command=lambda: print(f"Entered: {entry2.get()}"))
# button2.pack()

# Tab 3: Frame and Widgets
tab3 = ttk.Frame(notebook)
notebook.add(tab3, text="Tab 3")

# Create an HtmlFrame widget
label3 = tk.Label(tab3, text="This is Tab 3", font=("Arial", 14))
label3.pack(pady=20)

text3 = tk.Text(tab3, height=5, width=40)
text3.pack()

# Run the application
root.mainloop()