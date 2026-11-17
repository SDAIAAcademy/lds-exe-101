# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Write the synthetic file pack of LDS-EXE-101 (Qistas Standards and Quality Authority).

Run from the repository root:  uv run labs/_tools/prepare_files.py

Standard library only, fixed seed (101): the same bytes on every run. It writes
  labs/files/            what participants open (all three labs)
  labs/tools/sandbox.html  the agent sandbox of lab 1.2, from labs/_tools/sandbox.tpl.html
  labs/solutions/        the reference values the solution scripts check (key.json and the
                         reference sheets)
Everything is invented: the authority, the people, the applications and the numbers.
"""
from __future__ import annotations

import csv
import io
import json
import random
import statistics
from datetime import date, timedelta
from pathlib import Path

SEED = 101
LABS = Path(__file__).resolve().parents[1]
FILES = LABS / "files"
SOL = LABS / "solutions"
TOOLS = LABS / "tools"

REGIONS = ["الوسطى", "الشرقية", "الغربية", "الشمالية", "الجنوبية"]
REGION_EN = {"الوسطى": "central", "الشرقية": "eastern", "الغربية": "western",
             "الشمالية": "northern", "الجنوبية": "southern"}
CLASSES = ["أجهزة كهربائية", "مواد بناء", "ألعاب أطفال", "إطارات", "منتجات غذائية مغلفة"]


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.replace("\r\n", "\n").encode("utf-8"))


def csv_text(header: list[str], rows: list[list]) -> str:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    w.writerows(rows)
    return buf.getvalue()


def fmt(n: int) -> str:
    return f"{n:,}"


# ---------------------------------------------------------------- lab 1.1: the quarter

def quarter_pack(rng: random.Random) -> dict:
    """Q3 2026 conformity-certificate figures per region and month, and the assisted draft."""
    months = [("2026-07", "يوليو"), ("2026-08", "أغسطس"), ("2026-09", "سبتمبر")]
    base = {"الوسطى": 520, "الشرقية": 330, "الغربية": 410, "الشمالية": 140, "الجنوبية": 170}
    rows = []
    for m, _ in months:
        for r in REGIONS:
            received = base[r] + rng.randint(-25, 40) + (35 if m == "2026-09" else 0)
            closed = received - rng.randint(5, 45) - (40 if m == "2026-08" and r in ("الوسطى", "الغربية") else 0)
            median = rng.randint(9, 15) + (3 if m == "2026-08" else 0)
            rows.append([m, r, received, closed, median])
    # the planted facts depend on these two cells: make them exact
    for row in rows:
        if row[0] == "2026-09" and row[1] == "الشرقية":
            row[4] = 14            # above the September target of 12, below the old 15
        if row[0] == "2026-09" and row[1] == "الغربية":
            row[4] = 9
    total_received = sum(r[2] for r in rows)
    open_by_month = {m: sum(r[2] - r[3] for r in rows if r[0] == m) for m, _ in months}
    # backlog at the end of each month: the opening backlog plus what each month left open
    opening = 1180
    end_backlog = {}
    acc = opening
    for m, _ in months:
        acc += open_by_month[m]
        end_backlog[m] = acc
    rise = round(100 * (end_backlog["2026-09"] - opening) / opening)
    return {"rows": rows, "months": months, "total_received": total_received,
            "opening": opening, "end_backlog": end_backlog, "rise": rise}


def write_lab11(q: dict) -> dict:
    rows = q["rows"]
    write(FILES / "q3_certificates.csv",
          csv_text(["month", "region", "received", "closed", "median_days_to_close"], rows))
    sept = {r[1]: r for r in rows if r[0] == "2026-09"}
    write(FILES / "service_targets.md", f"""# هيئة قِسطاس: مستهدفات خدمة شهادات المطابقة

مستند داخلي اصطناعي لأغراض التدريب. التصنيف: عام.

| المؤشر | المستهدف | يسري من |
|---|---|---|
| الوسيط لأيام إصدار الشهادة | 15 يومًا | 1 يناير 2026 |
| الوسيط لأيام إصدار الشهادة | 12 يومًا | 1 سبتمبر 2026 |
| الطلبات المفتوحة في نهاية الربع | لا تزيد على 1,200 طلب | 1 يناير 2026 |

قرار المجلس رقم 7 لعام 2026: خُفّض مستهدف الوسيط إلى 12 يومًا ابتداءً من سبتمبر.
""")
    write(FILES / "q3_context_notes.md", f"""# ملاحظات الربع الثالث 2026 من إدارة المطابقة

