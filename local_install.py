import os
import subprocess
import platform

def run_script(script_path):
    """运行指定的脚本"""
    try:
        result = subprocess.run([script_path], check=True, shell=True)
        print(f"Successfully ran {script_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running {script_path}: {e}")
        exit(1)

def main():
    """根据操作系统运行相应的脚本"""
    os_type = platform.system()

    if os_type == "Linux":
        # 运行 install.sh 脚本
        script_path = "./install.sh"
        if not os.path.isfile(script_path):
            print("Error: install.sh not found. Please ensure it is in the current directory.")
            exit(1)
        run_script(script_path)
    elif os_type == "Windows":
        # 运行 install.ps1 脚本
        script_path = ".\\install.ps1"
        if not os.path.isfile(script_path):
            print("Error: install.ps1 not found. Please ensure it is in the current directory.")
            exit(1)
        # 使用 PowerShell 执行 PowerShell 脚本
        try:
            result = subprocess.run(["powershell", "-ExecutionPolicy", "RemoteSigned", "-File", script_path], check=True)
            print(f"Successfully ran {script_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while running {script_path}: {e}")
            exit(1)
    else:
        print("Unsupported operating system.")
        exit(1)

if __name__ == "__main__":
    main()
