'''
by Lukas Chrostowski, 2015
written with the help of ChatGPT 4.o
'''


import os
import re
import requests
import zipfile
import shutil
import pathlib
import klayout.db as pya
import siepic_ebeam_pdk
from SiEPIC.utils import find_automated_measurement_labels
import matplotlib.pyplot as plt
import scipy.io

def extract_measurement_url():
    """
    Extracts the measurement data URL from the README.md file in the parent directory.
    
    Returns:
        str: The extracted URL with '/download' appended.
    
    Raises:
        FileNotFoundError: If README.md is not found.
        ValueError: If the required section or valid URL is not found.
        RuntimeError: If there is an error reading the file.
    """

    script_dir = os.path.dirname(os.path.abspath(__file__))
    readme_path = os.path.join(script_dir, '..', 'README.md')
    readme_path = os.path.abspath(readme_path)
    
    if not os.path.exists(readme_path):
        raise FileNotFoundError(f"README.md file not found at expected location: {readme_path}")
    
    try:
        with open(readme_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        for i, line in enumerate(lines):
            if line.strip() == "## Measurement data" and i + 1 < len(lines):
                url = lines[i + 1].strip()
                
                # Validate the URL format
                url_pattern = re.compile(r'^https?://[\w.-]+(:\d+)?/s/\w+$')
                if url_pattern.match(url):
                    return url + "/download"
                else:
                    raise ValueError("The line following '## Measurement data' is not a valid URL.")
        
        raise ValueError("'## Measurement data' section not found or does not contain a URL.")
    
    except Exception as e:
        raise RuntimeError(f"Error reading the README.md file: {e}")


def download_file(url, output_dir="downloaded_files"):
    """
    Downloads a file from the given URL and saves it to the specified output directory.
    
    Args:
        url (str): The URL to download from.
        output_dir (str): The directory where the file will be saved.
    
    Returns:
        str: The path to the downloaded file, or None if an error occurs.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        filename = os.path.join(output_dir, "downloaded_data.zip")
        with open(filename, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Downloaded file saved to {filename}")
        return filename
    
    except requests.RequestException as e:
        print(f"Error downloading file: {e}")
        return None

def unzip_and_clean(filename, output_dir):
    """
    Unzips a given ZIP file and copies all .mat files to a separate directory while maintaining folder structure.
    
    Args:
        filename (str): The path to the ZIP file.
        output_dir (str): The directory where files will be extracted.
        mat_files_dir (str): The directory where .mat files will be copied.
    """
    if filename and filename.endswith(".zip"):
        try:
            with zipfile.ZipFile(filename, 'r') as zip_ref:
                zip_ref.extractall(output_dir)
            print(f"Extracted contents of {filename} into {output_dir}")
            delete_unwanted_files(output_dir)
        except zipfile.BadZipFile:
            print("Downloaded file is not a valid ZIP archive.")

def delete_unwanted_files(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".csv") or file.endswith(".pdf"):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")


def unzip_and_copy_mat_files(filename, output_dir, mat_files_dir="mat_files"):
    if filename and filename.endswith(".zip"):
        try:
            with zipfile.ZipFile(filename, 'r') as zip_ref:
                zip_ref.extractall(output_dir)
            print(f"Extracted contents of {filename} into {output_dir}")
            copy_mat_files(output_dir, mat_files_dir)
        except zipfile.BadZipFile:
            print("Downloaded file is not a valid ZIP archive.")

def copy_mat_files(source_dir, destination_dir):
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    
    for root, _, files in os.walk(source_dir):
        mat_files = [file for file in files if file.lower().endswith(".mat")]
        if mat_files:
            relative_path = os.path.relpath(root, source_dir)
            destination_path = os.path.join(destination_dir, relative_path)
            pathlib.Path(destination_path).mkdir(parents=True, exist_ok=True)
            for file in mat_files:
                source_path = os.path.join(root, file)
                dest_file_path = os.path.join(destination_path, file)
                try:
                    shutil.copy2(source_path, dest_file_path)
                    print(f"Copied: \"{source_path}\" to \"{dest_file_path}\"")
                except Exception as e:
                    print(f"Error copying \"{source_path}\": {e}")



if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if 1:
        # Download, extract, copy .mat files
        try:
            url = extract_measurement_url()
            print(f"Extracted URL: {url}")
            download_path = os.path.join(script_dir,'downloaded')
            filename = download_file(url, output_dir=download_path)
            mat_path = os.path.join(script_dir,'mat_files')
            unzip_and_copy_mat_files(filename, download_path, mat_path)
        except Exception as e:
            print(f"Error: {e}")

    if 0:        
        # Download, extract, copy .mat files
        try:
            url = "https://stratus.ece.ubc.ca/s/kfHwqfkcxNEMgXs/download"  # Test URL
            print(f"Using test URL: {url}")
            download_path = os.path.join(script_dir,'downloaded')
            filename = download_file(url, output_dir=download_path)
            mat_path = os.path.join(script_dir,'mat_files')
            unzip_and_copy_mat_files(filename, download_path, mat_path)
            # unzip_and_clean(filename, "downloaded_files")
        except Exception as e:
            print(f"Error: {e}")

    if 0:
        # copy from local folder
        source_dir = '/Users/lukasc/Downloads/die_1'
        mat_path = os.path.join(script_dir,'mat_files')
        print(source_dir, mat_path)
        copy_mat_files(source_dir, mat_path)
        
