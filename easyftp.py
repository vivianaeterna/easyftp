import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QFileDialog, QMessageBox, QWidget
from PyQt5.QtCore import Qt
import paramiko
from ftplib import FTP
import os

# Global variables to hold connections and current path
sftp_client = None
ftp_client = None
current_path = "/"

class EasyFTPApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("easyFTP")
        self.setGeometry(100, 100, 300, 200)

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # Host
        self.host_label = QLabel("Host")
        layout.addWidget(self.host_label)
        self.host_entry = QLineEdit()
        layout.addWidget(self.host_entry)

        # Username
        self.username_label = QLabel("Username")
        layout.addWidget(self.username_label)
        self.username_entry = QLineEdit()
        layout.addWidget(self.username_entry)

        # Password
        self.password_label = QLabel("Password")
        layout.addWidget(self.password_label)
        self.password_entry = QLineEdit()
        self.password_entry.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_entry)

        # Connect Buttons
        connect_buttons_layout = QHBoxLayout()
        layout.addLayout(connect_buttons_layout)

        self.connect_sftp_button = QPushButton("Connect SFTP")
        self.connect_sftp_button.clicked.connect(self.connect_sftp)
        connect_buttons_layout.addWidget(self.connect_sftp_button)

        self.connect_ftp_button = QPushButton("Connect FTP")
        self.connect_ftp_button.clicked.connect(self.connect_ftp)
        connect_buttons_layout.addWidget(self.connect_ftp_button)

        self.disconnect_button = QPushButton("Disconnect")
        self.disconnect_button.clicked.connect(self.disconnect)
        connect_buttons_layout.addWidget(self.disconnect_button)

        # File Path
        self.file_path_label = QLabel("File Path")
        layout.addWidget(self.file_path_label)
        self.file_path_entry = QLineEdit()
        layout.addWidget(self.file_path_entry)

        browse_upload_layout = QHBoxLayout()
        layout.addLayout(browse_upload_layout)

        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_files)
        browse_upload_layout.addWidget(self.browse_button)

        # Upload Button
        self.upload_button = QPushButton("Upload")
        self.upload_button.clicked.connect(self.upload_file)
        browse_upload_layout.addWidget(self.upload_button)

        # Status Label
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        # Path Label
        self.path_label = QLabel(f"Current Path: {current_path}")
        layout.addWidget(self.path_label)

        navigation_layout = QHBoxLayout()
        layout.addLayout(navigation_layout)

        # Go Up Button
        self.go_up_button = QPushButton("Go Up")
        self.go_up_button.clicked.connect(self.go_up)
        navigation_layout.addWidget(self.go_up_button)

        # Refresh Button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_view)
        navigation_layout.addWidget(self.refresh_button)

        # Delete Button
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_file)
        navigation_layout.addWidget(self.delete_button)

        # File List
        self.file_list_label = QLabel("Files on Server")
        layout.addWidget(self.file_list_label)
        self.file_list = QListWidget()
        self.file_list.itemDoubleClicked.connect(self.change_directory)
        layout.addWidget(self.file_list)

        # Initially hide all elements under the connect buttons
        self.hide_elements()

    def show_elements(self):
        self.file_path_label.show()
        self.file_path_entry.show()
        self.browse_button.show()
        self.upload_button.show()
        self.status_label.show()
        self.path_label.show()
        self.go_up_button.show()
        self.refresh_button.show()
        self.delete_button.show()
        self.file_list_label.show()
        self.file_list.show()
        self.adjustSize()

    def hide_elements(self):
        self.file_path_label.hide()
        self.file_path_entry.hide()
        self.browse_button.hide()
        self.upload_button.hide()
        self.status_label.hide()
        self.path_label.hide()
        self.go_up_button.hide()
        self.refresh_button.hide()
        self.delete_button.hide()
        self.file_list_label.hide()
        self.file_list.hide()

    def connect_sftp(self):
        global sftp_client, current_path
        host = self.host_entry.text()
        username = self.username_entry.text()
        password = self.password_entry.text()
        port = 22

        try:
            transport = paramiko.Transport((host, port))
            transport.connect(username=username, password=password)
            sftp_client = paramiko.SFTPClient.from_transport(transport)
            self.status_label.setText("SFTP Connected")
            current_path = "/"
            self.show_elements()
            self.list_files()
        except Exception as e:
            self.status_label.setText(f"SFTP Connection Failed: {e}")
            sftp_client = None

    def connect_ftp(self):
        global ftp_client, current_path
        host = self.host_entry.text()
        username = self.username_entry.text()
        password = self.password_entry.text()

        try:
            ftp_client = FTP(host)
            ftp_client.login(user=username, passwd=password)
            self.status_label.setText("FTP Connected")
            current_path = "/"
            self.show_elements()
            self.list_files()
        except Exception as e:
            self.status_label.setText(f"FTP Connection Failed: {e}")
            ftp_client = None

    def disconnect(self):
        global sftp_client, ftp_client
        if sftp_client:
            sftp_client.close()
            sftp_client = None
            self.status_label.setText("SFTP Disconnected")
        elif ftp_client:
            ftp_client.quit()
            ftp_client = None
            self.status_label.setText("FTP Disconnected")

        self.file_list.clear()
        self.path_label.setText("Current Path: ")
        self.hide_elements()

    def browse_files(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if file_path:
            self.file_path_entry.setText(file_path)

    def upload_file(self):
        file_path = self.file_path_entry.text()
        if not file_path:
            QMessageBox.critical(self, "Error", "Please select a file to upload.")
            return

        filename = os.path.basename(file_path)
        remote_path = os.path.join(current_path, filename).replace("\\", "/")

        if self.file_exists(filename):
            reply = QMessageBox.question(self, "File Exists",
                                         f"A file with the name '{filename}' already exists. Do you want to overwrite it?",
                                         QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if reply == QMessageBox.Cancel:
                self.status_label.setText("Upload Cancelled")
                return
            elif reply == QMessageBox.No:
                filename = f"{os.path.splitext(filename)[0]}_copy{os.path.splitext(filename)[1]}"
                remote_path = os.path.join(current_path, filename).replace("\\", "/")

        if sftp_client:
            try:
                sftp_client.put(file_path, remote_path)
                self.status_label.setText(f"Uploaded {file_path} to {remote_path}")
                self.list_files()
            except Exception as e:
                self.status_label.setText(f"SFTP Upload Failed: {e}")
        elif ftp_client:
            try:
                with open(file_path, 'rb') as f:
                    ftp_client.storbinary(f"STOR {remote_path}", f)
                self.status_label.setText(f"Uploaded {file_path} to {remote_path}")
                self.list_files()
            except Exception as e:
                self.status_label.setText(f"FTP Upload Failed: {e}")
        else:
            QMessageBox.critical(self, "Error", "Please connect to a server first.")

    def file_exists(self, filename):
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
            self.status_label.setText(f"Error checking file existence: {e}")
            return False

    def list_files(self):
        self.file_list.clear()
        if sftp_client:
            try:
                files = sftp_client.listdir(current_path)
                for file in files:
                    self.file_list.addItem(file)
            except Exception as e:
                self.status_label.setText(f"SFTP List Files Failed: {e}")
        elif ftp_client:
            try:
                files = ftp_client.nlst(current_path)
                for file in files:
                    self.file_list.addItem(os.path.basename(file))
            except Exception as e:
                self.status_label.setText(f"FTP List Files Failed: {e}")

    def change_directory(self, item):
        global current_path
        selected_item = item.text()
        new_path = os.path.join(current_path, selected_item).replace("\\", "/")

        if sftp_client:
            try:
                sftp_client.chdir(new_path)
                current_path = new_path
                self.list_files()
                self.path_label.setText(f"Current Path: {current_path}")
            except Exception as e:
                self.status_label.setText(f"SFTP Change Directory Failed: {e}")
        elif ftp_client:
            try:
                ftp_client.cwd(new_path)
                current_path = new_path
                self.list_files()
                self.path_label.setText(f"Current Path: {current_path}")
            except Exception as e:
                self.status_label.setText(f"FTP Change Directory Failed: {e}")

    def go_up(self):
        global current_path
        if current_path != "/":
            current_path = os.path.dirname(current_path).replace("\\", "/")
            if sftp_client:
                sftp_client.chdir(current_path)
            elif ftp_client:
                ftp_client.cwd(current_path)
            self.list_files()
            self.path_label.setText(f"Current Path: {current_path}")

    def refresh_view(self):
        self.list_files()

    def delete_file(self):
        selected_item = self.file_list.currentItem()
        if not selected_item:
            QMessageBox.critical(self, "Error", "Please select a file to delete.")
            return

        selected_item = selected_item.text()
        remote_path = os.path.join(current_path, selected_item).replace("\\", "/")

        if sftp_client:
            try:
                sftp_client.remove(remote_path)
                self.status_label.setText(f"Deleted {remote_path}")
                self.list_files()
            except Exception as e:
                self.status_label.setText(f"SFTP Delete Failed: {e}")
        elif ftp_client:
            try:
                ftp_client.delete(remote_path)
                self.status_label.setText(f"Deleted {remote_path}")
                self.list_files()
            except Exception as e:
                self.status_label.setText(f"FTP Delete Failed: {e}")

# Create and run the application
app = QApplication(sys.argv)
win = EasyFTPApp()
win.show()
sys.exit(app.exec_())
