# 🛠️ DTA STUDIO - AGENT WORKSPACE INSTRUCTIONS

## Quy tắc GitHub CI/CD & Silent Auto-Update
Tài liệu hướng dẫn quy trình đóng gói tự động qua GitHub Actions và phát hành bản mới `/update` đã được thiết lập tại [github_cicd_auto_update.md](file:///d:/DTA%20VideoUnify/.agents/rules/github_cicd_auto_update.md).

### Khi người dùng yêu cầu `/update` hoặc phát hành phiên bản mới:
1. Thực hiện `git add .` và `git commit -m "[Mô tả thay đổi]"`
2. Tăng tag phiên bản (ví dụ `git tag v2.0.1`)
3. Thực hiện `git push origin main --tags` để kích hoạt CI/CD Pipeline tự động đóng gói bộ cài `.exe` qua Public Release!
