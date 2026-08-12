# BẢN CHỈ DẪN KỸ THUẬT DÙNG CHUNG FOR ANTIGRAVITY AGENT
## Thiết lập Hệ thống Đóng gói Tự động (GitHub Actions) & Cơ chế Silent Auto-Update

### Mục đích:
- Chỉ dẫn cho AI Agent (Antigravity) tự động kết nối GitHub, tạo Repo Private/Public và thiết lập CI/CD Pipeline.
- Áp dụng cho mọi ứng dụng Python Desktop (DTA AutoDown, DTA VideoUnify Pro, DTA Voice Pro,...)
- Bảo mật: Mã nguồn nằm hoàn toàn ở Private Repo. Chỉ công khai tệp Bộ cài/Cập nhật (.exe) ở Public Repo.

---

### 📌 CHỈ THỊ CHO ANTIGRAVITY AGENT:
Khi người dùng yêu cầu triển khai dự án này lên GitHub hoặc gõ `/update`, hãy đọc tài liệu chỉ dẫn này và thực hiện tuần tự các lệnh CLI, tạo thư mục, cấu hình Secrets và tạo tệp CI/CD Workflows mà không cần hỏi lại người dùng từng bước nhỏ.

#### 1. MÔ HÌNH BẢO MẬT VÀ PHÂN CHIA REPO
Hệ thống tự động hoạt động dựa trên mô hình liên kết giữa 2 Repository tách biệt hoàn toàn:

| Loại Repo | Quyền truy cập | Chức năng & Nhiệm vụ |
| :--- | :--- | :--- |
| **Private Repo** | Riêng tư (Chỉ chủ sở hữu) | Lưu trữ toàn bộ mã nguồn gốc (.py), assets nội bộ, file cấu hình phát triển. |
| **Public Repo** | Công khai (Cho Client) | Chứa GitHub Actions Runner đóng gói tệp .exe và lưu trữ các bản phát hành (Releases). |

#### 2. BƯỚC 1: KHỞI TẠO REPO VÀ CẤU HÌNH GITHUB CLI
Antigravity cần sử dụng công cụ `gh` (GitHub CLI) để thực hiện tự động hóa:
```bash
# 1. Kiểm tra đăng nhập GitHub CLI
gh auth status

# 2. Định nghĩa tên 2 Repo
PRIVATE_REPO="DTA-VideoUnify-Core"
PUBLIC_REPO="DTA-VideoUnify-Releases"

# 3. Tạo Private Repo chứa Mã Nguồn
gh repo create $PRIVATE_REPO --private --confirm

# 4. Tạo Public Repo chứa File Đóng Gói .exe & Release
gh repo create $PUBLIC_REPO --public --confirm
```

#### 3. BƯỚC 2: CẤU HÌNH ACCESS TOKEN VÀ SECRETS
- Tạo GitHub Personal Access Token (Fine-grained hoặc Classic Token) có quyền repo.
- Thêm Token này vào Secrets của Private Repo với tên: `PUBLIC_REPO_TRIGGER_TOKEN`.
- Thêm Token có quyền đọc vào Public Repo với tên: `PRIVATE_REPO_READ_TOKEN`.
```bash
# Thêm Secret vào Private Repo bằng CLI
gh secret set PUBLIC_REPO_TRIGGER_TOKEN --body "GH_PAT_TOKEN_HERE" --repo $PRIVATE_REPO

# Thêm Secret vào Public Repo bằng CLI
gh secret set PRIVATE_REPO_READ_TOKEN --body "GH_PAT_TOKEN_HERE" --repo $PUBLIC_REPO
```

#### 4. BƯỚC 3: TẠO WORKFLOW TRIGGER TẠI PRIVATE REPO (`.github/workflows/trigger_build.yml`)
```yaml
name: Trigger Public Build

on:
  push:
    tags:
      - 'v*'

jobs:
  dispatch:
    runs-on: ubuntu-latest
    steps:
      - name: Send Repository Dispatch Event
        uses: peter-evans/repository-dispatch@v3
        with:
          token: ${{ secrets.PUBLIC_REPO_TRIGGER_TOKEN }}
          repository: TruongAnh2706/DTA-VideoUnify-Releases
          event-type: build-exe-release
          client-payload: '{"version": "${{ github.ref_name }}"}'
```

