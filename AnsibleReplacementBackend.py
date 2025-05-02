# python test.py qa_spacereserveservices_user 8070
## This will only work if there is site configured on IIS Server
import os
import subprocess
import shutil
import sys
import time
from zipfile import ZipFile, BadZipFile

def run_powershell_command(command):
    """Run a PowerShell command and return the output and error."""
    try:
        result = subprocess.run(["powershell", "-Command", command], 
                                capture_output=True, text=True, shell=True)
        return result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return "", str(e)

def ensure_directory_exists(path):
    """Ensure a directory exists, creating it if necessary."""
    if not os.path.exists(path):
        os.makedirs(path)

def check_iis_app_pool_exists(site_name):
    """Check if an IIS Application Pool exists."""
    print(f"Checking if IIS Application Pool '{site_name}' exists...")
    command = f"""
    Import-Module WebAdministration
    if (Test-Path "IIS:\\AppPools\\{site_name}") {{ Write-Output "Exists" }} else {{ Write-Output "NotExists" }}
    """
    stdout, _ = run_powershell_command(command)
    return stdout.strip()

def create_iis_app_pool(site_name):
    """Create an IIS Application Pool."""
    print(f"Creating IIS Application Pool '{site_name}'...")
    command = f"""
    Import-Module WebAdministration
    New-WebAppPool -Name "{site_name}" | Out-Null
    Start-WebAppPool -Name "{site_name}"
    """
    run_powershell_command(command)

def check_iis_site_exists(site_name):
    """Check if an IIS Site exists."""
    print(f"Checking if IIS Site '{site_name}' exists...")
    command = f"""
    Import-Module WebAdministration
    $site = Get-Website -Name "{site_name}" -ErrorAction SilentlyContinue
    if ($site) {{ Write-Output "Exists" }} else {{ Write-Output "NotExists" }}
    """
    stdout, _ = run_powershell_command(command)
    return stdout.strip()

def create_iis_site(site_name, port_for_site):
    """Create an IIS Site."""
    print(f"Creating IIS Site '{site_name}' on port {port_for_site}...")
    physical_path = f"C:\\inetpub\\wwwroot\\{site_name}"
    command = f"""
    Import-Module WebAdministration
    New-Website -Name "{site_name}" -Port {port_for_site} -PhysicalPath "{physical_path}" -ApplicationPool "{site_name}" | Out-Null
    Start-Website -Name "{site_name}"
    """
    run_powershell_command(command)

def stop_iis_app_pool(site_name):
    """Stop an IIS Application Pool."""
    print(f"Stopping IIS Application Pool '{site_name}'...")
    command = f"""
    Import-Module WebAdministration
    Stop-WebAppPool -Name "{site_name}"
    """
    run_powershell_command(command)

def backup_file(src, dest):
    """Backup a file."""
    if os.path.exists(src):
        print(f"Backing up file from '{src}' to '{dest}'...")
        shutil.copy2(src, dest)

def backup_directory(src, dest):
    """Backup a directory."""
    if os.path.exists(src):
        print(f"Backing up directory from '{src}' to '{dest}'...")
        shutil.copytree(src, dest, dirs_exist_ok=True)

def remove_directory_contents(directory):
    """Remove all files and subdirectories from a directory."""
    print(f"Removing all contents of directory '{directory}'...")
    if os.path.exists(directory):
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            try:
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    # Remove read-only attribute if necessary
                    os.chmod(item_path, 0o777)
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path, onerror=handle_remove_readonly)
            except PermissionError as e:
                print(f"Permission error while deleting {item_path}: {e}")
            except Exception as e:
                print(f"Error while deleting {item_path}: {e}")

def handle_remove_readonly(func, path, exc_info):
    """Handle read-only files during shutil.rmtree."""
    if not os.access(path, os.W_OK):
        print(f"Removing read-only attribute: {path}")
        os.chmod(path, 0o777)  # Change the permissions to writable
        func(path)  # Retry the operation
    else:
        raise exc_info[1]