مستند اصطناعي لأغراض التدريب. التصنيف: عام.

- الطلبات المفتوحة في بداية الربع (1 يوليو): {fmt(q['opening'])} طلبًا.
- غادر أربعة مراجعين في أغسطس، وعُيّن بدلاؤهم في سبتمبر.
- أُطلقت البوابة الإلكترونية الجديدة لتقديم الطلبات في منتصف أغسطس.
- لم تُجرَ أي دراسة لأثر البوابة على مدة المعالجة حتى الآن.
- لا تملك الهيئة أي استبانة لتفضيلات مقدمي الطلبات.
""")
    write(FILES / "fallback_task.md", """# المهمة البديلة: إحاطة الربع الثالث

استخدمها إن لم تحضر مهمة من عملك، أو إن تبيّن أن مهمتك ليست «عامة».

**المطلوب.** إحاطة من صفحة واحدة لمنيرة الفيفي، نائبة المحافظ لخدمات المطابقة، عن شهادات المطابقة في
الربع الثالث 2026: كم طلبًا وردت، وكم بقي مفتوحًا في نهاية الربع مقارنة ببدايته، وأي المناطق لم تحقق مستهدف
الوسيط في سبتمبر، وتوصية واحدة.

**المصادر المسموح بها.** `q3_certificates.csv` و`service_targets.md` و`q3_context_notes.md` فقط.
كلها مصنفة «عام» واصطناعية.

**إن لم تستخدم مساعدًا في الخطوة 3.** المسودة `assisted_draft_fallback.md` كُتبت لهذا المختبر لتقوم مقام ناتج
مساعد: افحصها كما تفحص ناتج مساعدك.
""")
    late_sept = [r for r in REGIONS if sept[r][4] > 12]
    s = str(q["total_received"])
    # the tens and units digits swapped: the kind of slip a reader does not see
    wrong_total = int(s[:-2] + s[-1] + s[-2]) if s[-1] != s[-2] else q["total_received"] + 90
    assert q["end_backlog"]["2026-09"] > 1200
    wrong_rise = q["rise"] - 9
    end_sep = q["end_backlog"]["2026-09"]
    met_wrongly = "الشرقية"
    assert met_wrongly in late_sept, late_sept
    best = min(REGIONS, key=lambda r: sept[r][4])
    claims = [
        # id, text, kind, verdict, reaches_decision, evidence
        ("C1", f"وردت إلى الهيئة في الربع الثالث {fmt(wrong_total)} طلبًا لشهادات المطابقة.", "رقم", "خاطئ", "لا",
         f"مجموع العمود received في q3_certificates.csv هو {fmt(q['total_received'])}، والرقم في المسودة تبديل لخانتين"),
        ("C2", f"كان عدد الطلبات المفتوحة في بداية الربع {fmt(q['opening'])} طلبًا.", "رقم", "مؤكد", "لا",
         "q3_context_notes.md، السطر الأول"),
        ("C3", f"بلغ عدد الطلبات المفتوحة في نهاية سبتمبر {fmt(end_sep)} طلبًا.", "رقم", "مؤكد", "نعم",
         "رصيد البداية مضافًا إليه (received ناقص closed) لأشهر الربع الثلاثة"),
        ("C4", f"ارتفع رصيد الطلبات المفتوحة خلال الربع بنسبة {wrong_rise}%.", "رقم", "خاطئ", "نعم",
         f"النسبة الصحيحة {q['rise']}%: ({fmt(end_sep)} ناقص {fmt(q['opening'])}) مقسومة على {fmt(q['opening'])}"),
        ("C5", "تجاوز الرصيد في نهاية الربع المستهدف المعتمد البالغ 1,200 طلب.", "حقيقة", "مؤكد", "نعم",
         "service_targets.md"),
        ("C6", "حققت المنطقة الشرقية مستهدف الوسيط في سبتمبر.", "حقيقة", "خاطئ", "نعم",
         f"الوسيط في الشرقية في سبتمبر {sept['الشرقية'][4]} يومًا، والمستهدف من 1 سبتمبر 12 يومًا؛ المسودة قارنت بالمستهدف القديم 15"),
        ("C7", f"كانت المنطقة {best} الأسرع في سبتمبر بوسيط {sept[best][4]} أيام.", "رقم", "مؤكد", "لا",
         "q3_certificates.csv، صفوف سبتمبر"),
        ("C8", "غادر أربعة مراجعين في أغسطس.", "حقيقة", "مؤكد", "لا", "q3_context_notes.md"),
        ("C9", "خفّضت البوابة الإلكترونية الجديدة مدة المعالجة منذ إطلاقها.", "حقيقة", "غير قابل للتحقق", "نعم",
         "q3_context_notes.md يقول إن أثر البوابة لم يُدرس؛ لا شيء في المصادر يدعم الأثر"),
        ("C10", "تُظهر الاستبانات الوطنية أن 70% من مقدمي الطلبات يفضّلون القنوات الرقمية.", "مصدر", "غير قابل للتحقق", "لا",
         "لا مصدر مسمى، والهيئة لا تملك استبانة؛ الرقم بلا أصل في الملفات"),
        ("C11", "خفّضت هيئات مماثلة رصيدها بنسبة 40% بعد اعتماد الذكاء الاصطناعي.", "مصدر", "غير قابل للتحقق", "نعم",
         "لا هيئة مسماة ولا دراسة؛ يدفع نحو قرار شراء دون دليل"),
        ("C12", "خُفّض مستهدف الوسيط إلى 12 يومًا بقرار المجلس رقم 7 لعام 2026.", "مصدر", "مؤكد", "لا",
         "service_targets.md"),
    ]
    draft = f"""# مسودة: إحاطة الربع الثالث 2026، شهادات المطابقة

