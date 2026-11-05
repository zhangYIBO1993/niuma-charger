#!/usr/bin/env python3
"""上班鼓励器 for SwiftBar. Run with --selftest for an offline check."""
import contextlib
import datetime as dt
import io
import json
from pathlib import Path
import shlex
import sys

CONFIG_PATH = Path.home() / ".config/swiftbar/encourage.json"
OFFSET_PATH = Path.home() / ".config/swiftbar/encourage.offset"
SCRIPT = str(Path(__file__).resolve())
SECONDARY = "#6d6d72,#b5b5bd"
A_GREEN, A_YELLOW, A_GRAY, A_OFF = "\033[32m", "\033[33m", "\033[90m", "\033[0m"
BAR_SLOTS = 20

# 官方放假安排按年登记：每年 10-11 月国务院办公厅发布次年通知后，往 TABLES 加一年即可。
# 2026 来源：国办发明电〔2025〕7号《关于2026年部分节假日安排的通知》
TABLES = {
    2026: {
        "holidays": (
            ("2026-01-01", "2026-01-03", "元旦"),
            ("2026-02-15", "2026-02-23", "春节"),
            ("2026-04-04", "2026-04-06", "清明节"),
            ("2026-05-01", "2026-05-05", "劳动节"),
            ("2026-06-19", "2026-06-21", "端午节"),
            ("2026-09-25", "2026-09-27", "中秋节"),
            ("2026-10-01", "2026-10-07", "国庆节"),
        ),
        "makeup": ("2026-01-04", "2026-02-14", "2026-02-28", "2026-05-09",
                   "2026-09-20", "2026-10-10"),  # 调休补班
    },
}


def _build_tables():
    holidays = {}
    for table in TABLES.values():
        for first, last, name in table["holidays"]:
            day = dt.date.fromisoformat(first)
            while day <= dt.date.fromisoformat(last):
                holidays[day] = name
                day += dt.timedelta(days=1)
    makeup = {dt.date.fromisoformat(d) for t in TABLES.values() for d in t["makeup"]}
    return holidays, makeup


HOLIDAYS, WORKDAY_OVERRIDES = _build_tables()
WEEKDAY_CN = "一二三四五六日"

