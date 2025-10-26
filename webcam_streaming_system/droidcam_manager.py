import subprocess
import os
import json

class DroidCamManager:
    def __init__(self, config_path='streaming_config.json'):
        self.config_path = config_path
        self.config = self._load_config()
        # Path to the droidcam-cli executable, assuming it's in the user's PATH
        self.cli_path = "droidcam-cli"

    def _load_config(self):
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Config file not found at {self.config_path}. Using empty config.")
            return {}
        except json.JSONDecodeError:
            print(f"Warning: Could not decode JSON from {self.config_path}. Using empty config.")
            return {}

    def _save_config(self):
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except IOError as e:
            print(f"Error saving config file: {e}")

    def connect(self, ip, port):
        """
        Connects to the DroidCam server using the provided IP and port.
        """
        print(f"Attempting to connect DroidCam to {ip}:{port}...")
        try:
            # The droidcam-cli command for adb connection is `droidcam-cli adb <IP> <PORT>`
            # We will use the wifi command: `droidcam-cli wifi <IP> <PORT>`
            command = [self.cli_path, ip, port, "-video"]

            # Start the process
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # For now, we are just launching it. A more robust solution might monitor this process.
            print(f"Launched DroidCam CLI with PID: {process.pid}")

            # Update and save the new IP and port as the defaults
            if 'droidcam_settings' not in self.config:
                self.config['droidcam_settings'] = {}
            self.config['droidcam_settings']['default_ip'] = ip
            self.config['droidcam_settings']['default_port'] = port
            self._save_config()

            return True, "DroidCam connection process started."
        except FileNotFoundError:
            return False, f"Error: '{self.cli_path}' not found. Please ensure droidcam-cli is installed and in your PATH."
        except Exception as e:
            return False, f"An unexpected error occurred: {e}"

    def disconnect(self):
        """
        Disconnects DroidCam by killing the droidcam-cli process.
        """
        print("Attempting to disconnect DroidCam...")
        try:
            # A simple way to disconnect is to kill the process
            subprocess.run(["pkill", "-f", self.cli_path], check=True)
            print("DroidCam CLI process terminated.")
            return True, "DroidCam disconnected."
        except subprocess.CalledProcessError:
            print("Could not find a DroidCam CLI process to kill (it may not be running).")
            return True, "No active DroidCam connection found to disconnect."
        except FileNotFoundError:
             return False, "Error: 'pkill' command not found. Cannot disconnect."
        except Exception as e:
            return False, f"An unexpected error occurred during disconnect: {e}"

    def get_default_ip(self):
        return self.config.get('droidcam_settings', {}).get('default_ip', '')

    def get_default_port(self):
        return self.config.get('droidcam_settings', {}).get('default_port', '')

if __name__ == '__main__':
    # Example Usage
    manager = DroidCamManager()
    
    # Get default connection info
    ip = manager.get_default_ip()
    port = manager.get_default_port()
    print(f"Default DroidCam IP: {ip}, Port: {port}")

    # Connect
    success, message = manager.connect("192.168.1.123", "4747")
    print(f"Connection attempt: {success}, {message}")

    # Disconnect after a delay
    import time
    time.sleep(5)
    success, message = manager.disconnect()
    print(f"Disconnection attempt: {success}, {message}")