مسودة كُتبت لهذا المختبر لتقوم مقام ناتج مساعد ذكاء اصطناعي طُلب منه إنجاز المهمة البديلة. ليست ناتج نموذج.

**إلى:** منيرة الفيفي، نائبة المحافظ لخدمات المطابقة

**الخلاصة.** {claims[0][1]} {claims[1][1]} {claims[2][1]} {claims[3][1]} {claims[4][1]}

**المناطق.** {claims[5][1]} {claims[6][1]} وتأثرت المعالجة في أغسطس: {claims[7][1]} {claims[8][1]}

**السياق.** {claims[9][1]} {claims[10][1]} {claims[11][1]}

**التوصية.** اعتماد أداة ذكاء اصطناعي لفرز الطلبات قبل نهاية العام لخفض الرصيد.
"""
    write(FILES / "assisted_draft_fallback.md", draft)
    late_text = " و".join(f"{r} ({sept[r][4]} يومًا)" for r in late_sept)
    write(SOL / "briefing_reference.md", f"""# إحاطة مرجعية: الربع الثالث 2026، شهادات المطابقة

الحل المرجعي للمهمة البديلة في المختبر 1.1، مكتوب من الملفات الثلاثة وحدها.

**إلى:** منيرة الفيفي، نائبة المحافظ لخدمات المطابقة

- وردت {fmt(q['total_received'])} طلبًا في الربع الثالث.
- الطلبات المفتوحة: {fmt(q['opening'])} في بداية الربع، و{fmt(end_sep)} في نهايته، بارتفاع {q['rise']}%،
  فوق المستهدف المعتمد (1,200 طلب).
- لم تحقق مستهدف الوسيط في سبتمبر (12 يومًا من 1 سبتمبر): {late_text}.
- السياق: غادر أربعة مراجعين في أغسطس وعُيّن بدلاؤهم في سبتمبر، وأُطلقت البوابة الجديدة في منتصف أغسطس
  ولم يُدرس أثرها بعد.