def download_artifact(script_path, site_name, latest_build_path):
    """Download the latest build artifact using a Python script."""
    print(f"Downloading the artifact using script '{script_path}' for site '{site_name}'...")
    try:
        command = f"python \"{script_path}\" \"{site_name}\""
        subprocess.run(command, cwd=latest_build_path, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error while running the artifact download script: {e}")
        raise

def wait_for_file(file_path, timeout=60):
    """Wait for a file to exist, with a timeout."""
    print(f"Waiting for file '{file_path}' to appear (timeout: {timeout} seconds)...")
    start_time = time.time()
    while not os.path.exists(file_path):
        if time.time() - start_time > timeout:
            raise FileNotFoundError(f"The file {file_path} did not appear within {timeout} seconds.")
        time.sleep(1)

def unzip_artifact(src, dest):
    """Unzip an artifact."""
    print(f"Unzipping artifact from '{src}' to '{dest}'...")
    if not os.path.exists(src):
        raise FileNotFoundError(f"The file {src} does not exist.")
    try:
        with ZipFile(src, 'r') as zip_ref:
            zip_ref.extractall(dest)
    except BadZipFile:
        raise ValueError(f"The file {src} is not a valid zip file.")

def start_iis_app_pool(site_name):
    """Start an IIS Application Pool."""
    print(f"Starting IIS Application Pool '{site_name}'...")
    command = f"""
    Import-Module WebAdministration
    Start-WebAppPool -Name "{site_name}"
    """
    run_powershell_command(command)

def start_iis_site(site_name):
    """Start an IIS Site."""
    print(f"Starting IIS Site '{site_name}'...")
    command = f"""
    Import-Module WebAdministration
    Start-Website -Name "{site_name}"
    """
    run_powershell_command(command)

def main(site_name, port_for_site):
    # Variables
    script_path = "C:\\Script\\script.py"
    backup_path = f"C:\\Backup-{site_name}"
    latest_build_path = "C:\\Latest_Build"
    site_directory = f"C:\\inetpub\\wwwroot\\{site_name}"
    config_file_path = os.path.join(site_directory, "web.config")
    logs_dir = os.path.join(site_directory, "logs")
    runtimes_dir = os.path.join(site_directory, "runtimes")
    latest_build_zip = os.path.join(latest_build_path, "latest_build.zip")

    print(f"Starting deployment for site '{site_name}' on port {port_for_site}...")

    # 1. Ensure Application Pool Exists
    if check_iis_app_pool_exists(site_name) == "NotExists":
        create_iis_app_pool(site_name)

    # 2. Ensure IIS Site Directory Exists
    ensure_directory_exists(site_directory)

    # 3. Check if IIS Site Exists
    if check_iis_site_exists(site_name) == "NotExists":
        create_iis_site(site_name, port_for_site)

    # 4. Stop IIS Application Pool
    stop_iis_app_pool(site_name)

    # 5. Backup Preparation
    ensure_directory_exists(backup_path)
    backup_file(config_file_path, backup_path)
    backup_directory(logs_dir, os.path.join(backup_path, "logs"))
    backup_directory(runtimes_dir, os.path.join(backup_path, "runtimes"))

    # 7. Clean Old Build
    remove_directory_contents(site_directory)

    # 8. Download & Deploy New Build
    ensure_directory_exists(latest_build_path)
    remove_directory_contents(latest_build_path)
    download_artifact(script_path, site_name, latest_build_path)

    # Wait for the zip file to appear
    try:
        wait_for_file(latest_build_zip, timeout=60)
    except FileNotFoundError as e:
        print(e)
        return

    # Check and unzip the artifact
    try:
        unzip_artifact(latest_build_zip, site_directory)
    except Exception as e:
        print(f"Error during unzipping: {e}")
        return

    # 9. Restore Configurations from Backup
    backup_file(os.path.join(backup_path, "web.config"), config_file_path)

    # 10. Restart IIS (App Pool + Site)
    start_iis_app_pool(site_name)
    start_iis_site(site_name)

    print(f"Deployment completed successfully for '{site_name}' on port {port_for_site}!")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <site_name> <port>")
        sys.exit(1)
    
    site_name = sys.argv[1]
    port_for_site = sys.argv[2]
    main(site_name, port_for_site)
