import os
import subprocess
import platform
import requests
from bs4 import BeautifulSoup
import re
import sys
import importlib

# Function to check if packages are installed, and install if not
def check_and_install_packages(packages):
    for package in packages:
        try:
            importlib.import_module(package)
            print(f"{package} is already installed.")
        except ImportError:
            print(f"{package} is not installed. Installing now...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Function to check the installed version of .NET
def check_dotnet_installed():
    try:
        result = subprocess.run(["dotnet", "--version"], check=True, capture_output=True, text=True)
        installed_version = result.stdout.strip()
        print(f".NET SDK is installed, version: {installed_version}")
        return installed_version
    except subprocess.CalledProcessError:
        print(".NET SDK is not installed.")
        return None

# Function to fetch the latest .NET version by scraping the official website
def get_latest_dotnet_version():
    try:
        print("Fetching latest .NET version...")
        url = "https://dotnet.microsoft.com/en-us/download/dotnet"
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Regex to match version numbers like 6.0, 7.0, 8.0, etc.
            version_pattern = re.compile(r'\d+\.\d+')
            
            # Find the anchor tags where the version numbers are mentioned
            version_tags = soup.find_all('a', href=True, text=version_pattern)

            if version_tags:
                # Extract the first match (the latest version)
                latest_version = version_pattern.search(version_tags[0].text).group()
                print(f"Latest .NET SDK version available: {latest_version}")
                return latest_version
            else:
                print("Could not find any version information.")
                return None
        else:
            print(f"Failed to fetch the latest version. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching latest .NET version: {str(e)}")
        return None

# Compare installed version with the latest version
def compare_versions(installed_version, latest_version):
    if installed_version and installed_version.startswith(latest_version):
        print("You are already using the latest version of .NET.")
        return True
    else:
        print(f"A newer version ({latest_version}) is available. Updating...")
        return False

# Install the latest .NET SDK
def install_latest_dotnet(version):
    os_type = platform.system()
    
    if os_type == "Linux":
        print(f"Installing .NET SDK {version} for Linux...")
        subprocess.run(["sudo", "apt-get", "update"], check=True)
        subprocess.run(["sudo", "apt-get", "install", "-y", f"dotnet-sdk-{version}"], check=True)
    
    elif os_type == "Darwin":
        print(f"Installing .NET SDK {version} for macOS...")
        subprocess.run(["brew", "update"], check=True)
        subprocess.run(["brew", "install", "--cask", f"dotnet-sdk-{version}"], check=True)
    
    elif os_type == "Windows":
        print(f"Please install .NET SDK {version} manually from https://dotnet.microsoft.com/download/dotnet/{version}")
        subprocess.run(["start", f"https://dotnet.microsoft.com/download/dotnet/{version}"], shell=True)
    else:
        print(f"Unsupported OS: {os_type}")
        sys.exit(1)

# Main function to set up dnSpy with .NET check and update
def setup_dnspy():
    # Check if required packages are installed
    required_packages = ["requests", "beautifulsoup4", "re"]
    check_and_install_packages(required_packages)
    
    installed_version = check_dotnet_installed()
    latest_version = get_latest_dotnet_version()

    if latest_version and not compare_versions(installed_version, latest_version):
        install_latest_dotnet(latest_version)
    
    clone_dnspy_repo()
    build_dnspy()
    create_readme(latest_version)

# Cloning dnSpy repository
def clone_dnspy_repo():
    repo_url = "https://github.com/dnSpyEx/dnSpy.git"
    destination = "dnSpy"
    if not os.path.exists(destination):
        print("Cloning dnSpy repository...")
        subprocess.run(["git", "clone", repo_url], check=True)
    else:
        print("dnSpy repository already exists. Skipping cloning.")

# Building dnSpy using .NET
def build_dnspy():
    os.chdir("dnSpy")
    print("Building dnSpy...")
    subprocess.run(["dotnet", "build"], check=True)

# Create a README file with dynamic .NET version
def create_readme(version):
    readme_content = f"""
# dnSpy Setup Script

This script will automate the process of downloading and setting up dnSpy.

## Steps:
1. Clone the dnSpy repository.
2. Install the .NET SDK (v{version} or latest).
3. Build dnSpy.

## How to Use:
1. Run the script:
    ```bash
    python dnspy_setup.py
    ```
2. After building, you'll find the dnSpy binaries in the `dnSpy/bin/Debug/net{version}-windows/` folder.
3. Follow dnSpy's official documentation for further usage: https://github.com/dnSpyEx/dnSpy

Enjoy reverse engineering!
"""
    with open("README.md", "w") as readme_file:
        readme_file.write(readme_content)
    print(f"README file created with .NET version {version}.")

# Main function execution
if __name__ == "__main__":
    setup_dnspy()
