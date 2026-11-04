# 动迹 · MoveLog

记录每一次出发。个人跑步、骑行、徒步和健身档案。

- 网站：https://leohc92.github.io/movelog/
- 仓库：https://github.com/Leohc92/movelog
- 本地目录：`~/Workspace/movelog`

## 开发与部署

```bash
pnpm install --frozen-lockfile
pnpm dev
PATH_PREFIX=/movelog pnpm build
```

推送 `master` 后由 GitHub Actions 部署。仓库 Settings → Pages 的 Source 应设为 GitHub Actions。

## COROS 数据

首次数据通过已连接的 COROS 导入。连接器每天最多导出 50 个 FIT 文件；尚未取得 FIT 的活动只显示概要，不生成或猜测轨迹。更早活动的轨迹可通过完整同步补齐。

配置每日自动同步：在仓库 Settings → Secrets and variables → Actions 中添加 Secrets `COROS_ACCOUNT`（登录邮箱）和 `COROS_PASSWORD`（登录密码），再设置 Variable `COROS_SYNC_ENABLED=true`。首次启用后可在 Actions → Run Data Sync 手动运行。此脚本使用 COROS 中国区接口，每天北京时间 08:00 同步并重新部署。

这里只向仓库提交 `src/static/activities.json`，原始 FIT 和 SQLite 数据库均忽略。已选择公开运动地点、GPS 轨迹及心率；发布的 JSON 文件可以被所有人访问。账号密码只放在 GitHub Secrets。

轨迹墙的 SVG 缩略图无需地图服务。交互底图需配置你自己的 Mapbox public token：本地 `.env.local` 中设置 `VITE_MAPBOX_TOKEN`；GitHub Actions 使用同名 Repository Variable。未配置时不显示底图。

`config.yml` 可调整语言、主题和运动目标；现有目标是模板默认值，按个人计划修改。

## 来源

