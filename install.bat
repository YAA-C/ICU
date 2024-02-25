@echo off
set req_python_version=3.10.0
for /f "delims=" %%i in ('py --version 2^>^&1') do set python_version=%%i

if not "%python_version%" == "Python %req_python_version%" (
    echo Install Python %req_python_version%
    exit
)

if not exist "venv\" (
    echo Creating Virtual Environment...
    py -m venv venv
)

call .\venv\Scripts\activate

echo Checking and downloading dependencies
pip install -q -r requirements.txt

echo Checking if Rust is installed
where rustc > nul 2>&1
if %errorlevel% neq 0 (
    echo Install Rust...
    exit
)

echo compile and build demoparserLib for current system
maturin develop --release --manifest-path=.\parser\demoparserLib\Cargo.toml

call deactivate

echo Setup completed Successfully...