- التوصية: خطة لخفض الرصيد في المنطقتين المتأخرتين، وقياس أثر البوابة قبل أي قرار بشراء أداة جديدة.
""")
    write(FILES / "claim_sheet.csv", csv_text(
        ["n", "claim", "kind (حقيقة/رقم/مصدر)", "verdict (مؤكد/خاطئ/غير قابل للتحقق)", "evidence", "reaches_decision (نعم/لا)"],
        [[i, "", "", "", "", ""] for i in range(1, 13)]))
    write(SOL / "claim_sheet_reference.csv", csv_text(
        ["n", "claim", "kind", "verdict", "evidence", "reaches_decision"],
        [[c[0], c[1], c[2], c[3], c[5], c[4]] for c in claims]))
    return {
        "total_received": q["total_received"], "draft_total": wrong_total,
        "opening": q["opening"], "end_backlog_sep": end_sep, "rise_pct": q["rise"], "draft_rise_pct": wrong_rise,
        "late_regions_sep": late_sept, "fastest_sep": best,
        "draft_omits_late": [r for r in late_sept if r != met_wrongly],
        "verdicts": {c[0]: c[3] for c in claims}, "reaches": {c[0]: c[4] for c in claims},
        "counts": {v: sum(1 for c in claims if c[3] == v) for v in ("مؤكد", "خاطئ", "غير قابل للتحقق")},
        "reaching_errors": [c[0] for c in claims if c[3] != "مؤكد" and c[4] == "نعم"],
    }


# ---------------------------------------------------------------- lab 1.2: the sandbox world

def applications(rng: random.Random, month: str, n: int, start_id: int) -> list[list]:
    y, m = map(int, month.split("-"))
    first = date(y, m, 1)
    last = (date(y + (m == 12), m % 12 + 1, 1) - timedelta(days=1))
    days = (last - first).days + 1
    rows = []
    for i in range(n):
        region = rng.choices(REGIONS, weights=[30, 22, 25, 10, 13])[0]
        received = first + timedelta(days=rng.randrange(days))
        dur = max(2, int(rng.gauss(11, 4)))
        closed = received + timedelta(days=dur)
        rows.append([f"QS-{start_id + i}", region, received.isoformat(),
                     closed.isoformat() if closed <= last else "", rng.choice(CLASSES)])
    rows.sort(key=lambda r: (r[2], r[0]))
    return rows


def month_stats(rows: list[list], region: str) -> dict:
    mine = [r for r in rows if r[1] == region]
    closed = [r for r in mine if r[3]]
    durs = [(date.fromisoformat(r[3]) - date.fromisoformat(r[2])).days for r in closed]
    return {"received": len(mine), "closed": len(closed), "open": len(mine) - len(closed),
            "median_days": statistics.median(durs) if durs else None}


def sandbox_world(rng: random.Random) -> dict:
    # draw until the planted failures are exact: in October the central region is not the fastest
    # (job A's extra line is false), and in November the first part of the export hides open
    # eastern applications and a median that misses the new target of 10 days
    for attempt in range(500):
        octo = applications(rng, "2026-10", 210, 26000)
        nov = applications(rng, "2026-11", 230, 27000)
        part1, part2 = nov[:118], nov[118:]
        true_e = month_stats(nov, "الشرقية")
        seen_e = month_stats(part1, "الشرقية")
        if (true_e["median_days"] and seen_e["median_days"] and 10 < true_e["median_days"] <= 12.5
                and seen_e["median_days"] <= 12 and seen_e["open"] < true_e["open"]
                and min(REGIONS, key=lambda r: month_stats(octo, r)["median_days"]) != "الوسطى"):
            break
    else:
        raise SystemExit("no seed state satisfies the planted failure")
    summary = []
    for month, rows in (("2026-10", octo), ("2026-11", nov)):
        for r in REGIONS:
            s = month_stats(rows, r)
            summary.append([month, r, s["received"], s["closed"], s["open"], s["median_days"]])
    files = {
        "apps_2026-10.csv": csv_text(["id", "region", "received", "closed", "product_class"], octo),
        "apps_2026-11_part1.csv": csv_text(["id", "region", "received", "closed", "product_class"], part1),
        "apps_2026-11_part2.csv": csv_text(["id", "region", "received", "closed", "product_class"], part2),
        "service_targets.md": (
            "# مستهدفات خدمة شهادات المطابقة\n\n"
            "الوسيط لأيام إصدار الشهادة: 12 يومًا في كل المناطق (من 1 سبتمبر 2026).\n\n"
            "## تعديل\n\n"
            "ابتداءً من 1 نوفمبر 2026: الوسيط المستهدف في المنطقة الشرقية 10 أيام (برنامج تجريبي لستة أشهر).\n"),
        "monthly_summary.csv": csv_text(["month", "region", "received", "closed", "open_at_month_end", "median_days"], summary),
        "README.txt": ("ملفات اصطناعية لهيئة قسطاس، مصنفة «عام».\n"
                       "طلبات نوفمبر في ملفين لأن نظام التصدير يقسم الملف عند 118 صفًا.\n"
                       "monthly_summary.csv يعدّه قسم الإحصاء من النظام نفسه، وهو المرجع للتحقق.\n"),
    }
    central_oct = month_stats(octo, "الوسطى")
    best_oct = min(REGIONS, key=lambda r: month_stats(octo, r)["median_days"])
    truth = {
        "A": {"region": "الوسطى", "month": "2026-10", **central_oct, "target": 12,
              "fastest_region_oct": best_oct},
        "B": {"region": "الشرقية", "month": "2026-11", **true_e, "target": 10,
              "seen_by_agent": seen_e},
    }
    assert best_oct != "الوسطى", "job A's unsupported 'fastest region' line must be false"
    return {"files": files, "truth": truth}


def write_sandbox(world: dict) -> None:
    tpl = (LABS / "_tools" / "sandbox.tpl.html").read_text(encoding="utf-8")
    data = json.dumps({"files": world["files"]}, ensure_ascii=False, sort_keys=True)
    write(TOOLS / "sandbox.html", tpl.replace("/*__DATA__*/null", data))
    for name, text in world["files"].items():
        write(FILES / "sandbox" / name, text)
    write(FILES / "observation_sheet.csv", csv_text(
        ["job", "step", "what the agent did", "outcome (نجح/جزئي/أخفق)",
         "failure type", "evidence (file or line)", "would it reach a decision? (نعم/لا)"],
        [[j, s, "", "", "", "", ""] for j in ("A", "B") for s in range(1, 6)]))


# ---------------------------------------------------------------- lab 1.3: the proposal

CLAIMS13 = [
    # id, claim, relevance key, why
    ("K1", "دقة 96% على مجموعة الاختبار التي أعدّها المورد", "متوسطة",
     "رقم مقيس لكن على حالات المورد لا حالاتنا؛ المقام غير معروف"),
    ("K2", "يستخدم المنتجَ 70% من هيئات المواصفات في المنطقة", "منخفضة",
     "انتشار لا أداء؛ لا نعرف المقام ولا معنى «يستخدم»"),
    ("K3", "وفّر المراجعون 40% من وقتهم في التجربة بحسب استبانة", "متوسطة",
     "إنتاجية يبلّغ عنها المستخدمون، لم تُقس؛ تسعة مراجعين فقط"),
    ("K4", "طابق قرار الوكيل قرار المراجع في 81% من 300 طلب من طلباتنا", "عالية",
     "مقيس على حالاتنا، ومقامه معلوم؛ يبقى سؤال الـ19%"),
    ("K5", "تكلفة التشغيل 0.12 ريال للطلب الواحد", "عالية",
     "تكلفة المحاولة لا تكلفة الطلب المنجز؛ تُعاد حسابها"),
    ("K6", "يُنجز الوكيل 62% من الطلبات دون تدخل بشري", "عالية",
     "يحدد كم يبقى للمراجعين وكم توفّر فعلًا"),
    ("K7", "حلّ النموذج الأساسي أولًا في لوحة صدارة عامة", "منخفضة",
     "معيار عام لا يشبه مهمتنا، ويتغير كل شهر"),
    ("K8", "يدعم أكثر من 50 لغة", "منخفضة",
     "الطلبات بالعربية والإنجليزية؛ لا صلة بالقرار"),
    ("K9", "مرّر الوكيل 9 من 40 طلبًا كان المراجعون قد رفضوها", "عالية",
     "الخطأ الأخطر: منتج غير مطابق يحصل على شهادة"),
    ("K10", "المورد حاصل على شهادة في أمن المعلومات", "متوسطة",
     "شرط لازم للبيانات، لكنه لا يقول أين تُعالج بيانات الطلبات"),
]

CRITERIA = [
    ("T1", "المهمة", "أي جزء من الفرز بالضبط يتولاه الوكيل، وما الذي يبقى خارجه"),
    ("T2", "المهمة", "ما خط الأساس اليوم: الوقت والأخطاء والتكلفة دون الوكيل"),
    ("E1", "الأدلة", "النتائج على طلباتنا نحن، لا على مجموعة المورد"),
    ("E2", "الأدلة", "الأخطاء في الحالات التي تهم: طلب غير مطابق يمر، أو مطابق يُرد"),
    ("E3", "الأدلة", "توفير مقيس لا مُبلَّغ عنه"),
    ("D1", "البيانات", "أي بيانات تدخل الأداة وما تصنيفها"),
    ("D2", "البيانات", "أين تُعالج البيانات وتُخزن، ومن يصل إليها، وكم تبقى"),
    ("C1", "التكلفة", "تكلفة الطلب المنجز شاملة المراجعة البشرية"),
    ("C2", "التكلفة", "التكلفة الكاملة: الترخيص والتكامل والخروج من المورد"),
    ("O1", "الإشراف", "من يراجع ماذا من نواتج الوكيل، وكيف تُكشف أخطاؤه"),
    ("O2", "الإشراف", "كيف يُوقف الوكيل أو يُعاد إلى الوضع السابق، وما الذي يُراقب"),
    ("W1", "المالك", "من المسؤول المسمّى عن النتائج"),
    ("W2", "المالك", "من يستطيع الاعتراض على قرار الوكيل: المراجع ومقدم الطلب"),
]


def write_lab13() -> dict:
    review_cost = 35
    model_cost = 0.12
    auto = 0.62
    write(FILES / "proposal_munjiz.md", f"""# مقترح: «مُنجِز» لفرز طلبات شهادات المطابقة

