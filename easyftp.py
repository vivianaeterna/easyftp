import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import paramiko
from ftplib import FTP
import os

# Global variables to hold connections and current path
sftp_client = None
ftp_client = None
current_path = "/"

def show_elements():
    # Show all elements under the connect buttons
    file_path_label.grid(row=4, column=0)
    file_path_entry.grid(row=4, column=1)
    browse_button.grid(row=4, column=2)
    upload_button.grid(row=5, column=1)
    status_label.grid(row=6, column=0, columnspan=3)
    path_label.grid(row=7, column=0, columnspan=3)
    go_up_button.grid(row=8, column=0, columnspan=3)
    refresh_button.grid(row=9, column=0)
    delete_button.grid(row=9, column=1)
    file_list_label.grid(row=10, column=0, columnspan=3)
    file_list.grid(row=11, column=0, columnspan=3)

def hide_elements():
    # Hide all elements under the connect buttons
    file_path_label.grid_remove()
    file_path_entry.grid_remove()
    browse_button.grid_remove()
    upload_button.grid_remove()
    status_label.grid_remove()
    path_label.grid_remove()
    go_up_button.grid_remove()
    refresh_button.grid_remove()
    delete_button.grid_remove()
    file_list_label.grid_remove()
    file_list.grid_remove()

def connect_sftp():
    global sftp_client, current_path
    host = host_entry.get()
    username = username_entry.get()
    password = password_entry.get()
    port = 22

    try:
        transport = paramiko.Transport((host, port))
        transport.connect(username=username, password=password)
        sftp_client = paramiko.SFTPClient.from_transport(transport)
        status_label.config(text="SFTP Connected")
        current_path = "/"        
        show_elements()
        list_files()
    except Exception as e:
        status_label.config(text=f"SFTP Connection Failed: {e}")
        sftp_client = None

def connect_ftp():
    global ftp_client, current_path
    host = host_entry.get()
    username = username_entry.get()
    password = password_entry.get()

    try:
        ftp_client = FTP(host)
        ftp_client.login(user=username, passwd=password)
        status_label.config(text="FTP Connected")
        current_path = "/"
        show_elements()
        list_files()
    except Exception as e:
        status_label.config(text=f"FTP Connection Failed: {e}")
        ftp_client = None

def disconnect():
    global sftp_client, ftp_client
    if sftp_client:
        sftp_client.close()
        sftp_client = None
        status_label.config(text="SFTP Disconnected")
    elif ftp_client:
        ftp_client.quit()
        ftp_client = None
        status_label.config(text="FTP Disconnected")
    file_list.delete(0, tk.END)
    path_label.config(text="Current Path: ")
    hide_elements()

def browse_files():
    file_path = filedialog.askopenfilename()
    file_path_entry.delete(0, tk.END)
    file_path_entry.insert(0, file_path)

def upload_file():
    file_path = file_path_entry.get()
    if not file_path:
        messagebox.showerror("Error", "Please select a file to upload.")
        return

    filename = os.path.basename(file_path)
    remote_path = os.path.join(current_path, filename).replace("\\", "/")

    if file_exists(filename):
        user_choice = messagebox.askyesnocancel(
            "File Exists",
            f"A file with the name '{filename}' already exists. Do you want to overwrite it?"
        )
        if user_choice is None:
            status_label.config(text="Upload Cancelled")
            return
        elif not user_choice:
            filename = f"{os.path.splitext(filename)[0]}_copy{os.path.splitext(filename)[1]}"
            remote_path = os.path.join(current_path, filename).replace("\\", "/")

    if sftp_client:
        try:
            sftp_client.put(file_path, remote_path)
            status_label.config(text=f"Uploaded {file_path} to {remote_path}")
            list_files()
        except Exception as e:
            status_label.config(text=f"SFTP Upload Failed: {e}")
    elif ftp_client:
        try:
            with open(file_path, 'rb') as f:
                ftp_client.storbinary(f"STOR {remote_path}", f)
            status_label.config(text=f"Uploaded {file_path} to {remote_path}")
            list_files()
        except Exception as e:
            status_label.config(text=f"FTP Upload Failed: {e}")
    else:
        messagebox.showerror("Error", "Please connect to a server first.")

def file_exists(filename):
    try:
        if sftp_client:
            files = sftp_client.listdir(current_path)
        elif ftp_client:
            files = ftp_client.nlst(current_path)
            files = [os.path.basename(file) for file in files]
        else:
            return False
        return filename in files
    except Exception as e:
        status_label.config(text=f"Error checking file existence: {e}")
        return False

