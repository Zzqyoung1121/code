# Homework OCR Tracker (Mini Program Backend)

这是一个配套小程序的后端 MVP，用于：
- 录入班级名单
- 创建作业任务
- 上传作业本照片
- OCR 识别（演示版：需传入识别文本）
- 确认提交状态
- 生成作业统计报表

## 目录结构
```
backend/
  app/
    main.py
    db.py
    models.py
    schemas.py
  data/
    images/
  requirements.txt
```

## 运行方式
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

启动后访问：`http://127.0.0.1:8000/docs`

## OCR 服务配置
默认是演示模式，需要在调用 `/ocr/recognize` 时传入 `recognized_text`。若要启用真实 OCR：

### 1) 百度 OCR
```bash
export OCR_PROVIDER=baidu
export BAIDU_API_KEY=你的百度API_KEY
export BAIDU_SECRET_KEY=你的百度SECRET_KEY
```

### 2) 腾讯 OCR
```bash
export OCR_PROVIDER=tencent
export TENCENT_SECRET_ID=你的SECRET_ID
export TENCENT_SECRET_KEY=你的SECRET_KEY
export TENCENT_REGION=ap-beijing
```

### 3) 自建 OCR 服务（PaddleOCR）
运行自建 OCR 服务（端口 9000）：
```bash
cd ocr_service
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 9000
```

后端使用自建 OCR：
```bash
export OCR_PROVIDER=self_hosted
export OCR_SERVICE_URL=http://127.0.0.1:9000/ocr
```

启用后，`/ocr/recognize` 会根据图片自动识别文字，无需传入 `recognized_text`。

## 小程序端（原生微信小程序）
小程序代码位于 `miniprogram/`。在微信开发者工具中打开该目录即可预览。

### 基本配置
- 修改 `miniprogram/app.js` 中的 `baseUrl` 指向后端服务地址。
- API 流程：创建班级 → 导入名单 → 创建作业 → 上传照片 → OCR 识别 → 确认 → 报表。

主要页面：
- 首页：任务概览与入口
- 班级与名单：创建班级 + CSV 导入
- 作业任务：创建作业任务
- 拍照上传：批量上传作业本照片
- 识别确认：OCR 识别 + 确认提交
- 作业统计：查看统计报表

## 使用说明（API 流程）
1. 创建班级
```bash
curl -X POST http://127.0.0.1:8000/classes \
  -H "Content-Type: application/json" \
  -d '{"name":"三年二班"}'
```

2. 导入名单（CSV 文件，字段示例：`name,student_number`）
```bash
curl -X POST "http://127.0.0.1:8000/students/import?class_id=1" \
  -F "file=@students.csv"
```

3. 创建作业任务
```bash
curl -X POST http://127.0.0.1:8000/homework_tasks \
  -H "Content-Type: application/json" \
  -d '{"class_id":1,"subject":"语文","notes":"第3课习题"}'
```

4. 上传作业本照片
```bash
curl -X POST "http://127.0.0.1:8000/images/upload?class_id=1" \
  -F "file=@cover.jpg"
```

5. OCR 识别（演示版本，需要传入 recognized_text）
```bash
curl -X POST http://127.0.0.1:8000/ocr/recognize \
  -H "Content-Type: application/json" \
  -d '{"class_id":1,"image_id":1,"recognized_text":"张三"}'
```

6. 确认提交状态
```bash
curl -X POST http://127.0.0.1:8000/submissions/confirm \
  -H "Content-Type: application/json" \
  -d '{"task_id":1,"student_id":1,"image_id":1,"status":"submitted"}'
```

7. 获取作业统计报表
```bash
curl http://127.0.0.1:8000/reports/homework/1
```

## 下一步建议
- 接入真实 OCR 服务（PaddleOCR/第三方 API）
- 小程序端实现批量拍照、识别确认和统计导出
- 权限与隐私控制、对象存储与 CDN 优化
