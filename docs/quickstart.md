# 快速启动

本项目无需编译；可直接打开 Markdown，或运行本地服务进行浏览。

## 本地启动（离线）
1) 克隆仓库或保持本地副本。  
2) 打开 `docs/index.md` 作为入口索引。  
3) 按分类进入 `templates/<分类>/<算法名>/README.md`。  

### 本地服务（可选）
```bash
python3 scripts/serve.py --port 8000 --open
```

## 云端启动（在线）
1) 将仓库推送至 GitHub / GitLab。  
2) 在仓库页面直接打开 `docs/index.md`。  
3) 按索引跳转到算法模块。  

## 用户板子发布
- 每个算法模块下使用 `users/<user>/` 存放个人板子。  
- 在对应模块的 `README.md` “用户板子”中登记入口。  
