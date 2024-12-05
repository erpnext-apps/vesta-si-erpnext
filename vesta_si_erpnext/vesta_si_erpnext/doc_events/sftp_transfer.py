import pysftp
import paramiko
from urllib.parse import urlparse
import os


class Sftp:
    def __init__(self, hostname, username, local_file, remote_path, password=None, port=22, pem_file_path = None):
        """Constructor Method"""
        # Set connection object to None (initial value)
        self.connection = None
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port
        self.pem_file_path= pem_file_path
        self.local_file= local_file
        self.remote_path = remote_path

    def connect(self):
        """Connects to the sftp server and returns the sftp connection object"""

        try:
            # Get the sftp connection object
            self.connection = pysftp.Connection(
                host=self.hostname,
                username=self.username,
                password=self.password,
                port=self.port,
            )
        except Exception as err:
            raise Exception(err)
        finally:
            print(f"Connected to {self.hostname} as {self.username}.")

    def listdir(self, remote_path):
        """lists all the files and directories in the specified path and returns them"""
        for obj in self.connection.listdir(remote_path):
            return obj

    def listdir_attr(self, remote_path):
        """lists all the files and directories (with their attributes) in the specified path and returns them"""
        for attr in self.connection.listdir_attr(remote_path):
            return attr

    def disconnect(self):
        """Closes the sftp connection"""
        self.connection.close()
        print(f"Disconnected from host {self.hostname}")

    def sftp_upload(self):
        # try:
        if self.pem_file_path:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            private_key = paramiko.RSAKey.from_private_key_file(self.pem_file_path)
            ssh.connect(hostname, self.port, username=username, pkey=private_key)
            sftp = ssh.open_sftp()
        if self.password:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.hostname, self.port, username=self.username, password=self.password)
            sftp = ssh.open_sftp()

        # Create remote directory if it doesn't exist
        try:
            sftp.chdir(self.remote_path)
        except IOError:
            sftp.mkdir(self.remote_path)
            sftp.chdir(self.remote_path)

        # Upload the file
        sftp.put(self.local_file, self.remote_path + '/' + os.path.basename(self.local_file))

        sftp.close()
        ssh.close()

        print(f"File {self.local_file} uploaded successfully to {self.remote_path}")
        # except Exception as e:
        #     print(f"Error: {e}")


# # Example values for initialization
hostname = "52.157.97.77"
username = "cm-skftest-12"
password = "*EklmvpLlzV!.xKt7rTsd7Mh"
local_file = "/home/frappe/frappe-bench/KGS - COA.xlsx"  # Replace with your local file path
remote_path = "/in/payments/"     # Replace with your remote path
port = 22

# # Create an instance of the Sftp class
sftp_instance = Sftp(
    hostname=hostname,
    username=username,
    local_file=local_file,
    remote_path=remote_path,
    password=password,
    port=port
)

sftp_instance.sftp_upload()

#from vesta_si_erpnext.vesta_si_erpnext.doc_events.sftp_transfer import Sftp
# You can now use this instance for further SFTP operations (assuming methods are implemented).