# 语料：打工人自嘲 + 温柔夸夸 + 轻鸡汤混合，社媒风格短句（部分为流传梗的改写，非逐字引用）。
# 参考（均为二手报道，未直接抓取小红书登录墙内原帖）：牛马文案合集 ganhuoku.cn/archives/311048、
# sina.cn/news/detail/5315582595697267 与 5317592119251454、"确诊为马" uied.cn/posts/110766、
# 4anet.com 品牌借势案例；夸夸/反内耗：socialbeta.com/article/110889（小跨一步，大夸一场）、
# jiemian.com/article/12315060、m.huxiu.com/article/4849811.html；
# 离线休息/周末：36kr.com/p/3382705161811969、pinglun.youth.cn/wztt/202504/t20250428_15970303.htm
QUOTES_WORK = (
    "为老板的玛莎拉蒂添砖加瓦的日子，今天也准时开窑。",
    "钱虽然还没到账，但正在以稳定的秒薪向你飞奔。",
    "你敲的不是键盘，是自己未来的首付。",
    "会议开得再长，也长不过你赚钱的耐心。",
    "打工可能不能致富，但不打工连奶茶都喝不起。",
    "今天也是被自己的敬业程度感动的一天。",
    "老板画的饼不管饱，自己赚的钱才香。",
    "上班如上山，一步一个台阶，山顶有工资。",
    "别人卷是内耗，你卷是给自己攒底气。",
    "KPI 会撒谎，倒计时不会——离下班又近了一分钟。",
    "咖啡续的是命，工资续的是梦想。",
    "认真工作的样子，是你今天最好看的穿搭。",
    "带薪喝水，带薪呼吸，带薪成为更好的自己。",
    "甲方虐我千百遍，发薪日待我如初恋。",
    "你不是在上班，你是在给自己的人生充值。",
    "平日的坚持，都是周末的底气。",
    "累了就看看进度条：绿色那截，都是你赚到的。",
    "今天流的汗，月底都会变成到账短信。",
    "牛马也要有梦想：先把这几个小时耕完。",
    "世界是个巨大的草台班子，但你今日营业格外专业。",
    "工资不高，志气不短；进度不满，干劲不减。",
    "下班前的每一分钟，都值得被认真对待。",
    "神仙也要下凡历劫，牛马上班历的是月薪。",
    "每封邮件都是一颗子弹，正中下月账单的心脏。",
    "充电条在涨，钱包在鼓，未来在亮。",
    "又向自由职业的存款目标，推进了一小格。",
    "今天的班，是为将来的不上班攒资本。",
    "工位是临时的，本事是自己的。",
    "牛累了会歇息，牛马累了只会点咖啡。",
    "人生很短，周一很长。",
    "乾坤未定你我皆是黑马，闹钟一响你我皆是牛马。",
    "今日职场人设：专业捕薪小能手。",
    "生活本是细碎日常，上班只为碎银几两。",
    "确认过眼神，都是拼命搞钱的打工人。",
    "只要我们努努力，领导就能开上玛莎拉蒂。",
    "天天想罢工，月月上满勤。",
    "正式确诊为班马：一匹还在工位上的马。",
    "工作不会彻底击垮你，只会让你越发 ok。",
    "上班使我快乐，主要是快，乐不太确定。",
    "会议一小时，重点五分钟，你坚持下来了。",
    "摸鱼不是罪，是带薪冥想。",
    "只要我摸鱼摸得够快，KPI 就追不上我。",
    "辞职信在心里已经改到第 800 稿，今天也忍住了。",
    "成年人的崩溃从打开工作群开始，自愈从工资到账开始。",
    "起床困难户，上班特困生，下班艺术家。",
    "挣钱嘛，生意，不寒碜。",
    "上班是为了等下班，下班是为了等发薪，闭环了。",
    "工资到账三天，余额已经不知所踪。",
    "苟住，这个月的工资已经在路上了。",
    "小跨一步，大夸一场——今天的你也跨了一步。",
    "上班暂停一秒：恭喜这位准时到岗的朋友！",
    "在别人笑你之前先笑自己，你就夺回了定义权。",
    "情绪稳定，按时出勤，你已经赢过很多人。",
    "认真搬砖的你，今天也自带柔光滤镜。",
    "没有迟到，没有崩溃，这很了不起。",
    "比昨天的你，又多赚了一天工资。",
    "把「算了」咽回去继续干，是成年人的冠军操作。",
    "你解决问题的方式，比问题本身优雅多了。",
    "今天也把自己照顾得不错的成年人，是你呀。",
    "世界破破烂烂，你在缝缝补补还领着工资。",
    "秒薪在走，进度在涨，生活在稳稳向前。",
    "复利的世界里，每个小时都算数。",
    "班是老板的，钱和命是自己的，都护住了。",
    "上班的尽头不是退休，是随时能选择的底气。",
    "此刻的坚持，月底会连本带利结给你。",
    "进度条不会撒谎，付出过的都会显形。",
    "进度条会替你记着：你今天真的有在认真活。",
    "打工的意义：把日子过成自己说了算的样子。",
)
QUOTES_REST = (
    "休息日不接工作消息，是对周末最基本的尊重。",
    "躺平不是摆烂，是给电池放电再充满。",
    "今天的主要工作：把自己哄开心。",
    "好好休息，下个进度条才充得快。",
    "周末的快乐是免费的，也是最贵的。",
    "上班养家，休息养心，缺一不可。",
    "今天不赚钱，是为了明天更值钱。",
    "把闹钟关掉，是成年人最盛大的仪式感。",
    "休息也是一种生产力，老板不懂，身体懂。",
    "愿你的休息日：睡到自然醒，吃到心满足。",
    "充电中，请勿打扰——说的就是你自己。",
    "今天的待办清单只有一项：开心。",
    "会休息的人才会工作，会工作的人更会休息。",
    "工作日很远，快乐很近。",
    "什么都不做的日子，也是生活的一部分。",
    "今天理直气壮地无所事事，这叫蓄能。",
    "休息不是奖励，是和吃饭一样的必需品。",
    "睡到自然醒，是对闹钟最有礼貌的告别。",
    "沙发陷得越深，电充得越满。",
    "今天什么都不做，也依然是个很好的人。",
    "摆烂一天不叫摆烂，叫战略性休整。",
    "把下午过成一首慢歌，不赶拍子。",
    "你已经很努力了，今天允许自己关机。",
    "上班的你很棒，休息的你也很棒。",
    "这周辛苦了，给自己发一朵小红花。",
    "你不需要变得更有用，才配得上休息。",
    "把五天的自己，慢慢粘回完整的你。",
    "今天的主角是你，不是待办清单。",
    "周末不是用来焦虑的，是用来喜欢自己的。",
    "这周的你已经很棒了，剩下的交给下周。",
    "关掉工作群，打开好心情，顺序别搞反了。",
    "周一才上班，周日就该理直气壮地快乐。",
    "离线不是失踪，是合法断联。",
    "下班后的你，只归你自己管。",
    "把「离线休息权」用满，是你的正当权利。",
    "休息不需要理由，累就是理由。",
    "周末的快乐很简单：不设闹钟，不定目标。",
    "好好吃饭，好好睡觉，就是周末的头等大事。",
    "愿你的假期像工资一样，多多益善。",
    "电量满格的你，下周谁都拦不住。",
)


