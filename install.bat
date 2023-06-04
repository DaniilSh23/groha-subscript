set "current_path=%~dp0"

cd C:\
mkdir Python
cd Python
powershell -Command "(New-Object System.Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe', './python-3.10.0-amd64.exe')"
python-3.10.0-amd64.exe /passive

set PATH=%PATH%;C:\Python\Python310\;
echo Python3 has been added to the PATH variable.

powershell -Command "(Invoke-WebRequest https://bootstrap.pypa.io/get-pip.py -OutFile get-pip.py)"
python get-pip.py
echo Pip has been installed successfully.

cd %current_path%
python -m pip install -r requirements.txt
echo Dependencies has been installed successfully.