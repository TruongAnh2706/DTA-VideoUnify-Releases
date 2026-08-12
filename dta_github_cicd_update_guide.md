# 🚀 HƯỚNG DẪN TỰ ĐỘNG HÓA GITHUB CI/CD & SILENT AUTO-UPDATE DTA VIDEOUNIFY PRO

**Phát triển bởi:** DTA Studio - Chủ quản: Đức Trường  
**SĐT/Zalo:** 0962.775.506 | **Email:** ductruong.onl@gmail.com  
**Website:** [https://dta-studio.vercel.app/](https://dta-studio.vercel.app/)

---

## 📌 OVERVIEW (TỔNG QUAN HỆ THỐNG CẬP NHẬT)
Hệ thống **Silent Auto-Update Engine** của **DTA VideoUnify Pro** được thiết kế dựa trên tiêu chuẩn kiến trúc ứng dụng Desktop mới nhất của **DTA Studio** (đồng bộ với DTA DownDrama và DTA EditSub):

1. **GitHub Repository Công Khai**:
   - `TruongAnh2706/DTA-VideoUnify-Releases`
2. **Cơ Chế Kiểm Tra Cập Nhật Ngầm (Silent Checking)**:
   - Khi mở app, ứng dụng chạy một QThread ngầm gọi API `https://api.github.com/repos/TruongAnh2706/DTA-VideoUnify-Releases/releases/latest`.
   - So sánh `tag_name` (ví dụ `v2.0.1`) với `CURRENT_VERSION` trong app (`2.0.0`) sử dụng thư viện `packaging.version`.
3. **Cơ Chế Tải & Nâng Cấp Ngầm (Silent Upgrade)**:
   - Tải file `DTA_VideoUnify_Pro_Setup.exe` mới nhất vào thư mục tạm `%TEMP%`.
   - Tự động tạo và thực thi script `silent_unify_updater.bat` khởi chạy Inno Setup Installer ở chế độ im lặng:
     `"DTA_VideoUnify_Pro_Update_Setup.exe" /VERYSILENT /SUPPRESSMSGBOXES /NORESTART`
   - Thoát app cũ, Inno Setup ghi đè bản mới và bật lại phần mềm tức thì cho người dùng.

---

## 🛠️ QUY TRÌNH PHÁT HÀNH BẢN CẬP NHẬT MỚI (RELEASE WORKFLOW)

Khi anh Đức Trường muốn phát hành một phiên bản nâng cấp mới (ví dụ **v2.0.1**):

### Bước 1: Cập Nhật Version Trong Mã Nguồn
Trong file `config.py`:
```python
APP_VERSION = "2.0.1"
```

### Bước 2: Đóng Gói Bộ Cài Inno Setup Mới
Chạy lệnh biên dịch PyInstaller & Inno Setup Compiler (`ISCC.exe`):
```powershell
pyinstaller --noconfirm --onedir --windowed --icon=logo.ico --name="DTA_VideoUnify_Pro" --add-data="logo.png;." --add-data="logo.ico;." main.py
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" "setup_script.iss"
```
Kết quả tạo ra bộ cài `Output\DTA_VideoUnify_Pro_Setup.exe`.

### Bước 3: Tạo Release Trên GitHub (`TruongAnh2706/DTA-VideoUnify-Releases`)
1. Truy cập repo GitHub: `https://github.com/TruongAnh2706/DTA-VideoUnify-Releases/releases/new`
2. Đặt **Tag version**: `v2.0.1` (có chữ `v` ở đầu).
3. Đặt **Release title**: `DTA VideoUnify Pro v2.0.1 Enterprise`
4. Viết **Description / Changelog** những tính năng mới.
5. **Kéo thả đính kèm file**: `DTA_VideoUnify_Pro_Setup.exe` vào mục Attach binaries.
6. Nhấn **Publish Release**.

---

## 🎯 KẾT QUẢ VÀ TRẢI NGHIỆM NGƯỜI DÙNG

- Tất cả người dùng đang mở **DTA VideoUnify Pro** trên toàn quốc sẽ lập tức nhận được thông báo cập nhật rực rỡ.
- Người dùng chỉ cần bấm nút **`🚀 CẬP NHẬT NGAY (SILENT UPDATE)`**, phần mềm sẽ tự nâng cấp 100% tự động mà không cần thao tác gỡ cài đặt hay tải thủ công!
