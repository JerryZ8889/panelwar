# 美伊局势看板

实时聚合美伊冲突相关市场指标的单页看板，涵盖能源、避险资产、军工、航运、中东市场等 27+ 项指标，配合 Polymarket 停战概率和四层因果分析框架，辅助判断局势走向与交易方向。

**在线访问：[warpanel.sophia.beer](https://warpanel.sophia.beer)**

## 功能

- **27+ 市场指标** — VIX、原油、黄金、美股、军工、航运、中东 ETF 等，含近 1 月迷你 K 线图
- **Polymarket 停战预测** — 实时抓取市场对停火概率的定价
- **综合分析面板** — 风险等级、经济体制判定（滞胀/衰退/正常化）、情景概率推演、操作建议、拐点监控
- **移动端适配** — Header 滚动自动收起，响应式卡片布局

## 技术栈

| 层 | 技术 |
|---|------|
| 前端 | 单页 HTML + CSS + JS（无框架），Chart.js |
| 后端 | Python FastAPI |
| 数据源 | Yahoo Finance (yfinance)、Polymarket Gamma API、AKShare |
| 存储 | SQLite（5 分钟缓存，保留最近 5 条快照） |
| 部署 | Vercel Serverless |

## 本地运行

```bash
pip install -r requirements.txt
cd backend
python main.py
# 打开 http://localhost:8000
```

## 项目结构

```
├── api/                # FastAPI 后端（Vercel serverless 共用）
│   ├── index.py        # API 入口 + 路由
│   ├── data_fetcher.py # Yahoo Finance 数据获取
│   ├── polymarket.py   # Polymarket API 对接
│   ├── analyzer.py     # 四层因果分析引擎
│   └── database.py     # SQLite 缓存
├── public/
│   └── index.html      # 单页看板
├── backend/
│   └── main.py         # 本地开发入口
└── DESIGN.md           # 详细设计文档
```

## 数据说明

所有数据来自公开免费 API，5 分钟后端缓存防止限流。**仅供参考，不构成投资建议。**

## 许可证

[Apache License 2.0](LICENSE)