def load_config():
    config = {"salary": 0.0, "start": "09:00", "end": "18:00"}
    try:
        loaded = json.loads(CONFIG_PATH.read_text())
        if isinstance(loaded, dict):
            config.update({k: loaded[k] for k in config if k in loaded})
    except (OSError, ValueError):
        pass
    return config


def parse_hhmm(value, fallback):
    try:
        hours, minutes = str(value).split(":")
        parsed = int(hours) * 60 + int(minutes)
        if 0 <= parsed < 24 * 60:
            return parsed
    except (AttributeError, TypeError, ValueError):
        pass
    return fallback


def day_kind(day):
    """-> (is_workday, label, table_stale)"""
    stale = day.year not in TABLES
    if day in HOLIDAYS:
        return False, HOLIDAYS[day], stale
    if day in WORKDAY_OVERRIDES:
        return True, "调休补班", stale
    return day.weekday() < 5, None, stale


def next_workday(day):
    probe = day
    for _ in range(60):
        probe += dt.timedelta(days=1)
        if day_kind(probe)[0]:
            return probe
    return probe


def phase(now, start_min, end_min, is_work):
    if not is_work:
        return "rest"
    minute = now.hour * 60 + now.minute
    if minute < start_min:
        return "pre"
    return "work" if minute < end_min else "done"


def rates_line(salary, span_min):
    if not salary or salary <= 0 or span_min <= 0:
        return None
    hourly = salary / 21.75 / (span_min / 60)
    per_min, per_sec = hourly / 60, hourly / 3600
    return f"时薪 ¥{hourly:,.1f} · 分薪 ¥{per_min:,.2f} · 秒薪 ¥{per_sec:,.3f}"


def earned(salary, elapsed_min, span_min):
    if not salary or salary <= 0 or span_min <= 0:
        return None
    return salary / 21.75 * min(elapsed_min, span_min) / span_min


def fmt_hm(minutes):
    hours, minutes = divmod(int(minutes), 60)
    return f"{hours}时{minutes:02d}分" if hours else f"{minutes}分钟"


def bar(pct):
    """充电条：绿已充 · 黄色⚡在充电前沿 · 灰未充。"""
    if pct >= 100:
        return A_GREEN + "▰" * BAR_SLOTS + A_OFF
    if pct <= 0:
        return A_GRAY + "▱" * BAR_SLOTS + A_OFF
    reached = min(BAR_SLOTS, max(1, round(pct * BAR_SLOTS / 100)))
    return (A_GREEN + "▰" * (reached - 1) + A_OFF + A_YELLOW + "⚡" + A_OFF
            + A_GRAY + "▱" * (BAR_SLOTS - reached) + A_OFF)


def quote(now, offset, is_rest):
    pool = QUOTES_REST if is_rest else QUOTES_WORK
    # 步进 7 与池长互质，相邻小时跳到不同风格块，避免连续同款。
    index = (now.toordinal() * 24 + now.hour + offset) * 7 % len(pool)
    return pool[index]


def read_offset():
    try:
        return int(OFFSET_PATH.read_text())
    except (OSError, ValueError):
        return 0


def bump_offset():
    OFFSET_PATH.parent.mkdir(parents=True, exist_ok=True)
    OFFSET_PATH.write_text(str(read_offset() + 1))


def sub(text):
    print(f"{text} | size=11 color={SECONDARY}")


