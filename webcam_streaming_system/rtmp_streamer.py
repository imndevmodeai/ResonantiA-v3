import subprocess
import shlex
import threading
import time

class RTMPStreamer:
    def __init__(self, width: int, height: int, fps: int, bitrate_kbps: int):
        """
        Initializes the RTMP Streamer.
        """
        self.width = width
        self.height = height
        self.fps = fps
        self.bitrate = f"{bitrate_kbps}k"
        self.streams = {}

    def start_stream(self, platform_name: str, rtmp_url: str, stream_key: str):
        """
        Starts an ffmpeg process to stream to a given RTMP endpoint.
        """
        if platform_name in self.streams:
            print(f"Stream for '{platform_name}' is already running.")
            return

        command = [
            'ffmpeg',
            '-y',  # Overwrite output file if it exists
            '-f', 'rawvideo',
            '-vcodec', 'rawvideo',
            '-pix_fmt', 'rgb24',  # The format we'll pipe from our app
            '-s', f'{self.width}x{self.height}',
            '-r', str(self.fps),
            '-i', '-',  # Input from stdin
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-preset', 'ultrafast',
            '-b:v', self.bitrate,
            '-maxrate', self.bitrate,
            '-bufsize', f"{int(self.bitrate.replace('k',''))*2}k",
            '-g', str(self.fps * 2),
            '-f', 'flv',
            f"{rtmp_url}/{stream_key}"
        ]

        try:
            process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            self.streams[platform_name] = process
            print(f"Started RTMP stream for '{platform_name}'.")

            # Start a thread to monitor stderr for errors
            threading.Thread(target=self._monitor_stream, args=(platform_name, process), daemon=True).start()

        except Exception as e:
            print(f"Error starting ffmpeg for '{platform_name}': {e}")

    def _monitor_stream(self, platform_name: str, process: subprocess.Popen):
        """
        Monitors the stderr of an ffmpeg process for any errors.
        """
        while process.poll() is None:
            error_line = process.stderr.readline().decode('utf-8', errors='ignore').strip()
            if error_line:
                # You can add more sophisticated error logging here
                if "failed to connect" in error_line.lower() or "error" in error_line.lower():
                     print(f"FFMPEG Error ({platform_name}): {error_line}")
        
        print(f"Stream for '{platform_name}' has stopped (exit code: {process.returncode}).")
        if platform_name in self.streams:
            del self.streams[platform_name]

    def send_frame(self, frame_rgb: bytes):
        """
        Sends a single RGB frame to all active ffmpeg processes.
        """
        for platform, process in self.streams.items():
            try:
                if process.poll() is None: # If the process is still running
                    process.stdin.write(frame_rgb)
            except (BrokenPipeError, IOError):
                print(f"Pipe to ffmpeg for '{platform}' is broken. Stream may have stopped.")
            except Exception as e:
                print(f"Error writing frame to ffmpeg for '{platform}': {e}")

    def stop_all_streams(self):
        """
        Stops all running ffmpeg processes.
        """
        print("Stopping all RTMP streams...")
        for platform, process in list(self.streams.items()):
            try:
                if process.poll() is None:
                    process.stdin.close()
                    process.terminate()
                    process.wait(timeout=5)
            except Exception as e:
                print(f"Error stopping stream for '{platform}': {e}")
                process.kill()
        
        self.streams.clear()
        print("All streams stopped.")