def list_files():
    file_list.delete(0, tk.END)
    if sftp_client:
        try:
            files = sftp_client.listdir(current_path)
            for file in files:
                file_list.insert(tk.END, file)
        except Exception as e:
            status_label.config(text=f"SFTP List Files Failed: {e}")
    elif ftp_client:
        try:
            files = ftp_client.nlst(current_path)
            for file in files:
                file_list.insert(tk.END, os.path.basename(file))
        except Exception as e:
            status_label.config(text=f"FTP List Files Failed: {e}")

def change_directory(event):
    global current_path
    selected_item = file_list.get(file_list.curselection())
    new_path = os.path.join(current_path, selected_item).replace("\\", "/")

    if sftp_client:
        try:
            sftp_client.chdir(new_path)
            current_path = new_path
            list_files()
            path_label.config(text=f"Current Path: {current_path}")
        except Exception as e:
            status_label.config(text=f"SFTP Change Directory Failed: {e}")
    elif ftp_client:
        try:
            ftp_client.cwd(new_path)
            current_path = new_path
            list_files()
            path_label.config(text=f"Current Path: {current_path}")
        except Exception as e:
            status_label.config(text=f"FTP Change Directory Failed: {e}")

def go_up():
    global current_path
    if current_path != "/":
        current_path = os.path.dirname(current_path).replace("\\", "/")
        if sftp_client:
            sftp_client.chdir(current_path)
        elif ftp_client:
            ftp_client.cwd(current_path)
        list_files()
        path_label.config(text=f"Current Path: {current_path}")

def refresh_view():
    list_files()

def delete_file():
    selected_item = file_list.get(file_list.curselection())
    if not selected_item:
        messagebox.showerror("Error", "Please select a file to delete.")
        return

    remote_path = os.path.join(current_path, selected_item).replace("\\", "/")

    if sftp_client:
        try:
            sftp_client.remove(remote_path)
            status_label.config(text=f"Deleted {remote_path}")
            list_files()
        except Exception as e:
            status_label.config(text=f"SFTP Delete Failed: {e}")
    elif ftp_client:
        try:
            ftp_client.delete(remote_path)
            status_label.config(text=f"Deleted {remote_path}")
            list_files()
        except Exception as e:
            status_label.config(text=f"FTP Delete Failed: {e}")

def on_select(event):
    # Single click selects a file
    pass

# Create the main window
root = tk.Tk()
root.title("FTP/SFTP Client")

# Host
tk.Label(root, text="Host").grid(row=0, column=0)
host_entry = tk.Entry(root)
host_entry.grid(row=0, column=1)

# Username
tk.Label(root, text="Username").grid(row=1, column=0)
username_entry = tk.Entry(root)
username_entry.grid(row=1, column=1)

# Password
tk.Label(root, text="Password").grid(row=2, column=0)
password_entry = tk.Entry(root, show="*")
password_entry.grid(row=2, column=1)

# Connect Buttons
connect_sftp_button = tk.Button(root, text="Connect SFTP", command=connect_sftp)
connect_sftp_button.grid(row=3, column=0)

connect_ftp_button = tk.Button(root, text="Connect FTP", command=connect_ftp)
connect_ftp_button.grid(row=3, column=1)

# Disconnect Button
disconnect_button = tk.Button(root, text="Disconnect", command=disconnect)
disconnect_button.grid(row=3, column=2)

# File Path
file_path_label = tk.Label(root, text="File Path")
file_path_label.grid(row=4, column=0)
file_path_entry = tk.Entry(root)
file_path_entry.grid(row=4, column=1)
browse_button = tk.Button(root, text="Browse", command=browse_files)
browse_button.grid(row=4, column=2)

# Upload Button
upload_button = tk.Button(root, text="Upload", command=upload_file)
upload_button.grid(row=5, column=1)

# Status Label
status_label = tk.Label(root, text="")
status_label.grid(row=6, column=0, columnspan=3)

# Path Label
path_label = tk.Label(root, text=f"Current Path: {current_path}")
path_label.grid(row=7, column=0, columnspan=3)

# Go Up Button
go_up_button = tk.Button(root, text="Go Up", command=go_up)
go_up_button.grid(row=8, column=0, columnspan=3)

# Refresh Button
refresh_button = tk.Button(root, text="Refresh", command=refresh_view)
refresh_button.grid(row=9, column=0)

# Delete Button
delete_button = tk.Button(root, text="Delete", command=delete_file)
delete_button.grid(row=9, column=1)

# File List
file_list_label = tk.Label(root, text="Files on Server")
file_list_label.grid(row=10, column=0, columnspan=3)
file_list = tk.Listbox(root, width=50)
file_list.grid(row=11, column=0, columnspan=3)
file_list.bind('<<ListboxSelect>>', on_select)
file_list.bind('<Double-1>', change_directory)

# Initially hide all elements under the connect buttons
hide_elements()

# Run the application
root.mainloop()
