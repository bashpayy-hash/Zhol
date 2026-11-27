"""Business plan of zhol as a deck-style PDF source: one HTML file, 1920x1080 pages, pitch deck look."""
import csv
import html
from pathlib import Path

HERE = Path(__file__).parent
DECK_CSS = (HERE / "deck.css").read_text()
FIN = list(csv.DictReader(open("/home/user/Zhol/docs/finplan.csv")))
QR = (HERE / "qr-zhol.svg").read_text()

EXTRA = """
@page { size: 1920px 1080px; margin: 0 }
* { margin: 0 }
html, body { background: #ddd; }
body > section { width: 1920px; height: 1080px; overflow: hidden; position: relative; isolation: isolate; break-after: page; }
.bleed, .veil { z-index: -1 }
*, *::before { animation: none !important; }
p, li, h1, h2, h3, td, th { text-wrap: pretty; }
h2 { max-width: 1500px; }
.stats.four { grid-template-columns: repeat(4, 1fr); gap: 40px; }
.stats.paper .stat { border-top-color: var(--red); }
.stats.paper .big { color: var(--ink); }
.stats .big.s { font-size: 80px; letter-spacing: -2px; white-space: nowrap; }
section svg { flex: none; display: block; }
.body { flex: 1 0 auto; display: flex; flex-direction: column; justify-content: safe center; gap: 40px; }
.sm { font-size: 27px; line-height: 1.4; margin: 0; }
.sm b { color: var(--ink); font-weight: 600; }
section.dark .sm b { color: var(--on-dark); }
.cards.three { grid-template-columns: repeat(3, 1fr); }
.cards.five { grid-template-columns: repeat(5, 1fr); gap: 20px; }
.cards.five .sm { font-size: 25px; }
.card h3 { font-size: 32px; }
section.dark .card h3 { color: var(--on-dark); }
.tag { display: inline-block; align-self: flex-start; font-size: 20px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; border-radius: 999px; padding: 6px 16px; background: var(--sage); color: var(--sage-ink); margin: 0; }
.tag.soon { background: #efe2d6; color: var(--red); }
table.t { width: 100%; border-collapse: collapse; font-size: 27px; line-height: 1.32; color: var(--ink2); }
table.t th { font-size: 20px; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase; color: var(--red); text-align: left; padding: 0 20px 14px 0; border-bottom: 2px solid var(--ink); }
table.t td { padding: 15px 20px 15px 0; border-bottom: 2px solid var(--line); vertical-align: top; }
table.t td:first-child { color: var(--ink); font-weight: 600; }
table.t td.num, table.t th.num { text-align: right; white-space: nowrap; font-variant-numeric: tabular-nums; }
table.t tr.hl td { background: var(--sage); }
table.t th:first-child, table.t td:first-child { padding-left: 16px; }
table.t th:last-child, table.t td:last-child { padding-right: 16px; }
table.t.tight td { padding-top: 11px; padding-bottom: 11px; }
table.t.small { font-size: 25px; }
section.dark table.t { color: var(--on-dark2); }
section.dark table.t th { color: var(--red-on-dark); border-bottom-color: var(--on-dark2); }
section.dark table.t td { border-bottom-color: var(--esp2); }
section.dark table.t td:first-child { color: var(--on-dark); }
.row { display: flex; flex-direction: row; gap: 56px; align-items: flex-start; }
.row > .grow { flex: 1; min-width: 0; }
.panel { box-sizing: border-box; background: var(--card); border: 2px solid var(--line); border-radius: 24px; padding: 32px 36px; display: flex; flex-direction: column; gap: 16px; }
.panel.sage { background: var(--sage); border-color: var(--sage); }
section.dark .panel { background: var(--esp2); border-color: var(--esp2); }
.panel .k { margin-bottom: 2px; }
.mid.red { color: var(--red); }
.mid.sage { color: var(--sage-ink); }
.bar-row { display: grid; grid-template-columns: 360px 1fr; gap: 28px; align-items: center; }
.bar-track { position: relative; height: 40px; }
.bar { height: 40px; border-radius: 10px; background: #948774; }
.bar.on { background: var(--red); }
.bar-n { position: absolute; top: 2px; font-size: 30px; font-weight: 700; color: var(--ink); }
.go-on { font-size: 20px; line-height: 1; color: var(--muted); margin: -8px 0 -8px 388px; }
.steps4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; }
.scene-corner { position: absolute; right: 0; bottom: 0; z-index: -1; }
.qr { width: 220px; height: 220px; border-radius: 16px; overflow: hidden; flex: none; }
.qr svg { width: 220px; height: 220px; display: block; }
.end-row { display: flex; flex-direction: row; gap: 40px; align-items: center; }
.end-url { font-size: 56px; font-weight: 700; letter-spacing: -1px; color: var(--ink); margin: 0; }
.chain { display: flex; flex-direction: row; gap: 14px; align-items: stretch; }
.chain .panel { flex: 1; padding: 24px 26px; gap: 10px; }
.chain .n { font-size: 32px; }
ul.l { margin: 0; padding: 0 0 0 28px; display: flex; flex-direction: column; gap: 10px; font-size: 26px; line-height: 1.38; }
ul.l li::marker { color: var(--red); }
.src { columns: 3; column-gap: 56px; }
.src .panel { break-inside: avoid; margin-bottom: 24px; }
"""


def esc(s):
    return html.escape(s, quote=False)


def page(cls, inner, sid):
    cut = inner.find('</h2></div>')
    if cut >= 0:
        cut += len('</h2></div>')
        inner = inner[:cut] + '\n<div class="body">' + inner[cut:] + '</div>'
    return f'<section id="{sid}" class="{cls}">\n{inner}\n</section>'