def actions(stale=False, year=None):
    if stale:
        sub(f"⚠ {year} 年节假日表待官方发布后更新")
    print(f"🎲 换一条语录 | bash={shlex.quote(SCRIPT)} param1=--quote "
          "terminal=false refresh=true")
    print("↻ 立即刷新 | refresh=true")


def render_quote(now, offset, is_rest):
    print(f"「{quote(now, offset, is_rest)}」")
    sub("语录每小时换一条")


def render(now, config, offset=0):
    start = parse_hhmm(config["start"], 540)
    end = parse_hhmm(config["end"], 1080)
    span = max(1, end - start)
    is_work, label, stale = day_kind(now.date())
    state = phase(now, start, end, is_work)
    rates = rates_line(config["salary"], span)
    minute = now.hour * 60 + now.minute

    if state == "rest":
        gap = (next_workday(now.date()) - now.date()).days
        weekday = WEEKDAY_CN[next_workday(now.date()).weekday()]
        back = f"明天（周{weekday}）上班" if gap == 1 else f"距下次上班还有 {gap} 天（周{weekday}）"
        print(A_GRAY + "🏖 休息中 | ansi=true")
        print("---")
        print(f"🏖 今天是{label or '休息日'} · 好好休息")
        sub(back)
        print("---")
        render_quote(now, offset, True)
        print("---")
        actions(stale, now.year)
        return

    if state == "pre":
        wait = start - minute
        print(f"🌅 {fmt_hm(wait)}后开工")
        print("---")
        print(f"{fmt_hm(wait)}后开工（{config['start']}）")
        if earned(config["salary"], span, span) is not None:
            print(f"预计今日入账 ¥{earned(config['salary'], span, span):,.0f}")
        sub(rates or f"月薪未配置 · 编辑 {CONFIG_PATH}")
        if label:
            sub(f"今天{label}")
        print("---")
        render_quote(now, offset, False)
        print("---")
        actions(stale, now.year)
        return

    elapsed = minute - start
    pct = min(100.0, elapsed / span * 100)
    money = earned(config["salary"], elapsed, span)

    if state == "work":
        print(A_YELLOW + f"⏳ {fmt_hm(end - minute)} | ansi=true")
        print("---")
        if money is None:
            print("牛马充电中")
        else:
            print(f"今日已赚 ¥{money:,.1f}")
        sub(rates or f"月薪未配置 · 编辑 {CONFIG_PATH}")
        print(f"今日进度 {pct:.0f}% · 剩 {fmt_hm(end - minute)}")
        print(f"{bar(pct)} | ansi=true")
        if label:
            sub(f"今天{label}")
        print("---")
        render_quote(now, offset, False)
        print("---")
        actions(stale, now.year)
        return

    print(A_GREEN + "🎉 已下班" + (f" · 已赚 ¥{money:,.0f}" if money is not None else "") + " | ansi=true")
    print("---")
    if money is None:
        print("🎉 今日收官")
    else:
        print(f"🎉 今日收官 · 共赚 ¥{money:,.1f}")
    sub(rates or f"月薪未配置 · 编辑 {CONFIG_PATH}")
    print(f"{bar(100)} | ansi=true")
    print("---")
    following = next_workday(now.date())
    gap = (following - now.date()).days
    weekday = WEEKDAY_CN[following.weekday()]
    print(f"明天 {config['start']} 再战" if gap == 1
          else f"{gap} 天后再战（周{weekday} {config['start']}）")
    print("---")
    render_quote(now, offset, False)
    print("---")
    actions(stale, now.year)


