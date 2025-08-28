"""
APK Processor
Handles the downloading and processing of APK files
"""

import os
import subprocess
from pathlib import Path
from . import ToolsManager


class APKProcessor:
    """Handles APK processing with apkeep and assetripper"""

    def __init__(self, log_callback=None):
        self.tools: ToolsManager = ToolsManager()
        self.log_callback = log_callback or (lambda x: None)
        self.current_process = None

    def log(self, message):
        """Log message with callback"""
        self.log_callback(message)

    def parse_apkeep_progress(self, line, current_progress):
        """Parse apkeep output to extract download progress"""
        line_lower = line.lower()

        # Look for progress indicators in apkeep output
        if "downloading" in line_lower:
            return max(current_progress, 0.2)  # 20% when download starts
        elif "fetching" in line_lower or "requesting" in line_lower:
            return max(current_progress, 0.15)  # 15% when fetching info
        elif "found" in line_lower and "version" in line_lower:
            return max(current_progress, 0.25)  # 25% when version found
        elif "connecting" in line_lower:
            return max(current_progress, 0.3)  # 30% when connecting
        elif "progress" in line_lower or "%" in line:
            # Try to extract percentage from line
            import re

            percentage_match = re.search(r"(\d+)%", line)
            if percentage_match:
                percentage = int(percentage_match.group(1))
                return min(0.9, percentage / 100.0)  # Convert to 0-0.9 range
            return max(current_progress, 0.5)  # 50% if progress mentioned
        elif "saving" in line_lower or "writing" in line_lower:
            return max(current_progress, 0.7)  # 70% when saving
        elif (
            "saved" in line_lower
            or "downloaded" in line_lower
            or "complete" in line_lower
        ):
            return 0.9  # 90% when completed
        elif "error" in line_lower or "failed" in line_lower:
            return current_progress  # Don't increase on error
        else:
            # Gradual progress increase for other activities
            return min(current_progress + 0.05, 0.8)  # Slow increment up to 80%

    def download_apk(self, package_name, version, output_dir, progress_callback=None):
        """Download APK with specific version using apkeep"""
        try:
            self.log(f"🔍 Bắt đầu tải APK cho package: {package_name}")
            self.log(f"📋 Version yêu cầu: {version}")
            # Build command with version support
            if version and version.lower() not in [
                "latest",
                "",
                "🔄 loading...",
                "loading...",
            ]:
                package_with_version = f"{package_name}@{version}"
                cmd_args = ["-a", package_with_version, str(output_dir)]
            else:
                cmd_args = ["-a", package_name, str(output_dir)]
            cmd = self.tools.apkeep(cmd_args)
            self.log(f"🔧 Executing: {' '.join(cmd)}")
            self.current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                cwd=str(output_dir),
            )
            download_progress = 0.1
            if self.current_process.stdout:
                while True:
                    output = self.current_process.stdout.readline()
                    if output == "" and self.current_process.poll() is not None:
                        break
                    if output:
                        line = output.strip()
                        self.log(f"📥 {line}")
                        progress_value = self.parse_apkeep_progress(
                            line, download_progress
                        )
                        if progress_value > download_progress:
                            download_progress = progress_value
                            if progress_callback:
                                progress_callback(line, download_progress)
                        if (
                            "downloaded" in line.lower()
                            or "complete" in line.lower()
                            or "saved" in line.lower()
                        ):
                            download_progress = 0.9
                            if progress_callback:
                                progress_callback(line, download_progress)
            return_code = self.current_process.wait()
            if self.current_process.stderr:
                stderr_output = self.current_process.stderr.read()
                if stderr_output:
                    self.log("⚠️ Error output:")
                    for line in stderr_output.splitlines():
                        if line.strip():
                            self.log(f"  {line}")
            self.log(f"📊 Return code: {return_code}")
            if return_code == 0:
                self.log(f"✅ Tải APK thành công! Version: {version}")
                apk_files = list(Path(output_dir).glob("*.xapk"))
                if apk_files:
                    self.log(f"📁 Downloaded: {[f.name for f in apk_files]}")
                    if progress_callback:
                        progress_callback("Download completed successfully!", 1.0)
                    return True
                else:
                    self.log("⚠️ No APK/XAPK files found after download")
                    return False
            else:
                error_msg = "Check logs for details"
                self.log(f"❌ Download failed (code {return_code}): {error_msg}")
                if version and version.lower() not in ["latest", ""]:
                    self.log(f"🔄 Trying fallback to latest version...")
                    return self.download_apk(
                        package_name, version, output_dir, progress_callback
                    )
                return False
        except subprocess.TimeoutExpired:
            self.log(f"⏰ Download timeout after 5 minutes")
            return False
        except Exception as e:
            self.log(f"❌ Exception during download: {str(e)}")
            import traceback

            self.log(f"📋 Traceback: {traceback.format_exc()}")
            return False

    def extract_assets(self, apk_path, output_dir, progress_callback=None):
        """Extract assets using AssetRipper (safe, never crash app)"""
        import traceback

        try:
            self.log(f"🔧 Bắt đầu trích xuất assets từ: {os.path.basename(apk_path)}")
            output_dir = os.path.dirname(apk_path)

            cmd = self.tools.asset_ripper([str(apk_path), str(output_dir)])

            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                universal_newlines=True,
            )
            # Đọc stdout và stderr song song, không để block
            import threading

            stdout_lines = []
            stderr_lines = []

            def read_stdout():
                try:
                    if proc.stdout:
                        for line in iter(proc.stdout.readline, ""):
                            line = line.strip()
                            if line:
                                stdout_lines.append(line)
                                self.log(f"🔧 {line}")
                                if progress_callback:
                                    progress_callback(line)
                except Exception as e:
                    self.log(f"❌ Exception đọc stdout: {e}")

            def read_stderr():
                try:
                    if proc.stderr:
                        for line in iter(proc.stderr.readline, ""):
                            line = line.strip()
                            if line:
                                stderr_lines.append(line)
                except Exception as e:
                    self.log(f"❌ Exception đọc stderr: {e}")

            t_out = threading.Thread(target=read_stdout)
            t_err = threading.Thread(target=read_stderr)
            t_out.start()
            t_err.start()
            t_out.join()
            t_err.join()
            proc.wait()
            if proc.returncode == 0:
                self.log("✅ Trích xuất assets thành công!")
                return True
            else:
                error = "\n".join(stderr_lines)
                self.log(f"❌ Lỗi khi trích xuất assets: {error}")
                return False
        except Exception as e:
            self.log(f"❌ Exception khi trích xuất assets: {str(e)}")
            self.log(f"📋 Traceback: {traceback.format_exc()}")
            return False