def head(eyebrow, title, lead=None):
    out = f'<div class="head"><p class="eyebrow">{eyebrow}</p><h2>{title}</h2></div>'
    if lead:
        out += f'<p class="lead">{lead}</p>'
    return out


pages = []

# 1 cover
pages.append(page("", """
<img class="bleed" src="cover-viaduct.jpg" alt="">
<div class="veil"></div>
<div class="col">
<p class="eyebrow">Business plan · November 2026</p>
<img class="logo" src="zhol-logo.png" alt="zhol">
<p class="lead">Estimates the risk, warns in advance, updates in real time.</p>
<p class="txt">For every shipment by road, rail and sea, starting in Italy, built for all of Europe.</p>
<p class="note">zhol.live · Oyu team, Bocconi University, Milan · 27 November 2026</p>
</div>
""", "cover"))

# 2 summary
pages.append(page("dark", f"""
{head("The plan on one page", "Start with Northern Italy’s traffic offices, break even in May 2029.")}
<div class="stats four">
<div class="stat"><p class="big s">≈2,350</p><p class="txt">traffic offices in our first market, Northern Italy</p></div>
<div class="stat"><p class="big s">€12</p><p class="txt">a vehicle a month, about 14% of what an office saves</p></div>
<div class="stat"><p class="big s">May 2029</p><p class="txt">monthly revenue passes costs, in our model</p></div>
<div class="stat"><p class="big s">€155k</p><p class="txt">to raise in two tranches, 2027 and early 2028</p></div>
</div>
<div class="box"><p class="txt"><b>zhol</b> is an AI platform that estimates whether a shipment, by road, rail or sea, risks a ban, a closure or a strike and what it would cost, warns the people who plan it in advance and updates them in real time as things change.</p></div>
<p class="note"><b style="color:var(--on-dark)">Measured:</b> survey answers, the forecast log, letters sent and answered, money spent. <b style="color:var(--on-dark)">Assumed:</b> market shares, price, costs and growth, to be tested in pilots.</p>
""", "summary"))

# 3 problem
pages.append(page("", f"""
{head("The problem", "Freight stops in many ways; warnings are scattered.")}
<div class="cards five">
<div class="card"><p class="k">Truck bans</p><p class="sm">Weekends, holidays and nights, with different rules in each of 7 countries.</p></div>
<div class="card"><p class="k">Tyrol dosing</p><p class="sm">Kufstein lets trucks through in batches. In 2025, 21 of 57 dosing days came outside the published calendar.</p></div>
<div class="card"><p class="k">Strikes</p><p class="sm">Rail, ports and general strikes, often announced weeks ahead on Italy’s official calendar.</p></div>
<div class="card"><p class="k">Closures</p><p class="sm">Fréjus and Mont Blanc at night, Alpine passes in snow, ferries held by wind at Messina.</p></div>
<div class="card"><p class="k">Blockades</p><p class="sm">In the South they cost the sector over €400M in eight days in October 2026.</p></div>
</div>
<div class="tiles">
<div class="tile"><p class="k">Today</p><p class="txt">A dispatcher checks <b>6–10 websites</b>, PDF calendars, WhatsApp groups and the news by hand, then re-plans by phone, often when the truck is already queuing or the train is cancelled.</p></div>
<div class="tile"><p class="k">What it costs</p><p class="txt"><b>€300–1,000</b> for one stopped shipment, the median answer of people in the field. Italian law values <b>an hour of a truck kept waiting at €100</b>.</p></div>
</div>
""", "problem"))

# 4 product
pages.append(page("", f"""
{head("The product", "Risk, cost and a plan for each shipment.")}
<div class="cards three">
<div class="card sage"><p class="k">Estimates</p><p class="sm">Will a ban, a closure or a strike hit this shipment by road, rail or sea? How long would it wait, and what would it cost?</p></div>
<div class="card sage"><p class="k">Warns in advance</p><p class="sm">As soon as an event is announced or likely, days and weeks ahead, while the plan can still change.</p></div>
<div class="card sage"><p class="k">Updates in real time</p><p class="sm">While the load moves: a strike called off, a pass closed, a ferry held in port.</p></div>
</div>
<div class="cards three">
<div class="card"><span class="tag">Live</span><h3>Radar</h3><p class="sm">600–800 articles a day in four languages, official feeds, strike calendars, mountain weather. Each event gets a mode, a chance, a delay and a decide-by time.</p></div>
<div class="card"><span class="tag">Live</span><h3>Company report and corridor bulletin</h3><p class="sm">A company’s own lanes for four weeks, saving first, ready for 286 Italian hauliers; one page per corridor for associations.</p></div>
<div class="card"><span class="tag soon">On the way</span><h3>Beta for traffic offices</h3><p class="sm">Shipments from Excel or a photo, WhatsApp alerts after a person’s check, the pilot’s savings statement. Opens once alerts can go out on their own.</p></div>
</div>
""", "product"))

# 5 market
pages.append(page("", f"""
{head("Market", "About €230M a year in Europe. We start with what we can serve from Italy.")}
<div class="stats four paper">
<div class="stat"><p class="k">Europe · TAM</p><p class="mid">≈ €230M</p><p class="sm">6.2M EU trucks × 24.6% on international work × €144 a year ≈ €220M; about 78,000 traffic offices × ≈€3,000 ≈ €235M</p></div>
<div class="stat"><p class="k">From Italy · SAM</p><p class="mid">€18.6M</p><p class="sm">26,260 hauliers with 6–100 vehicles (national register, March 2025) × 1 in 5 with weekly lanes abroad, plus ≈800 forwarders: 6,050 offices × €3,080</p></div>
<div class="stat"><p class="k">Beachhead</p><p class="mid">≈ 2,350</p><p class="sm">offices in Lombardy, Veneto, Emilia-Romagna, Piemonte and Trentino-Alto Adige; range 1,170–3,500 at 10–30%</p></div>
<div class="stat"><p class="k">Year 3 · SOM</p><p class="mid mid red">€0.77M</p><p class="sm">250 paying offices, 220 of them in Italy: 3.6% of what we can serve</p></div>
</div>
<div class="panel sage"><p class="txt"><b>The weakest number is ours:</b> that 1 in 5 small firms has weekly lanes abroad. Interviews test it first. Cross-check: Europe’s transport software market is about €1.4bn (Berg Insight, 2025); zhol is an add-on worth about 16% of it.</p></div>
""", "market"))

