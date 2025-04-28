import urllib.request
import os
import csv
import pandas as pd
import time
import subprocess
import glob

# Destination folder
dest_folder = "D:\\BenignPackagesTar"
os.makedirs(dest_folder, exist_ok=True)
filename = './FilteredBenignPackages.xlsx'
SuccessCount = 0
FailCount = 0
df = pd.read_excel(filename)

for index, row in df.iterrows():
    name = str(row.iloc[0]).strip()
    firstLetter = name[0].lower()
    pkgName = name.replace(" ", "")
    version = str(row.iloc[8]).strip().replace(" ", "")

    url = f"https://files.pythonhosted.org/packages/source/{firstLetter}/{pkgName}/{pkgName}-{version}.tar.gz"
    file_name = os.path.join(dest_folder, url.split("/")[-1])
    
    try:
        urllib.request.urlretrieve(url, file_name)
        print(f"Downloaded: {file_name}")
        SuccessCount += 1
    except Exception as e:
        print(f"failed to download {url}: {e}")
        whl_url = f"https://files.pythonhosted.org/packages/{firstLetter}/{pkgName}/{pkgName}-{version}-py3-none-any.whl"
        whl_file_name = os.path.join(dest_folder, f"{pkgName}-{version}.whl")

        try:
            urllib.request.urlretrieve(whl_url, whl_file_name)
            print(f"Downloaded: {whl_file_name}")

            print(f"Converting {whl_file_name} to .tar.gz...")
            subprocess.run(["wheel2tar", whl_file_name], check=True)
            converted_tar_file = whl_file_name.replace(".whl", ".tar.gz")
            if os.path.exists(converted_tar_file):
                os.rename(converted_tar_file, os.path.join(dest_folder, os.path.basename(converted_tar_file)))
                print(f"Converted and moved: {converted_tar_file}")
            SuccessCount += 1
        except Exception as e:
            print(f"Failed to download {whl_url}: {e}")

            try:
                print(f"Trying pip download for {pkgName}...")
                subprocess.run(["pip", "download", "--no-deps", "--verbose", "--no-binary=:all:", "--dest", dest_folder, f"{pkgName}=={version}"], check=True)
                print(f"Successfully downloaded {pkgName}-{version} via pip")
                SuccessCount += 1
            except subprocess.CalledProcessError as e:
                print(f"Failed to download {pkgName}-{version} using pip: {e}")
                FailCount += 1
        
print("Download process completed.")
print(f"Successfull downloads: {SuccessCount}")
print(f"Failed downloads: {FailCount}")
#Downloads packages in CSV file as tar balls


# File path






# Download the file

 
#Downloads packages in CSV file as tar balls


# File path






# Download the file

