# NOI 信竞板子库（规划稿）

本仓库用于构建面向 NOI 方向的算法模板（板子库），主要内容参考 [oi-wiki](https://oi-wiki.org/) 的知识体系，但会结合比赛使用习惯进行模板化整理。

## 目标
- 形成可复制粘贴的算法模板集合。
- 为每个模板提供适用场景、复杂度、注意事项。
- 提供索引文档，便于快速检索。

## 目录结构
```
.
├── README.md
├── docs/                  # 规划/索引/使用说明
├── templates/             # 板子代码
│   ├── data_structure/
│   ├── graph/
│   ├── string/
│   ├── math/
│   ├── geometry/
│   ├── dp/
│   └── misc/
├── notes/                 # 算法笔记/注意事项/复杂度
├── tests/                 # 模板验证用例
└── examples/              # 典型例题/用法示例
```

## 模板规范（执行标准）
- 每个模板文件头必须包含：
  - 适用场景
  - 时间/空间复杂度
  - 依赖与注意事项
- 模板函数命名清晰、参数一致（同类算法尽量统一接口）。
- 代码风格以简洁、可读、易复制为主。

## 迭代路线（NOI 方向）
详见 `docs/roadmap.md`。

## 本地与云端方案
详见 `docs/deployment.md` 与 `docs/local_cloud_plan.md`。

## UI 与索引
- 统一索引入口：`docs/index.md`
- UI 规划：`docs/ui.md`

## 快速启动
详见 `docs/quickstart.md`。

## 本地可运行程序
- 本地服务脚本：`scripts/serve.py`
- Windows 启动脚本：`scripts/serve.bat`
- UI 首页：`ui/index.html`
- OI-wiki 目录同步脚本：`scripts/sync_oiwiki_catalog.py`