#### 5. BƯỚC 4: TẠO WORKFLOW BUILD & RELEASE TẠI PUBLIC REPO (`.github/workflows/build_release.yml`)
```yaml
name: Package and Release App

on:
  repository_dispatch:
    types: [build-exe-release]

jobs:
  build-and-release:
    runs-on: windows-latest

    steps:
      - name: Checkout Code from Private Repo
        uses: actions/checkout@v4
        with:
          repository: TruongAnh2706/DTA-VideoUnify-Core
          token: ${{ secrets.PRIVATE_REPO_READ_TOKEN }}
          ref: ${{ github.event.client_payload.version }}

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Dependencies
        run: |
          pip install -r requirements.txt
          pip install pyinstaller

      - name: Build Executable with PyInstaller
        run: |
          pyinstaller --noconfirm --onedir --windowed --name "DTA_VideoUnify_Pro" main.py

      - name: Setup Inno Setup
        uses: aminya/setup-innosetup@v2

      - name: Compile Inno Setup Installer
        run: |
          iscc setup_script.iss /DAppVersion=${{ github.event.client_payload.version }}

      - name: Publish to GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          tag_name: ${{ github.event.client_payload.version }}
          name: "Release ${{ github.event.client_payload.version }}"
          files: Output/DTA_VideoUnify_Pro_Setup.exe
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

#### 6. BƯỚC 5: TÍNH NĂNG SILENT AUTO-UPDATE TRÊN CLIENT APP
Chèn đoạn mã kiểm tra Cập nhật ngầm này vào màn hình Splash Screen hoặc luồng khởi động chính của ứng dụng Desktop:
```python
import sys
import os
import requests
import subprocess
from packaging import version

CURRENT_VERSION = "2.0.0"
PUBLIC_REPO = "TruongAnh2706/DTA-VideoUnify-Releases"

def check_for_updates():
    try:
        url = f"https://api.github.com/repos/{PUBLIC_REPO}/releases/latest"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            latest_ver = data["tag_name"].lstrip("v")
            
            if version.parse(latest_ver) > version.parse(CURRENT_VERSION):
                for asset in data.get("assets", []):
                    if asset["name"].endswith(".exe"):
                        return True, latest_ver, asset["browser_download_url"]
    except Exception as e:
        print(f"Update Check Error: {e}")
    return False, CURRENT_VERSION, None

def perform_silent_update(download_url):
    temp_dir = os.getenv("TEMP")
    installer_path = os.path.join(temp_dir, "update_installer.exe")
    
    # 1. Tải bản cài đặt mới ngầm
    res = requests.get(download_url, stream=True)
    with open(installer_path, "wb") as f:
        for chunk in res.iter_content(chunk_size=8192):
            f.write(chunk)
            
    # 2. Tạo kịch bản Batch thực thi ngầm sau khi thoát App
    bat_path = os.path.join(temp_dir, "silent_updater.bat")
    batch_script_content = f'''@echo off
timeout /t 2 /nobreak > nul
"{installer_path}" /VERYSILENT /SUPPRESSMSGBOXES /NORESTART
start "" "{sys.executable}"
del "%~f0"
'''
    with open(bat_path, "w") as f:
        f.write(batch_script_content)
    
    # 3. Chạy script và đóng ứng dụng hiện tại
    subprocess.Popen(["cmd.exe", "/c", bat_path], creationflags=subprocess.CREATE_NO_WINDOW)
    sys.exit(0)
```

#### 7. QUY TRÌNH PHÁT HÀNH BẢN MỚI (KHI DÙNG /update)
Khi người dùng gõ `/update` hoặc yêu cầu cập nhật bản mới:
```bash
# 1. Commit code đã sửa
git add .
git commit -m "Update feature and optimize logic"

# 2. Đánh Tag phiên bản mới (Trùng với CURRENT_VERSION trong code)
git tag v2.0.1

# 3. Push lên Private Repo (Hệ thống sẽ tự chạy đóng gói ngầm sang Public Repo)
git push origin main --tags
```