# 6 evidence: survey and outreach
pages.append(page("", f"""
{head("Evidence · survey and outreach, measured", "People in the field: the problem is real and costly.")}
<div class="stats four paper">
<div class="stat"><p class="mid">8 of 9</p><p class="sm">see at least 2 in 100 shipments abroad change in a typical month; 3 of them see more than 10</p></div>
<div class="stat"><p class="mid">€300–1,000</p><p class="sm">what one stopped shipment costs the carrier</p></div>
<div class="stat"><p class="mid">€5–10</p><p class="sm">a vehicle a month is a fair price; our founding price is €8</p></div>
<div class="stat"><p class="mid">7 of 9</p><p class="sm">would share what their drivers see on the road</p></div>
</div>
<div class="row">
<div class="panel grow"><p class="k">What stops them</p><p class="txt">Software they already use <b>3</b> · habits <b>3</b> · trust <b>2</b> · price <b>1</b></p></div>
<div class="panel sage grow"><p class="k">Reaching them</p><p class="txt"><b>66 letters</b> to companies, <b>2 replies</b>. <b>8 of 9</b> professors replied, and their links brought <b>7 of 11</b> answers.</p></div>
</div>
<p class="note">11 answers since 9 November 2026: 2 from companies, 9 from people who know the field. Not yet proven: no paying customer, no pilot on real loads, no answer from an office in our beachhead. Source: zhol.live/results.</p>
""", "survey"))

# 7 evidence: forecast log
pages.append(page("dark", f"""
{head("Evidence · forecast log, measured", "We keep score of our own forecasts.")}
<div class="stats">
<div class="stat"><p class="big">86</p><p class="txt">events tracked in 14 days, one snapshot a day, never edited after the fact</p></div>
<div class="stat"><p class="big">25 days</p><p class="txt">median notice before a strike began (16 strikes)</p></div>
<div class="stat"><p class="big">4 days</p><p class="txt">median notice for storms and snow (23 events)</p></div>
</div>
<div class="box"><p class="txt"><b>First scored forecasts.</b> Italy’s strikes of 20–22 November were forecast at 94%, 75%, 64% and 59%, and all four happened: Brier score 0.09, where 0.25 is a coin toss. Four is too few: we call the radar calibrated after 30.</p></div>
<p class="foot">Source: zhol forecast log, 13–26 November 2026 (data/radar_log, scored by zhol/radar/verify.py)</p>
""", "radar"))

# 8 competition
pages.append(page("", f"""
{head("Competition", "Others cover part of the job, not the shipment.")}
<table class="t tight small">
<tr><th>Category</th><th>Examples</th><th>Price</th><th>What it misses</th></tr>
<tr><td>Fleet telematics</td><td>Webfleet, Samsara, Geotab, Targa / Viasat</td><td>€10–35 a vehicle a month</td><td>Where vehicles are now, not what will hit tomorrow’s plan</td></tr>
<tr><td>Freight exchanges</td><td>TIMOCOM, Trans.eu, Teleroute</td><td>€120–200 a user a month (est.)</td><td>A free ban calendar; nothing per shipment, no strikes</td></tr>
<tr><td>Route planning</td><td>PTV Map&amp;Guide, Sygic Truck, CoPilot</td><td>€5–49 a user a month</td><td>One route on request, permanent rules only</td></tr>
<tr><td>Free ban apps</td><td>Truck Bans, ASFINAG, My Way Truck</td><td>Free to €3 a month</td><td>One country or the calendar, not matched to shipments</td></tr>
<tr><td>Real-time visibility</td><td>Shippeo, project44, FourKites</td><td>Enterprise, paid by shippers</td><td>Reacts once a shipment is already late</td></tr>
<tr><td>Supply-chain risk</td><td>Everstream, Prewave, Dataminr</td><td>$20k+ a year</td><td>Watches suppliers, not roads; far too costly for 20 vehicles</td></tr>
</table>
<p class="note">None checks an office’s own planned shipments against unplanned events ahead of time. Source: public price pages, November 2026.</p>
""", "competition"))

# 9 threat
pages.append(page("", f"""
{head("Competition · what could change", "The biggest threat: transport software that already holds tomorrow’s shipments adds alerts.")}
<p class="txt">For example Qargo, used by 400+ European hauliers. We expect it in 2027–2028.</p>
<div class="cards three">
<div class="card sage"><p class="k">1 · Where to start</p><h3>Offices with no such system</h3><p class="sm">Most offices with 6–100 vehicles plan in Excel and WhatsApp.</p></div>
<div class="card sage"><p class="k">2 · Sell to them too</p><h3>The checked event layer as an API</h3><p class="sm">€3–5 a vehicle a month, wholesale, for transport software, telematics and freight exchanges.</p></div>
<div class="card sage"><p class="k">3 · Slow to copy</p><h3>History, ledger, trust</h3><p class="sm">Events with their real outcomes, a savings ledger per customer, trust through associations.</p></div>
</div>
<div class="panel"><p class="txt"><b>Honest weakness.</b> The calendar part is free elsewhere. Without the unplanned events, zhol would be a nice-to-have.</p></div>
""", "threat"))

