# Claw ERP

Python + Vue 进销存管理系统

## 技术栈

- **后端**: Python
- **前端**: Vue.js

## 项目结构

```
claw-erp/
├── backend/     # 后端服务
└── frontend/   # 前端应用
```

## 开发指南

### 后端 setup
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### 后端测试
```bash
cd backend
pytest
# 查看测试覆盖率
pytest --cov=. --cov-report=html
# 运行特定测试文件
pytest tests/test_auth.py
# 运行特定测试
pytest tests/test_auth.py::test_login_success
```

### 前端 setup
```bash
cd frontend
npm install
npm run dev
```
