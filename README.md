# niuma-charger · 牛马充电器

> SwiftBar 上班鼓励器 —— 把上班变成一场看得见的充电：菜单栏倒数下班，钱包按秒进账，语录按小时打气。工作日自动营业，休息日自动休眠。

![四种工作状态](screenshots/demo.png)

一段纯 Python 标准库写成的 macOS 菜单栏插件（[SwiftBar](https://swiftbar.app) 插件协议），无任何第三方依赖。装好之后，你的菜单栏会多出一个常驻小组件：

| 状态 | 菜单栏显示 | 点开下拉可见 |
|---|---|---|
| 🌅 上班前 | 距开工倒计时 | 预计今日入账 · 时薪/分薪/秒薪 · 语录 |
| ⏳ 上班中 | 距下班倒计时（黄色） | 今日已赚按分钟累计 · 赚钱速度 · 充电进度条 · 语录 |
| 🎉 已下班 | 已下班 · 今日总入账（绿色） | 收官结算 · 满格进度条 · 下个开工日 · 语录 |
| 🏖 休息日 | 休息中（灰色） | 假期名称 · 距下次上班天数 · 休息专属语录 |

工资口径：时薪 = 月薪 ÷ 21.75 ÷ 每日工时。调休补班的周末照常营业，并在下拉里标注「今天调休补班」。

## 特色：充电进度条

下拉里的 20 格进度条模拟电池充电——**绿色是你已经赚到手的，黄色 ⚡ 停在充电前沿，表示钱正在流入口袋**。从开工到下班，一格一格充满：

![充电进度条](screenshots/charging.png)

下班那一刻整条变绿，充电完成 🎉。

## 特色：108 条语料，每小时换一条

打工人自嘲（「人生很短，周一很长」）、温柔夸夸（「没有迟到，没有崩溃，这很了不起」）、轻鸡汤（「秒薪在走，进度在涨，生活在稳稳向前」）三种风格混合轮换，上班/休息各用专属语料池。下拉里点「🎲 换一条语录」可随时手动换。

## 特色：中国节假日感知

内置国务院 2026–2027 年官方放假 + 调休补班表：双休与法定节假日自动切休息模式（下拉显示假期名称），调休补班日正常开工。表按年登记，官方发布次年通知后追加一段数据即可（见[下文](#节假日表更新)）。

## 安装

前置：macOS + [SwiftBar](https://swiftbar.app)（终端执行 `brew install --cask swiftbar`，或官网下载）。

### 方式一：一键脚本（推荐）

```bash
git clone https://github.com/zhangYIBO1993/niuma-charger.git
cd niuma-charger
./install.sh
```

脚本会把插件装进 SwiftBar、引导你写入月薪配置，一分钟内菜单栏出现 `⏳`。已装过再跑一遍 = 更新，配置不会被覆盖。

### 方式二：手动三步

```bash
cp encourage.1m.py ~/Library/Application\ Support/SwiftBar/Plugins/
chmod +x ~/Library/Application\ Support/SwiftBar/Plugins/encourage.1m.py
mkdir -p ~/.config/swiftbar && cp encourage.json.example ~/.config/swiftbar/encourage.json
```

然后编辑 `~/.config/swiftbar/encourage.json` 填上月薪。

## 配置 `~/.config/swiftbar/encourage.json`

| 键 | 默认 | 说明 |
|---|---|---|
| `salary` | `0` | 月薪（元）。为 0 时隐藏工资相关行，其余功能照常——不想暴露收入也能用 |
| `start` | `09:00` | 上班时间（倒计时起点） |
| `end` | `18:00` | 下班时间（倒计时终点） |

改完保存即可，下一次刷新（1 分钟内）生效。

## 自定义语料

编辑 `encourage.1m.py` 里的 `QUOTES_WORK`（上班池）和 `QUOTES_REST`（休息池）两个元组，一行一条。唯一要求：不要包含竖线 `|`（SwiftBar 菜单协议保留字符）。改完跑一次校验：

```bash
python3 encourage.1m.py --selftest
```

## 更新与卸载

```bash
cd niuma-charger && git pull && ./install.sh   # 更新（配置保留）
rm ~/Library/Application\ Support/SwiftBar/Plugins/encourage.1m.py   # 卸载
rm ~/.config/swiftbar/encourage.json ~/.config/swiftbar/encourage.offset
```

## 节假日表更新

每年 10–11 月国务院办公厅发布次年放假安排后，在 `encourage.1m.py` 的 `TABLES` 里按年份追加节假日区间与调休补班日，无需改任何逻辑。表外年份自动退化为「周末休 / 平日上」，菜单下拉中会提示待更新。当前数据来源：国办发明电〔2025〕7 号《关于 2026 年部分节假日安排的通知》、国办发明电〔2026〕10 号《关于 2027 年部分节假日安排的通知》。

## 开发与自检

```bash
python3 encourage.1m.py --selftest  # 离线自检：日历/工资/进度条/语料不变量
python3 encourage.1m.py             # 手动渲染一次菜单输出（调试用）
```

自检覆盖：节假日与调休分类、四个状态的边界时刻、工资数学、进度条各百分比形态、语料池去重与长度约束。

## 致谢

- 灵感来自「上班鼓励机」类产品（实时工资 + 下班倒计时 + 鼓励语录三件套）
- 语料风格参考社媒流传的打工人文案趋势，均为改写而非逐字搬运，来源链接见 `encourage.1m.py` 语料区注释
- 节假日数据来自国务院办公厅公开发布的通知

## License

[MIT](LICENSE)