# 10 business model
pages.append(page("", f"""
{head("Business model", "A simple subscription: €12 a vehicle a month.")}
<div class="row">
<div class="grow">
<table class="t tight">
<tr><th>Plan</th><th>Price</th><th>For whom</th></tr>
<tr><td>Pilot</td><td>Free for 4 weeks, with a savings statement</td><td>Every new office</td></tr>
<tr class="hl"><td>Standard</td><td>€12 a vehicle a month, minimum €99</td><td>The default</td></tr>
<tr><td>Performance</td><td>€49 + 15% of verified savings, capped at €25 a vehicle</td><td>Owners who pay for results</td></tr>
<tr><td>Founding</td><td>€8 a vehicle for 12 months</td><td>The first 10 offices</td></tr>
<tr><td>API, later</td><td>€3–5 a vehicle a month, wholesale</td><td>Software vendors</td></tr>
</table>
</div>
<div class="panel sage" style="width:620px;flex:none">
<p class="k">Why an office pays · assumption</p>
<p class="mid sage">€1,740</p>
<p class="sm">saved a month by an office of 20 vehicles, against <b>€240</b> for zhol:</p>
<ul class="l">
<li><b>€1,200</b> · 4 waits avoided × 3 h × €100</li>
<li><b>€275</b> · dispatcher time</li>
<li><b>€267</b> · strike and blockade days</li>
</ul>
<p class="sm">Calendar bans are not counted: anyone can look them up for free.</p>
</div>
</div>
""", "model"))

# 11 unit economics
pages.append(page("dark", f"""
{head("Unit economics · assumptions", "Most of the cost is shared: every customer watches the same roads.")}
<div class="stats">
<div class="stat"><p class="big">€257</p><p class="txt">revenue per office a month; variable cost €11</p></div>
<div class="stat"><p class="big">2.4 mo</p><p class="txt">to pay back the €600 it costs to win an office</p></div>
<div class="stat"><p class="big">16.4×</p><p class="txt">lifetime value of €9,827 over the cost to win, at 2.5% monthly churn</p></div>
</div>
<table class="t">
<tr><th>A month</th><th class="num">At 10 offices</th><th class="num">At 100 offices</th></tr>
<tr><td>Cost to serve: AI reading, a person’s check, WhatsApp, hosting</td><td class="num">€1,230</td><td class="num">€1,985</td></tr>
<tr><td>Revenue</td><td class="num">€2,570</td><td class="num">€25,700</td></tr>
<tr><td>Gross margin</td><td class="num">52%</td><td class="num">92%</td></tr>
</table>
""", "unit"))

# 12 go-to-market funnel
fun = [("Targeted contacts", "from the register, maps, LinkedIn", 200),
       ("Conversations", "first touch by phone or WhatsApp", 40),
       ("Discovery interviews", "30 min on one recent disruption", 12),
       ("Free pilots", "4 weeks on real shipments", 4),
       ("Paying offices", "founding price, €8 a vehicle", 2)]
rows = []
for i, (name, sub, n) in enumerate(fun):
    w = max(1.2, n / fun[0][2] * 100)
    last = i == len(fun) - 1
    if i:
        rows.append(f'<p class="go-on">{round(n / fun[i - 1][2] * 100)}% go on</p>')
    inside = w > 15
    lab = (f'<span class="bar-n" style="left:24px;color:#fff">{n}</span>' if inside
           else f'<span class="bar-n" style="left:calc({w}% + 16px)">{n}</span>')
    rows.append(f'<div class="bar-row"><div><p class="sm" style="font-size:26px;font-weight:600;color:var(--ink)">{name}</p>'
                f'<p class="sm" style="font-size:20px;line-height:1.3;color:var(--muted)">{sub}</p></div>'
                f'<div class="bar-track"><div class="bar{" on" if last else ""}" style="width:{w}%;{"background:var(--ink2)" if inside else ""}"></div>{lab}</div></div>')
pages.append(page("", f"""
{head("Go-to-market", "Start close to home: Northern Italy’s Alpine lanes.")}
<div class="row">
<div style="width:520px;flex:none;display:flex;flex-direction:column;gap:24px">
<p class="txt"><b>Beachhead:</b> offices with 6–100 vehicles on the Brenner, Fréjus, Mont Blanc and Tarvisio lanes, where the pain is highest and we can visit in a day. We sell in Italian, through people they already trust.</p>
<p class="txt">Our lists already name <b>92 companies</b> and <b>87 people</b>.</p>
<div class="panel sage"><p class="sm"><b>Measured so far:</b> 66 letters to companies brought 2 replies; 7 of 11 survey answers came through professors.</p></div>
</div>
<div class="grow" style="display:flex;flex-direction:column;gap:18px">
<p class="k">Plan for the first 90 days · assumptions</p>
{''.join(rows)}
</div>
</div>
""", "gtm"))

# 13 channels and expansion
chan = [("Founder-led, in person", "Register, maps and LinkedIn; first touch by phone or WhatsApp in Italian, then a 30-minute visit about one recent disruption", 60),
        ("Associations", "FAI Conftrasporto, CNA Fita, Confartigianato Trasporti, ANITA, Assotir; Fedespedi for forwarders: a member webinar and a discount", 25),
        ("Weekly digest by subscription", "The radar’s events for the coming week, free; readers who want their own shipments checked become leads", 10),
        ("Partners", "Transport software, telematics resellers, fuel-card companies: 20% of the first year as a referral fee", 5)]
