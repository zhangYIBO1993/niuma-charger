# niuma-charger · 牛马充电器

[SwiftBar](https://swiftbar.app) 上班鼓励器 —— 菜单栏里的打工人充电面板。工作日自动上线，休息日自动下班。

![screenshot](screenshots/demo.png)

## 功能

- **四状态感知**：上班前倒计时 / 上班中充电 / 已下班结算 / 休息日休眠
- **实时工资**：今日已赚按分钟累计，附时薪 / 分薪 / 秒薪（月薪 ÷ 21.75 ÷ 每日工时）
- **充电进度条**：20 格——绿色已充、黄色 ⚡ 在充电前沿、灰色未充，下班时满格
- **108 条语料**：打工人自嘲 / 温柔夸夸 / 轻鸡汤混合轮换，每小时换一条，菜单里可手动换
- **中国节假日感知**：内置 2026 官方放假 + 调休补班表，双休与法定节假日自动切休息模式，调休补班日正常开工并标注

## 安装

```bash
# 1. 安装 SwiftBar：https://swiftbar.app
# 2. 放入插件并赋执行权限
cp encourage.1m.py ~/Library/Application\ Support/SwiftBar/Plugins/
chmod +x ~/Library/Application\ Support/SwiftBar/Plugins/encourage.1m.py
# 3. 写入配置（月薪必填）
mkdir -p ~/.config/swiftbar
cp encourage.json.example ~/.config/swiftbar/encourage.json
# 编辑填上你的月薪，SwiftBar 一分钟内自动加载
```

## 配置 `~/.config/swiftbar/encourage.json`

| 键 | 默认 | 说明 |
|---|---|---|
| `salary` | `0` | 月薪（元）；为 0 时隐藏工资相关行，其余功能照常 |
| `start` | `09:00` | 上班时间，倒计时起点 |
| `end` | `18:00` | 下班时间，倒计时终点 |

## 节假日表更新

每年 10–11 月国务院办公厅发布次年放假安排后，在脚本 `TABLES` 里按年份追加节假日区间与调休补班日即可，无需改逻辑。表外年份自动退化为「周末休 / 平日上」，菜单下拉中会提示待更新。当前数据来源：国办发明电〔2025〕7 号《关于 2026 年部分节假日安排的通知》。

## 开发

```bash
python3 encourage.1m.py --selftest  # 离线自检：日历/工资/进度条/语料不变量
python3 encourage.1m.py             # 手动渲染一次菜单输出
```

纯 Python 标准库实现，无第三方依赖，macOS 菜单栏原生渲染（SwiftBar 插件协议 + ANSI 着色）。

## 致谢

- 灵感来自「上班鼓励机」类产品（实时工资 + 下班倒计时 + 鼓励语录）
- 语料风格参考了社媒上流传的打工人文案趋势（改写而非逐字搬运，来源链接见脚本注释）：牛马文案合集、「确诊为马」、小红书「小跨一步，大夸一场」、夸夸 / 反内耗、离线休息权等
- 节假日数据来自国务院办公厅公开发布的通知

## License

[MIT](LICENSE)