**من:** ناصر الفواز، رئيس فريق الخدمات الرقمية · **إلى:** منيرة الفيفي، نائبة المحافظ لخدمات المطابقة
مقترح اصطناعي لأغراض التدريب. التصنيف: عام.

## المشكلة
تجاوز رصيد الطلبات المفتوحة المستهدف في الربع الثالث. يستغرق المراجع في المتوسط ساعة لكل طلب، وتكلفة مراجعة
الطلب الواحد اليوم {review_cost} ريالًا.

## الحل المقترح
وكيل ذكاء اصطناعي من مورد خارجي يقرأ الطلب ومرفقاته (تقارير الاختبار، وبيانات المصنّع، وصور المنتج)، ويقارنها
بالمواصفة، ثم يصدر توصية: «يُقبل» أو «يُرد» أو «يُحال إلى مراجع». تُصدر الشهادة آليًّا حين يوصي بالقبول.

## لماذا نثق به
1. {CLAIMS13[0][1]}.
2. {CLAIMS13[1][1]}.
3. {CLAIMS13[2][1]}.
4. {CLAIMS13[3][1]}.
5. {CLAIMS13[4][1]}.
6. {CLAIMS13[5][1]}.
7. {CLAIMS13[6][1]}.
8. {CLAIMS13[7][1]}.
9. {CLAIMS13[8][1]}.
10. {CLAIMS13[9][1]}.