crow = ''.join(f'<tr><td>{a}</td><td>{b}</td><td class="num"><span style="display:inline-block;width:{c * 3}px;height:16px;border-radius:8px;background:var(--red);margin-right:14px;vertical-align:middle"></span>{c}%</td></tr>' for a, b, c in chan)
pages.append(page("", f"""
{head("Go-to-market · channels", "Introductions work; cold letters do not.")}
<table class="t tight small">
<tr><th>Channel</th><th>How</th><th class="num">Customers, year 1</th></tr>
{crow}
</table>
<div class="row">
<div class="panel sage grow"><p class="k">Learned this month</p><p class="sm">66 letters, 2 replies; 7 of 11 answers through professors. Next: warm introductions through faculty, TEF and associations, and visits in person.</p></div>
<div class="panel grow"><p class="k">Expansion path</p><p class="sm"><b>1</b> Italy, Alpine lanes → <b>2</b> Italy South–North, blockades and ferries → <b>3</b> Austrian, German, Slovenian hauliers → <b>4</b> forwarders, per shipment → <b>5</b> an API across Europe</p></div>
</div>
""", "channels"))

# 14 operations
pages.append(page("", f"""
{head("Operations and technology", "AI reads; a person approves every alert.")}
<div class="steps4">
<div class="card"><p class="n">1</p><h3>Watch</h3><p class="sm">News in Italian, French, German and English, trade and official feeds, strike calendars, mountain weather. Agents read operators’ own pages every hour.</p></div>
<div class="card"><p class="n">2</p><h3>Check</h3><p class="sm">AI pulls out place, date, mode of transport and chance. Anything found by the radar or an agent stays “not checked by a person” until someone looks.</p></div>
<div class="card"><p class="n">3</p><h3>Match</h3><p class="sm">Each event against the office’s planned shipments: corridor, EU driving-time rules, ban rules of 7 countries in code, the cost of each option (chance × cost).</p></div>
<div class="card"><p class="n">4</p><h3>Warn and update</h3><p class="sm">WhatsApp only when a shipment is hit, with options and a decide-by time, then updates while it moves.</p></div>
</div>
<div class="tiles">
<div class="tile"><p class="k">Cost to run · assumptions</p><p class="sm">AI reading ≈ €160 a month; a person’s check ≈ 1 hour a day, €900 a month + €6 per office; WhatsApp and hosting a few euros per office.</p></div>
<div class="tile"><p class="k">Not done yet</p><p class="sm">The WhatsApp business line has no key and the site sends no email, so the beta stays closed until alerts go out on their own.</p></div>
</div>
""", "ops"))

# 15 team
pages.append(page("", f"""
{head("Team", "A student team at Bocconi, building fast with AI.")}
<div class="row">
<div class="grow" style="display:flex;flex-direction:column;gap:24px">
<div class="panel"><p class="k">Founders</p><p class="txt"><b>Oyu team</b>, three founders, Bocconi University, Milan. AI reads, drafts and checks figures; a person approves every alert and every letter.</p></div>
<div class="panel sage"><p class="k">Who opened doors</p><p class="sm">Bocconi faculty in transport and supply chains, among them Oliviero Baccelli, Pietro De Giovanni, Lanfranco Senn, Francesco Gallmann and Silvia Zamboni. Their links brought 7 of 11 survey answers.</p></div>
</div>
<div style="width:820px;flex:none">
<p class="k" style="margin-bottom:16px">Hiring plan · assumptions from the model</p>
<table class="t tight small">
<tr><th>When</th><th>Who</th><th class="num">A month</th></tr>
<tr><td>2027</td><td>Part-time reviewer of events, ≈1 h a day</td><td class="num">in €900</td></tr>
<tr><td>From Jul 2027</td><td>Founders’ stipends, each</td><td class="num">€1,000</td></tr>
<tr><td>Jan, Jul 2028</td><td>Two Italian sales people, each</td><td class="num">€3,200</td></tr>
<tr><td>Jan 2029</td><td>First engineer</td><td class="num">€4,500</td></tr>
<tr><td>Apr 2029</td><td>Operations</td><td class="num">€2,800</td></tr>
</table>
<p class="sm" style="margin-top:14px;color:var(--muted)">Stipends rise to €2,500 in 2028 and €3,500 in 2029.</p>
</div>
</div>
""", "team"))


