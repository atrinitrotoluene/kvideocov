# OuonnkiTV → KVideo 视频源自动转换

自动将 [OuonnkiTV](https://github.com/Ouonnki/OuonnkiTV) 订阅源格式转为 [KVideo](https://github.com/KuekHaoYang/KVideo) 视频源格式，每天 UTC 22:00（北京时间 06:00）自动更新。

## 输出效果

转换后的文件 [kvideo_sources.json](kvideo_sources.json) 是一个可直接被 KVideo 使用的视频源 JSON 数组：

```json
[
  {
    "id": "iqiyizyapi-com",
    "name": "爱奇艺",
    "baseUrl": "https://iqiyizyapi.com/api.php/provide/vod",
    "group": "normal",
    "enabled": true,
    "priority": 1
  },
  {
    "id": "dbzy-tv",
    "name": "豆瓣资源",
    "baseUrl": "https://caiji.dbzy5.com/api.php/provide/vod",
    "group": "normal",
    "enabled": true,
    "priority": 2
  }
]
```

## 在 KVideo 中使用

### 方式一：环境变量订阅（推荐部署时使用）

部署 KVideo 时设置环境变量，让 KVideo 自动拉取本仓库生成的文件：

```bash
# 将 <USER> 和 <REPO> 替换为你的 GitHub 用户名和仓库名
SUBSCRIPTION_SOURCES='[{"name":"OuonnkiTV源","url":"https://raw.githubusercontent.com/<USER>/<REPO>/main/kvideo_sources.json"}]'
```

### 方式二：Web UI 手动导入

1. 打开 KVideo → 设置 → 数据管理 → 导入设置
2. 在 **订阅管理** 中添加：
   - **名称**：OuonnkiTV 源
   - **链接**：`https://raw.githubusercontent.com/<USER>/<REPO>/main/kvideo_sources.json`
3. 点击"获取"即可自动导入全部视频源

### 方式三：JSON 直接导入

将 [kvideo_sources.json](kvideo_sources.json) 的内容直接复制粘贴到 KVideo 的 JSON 批量导入框中。

## 本地使用

```bash
# 从默认源抓取并转换
python ouonnkitv2kvideo.py --fetch -o kvideo_sources.json

# 从自定义 URL 抓取
python ouonnkitv2kvideo.py --fetch https://example.com/sources.json -o output.json

# 转换本地 JSON 文件
python ouonnkitv2kvideo.py input.json -o output.json

# 仅输出到终端
python ouonnkitv2kvideo.py input.json --stdout

# 指定分组
python ouonnkitv2kvideo.py --fetch --group premium -o output.json
```

## 字段映射

| OuonnkiTV | → | KVideo | 说明 |
|-----------|:---:|--------|------|
| `name` | → | `name` | 视频源名称 |
| `url` | → | `baseUrl` | API 地址 |
| `isEnabled` | → | `enabled` | 是否启用 |
| `id` | → | `id` | 唯一标识（无则自动生成） |
| — | → | `group` | 固定为 `normal` |
| — | → | `priority` | 从 1 自增 |

## 手动触发更新

在 GitHub 仓库页面点击 **Actions** → **Daily Convert OuonnkiTV → KVideo** → **Run workflow** 即可立即执行一次转换。