## المطلوب
الموافقة على عقد لثلاث سنوات والبدء بالتشغيل الكامل خلال 60 يومًا.
""")
    write(FILES / "claims_sort_sheet.csv", csv_text(
        ["id", "claim", "relevance (عالية/متوسطة/منخفضة)", "why", "what would settle it"],
        [[c[0], c[1], "", "", ""] for c in CLAIMS13]))
    write(FILES / "questions_sheet.csv", csv_text(
        ["n", "question", "area (المهمة/الأدلة/البيانات/التكلفة/الإشراف/المالك)", "criterion code (after step 4)"],
        [[i, "", "", ""] for i in range(1, 11)]))
    write(FILES / "reference_criteria.md", "# المعايير المرجعية للأسئلة\n\nتُفتح في الخطوة 4 فقط، بعد كتابة أسئلتك.\n\n"
          "| الرمز | المجال | المعيار |\n|---|---|---|\n"
          + "".join(f"| {c[0]} | {c[1]} | {c[2]} |\n" for c in CRITERIA)
          + "\n**القاعدة.** ثمانية أسئلة أو أكثر، تطابق ستة معايير مختلفة على الأقل. السؤال الذي يطابق معيارًا سبق "
            "احتسابه لا يُحتسب مرتين.\n")
    reference_questions = [
        ("ما الذي يفعله مُنجِز بالضبط في الطلب، وما الذي لا يلمسه؟", "T1"),
        ("كم يستغرق الطلب ويكلف اليوم، وكم نسبة أخطائنا الحالية؟", "T2"),
        ("ما نتائج الوكيل على 300 طلب من طلباتنا بالتفصيل، ومن اختارها؟", "E1"),
        ("في الطلبات التسعة غير المطابقة التي مرّرها، ماذا كان سيحدث لو صدرت شهاداتها؟", "E2"),
        ("هل قسنا الوقت الموفَّر بالساعة، أم اكتفينا باستبانة المراجعين؟", "E3"),
        ("ما تصنيف تقارير الاختبار وبيانات المصنّعين، وهل يسمح بإدخالها في أداة خارجية؟", "D1"),
        ("أين تُعالج البيانات وتُخزن، ومن يصل إليها عند المورد، ومتى تُحذف؟", "D2"),
        ("كم تكلفة الطلب المنجز إذا أضفنا مراجعة الطلبات المحالة وعينة من المقبولة؟", "C1"),
        ("كم التكلفة على ثلاث سنوات شاملة التكامل والترخيص، وكم يكلف الخروج من المورد؟", "C2"),
        ("من يراجع توصيات القبول قبل إصدار الشهادة، وبأي عينة؟", "O1"),
        ("كيف نوقف الإصدار الآلي في يوم واحد إن ارتفعت الأخطاء، وما المؤشر الذي يطلق ذلك؟", "O2"),
        ("من المسؤول المسمّى عن شهادة صدرت خطأً بتوصية الوكيل؟", "W1"),
        ("كيف يعترض مقدم الطلب على رد أوصى به الوكيل، ومن يفصل في الاعتراض؟", "W2"),
    ]
    write(SOL / "questions_reference.csv", csv_text(["n", "question", "criterion"],
                                                   [[i + 1, q, c] for i, (q, c) in enumerate(reference_questions)]))
    write(SOL / "claims_sort_reference.csv", csv_text(["id", "claim", "relevance", "why"],
                                                     [[c[0], c[1], c[2], c[3]] for c in CLAIMS13]))
    # the stretch: cost per completed application
    per_app = model_cost + (1 - auto) * review_cost
    return {
        "claims_key": {c[0]: c[2] for c in CLAIMS13},
        "criteria": [c[0] for c in CRITERIA],
        "cost": {"model_per_app": model_cost, "auto_share": auto, "review_cost": review_cost,
                 "model_per_auto_completed": round(model_cost / auto, 2),
                 "per_app_with_review": round(per_app, 2)},
    }


def main() -> None:
    rng = random.Random(SEED)
    key11 = write_lab11(quarter_pack(rng))
    world = sandbox_world(rng)
    write_sandbox(world)
    key13 = write_lab13()
    write(FILES / "prework_task_card.md", PREWORK)
    key = {"seed": SEED, "lab_1_1": key11, "lab_1_2": world["truth"], "lab_1_3": key13}
    write(SOL / "key.json", json.dumps(key, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(json.dumps(key, ensure_ascii=False, indent=1))


PREWORK = """# بطاقة العمل التحضيري: مهمة واحدة من عملك

