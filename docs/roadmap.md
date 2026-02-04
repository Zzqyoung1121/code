# NOI 板子库建设大纲（对齐 oi-wiki 分类）

本大纲按 oi-wiki 的分类组织，不再分阶段；所有内容统一维护在相应分类下。

## 目录与模块规则
- 每个算法小模块必须包含三部分：
  1) 算法名称  
  2) 例题（可选）  
  3) 用户板子（每个用户可发布自己的模板/专栏）
- 模块建议落地为：`templates/<分类>/<算法名>/`，其中包含：
  - `README.md`（算法名称 + 例题 + 用户板子入口）
  - `users/<user>/`（用户板子模板）

## 基础（Basic）
- 二分
- 前缀和 / 差分
- 双指针

## 数据结构（Data Structure）
- 并查集
- 树状数组
- 线段树（含懒标记）
- Trie

## 图论（Graph Theory）
- BFS / DFS
- 最短路（Dijkstra / SPFA / 0-1 BFS）
- 最小生成树（Kruskal / Prim）
- 拓扑排序
- LCA
- Tarjan（SCC / 割点 / 桥）
- 网络流（Dinic）
- 最小费用最大流

## 数学（Math）
- 快速幂
- 扩展欧几里得
- 逆元与组合数
- 线性筛
- 质因数分解
- CRT
- NTT / FFT
- 矩阵快速幂

## 字符串（String）
- KMP
- 哈希
- AC 自动机

## 动态规划（Dynamic Programming）
- 常见区间 DP / 树形 DP 模板

## 计算几何（Geometry）
- 叉积 / 线段相交
- 凸包

## 模板文件约定
- 文件命名：`algo_name.cpp` 或 `algo_name.hpp`
- 文件头注释必须包含：
  - 适用场景
  - 复杂度
  - 注意事项
