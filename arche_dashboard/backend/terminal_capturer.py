#!/usr/bin/env python3
"""
Terminal Output Capturer for ArchE Dashboard
============================================

Captures terminal output from rich console and streams it for dashboard display.
This module provides utilities to capture console output and forward it via queues
for WebSocket streaming.

ResonantiA Protocol v3.5-GP
"""

import sys
import io
import asyncio
from typing import Optional, Callable, Any
from queue import Queue
from datetime import datetime
from rich.console import Console
from rich.terminal_theme import TerminalTheme


class TerminalOutputCapturer:
    """
    Captures terminal output from rich console and forwards it to a queue.
    This allows streaming terminal output to the dashboard via WebSocket.
    """
    
    def __init__(self, output_queue: Optional[Queue] = None):
        """
        Initialize the terminal output capturer.
        
        Args:
            output_queue: Queue to push captured output to (optional)
        """
        self.output_queue = output_queue or Queue()
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        self.captured_stdout = io.StringIO()
        self.captured_stderr = io.StringIO()
        self.is_capturing = False
        
    def start_capture(self):
        """Start capturing stdout and stderr."""
        if self.is_capturing:
            return
        
        self.is_capturing = True
        sys.stdout = self._create_capture_stream(self.captured_stdout, 'stdout')
        sys.stderr = self._create_capture_stream(self.captured_stderr, 'stderr')
    
    def stop_capture(self):
        """Stop capturing and restore original streams."""
        if not self.is_capturing:
            return
        
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr
        self.is_capturing = False
    
    def _create_capture_stream(self, buffer: io.StringIO, stream_type: str):
        """Create a stream that writes to both original stream and capture buffer."""
        class DualStream:
            def __init__(self, original, buffer, stream_type, queue):
                self.original = original
                self.buffer = buffer
                self.stream_type = stream_type
                self.queue = queue
            
            def write(self, text: str):
                if text.strip():  # Only queue non-empty text
                    timestamp = datetime.now().isoformat()
                    self.queue.put({
                        'type': 'terminal_output',
                        'stream': stream_type,
                        'text': text,
                        'timestamp': timestamp
                    })
                self.original.write(text)
                self.buffer.write(text)
            
            def flush(self):
                self.original.flush()
            
            def __getattr__(self, name):
                return getattr(self.original, name)
        
        return DualStream(
            self.original_stdout if stream_type == 'stdout' else self.original_stderr,
            buffer,
            stream_type,
            self.output_queue
        )
    
    def get_captured_output(self) -> tuple[str, str]:
        """
        Get all captured output.
        
        Returns:
            Tuple of (stdout_text, stderr_text)
        """
        stdout_text = self.captured_stdout.getvalue()
        stderr_text = self.captured_stderr.getvalue()
        return stdout_text, stderr_text
    
    def clear_capture(self):
        """Clear captured buffers."""
        self.captured_stdout.seek(0)
        self.captured_stdout.truncate(0)
        self.captured_stderr.seek(0)
        self.captured_stderr.truncate(0)


class RichConsoleCapturer:
    """
    Captures output from rich.console.Console by creating a custom console
    that forwards output to both the terminal and a queue.
    """
    
    def __init__(self, output_queue: Optional[Queue] = None, file: Optional[io.TextIO] = None):
        """
        Initialize the rich console capturer.
        
        Args:
            output_queue: Queue to push captured output to
            file: File-like object to write to (defaults to stdout)
        """
        self.output_queue = output_queue
        self.file = file or sys.stdout
        self._create_capturing_console()
    
    def _create_capturing_console(self):
        """Create a console that captures output."""
        # Create a custom file-like object that writes to both stdout and queue
        class CapturingFile:
            def __init__(self, original_file, queue):
                self.original_file = original_file
                self.queue = queue
            
            def write(self, text: str):
                if text:
                    timestamp = datetime.now().isoformat()
                    # Try to strip ANSI codes for cleaner output
                    plain_text = self._strip_ansi(text)
                    if plain_text.strip():
                        try:
                            self.queue.put({
                                'type': 'terminal_output',
                                'stream': 'console',
                                'text': plain_text,
                                'raw_text': text,  # Keep raw for formatting
                                'timestamp': timestamp
                            }, block=False)
                        except:
                            pass  # Queue full, skip
                if self.original_file:
                    self.original_file.write(text)
            
            def _strip_ansi(self, text: str) -> str:
                """Strip ANSI color codes from text."""
                import re
                ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                return ansi_escape.sub('', text)
            
            def flush(self):
                if self.original_file:
                    self.original_file.flush()
            
            def __getattr__(self, name):
                if self.original_file:
                    return getattr(self.original_file, name)
                raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
        
        capturing_file = CapturingFile(self.file, self.output_queue) if self.output_queue else self.file
        self.console = Console(file=capturing_file, force_terminal=True, width=None)
    
    def get_console(self) -> Console:
        """Get the capturing console instance."""
        return self.console


async def stream_terminal_output(queue: Queue, send_callback: Callable[[dict], None], interval: float = 0.1):
    """
    Continuously read from output queue and send to callback.
    
    Args:
        queue: Queue to read from
        send_callback: Async function to call with output chunks
        interval: Interval between queue checks (seconds)
    """
    while True:
        try:
            # Get all available items from queue
            outputs = []
            while not queue.empty():
                try:
                    output = queue.get_nowait()
                    outputs.append(output)
                except:
                    break
            
            # Send accumulated outputs
            if outputs:
                for output in outputs:
                    await send_callback(output)
            
            await asyncio.sleep(interval)
            
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"Error in terminal output streaming: {e}")
            await asyncio.sleep(interval)