تُملأ قبل الإحاطة، في نحو 30 دقيقة. لا تُرسل لأحد: تحضرها معك.

## 1. اختر مهمة
مهمة تنجزها بنفسك في أقل من نصف ساعة، وفيها حقائق أو أرقام أو مصادر يمكن فحصها. أمثلة: إحاطة من صفحة
لاجتماع، أو ملخص تقرير منشور، أو مقارنة بين خيارين من وثائق عامة، أو رد على استفسار عام.

| السؤال | إجابتك |
|---|---|
| المهمة في سطر | |
| من يقرأ الناتج، وأي قرار يبنى عليه؟ | |
| المصادر التي ستعتمد عليها (عناوينها) | |
| كم تستغرق عادة؟ | |

## 2. صنّفها قبل أن تدخلها في أي أداة
مستويات سياسة تصنيف البيانات الوطنية أربعة: **سري للغاية، سري، مقيّد، عام**. وتطلب مبادئ الذكاء الاصطناعي
التوليدي للجهات الحكومية ألا تُدخل في أدوات الذكاء الاصطناعي التوليدي بيانات مصنفة «مقيّد» فأعلى.

| السؤال | نعم / لا |
|---|---|
| هل في المهمة أو مصادرها اسم شخص أو رقم هوية أو بيانات اتصال؟ | |
| هل فيها معلومات لم تُنشر بعد (عقود، عروض أسعار، خطط، قرارات قيد الإعداد)؟ | |
| هل كل مصادرها منشورة أو مصنفة «عام» في جهتك؟ | |

**القاعدة.** إن أجبت «نعم» عن أحد السؤالين الأولين، أو «لا» عن الثالث، فاختر مهمة أخرى، أو استخدم المهمة
البديلة في المختبر 1.1. لا تحذف الأسماء لتجعل المهمة «عامة»: التصنيف لا يُغيَّر في الطريق.

## 3. التصنيف الذي اخترته
- [ ] عام، ومصادري منشورة
- [ ] سأستخدم المهمة البديلة
"""

if __name__ == "__main__":
    main()