# 16 financial chart (two panels, from docs/finplan.csv)
def fin_svg():
    W, H = 1664, 600
    rows = [{k: (v if k == "month" else float(v)) for k, v in r.items()} for r in FIN]
    n = len(rows)
    ink, ink2, muted, line, red, sage = "#352b28", "#554b45", "#675e57", "#e2dbcc", "#a2311e", "#2f5f45"
    grey = "#948774"
    out = [f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Inter, Arial, sans-serif">']
    # panel A
    ax0, ax1, ay0, ay1 = 110, 840, 70, 520
    maxA = 80000
    X = lambda i, a, b: a + i * (b - a) / (n - 1)
    YA = lambda v: ay1 - v / maxA * (ay1 - ay0)
    out.append(f'<text x="0" y="24" font-size="26" font-weight="600" fill="{ink}">Revenue and costs, a month</text>')
    for v in range(0, maxA + 1, 20000):
        out.append(f'<line x1="{ax0}" x2="{ax1}" y1="{YA(v)}" y2="{YA(v)}" stroke="{line if v else ink2}" stroke-width="{2 if v else 2}"/>')
        out.append(f'<text x="{ax0 - 14}" y="{YA(v) + 8}" font-size="22" text-anchor="end" fill="{muted}">{"0" if not v else f"€{v // 1000}k"}</text>')
    for i, r in enumerate(rows):
        if r["month"].endswith("-01"):
            x = X(i, ax0, ax1)
            out.append(f'<line x1="{x}" x2="{x}" y1="{ay0}" y2="{ay1}" stroke="{line}" stroke-width="2"/>')
            out.append(f'<text x="{x + 8}" y="{ay1 + 34}" font-size="22" fill="{muted}">{r["month"][:4]}</text>')
    cost = lambda r: r["cogs"] + r["opex"]
    pc = "M" + " L".join(f'{X(i, ax0, ax1):.1f} {YA(cost(r)):.1f}' for i, r in enumerate(rows))
    pr = "M" + " L".join(f'{X(i, ax0, ax1):.1f} {YA(r["mrr"]):.1f}' for i, r in enumerate(rows))
    out.append(f'<path d="{pc}" fill="none" stroke="{grey}" stroke-width="5" stroke-linejoin="round"/>')
    out.append(f'<path d="{pr}" fill="none" stroke="{red}" stroke-width="5" stroke-linejoin="round"/>')
    be = next(i for i in range(n) if all(rows[j]["ebitda"] >= 0 for j in range(i, n)))
    xb = X(be, ax0, ax1)
    out.append(f'<line x1="{xb}" x2="{xb}" y1="{ay0 + 10}" y2="{ay1}" stroke="{ink2}" stroke-width="2" stroke-dasharray="8 8"/>')
    m = rows[be]["month"]
    out.append(f'<text x="{xb - 12}" y="{ay0 + 34}" font-size="22" font-weight="600" text-anchor="end" fill="{ink}">Break-even, May {m[:4]}</text>')
    out.append(f'<text x="{ax1 - 6}" y="{YA(rows[-1]["mrr"]) - 16}" font-size="22" font-weight="600" text-anchor="end" fill="{red}">Revenue</text>')
    out.append(f'<text x="{ax1 - 6}" y="{YA(cost(rows[-1])) + 36}" font-size="22" text-anchor="end" fill="{muted}">Costs</text>')
    # panel B
    bx0, bx1, by0, by1 = 1010, 1650, 70, 520
    lowB = -160000
    YB = lambda v: by0 + v / lowB * (by1 - by0)
    out.append(f'<text x="{bx0 - 110}" y="24" font-size="26" font-weight="600" fill="{ink}">Cash before any funding</text>')
    for v in range(0, lowB - 1, -40000):
        out.append(f'<line x1="{bx0}" x2="{bx1}" y1="{YB(v)}" y2="{YB(v)}" stroke="{line if v else ink2}" stroke-width="2"/>')
        out.append(f'<text x="{bx0 - 14}" y="{YB(v) + 8}" font-size="22" text-anchor="end" fill="{muted}">{"0" if not v else f"−€{-v // 1000}k"}</text>')
    for i, r in enumerate(rows):
        if r["month"].endswith("-01"):
            x = X(i, bx0, bx1)
            out.append(f'<line x1="{x}" x2="{x}" y1="{by0}" y2="{by1}" stroke="{line}" stroke-width="2"/>')
            out.append(f'<text x="{x + 8}" y="{by1 + 34}" font-size="22" fill="{muted}">{r["month"][:4]}</text>')
    raise_ = 155000
    out.append(f'<line x1="{bx0}" x2="{bx1}" y1="{YB(-raise_)}" y2="{YB(-raise_)}" stroke="{sage}" stroke-width="3" stroke-dasharray="10 8"/>')
    out.append(f'<text x="{bx0 + 10}" y="{YB(-raise_) - 14}" font-size="22" font-weight="600" fill="{sage}">Planned funding €155k</text>')
    pcash = "M" + " L".join(f'{X(i, bx0, bx1):.1f} {YB(r["cash"]):.1f}' for i, r in enumerate(rows))
    out.append(f'<path d="{pcash}" fill="none" stroke="{ink2}" stroke-width="5" stroke-linejoin="round"/>')
    il = min(range(n), key=lambda i: rows[i]["cash"])
    lx, ly = X(il, bx0, bx1), YB(rows[il]["cash"])
    out.append(f'<circle cx="{lx}" cy="{ly}" r="10" fill="{red}"/>')
    out.append(f'<text x="{lx - 18}" y="{ly + 8}" font-size="22" font-weight="600" text-anchor="end" fill="{ink}">−€{round(-rows[il]["cash"] / 1000)}k, Apr {rows[il]["month"][:4]}</text>')
    out.append("</svg>")
    return "".join(out)


pages.append(page("", f"""
{head("Financial plan 2027–2029 · assumptions", "Revenue passes costs in May 2029; cash bottoms at −€124k.")}
{fin_svg()}
<p class="foot">Model: scripts/finplan.py, monthly table docs/finplan.csv. Every figure is an assumption, to be replaced with pilot data.</p>
""", "finchart"))

# 17 years and funding, with the weighing scene in the corner
pages.append(page("", f"""
<img class="scene-corner" src="funding-scale-corner.png" alt="" style="width:700px">
{head("Financial plan · by year and funding", "We plan to raise €155k: the lowest cash point plus a 25% reserve.")}
<div style="width:1100px">
<table class="t tight">
<tr><th>Year</th><th class="num">Offices, end</th><th class="num">ARR, end</th><th class="num">Revenue</th><th class="num">Gross margin</th><th class="num">EBITDA</th></tr>
<tr><td>2027</td><td class="num">15</td><td class="num">€34.6k</td><td class="num">€17.7k</td><td class="num">18%</td><td class="num">−€31.2k</td></tr>
<tr><td>2028</td><td class="num">80</td><td class="num">€246.7k</td><td class="num">€155.4k</td><td class="num">87%</td><td class="num">−€69.6k</td></tr>
<tr class="hl"><td>2029</td><td class="num">250</td><td class="num">€771.0k</td><td class="num">€543.9k</td><td class="num">93%</td><td class="num">+€75.3k</td></tr>
</table>
</div>
<div class="row" style="width:1180px">
<div class="tile grow"><p class="k">2027 · €40k</p><p class="sm">Pilots, the first 15 offices, founders’ stipends from July.</p></div>
<div class="tile grow"><p class="k">Early 2028 · €115k</p><p class="sm">Two Italian sales hires and the first engineer.</p></div>
<div class="tile grow"><p class="k">Where from</p><p class="sm">Bocconi’s accelerator and Italian start-up programmes once incorporated, then pre-seed after 10 paying offices.</p></div>
</div>
<p class="note" style="width:1100px">The 2027 margin is low because a person’s check costs about the same for 3 offices as for 15; with more offices on the same roads it rises to 87% and 93%.</p>
""", "funding"))

# 18 sensitivity
pages.append(page("", f"""
{head("Financial plan · what if we are wrong", "Price and the cost to win an office matter most.")}
<table class="t tight">
<tr><th>Scenario</th><th class="num">Break-even</th><th class="num">Money needed</th><th class="num">ARR, end 2029</th><th class="num">EBITDA 2029</th></tr>
<tr class="hl"><td>Base case</td><td class="num">May 2029</td><td class="num">€155k</td><td class="num">€771k</td><td class="num">+€75k</td></tr>
<tr><td>Price −33%, €8 a vehicle</td><td class="num">Nov 2029</td><td class="num">€325k</td><td class="num">€514k</td><td class="num">−€104k</td></tr>
<tr><td>Price +25%, €15 a vehicle</td><td class="num">Mar 2029</td><td class="num">€95k</td><td class="num">€964k</td><td class="num">+€210k</td></tr>
<tr><td>Churn 4% a month</td><td class="num">May 2029</td><td class="num">€165k</td><td class="num">€771k</td><td class="num">+€65k</td></tr>
<tr><td>Churn 1.5% a month</td><td class="num">May 2029</td><td class="num">€150k</td><td class="num">€771k</td><td class="num">+€82k</td></tr>
<tr><td>30% fewer offices</td><td class="num">Sep 2029</td><td class="num">€250k</td><td class="num">€540k</td><td class="num">−€41k</td></tr>
<tr><td>€1,200 to win an office</td><td class="num">Aug 2029</td><td class="num">€310k</td><td class="num">€771k</td><td class="num">−€56k</td></tr>
</table>
<p class="txt">At €8 a vehicle or €1,200 per office we would need <b>2–2.5 times the money</b>. So interviews test the price first, and associations, which make an office cheaper to win, come early.</p>
""", "sensitivity"))

# 19 spent so far
pages.append(page("", f"""
{head("Spent so far · September–November 2026", "About €520–540 in three months, all on software.")}
<div class="row">
<div class="grow">
<table class="t">
<tr><th>Service</th><th>What for</th><th class="num">Paid</th></tr>
<tr><td>Claude</td><td>Building the product, research, letters</td><td class="num">€125.83</td></tr>
<tr><td>ChatGPT</td><td>Research and checks</td><td class="num">€103.00</td></tr>
<tr><td>Higgsfield</td><td>Zholdas illustrations and scenes</td><td class="num">$258.00</td></tr>
<tr><td>Netlify</td><td>Site and radar hosting</td><td class="num">$77.98</td></tr>
<tr class="hl"><td>Total</td><td>three months of software</td><td class="num">≈ €520–540</td></tr>
</table>
<p class="note" style="margin-top:16px">The euro total depends on the dollar rate on each payment day.</p>
</div>
<div class="panel" style="width:520px;flex:none"><p class="k">No other costs</p><p class="sm">No salaries, no office, no paid advertising.</p><p class="k" style="margin-top:12px">Gaps in the receipts</p><p class="sm">Netlify invoices 1, 3 and 9 and the first Higgsfield invoice are missing; two Higgsfield documents are invoices, not receipts. A March Claude receipt from another account is left out.</p></div>
</div>
""", "spent"))

# 20 risks
pages.append(page("", f"""
{head("Risks", "Two big risks: the price, and reaching companies.")}
<table class="t tight small">
<tr><th>Risk</th><th>Early sign</th><th>What we do</th></tr>
<tr class="hl"><td>Price is wrong</td><td>€12 called too much, or €8 too little to matter</td><td>Four-price questions in every interview; founding price; a plan that charges only for verified savings</td></tr>
<tr class="hl"><td>Companies are hard to reach</td><td>Already seen: 2 replies from 66 letters</td><td>Warm introductions through faculty, TEF and associations; visits; the free weekly digest</td></tr>
<tr><td>Software vendors add alerts</td><td>Qargo or a telematics vendor ships them</td><td>Start with offices on Excel and WhatsApp; sell our checked events to vendors as an API</td></tr>
<tr><td>A wrong alert costs trust</td><td>Pilots mark alerts as useless</td><td>A person checks every alert; the forecast log is public; false alerts are counted</td></tr>
<tr><td>Offices won’t share plans</td><td>Pilots stall at the upload</td><td>Excel or a photo, only the fields we need, EU hosting</td></tr>
<tr><td>Too few unplanned hits</td><td>Under one useful alert a week</td><td>Widen to South–North lanes, blockades and ferries, or sell per corridor</td></tr>
<tr><td>Sending not automated yet</td><td>The beta opens late</td><td>WhatsApp business key and email before the beta opens</td></tr>
<tr><td>Founders’ time</td><td>Studies take the hours</td><td>A small paid reviewer early; stipends from July 2027</td></tr>
</table>
""", "risks"))


# 21 milestones timeline
def timeline_svg():
    items = [("Final TEF pitch", "the video, due 1 December", "2026-12-01", "2026-12-01", False),
             ("Alerts go out; beta opens", "WhatsApp line and email work on their own", "2026-12-01", "2027-01-31", False),
             ("8 interviews and replays", "2 offices share a past month; we show what we’d flag", "2026-12-07", "2027-01-31", False),
             ("Raise the first €40k", "pilots and the first 15 offices covered", "2027-01-01", "2027-04-30", False),
             ("2 live pilots", "≥80% of alerts useful; a check under 90 s an event", "2027-02-01", "2027-03-31", False),
             ("First 2 paying offices", "founding price, case study, reference call", "2027-03-31", "2027-03-31", False),
             ("South–North and ferries", "blockades, ferries, the Strait of Messina", "2027-07-01", "2027-09-30", False),
             ("15 paying offices", "the model’s target for 2027", "2027-12-31", "2027-12-31", True)]
    from datetime import date
    d = lambda s: date.fromisoformat(s).toordinal()
    lo, hi = d("2026-12-01"), d("2028-01-01")
    W, H = 1664, 640
    x0, x1 = 760, 1600
    X = lambda s: x0 + (d(s) - lo) / (hi - lo) * (x1 - x0)
    ink, muted, line, red, bar = "#352b28", "#675e57", "#e2dbcc", "#a2311e", "#948774"
    out = [f'<svg viewBox="0 -24 {W} {H}" width="{W}" height="{H}" font-family="Inter, Arial, sans-serif">']
    months = []
    y, m = 2026, 12
    while (y, m) <= (2028, 1):
        months.append(f"{y}-{m:02d}-01")
        m += 1
        if m == 13:
            y, m = y + 1, 1
    names = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
    for s in months:
        out.append(f'<line x1="{X(s)}" x2="{X(s)}" y1="40" y2="{H - 10}" stroke="{line}" stroke-width="2"/>')
    out.append(f'<text x="{X("2026-12-01") + 6}" y="-2" font-size="20" font-weight="600" fill="{ink}">2026</text>')
    out.append(f'<text x="{X("2027-01-01") + 6}" y="-2" font-size="20" font-weight="600" fill="{ink}">2027</text>')
    for s in months[:-1]:
        mm = int(s[5:7])
        lab = names[mm - 1]
        out.append(f'<text x="{X(s) + 6}" y="28" font-size="20" fill="{muted}">{lab}</text>')
    for i, (nm, sub, a, b, goal) in enumerate(items):
        yc = 84 + i * 70
        out.append(f'<text x="0" y="{yc - 2}" font-size="28" font-weight="600" fill="{ink}">{esc(nm)}</text>')
        out.append(f'<text x="0" y="{yc + 28}" font-size="21" fill="{muted}">{esc(sub)}</text>')
        c = red if goal else bar
        if a == b:
            xa = X(a)
            out.append(f'<path d="M{xa} {yc - 16} l16 16 l-16 16 l-16 -16z" fill="{c}"/>')
            out.append(f'<text x="{xa + (-26 if goal else 26)}" y="{yc + 8}" font-size="22" font-weight="{600 if goal else 400}" text-anchor="{"end" if goal else "start"}" fill="{red if goal else muted}">{"by " if a != "2026-12-01" else ""}{names[int(a[5:7]) - 1]} {int(a[8:])}</text>')
        else:
            out.append(f'<rect x="{X(a)}" y="{yc - 16}" width="{X(b) - X(a)}" height="32" rx="16" fill="{c}"/>')
    out.append("</svg>")
    return "".join(out)


pages.append(page("", f"""
{head("Milestones · next 12 months", "Pilots first, then 15 paying offices in 2027.")}
{timeline_svg()}
""", "milestones"))

# 22 sources
pages.append(page("", f"""
{head("Sources", "Measured by us, public data, and our own models.")}
<div class="cards three">
<div class="card"><p class="k">Measured by us</p><ul class="l">
<li>Survey of traffic offices and people in the field, 9–26 Nov 2026: zhol.live/results</li>
<li>Forecast log, 13–26 Nov 2026: data/radar_log, scored by zhol/radar/verify.py</li>
<li>Outreach log: letters, replies, introductions (private)</li>
<li>Software receipts, Sep–Nov 2026</li></ul></div>
<div class="card"><p class="k">Public data</p><ul class="l">
<li>Albo Nazionale degli Autotrasportatori, firms by fleet size and region, 31 Mar 2025</li>
<li>ACEA and Eurostat: EU trucks and international work</li>
<li>Berg Insight, transport management software in Europe, 2025</li>
<li>Italian ministry strike calendar; Fréjus, Mont Blanc, Tyrol dosing, Trenitalia pages</li>
<li>D.Lgs. 286/2005 art. 6-bis and L. 105/2025, waiting compensation</li></ul></div>
<div class="card"><p class="k">Our models</p><ul class="l">
<li>docs/18-model.md: the forecast model</li>
<li>docs/03-business-model.md: savings and unit economics</li>
<li>docs/13-financial-plan.md and scripts/finplan.py: the 36-month plan</li>
<li>docs/02-competitors.md: prices of the others</li></ul></div>
</div>
""", "sources"))

# 23 close
pages.append(page("", f"""
<img class="bleed" src="close-ferry-deck.jpg" alt="">
<div class="veil narrow"></div>
<div class="col" style="width:760px">
<p class="eyebrow">Thank you</p>
<img class="logo" src="zhol-logo.png" alt="zhol">
<p class="lead">Estimates the risk, warns in advance, updates in real time.</p>
<div class="end-row"><div class="qr">{QR}</div><div><p class="end-url">zhol.live</p><p class="sm">The radar is open to everyone. The beta for traffic offices is on the way.</p></div></div>
</div>
<p class="foot">Oyu team · Bocconi University, Milan</p>
""", "close"))

doc = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>zhol business plan</title>'
       f'<style>{DECK_CSS}\n{EXTRA}</style></head><body>\n' + "\n".join(pages) + "\n</body></html>")
(HERE / "bizplan.html").write_text(doc)
print(len(pages), "pages")