def selftest():
    work_sat = dt.date(2026, 2, 14)  # 调休补班周六
    assert day_kind(dt.date(2026, 1, 1)) == (False, "元旦", False)
    assert day_kind(dt.date(2026, 2, 16)) == (False, "春节", False)
    assert day_kind(dt.date(2026, 10, 7)) == (False, "国庆节", False)
    assert day_kind(work_sat) == (True, "调休补班", False)
    assert day_kind(dt.date(2026, 1, 4)) == (True, "调休补班", False)
    assert day_kind(dt.date(2026, 11, 7)) == (False, None, False)  # 周六
    assert day_kind(dt.date(2026, 11, 4)) == (True, None, False)  # 周三
    assert day_kind(dt.date(2027, 1, 1)) == (True, None, True)  # 周五，表外回退
    assert next_workday(dt.date(2026, 11, 5)) == dt.date(2026, 11, 6)
    assert next_workday(dt.date(2026, 10, 1)) == dt.date(2026, 10, 8)
    cfg = {"salary": 20000, "start": "09:00", "end": "18:00"}
    assert phase(dt.datetime(2026, 11, 4, 8, 59), 540, 1080, True) == "pre"
    assert phase(dt.datetime(2026, 11, 4, 9, 0), 540, 1080, True) == "work"
    assert phase(dt.datetime(2026, 11, 4, 17, 59), 540, 1080, True) == "work"
    assert phase(dt.datetime(2026, 11, 4, 18, 0), 540, 1080, True) == "done"
    assert phase(dt.datetime(2026, 11, 7, 12, 0), 540, 1080, False) == "rest"
    assert rates_line(20000, 540) == "时薪 ¥102.2 · 分薪 ¥1.70 · 秒薪 ¥0.028"
    assert rates_line(0, 540) is None
    assert f"{earned(20000, 389, 540):,.1f}" == "662.4"
    assert earned(20000, 700, 540) == earned(20000, 540, 540)
    assert bar(0) == A_GRAY + "▱" * BAR_SLOTS + A_OFF
    assert bar(100) == A_GREEN + "▰" * BAR_SLOTS + A_OFF
    assert bar(72) == (A_GREEN + "▰" * 13 + A_OFF + A_YELLOW + "⚡" + A_OFF
                       + A_GRAY + "▱" * 6 + A_OFF)
    assert bar(0.1) == (A_GREEN + A_OFF + A_YELLOW + "⚡" + A_OFF
                        + A_GRAY + "▱" * 19 + A_OFF)
    assert bar(99.9).endswith(A_OFF) and "▱" not in bar(99.9)
    now = dt.datetime(2026, 11, 4, 15, 29)
    assert quote(now, 0, False) == quote(now, 0, False)
    assert quote(now, 0, False) != quote(now, 1, False)
    assert quote(now, 0, False) in QUOTES_WORK and quote(now, 0, True) in QUOTES_REST
    all_quotes = QUOTES_WORK + QUOTES_REST
    assert len(QUOTES_WORK) >= 60 and len(QUOTES_REST) >= 30 and len(all_quotes) >= 100
    assert len(set(all_quotes)) == len(all_quotes)
    assert all("|" not in q and 0 < len(q) <= 32 for q in all_quotes)
    assert parse_hhmm("09:00", 0) == 540 and parse_hhmm("18:30", 0) == 1110
    assert parse_hhmm("bad", 540) == 540 and parse_hhmm("25:00", 540) == 540
    assert fmt_hm(151) == "2时31分" and fmt_hm(47) == "47分钟"

    for moment, first in ((dt.datetime(2026, 11, 4, 8, 13), "🌅 47分钟后开工"),
                          (dt.datetime(2026, 11, 4, 15, 29), A_YELLOW + "⏳ 2时31分 | ansi=true"),
                          (dt.datetime(2026, 11, 4, 18, 26), A_GREEN + "🎉 已下班 · 已赚 ¥920 | ansi=true"),
                          (dt.datetime(2026, 11, 7, 10, 0), A_GRAY + "🏖 休息中 | ansi=true")):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            render(moment, cfg)
        lines = out.getvalue().splitlines()
        assert lines[0] == first, lines[0]
        assert "param1=--quote" in out.getvalue() and "立即刷新" in out.getvalue()
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        render(dt.datetime(2026, 11, 4, 15, 29), cfg)
    body = out.getvalue()
    assert "今日已赚 ¥662.4" in body and "今日进度 72% · 剩 2时31分" in body
    assert f"{bar(72)} | ansi=true" in body and f"「{quote(dt.datetime(2026, 11, 4, 15, 29), 0, False)}」" in body
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        render(dt.datetime(2026, 11, 4, 15, 29), {"salary": 0, "start": "09:00", "end": "18:00"})
    assert "牛马充电中" in out.getvalue() and "月薪未配置" in out.getvalue()
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        render(dt.datetime(2027, 1, 5, 15, 0), cfg)  # 2027 表外
    assert "2027 年节假日表待官方发布后更新" in out.getvalue()
    print("selftest OK")


def main():
    if "--selftest" in sys.argv:
        selftest()
        return 0
    if "--quote" in sys.argv:
        bump_offset()
        return 0
    render(dt.datetime.now(), load_config(), read_offset())
    return 0


if __name__ == "__main__":
    sys.exit(main())
