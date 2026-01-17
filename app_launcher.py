import subprocess
import os
import time

def app_is_running(app_name):
    """
    Check if an application is currently running on macOS.
    
    Args:
        app_name (str): The name of the application to check.
        
    Returns:
        bool: True if running, False otherwise.
    """
    try:
        # pgrep -x matches exact process name
        # Note: Some apps might have different process names than their display names.
        subprocess.check_call(["pgrep", "-x", app_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def launch_app(app_name, wait=0.5):
    """
    Launch a single macOS application by name.
    
    Args:
        app_name (str): The name of the application (e.g., "Calculator").
        wait (float): Time in seconds to wait after launching. Default is 0.5.
        
    Returns:
        bool: True if command executed successfully, False otherwise.
    """
    try:
        print(f"Launching {app_name}...")
        subprocess.Popen(["open", "-a", app_name])
        if wait > 0:
            time.sleep(wait)
        return True
    except Exception as e:
        print(f"Error launching {app_name}: {e}")
        return False

def launch_app_with_path(app_name, folder_path):
    """
    Launch an application with a specific file or folder path.
    
    Args:
        app_name (str): The name of the application.
        folder_path (str): The absolute or relative path to open.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Expand user path (e.g. ~) and get absolute path
        abs_path = os.path.abspath(os.path.expanduser(folder_path))
        
        if not os.path.exists(abs_path):
            print(f"Error: Path does not exist: {abs_path}")
            return False
            
        print(f"Opening '{abs_path}' with {app_name}...")
        subprocess.Popen(["open", "-a", app_name, abs_path])
        return True
    except Exception as e:
        print(f"Error launching {app_name} with path {folder_path}: {e}")
        return False

def open_url_in_browser(url, browser="Google Chrome", new_window=True):
    """
    Open a URL in a specific browser.
    
    Args:
        url (str): The URL to open.
        browser (str): Browser name (e.g. "Google Chrome", "Safari", "Brave Browser", "Firefox").
        new_window (bool): If True, forces a new window. If False, opens in existing window/tab.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        print(f"Opening {url} in {browser}...")
        
        if new_window:
            # -n opens a new instance of the application
            # --args passes arguments to the application
            # --new-window is a common flag for Chromium based browsers to force new window
            cmd = ["open", "-na", browser, "--args", "--new-window", url]
        else:
            cmd = ["open", "-a", browser, url]
            
        subprocess.Popen(cmd)
        return True
    except Exception as e:
        print(f"Error opening URL in {browser}: {e}")
        return False

def launch_multiple_apps(app_list, delay=0.5):
    """
    Launch multiple applications sequentially.
    
    Args:
        app_list (list): List of strings (app names) or tuples (app_name, path).
        delay (float): Delay in seconds between launches.
        
    Returns:
        int: Count of successfully launched apps.
    """
    count = 0
    print(f"Starting launch sequence for {len(app_list)} apps...")
    
    for item in app_list:
        success = False
        if isinstance(item, str):
            success = launch_app(item, wait=delay)
        elif isinstance(item, tuple) and len(item) == 2:
            success = launch_app_with_path(item[0], item[1])
            if success and delay > 0:
                time.sleep(delay)
        
        if success:
            count += 1
            
    print(f"Launch sequence complete. Launched {count}/{len(app_list)} apps.")
    return count

def close_app(app_name):
    """
    Close a running application using AppleScript.
    
    Args:
        app_name (str): The name of the app to close.
        
    Returns:
        bool: True if command executed, False otherwise.
    """
    if not app_is_running(app_name):
        print(f"{app_name} is not running.")
        return False
        
    try:
        print(f"Closing {app_name}...")
        # specific osascript command to quit app gracefully
        cmd = ["osascript", "-e", f'quit app "{app_name}"']
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
        print(f"{app_name} closed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to close {app_name}: {e}")
        return False
    except Exception as e:
        print(f"Error executing close command: {e}")
        return False

# ==============================================================================
# EXAMPLE USAGE
# ==============================================================================
if __name__ == "__main__":
    print("--- Testing App Launcher Module ---")
    
    # 1. Check if an app is running
    is_running = app_is_running("Calculator")
    print(f"Is Calculator running? {is_running}")
    
    # 2. Launch single app
    # launch_app("Calculator")
    
    # 3. Launch app with path
    # launch_app_with_path("Visual Studio Code", "~/Downloads")
    
    # 4. Open URL in new window
    # open_url_in_browser("https://www.google.com", browser="Google Chrome", new_window=True)
    
    # 5. Launch multiple
    # my_apps = [
    #     "Calculator",
    #     ("Notes", "~/Documents"),  # Note: Notes app might not handle folder path argument directly like VS Code
    #     "Terminal"
    # ]
    # launch_multiple_apps(my_apps)
    
    # 6. Close app (uncomment to test - will close Calculator if running)
    # time.sleep(2)
    # close_app("Calculator")
