# Labseq

工业质量实验室（LIMS）：检验项目规格、样品收样、工作单、结果判定、仪器占用与报告草稿。

技术栈：Python / FastAPI / PostgreSQL / React / Vite。

## 启动

```bash
cd labseq
docker compose up --build
```

| 服务 | 地址 |
| --- | --- |
| 前端 | http://localhost:3200 |
| API | http://localhost:8200 |
| API 文档 | http://localhost:8200/docs |
| Postgres | localhost:5434 |

健康检查：`GET http://localhost:8200/api/health`

## 使用说明

1. 打开前端，选择实验室。
2. 在检验项目中维护规格限；在样品台账收样并勾选检验项。
3. 在工作单查看任务队列；在结果判定页录入测量值并查看 pass/fail/retest。
4. 在仪器页查看占用冲突；在报告页生成样品结论草稿。

种子数据含故意超标结果、未配置规格的检验项，以及仪器时段冲突，便于直接验证判定与冲突逻辑。

## 开发与测试

```bash
docker compose exec api pytest -q
```

## 目录结构

```
labseq/
├── backend/
├── frontend/
├── docker-compose.yml
└── README.md
```
