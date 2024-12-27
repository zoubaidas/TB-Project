import tempfile
import subprocess
import os

def execute_command(command):
    print(f"[INFO] command detected: {command}")
    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp_log_file:
            log_file_path = temp_log_file.name

        # Redirect both stdout and stderr to the log file
        command_with_redirection = f'bash -c "{command} 2>&1 | tee {log_file_path}"'

        process = subprocess.run(
            f"x-terminal-emulator -e '{command_with_redirection}'", shell=True
        )
        output = ""

        if os.path.exists(log_file_path):
            with open(log_file_path, 'rb') as f:  # Open in binary mode
                try:
                    output = f.read().decode('utf-8')  # Try decoding as UTF-8
                except UnicodeDecodeError:
                    print("[WARNING] Non-UTF-8 content detected in log file, attempting fallback decoding...")
                    output = f.read().decode('ISO-8859-1')  # Fallback to an alternate encoding

            try:
                os.remove(log_file_path)
            except PermissionError:
                print(f"[WARNING]: Could not delete temporary log file: {log_file_path}")

        # Parse stdout and stderr from the captured log
        ret = {
            "stdout": output.strip(),  # Assuming all output is merged
            "stderr": None,
            "status": "Success" if process.returncode == 0 else "Error"
        }
        # If the command is not a help command, display the output
        if not command.endswith("-h") and not command.startswith("man"):
            format_output(ret)
        return ret

    except FileNotFoundError:
        error_msg = "[ERROR] No graphical terminal detected. Please install a terminal emulator."
        print(error_msg)
        ret = {"stdout": None, "stderr": error_msg, "status": "Error"}
        format_output(ret)
        return ret


def format_output(result):
    if not isinstance(result, dict):
        raise ValueError("The result must be a dictionary.")
    required_keys = {"stdout", "stderr", "status"}
    if not required_keys.issubset(result.keys()):
        raise ValueError(f"The result dictionary must contain the keys: {required_keys}")
    print("\n" + "=" * 50)
    print("[COMMAND RESULTS]")
    print("=" * 50)
    if result["status"] == "Success":
        print("[STATUS]: ✅ Command successful")
    else:
        print("[STATUS]: ❌ Error during execution")
    print("\n[STDOUT]:")
    if result["stdout"]:
        print(result["stdout"])
    else:
        print("No standard output.")
    print("\n[STDERR]:")
    if result["stderr"]:
        print(result["stderr"])
    else:
        print("No errors detected.")
    print("=" * 50)


def get_tool_help(tool_name):
    """
    Retrieves the help information for a tool using the `--help` flag.

    Args:
        tool_name (str): The name of the tool to retrieve help information for.

    Returns:
        dict: Dictionary containing `stdout`, `stderr`, and `status`.
    """
    check_manual = subprocess.run(['man', tool_name.lower()], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check_manual.returncode != 0:
        return execute_command(f"{tool_name.lower()} -h")
    return execute_command(f"man {tool_name.lower()}")