基于 [zhaohongxuan/workouts](https://github.com/zhaohongxuan/workouts)，保留 MIT 许可证及原项目说明。

---

# Workout Log

基于 React + TypeScript + Tailwind CSS 构建的现代运动数据看板，支持跑步、骑行、徒步、健身等多种运动类型的可视化展示。

> 数据基于 [running_page](https://github.com/yihong0618/running_page) 项目同步 ， 脚本本项目的 run_page 文件夹下。
> 在线演示：[zhaohongxuan.github.io/workouts](http://zhaohongxuan.github.io/workouts)

<img width="1449" height="987" alt="image" src="https://github.com/user-attachments/assets/33c4eef1-0208-4d01-920b-3270633b7201" />

## 功能特性

- **活动热力图** — GitHub 风格的年度热力图，按运动类型区分颜色（跑步橙、骑行蓝、徒步绿、训练玫红），支持展开月度视图
- **轨迹墙** — SVG 路线缩略图墙，自动聚合相似路线，支持按年份筛选
- **路线地图** — Mapbox 驱动的交互式地图，展示所有 GPS 轨迹，支持全屏模式
- **个人最佳** — 5K / 10K / 半马 / 全马距离的 PR 记录
- **数据统计** — 年度、月度、周度目标及与同期对比
- **连续记录** — 连续打卡天数和周数，周历一览本周活动
- **活动记录** — 分页表格，支持年份和距离筛选
- **月度日历** — 展示每日运动公里数，hover 显示日期
- **健身记录** — 力量训练、综合训练等非有氧运动单独展示
- **双语支持** — 中文 / 英文一键切换
- **深色模式** — 跟随系统或手动切换
- **运动筛选** — 全部 / 跑步 / 骑行 / 徒步 / 健身 全局过滤

## 技术栈

| 类别 | 技术 |
|---|---|
| 框架 | React 18 + TypeScript |
| 构建 | Vite 6 |
| 样式 | Tailwind CSS v4 |
| 图表 | Recharts |
| 地图 | Mapbox GL + react-map-gl |
| 路线解码 | @mapbox/polyline |

## 快速开始

```bash
# 安装依赖
pnpm install

# 启动开发服务器
pnpm dev

# 生产构建
pnpm build

# 预览构建产物
pnpm preview
```

## 数据同步

活动数据通过 [running_page](https://github.com/yihong0618/running_page) 的同步脚本生成，存储为 `src/static/activities.json`，脚本位于本项目的 `run_page/` 目录下。

### 支持的数据源

| 数据源 | 脚本 | 认证方式 | 备注 |
|--------|------|----------|------|
| **Strava** | `strava_sync.py` | OAuth（Client ID / Secret / Refresh Token） | 支持全量同步 |
| **Strava（近期）** | `strava_sync_recent.py` | 同上，读取环境变量 | 仅同步最近 7 天，适合定时任务 |
| **Garmin（国际版）** | `garmin_sync.py` | Secret 字符串（由 `get_garmin_secret.py` 生成） | `--only-run` 可只同步跑步 |
| **Garmin（CN + 国际版）** | `garmin_sync_cn_global.py` | CN Secret + Global Secret 两个字符串 | 同时同步国区和国际区账号 |
| **Keep** | `keep_sync.py` | 手机号 + 密码 | 国内主流跑步 App |
| **Nike Run Club** | `nike_sync.py` | Access Token | 从 Nike App 抓取 token |
| **悦跑圈 JoyRun** | `joyrun_sync.py` | UID + Session ID | 从 App 抓包获取 |
| **COROS** | `coros_sync.py` | 账号邮箱 + 密码 | 高驰手表 |
| **行者 XingZhe** | `xingzhe_sync.py` | 账号 + 密码 | 骑行常用平台 |
| **咕咚 Codoon** | `codoon_sync.py` | HMAC 认证（账号体系） | 需从 App 抓取签名参数 |
| **OPPO Health** | `oppo_sync.py` | OAuth Refresh Token | OPPO 运动健康 |
| **本地 GPX 文件** | `gpx_sync.py` | 无需认证 | 将 GPX 文件放入配置的目录即可 |
| **本地 FIT 文件** | `fit_sync.py` | 无需认证 | 将 FIT 文件放入配置的目录即可 |

### Strava 快速开始

```bash
# 全量同步
python run_page/strava_sync.py CLIENT_ID CLIENT_SECRET REFRESH_TOKEN

# 增量同步（最近 7 天，适合配置为定时任务）
export STRAVA_CLIENT_ID=xxx
export STRAVA_CLIENT_SECRET=yyy
export STRAVA_REFRESH_TOKEN=zzz
python run_page/strava_sync_recent.py
```

### Garmin 快速开始

```bash
# 1. 先生成 secret 字符串（需要 Garmin 账号密码，只需执行一次）
python run_page/get_garmin_secret.py EMAIL PASSWORD
# 国区账号加上 --is-cn
python run_page/get_garmin_secret.py EMAIL PASSWORD --is-cn

# 2. 使用 secret 同步数据
python run_page/garmin_sync.py SECRET_STRING
```

> 完整的各平台接入说明请参考 [running_page 项目文档](https://github.com/yihong0618/running_page)。

## 个性化配置

编辑根目录 `config.yml` 即可完成个性化设置，无需改动源代码。

### 默认语言与主题

```yaml
# 默认语言：zh（中文）| en（英文）
locale: zh

# 默认主题：system（跟随系统）| light（浅色）| dark（深色）
theme: system
```

> 用户手动切换后，选择会保存在 `localStorage`，下次访问以用户选择为准。

### 运动目标

支持按运动类型分别设置年度 / 月度 / 周度目标。跑步、骑行、徒步的目标以 **km** 为单位；健身目标以**分钟**为单位，进度条和展示会自动切换为时长。

```yaml
goals:
  all:   { yearly: 2000, monthly: 150, weekly: 35,  unit: distance }
  Run:   { yearly: 1200, monthly: 100, weekly: 25,  unit: distance }
  Ride:  { yearly: 3000, monthly: 250, weekly: 60,  unit: distance }
  Hike:  { yearly: 300,  monthly: 25,  weekly: 6,   unit: distance }
  Gym:   { yearly: 6000, monthly: 600, weekly: 150, unit: time }   # 分钟
```


## 部署

项目通过 GitHub Actions 自动部署至 GitHub Pages，推送到 `master` 分支后自动触发构建，详见 `.github/workflows/gh-pages.yml`。


## 项目结构

```
src/
├── App.tsx                      # 应用入口与路由
├── i18n.ts                      # 中英文翻译字典
├── types.ts                     # TypeScript 类型定义
├── hooks/
│   ├── useActivities.ts         # 数据过滤与格式化工具
│   ├── useLocale.tsx            # 国际化 Context
│   └── useTheme.ts              # 深色/浅色模式
├── components/
│   ├── Header.tsx               # 顶部导航与运动类型筛选
│   ├── StatsCards.tsx           # 目标卡片与连续记录
│   ├── ProfileCard.tsx          # 个人数据摘要
│   ├── PersonalBest.tsx         # 个人最佳成绩
│   ├── ContributionHeatmap.tsx  # 年度活动热力图
│   ├── HeatmapPage.tsx          # 全年份热力图总览页
│   ├── ActivityLog.tsx          # 活动记录表格
│   ├── CalendarWidget.tsx       # 月度日历组件
│   ├── MonthlyChart.tsx         # 月度统计柱状图
│   ├── TrendCharts.tsx          # 趋势折线图
│   ├── RouteMap.tsx             # Mapbox 路线地图
│   └── TracksPage.tsx           # 轨迹墙页面
└── static/
    └── activities.json          # 活动数据（由 Python 脚本生成）
```


## 致谢

- [running_page](https://github.com/yihong0618/running_page) — 数据同步与原始项目灵感, @[yihong0618](https://github.com/yihong0618)
- [workouts_page](https://github.com/ben-29/workouts_page) — 多运动类型支持， @[ben-29](https://github.com/ben-29)
- [RUN.LOG](https://github.com/yihong0618/running_page/issues/12#issuecomment-3689275071) 给我的页面设计灵感

## License

MIT 

## 国家统计

每条活动的 `country_codes` 依据完整 GPS 轨迹与离线 Natural Earth 国界计算。跨国路线统计所有经过的国家；无 GPS 时只采用明确的国家或中国城市信息，不根据“徒步”“跑步”等通用名称推断国家。国家按主权国家去重，香港等地区计入所属国家；省级地区统计继续保留香港。

每日 COROS 同步会重新补齐地理字段。无需额外地图 API 请求。安装 `requirements-coros.txt` 后，可用 `python run_page/coros_geography.py` 对现有 JSON 补齐国家信息。

国界数据及来源校验信息位于 `run_page/geography/`，来源为 [Natural Earth Admin 0 Countries](https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-0-countries/)，属于公共领域；仅供运动足迹统计使用。
