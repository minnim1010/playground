import subprocess


def run_kubectl_command(command, use_shell):
    """Runs the provided kubectl command and returns the output and error."""
    try:
        result = subprocess.run(
            command,
            shell=use_shell,
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        return result.stdout, None
    except FileNotFoundError:
        return (
            None,
            "Error: 'kubectl' command not found. Please ensure it is installed and in your PATH.",
        )
    except subprocess.CalledProcessError as e:
        if use_shell and "grep" in command and e.returncode == 1 and not e.stderr:
            return "No matching pods found.", None
        return None, f"Error executing command:\n{e.stderr}"
    except subprocess.TimeoutExpired:
        return None, "Error: Command timed out."
    except Exception as e:
        return None, f"An unexpected error occurred: {e}"


def stream_command(command):
    """Runs a command and yields its output line by line."""
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        universal_newlines=True,
    )
    for line in iter(process.stdout.readline, ""):
        yield line
    process.stdout.close()
    return_code = process.wait()
    if return_code != 0:
        yield f"\nError: Process exited with code {return_code}"
