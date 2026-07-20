#!/usr/bin/env python3
"""Generate the standalone marketing landing pages ("brochures") for the
PandaTech systems that share ONE template.

Each brochure is a self-contained RTL HTML file (inline CSS+JS, no build step),
public and standalone (no link back into the app), with a "leave your details"
form that POSTs to the shared central endpoint  POST /api/public/leads  (SendMSG,
the marketing system) → leads table + Resend notification, and (when a phone is
given) a promoted prospect that Hila follows up on (approval-gated).

This script is the single source of truth for these systems' brochures. To
update a brochure with new capabilities (per the CLAUDE.md rule), edit its entry
in SYSTEMS below and re-run:  python3 generate.py

It writes each brochure to TWO places:
  1. The system's own repo (public/landing.html for web apps, landing/index.html
     otherwise) — so the file lives with the code.
  2. dist/<id>/index.html here — the ONE shared static host that serves the
     systems with no web frontend, path per system (/pandoosh, /argus, …).

NOTE: PandaPower and PandaSkill are intentionally NOT generated here — they are
hand-maintained and served from their own frontends. This generator owns the
other six.
"""

import os

ENDPOINT = "https://send-msg-zeta.vercel.app/api/public/leads"
FALLBACK_EMAIL = "avishai.lebenzon@gmail.com"
HERE = os.path.dirname(os.path.abspath(__file__))

# ── icon vocabulary (Lucide-style inner SVG, stroked) ───────────────────────
ICONS = {
    "bubble": '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/>',
    "link": '<path d="M10 13a5 5 0 0 0 7 0l3-3a5 5 0 0 0-7-7l-1 1"/><path d="M14 11a5 5 0 0 0-7 0l-3 3a5 5 0 0 0 7 7l1-1"/>',
    "pen": '<path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/>',
    "shieldcheck": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/><path d="m9 12 2 2 4-4"/>',
    "route": '<circle cx="6" cy="19" r="3"/><path d="M9 19h8.5a3.5 3.5 0 0 0 0-7h-11a3.5 3.5 0 0 1 0-7H15"/><circle cx="18" cy="5" r="3"/>',
    "lock": '<rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
    "grid": '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/>',
    "refresh": '<path d="M3 12a9 9 0 0 1 15-6.7L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-15 6.7L3 16"/><path d="M3 21v-5h5"/>',
    "spark": '<path d="M12 3v4"/><path d="m16.2 7.8 2.9-2.9"/><path d="M18 12h4"/><path d="M12 18v3"/><path d="M4.9 19.1 7.8 16.2"/><path d="M2 12h4"/><circle cx="12" cy="12" r="3"/>',
    "file": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="m9 15 2 2 4-4"/>',
    "chart": '<path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/>',
    "target": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    "map": '<path d="m9 3-6 3v15l6-3 6 3 6-3V3l-6 3z"/><path d="M9 3v15"/><path d="M15 6v15"/>',
    "activity": '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
    "eyeoff": '<path d="M9.9 4.24A9.1 9.1 0 0 1 12 4c7 0 10 8 10 8a13.2 13.2 0 0 1-1.67 2.68"/><path d="M6.6 6.6A13.1 13.1 0 0 0 2 12s3 8 10 8a9.3 9.3 0 0 0 5.4-1.6"/><path d="m2 2 20 20"/>',
    "calendar": '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4"/><path d="M8 2v4"/><path d="M3 10h18"/>',
    "sun": '<path d="M12 2v4"/><path d="m4.9 4.9 2.9 2.9"/><path d="M2 12h4"/><path d="M18 12h4"/><path d="m16.2 7.8 2.9-2.9"/><circle cx="12" cy="13" r="4"/>',
    "check": '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="m9 12 2 2 4-4"/>',
    "layers": '<path d="m12 2 9 5-9 5-9-5 9-5Z"/><path d="m3 12 9 5 9-5"/><path d="m3 17 9 5 9-5"/>',
    "wifioff": '<path d="M12 20h.01"/><path d="M8.5 16.5a5 5 0 0 1 7 0"/><path d="M2 8.8a15 15 0 0 1 4.2-2.6"/><path d="M20 8.8a15 15 0 0 0-5-3.3"/><path d="m2 2 20 20"/>',
    "pie": '<path d="M21 15.5A9 9 0 1 1 8.5 3"/><path d="M21 12A9 9 0 0 0 12 3v9z"/>',
    "trace": '<circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="m8.6 13.5 6.8 4M15.4 6.5l-6.8 4"/>',
    "star": '<polygon points="12 2 15 9 22 9 16 14 18 21 12 17 6 21 8 14 2 9 9 9"/>',
}

# ── the shared template (%%TOKEN%% placeholders → .replace) ──────────────────
TEMPLATE = r"""<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>%%TITLE%%</title>
<meta name="description" content="%%META_DESC%%" />
<meta property="og:title" content="%%OG_TITLE%%" />
<meta property="og:description" content="%%OG_DESC%%" />
<meta property="og:type" content="website" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;700;800;900&display=swap" rel="stylesheet" />
<style>
  :root { --accent: %%ACCENT%%; --accent-2: %%ACCENT2%%; --bg: %%BG%%; --bg-soft: %%BG_SOFT%%; --card: rgba(255,255,255,.04); --card-brd: rgba(255,255,255,.09); --txt: #e8eef7; --muted: #9aabc0; --ok: #34d399; --err: #f87171; --radius: 18px; --maxw: 1080px; }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; }
  body { font-family: "Heebo", system-ui, -apple-system, "Segoe UI", Arial, sans-serif; background: var(--bg); color: var(--txt); line-height: 1.6; -webkit-font-smoothing: antialiased; overflow-x: hidden; }
  a { color: inherit; }
  .wrap { max-width: var(--maxw); margin: 0 auto; padding: 0 22px; }
  .btn { display: inline-flex; align-items: center; gap: 10px; cursor: pointer; border: 0; border-radius: 999px; padding: 15px 30px; font-family: inherit; font-size: 17px; font-weight: 700; color: #0a0f1a; background: linear-gradient(135deg, var(--accent), var(--accent-2)); box-shadow: 0 10px 30px -8px color-mix(in srgb, var(--accent) 60%, transparent); transition: transform .15s ease, box-shadow .15s ease; text-decoration: none; }
  .btn:hover { transform: translateY(-2px); box-shadow: 0 16px 40px -10px color-mix(in srgb, var(--accent) 70%, transparent); }
  .btn[disabled] { opacity: .6; cursor: default; transform: none; }
  .glow { position: fixed; inset: 0; z-index: 0; pointer-events: none; overflow: hidden; }
  .glow::before, .glow::after { content: ""; position: absolute; width: 620px; height: 620px; border-radius: 50%; filter: blur(120px); opacity: .35; }
  .glow::before { background: var(--accent); top: -180px; inset-inline-start: -120px; }
  .glow::after  { background: var(--accent-2); bottom: -220px; inset-inline-end: -140px; opacity: .22; }
  header, main, footer { position: relative; z-index: 1; }
  .topbar { display: flex; align-items: center; justify-content: space-between; padding: 22px 0; }
  .brand { display: flex; align-items: center; gap: 12px; font-weight: 900; font-size: 22px; letter-spacing: -.5px; }
  .brand .dot { width: 34px; height: 34px; border-radius: 10px; background: linear-gradient(135deg, var(--accent), var(--accent-2)); display: grid; place-items: center; font-size: 18px; }
  .badge { font-size: 13px; color: var(--muted); border: 1px solid var(--card-brd); border-radius: 999px; padding: 6px 14px; }
  .hero { padding: 60px 0 40px; text-align: center; }
  .hero .kicker { display: inline-block; color: var(--accent-2); font-weight: 700; font-size: 15px; letter-spacing: .5px; margin-bottom: 18px; border: 1px solid var(--card-brd); border-radius: 999px; padding: 7px 16px; background: var(--card); }
  .hero h1 { font-size: clamp(36px, 6vw, 66px); line-height: 1.06; font-weight: 900; letter-spacing: -1.5px; margin: 0 0 20px; }
  .hero h1 .grad { background: linear-gradient(120deg, var(--accent), var(--accent-2)); -webkit-background-clip: text; background-clip: text; color: transparent; }
  .hero p.lead { font-size: clamp(17px, 2.4vw, 22px); color: var(--muted); max-width: 720px; margin: 0 auto 30px; }
  .hero .cta-row { display: flex; gap: 14px; justify-content: center; flex-wrap: wrap; }
  .ghost { background: var(--card); color: var(--txt); border: 1px solid var(--card-brd); box-shadow: none; }
  .ghost:hover { box-shadow: none; background: rgba(255,255,255,.07); }
  .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin: 46px 0; }
  .stat { background: var(--card); border: 1px solid var(--card-brd); border-radius: var(--radius); padding: 22px; text-align: center; }
  .stat b { display: block; font-size: 28px; font-weight: 900; background: linear-gradient(120deg, var(--accent), var(--accent-2)); -webkit-background-clip: text; background-clip: text; color: transparent; }
  .stat span { color: var(--muted); font-size: 15px; }
  section.block { padding: 46px 0; }
  .sec-head { text-align: center; max-width: 640px; margin: 0 auto 38px; }
  .sec-head h2 { font-size: clamp(28px, 4vw, 40px); font-weight: 900; letter-spacing: -1px; margin: 0 0 12px; }
  .sec-head p { color: var(--muted); font-size: 18px; margin: 0; }
  .features { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; }
  .feature { background: var(--card); border: 1px solid var(--card-brd); border-radius: var(--radius); padding: 26px; transition: transform .15s ease, border-color .15s ease; }
  .feature:hover { transform: translateY(-4px); border-color: color-mix(in srgb, var(--accent) 45%, var(--card-brd)); }
  .feature .ico { width: 48px; height: 48px; border-radius: 12px; display: grid; place-items: center; margin-bottom: 16px; background: color-mix(in srgb, var(--accent) 18%, transparent); }
  .feature .ico svg { width: 26px; height: 26px; stroke: var(--accent-2); fill: none; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }
  .feature h3 { margin: 0 0 8px; font-size: 20px; font-weight: 800; }
  .feature p { margin: 0; color: var(--muted); font-size: 15.5px; }
  .benefits { display: grid; grid-template-columns: 1fr 1fr; gap: 14px 30px; max-width: 820px; margin: 0 auto; }
  .benefit { display: flex; gap: 12px; align-items: flex-start; background: var(--card); border: 1px solid var(--card-brd); border-radius: 14px; padding: 16px 18px; }
  .benefit .chk { color: var(--ok); font-weight: 900; font-size: 18px; margin-top: 1px; }
  .benefit b { font-weight: 700; }
  .benefit span { color: var(--muted); }
  .lead { background: linear-gradient(180deg, var(--bg-soft), var(--bg)); border-top: 1px solid var(--card-brd); }
  .lead-card { background: var(--card); border: 1px solid var(--card-brd); border-radius: 24px; padding: 40px; max-width: 640px; margin: 0 auto; }
  .lead-card h2 { text-align: center; font-size: clamp(26px, 3.6vw, 34px); font-weight: 900; margin: 0 0 8px; }
  .lead-card .sub { text-align: center; color: var(--muted); margin: 0 0 28px; font-size: 17px; }
  form .grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
  .field { margin-bottom: 14px; }
  .field label { display: block; font-size: 14px; color: var(--muted); margin-bottom: 6px; font-weight: 500; }
  .field label .opt { color: #64748b; font-weight: 400; }
  .field input { width: 100%; padding: 14px 16px; border-radius: 12px; font-family: inherit; font-size: 16px; background: rgba(255,255,255,.04); border: 1px solid var(--card-brd); color: var(--txt); outline: none; transition: border-color .15s ease, box-shadow .15s ease; }
  .field input::placeholder { color: #64748b; }
  .field input:focus { border-color: var(--accent); box-shadow: 0 0 0 3px color-mix(in srgb, var(--accent) 25%, transparent); }
  .field input.invalid { border-color: var(--err); }
  .hp { position: absolute; left: -9999px; width: 1px; height: 1px; overflow: hidden; }
  form .btn { width: 100%; justify-content: center; margin-top: 8px; }
  .form-note { text-align: center; color: var(--muted); font-size: 13px; margin-top: 14px; }
  .msg { text-align: center; padding: 12px; border-radius: 12px; margin-top: 16px; font-weight: 600; display: none; }
  .msg.show { display: block; }
  .msg.err { background: color-mix(in srgb, var(--err) 15%, transparent); color: var(--err); }
  .success-state { text-align: center; padding: 20px 0; }
  .success-state .big { font-size: 54px; }
  .success-state h3 { font-size: 26px; margin: 8px 0; }
  .success-state p { color: var(--muted); margin: 0; }
  footer { border-top: 1px solid var(--card-brd); padding: 30px 0; text-align: center; color: var(--muted); font-size: 14px; }
  @media (max-width: 820px) { .features, .stats { grid-template-columns: 1fr; } .benefits { grid-template-columns: 1fr; } form .grid2 { grid-template-columns: 1fr; } .lead-card { padding: 26px; } }
  @media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
</style>
</head>
<body>
<div class="glow" aria-hidden="true"></div>
<header><div class="wrap topbar"><div class="brand"><span class="dot">%%EMOJI%%</span> %%BRAND%%</div><span class="badge">%%BADGE%%</span></div></header>
<main>
  <section class="wrap hero">
    <span class="kicker">%%KICKER%%</span>
    <h1>%%H1%%</h1>
    <p class="lead">%%LEAD%%</p>
    <div class="cta-row"><a href="#lead" class="btn">%%CTA1%%</a><a href="#features" class="btn ghost">%%CTA2%%</a></div>
  </section>
  <section class="wrap"><div class="stats">%%STATS%%</div></section>
  <section class="wrap block" id="features">
    <div class="sec-head"><h2>%%FEAT_H%%</h2><p>%%FEAT_SUB%%</p></div>
    <div class="features">%%FEATURES%%</div>
  </section>
  <section class="wrap block">
    <div class="sec-head"><h2>%%BEN_H%%</h2><p>%%BEN_SUB%%</p></div>
    <div class="benefits">%%BENEFITS%%</div>
  </section>
</main>
<section class="lead block" id="lead"><div class="wrap"><div class="lead-card">
  <div id="formView">
    <h2>%%FORM_H%%</h2>
    <p class="sub">%%FORM_SUB%%</p>
    <form id="leadForm" novalidate>
      <div class="grid2">
        <div class="field"><label for="first_name">שם פרטי</label><input id="first_name" name="first_name" type="text" autocomplete="given-name" placeholder="ישראל" required /></div>
        <div class="field"><label for="last_name">שם משפחה</label><input id="last_name" name="last_name" type="text" autocomplete="family-name" placeholder="ישראלי" required /></div>
      </div>
      <div class="field"><label for="email">אימייל</label><input id="email" name="email" type="email" autocomplete="email" placeholder="you@company.com" required /></div>
      <div class="field"><label for="phone">טלפון <span class="opt">(לא חובה)</span></label><input id="phone" name="phone" type="tel" autocomplete="tel" placeholder="050-0000000" /></div>
      <div class="hp" aria-hidden="true"><label>אל תמלאו שדה זה<input type="text" name="company_website" tabindex="-1" autocomplete="off" /></label></div>
      <button type="submit" class="btn" id="submitBtn">שליחת פרטים</button>
      <div class="form-note">הפרטים נשמרים אצלנו בלבד לצורך יצירת קשר. ללא ספאם.</div>
      <div class="msg err" id="errMsg"></div>
    </form>
  </div>
  <div id="successView" class="success-state" style="display:none"><div class="big">🎉</div><h3>תודה! קיבלנו את הפרטים</h3><p>נחזור אליכם בהקדם.</p></div>
</div></div></section>
<footer><div class="wrap">%%FOOTER%%</div></footer>
<script>
  var CONFIG = { systemId: "%%SYSTEM_ID%%", endpoint: "%%ENDPOINT%%", fallbackEmail: "%%FALLBACK%%" };
  (function () {
    var form = document.getElementById("leadForm"), errMsg = document.getElementById("errMsg"), btn = document.getElementById("submitBtn");
    function showErr(t){ errMsg.textContent = t; errMsg.classList.add("show"); }
    function clearErr(){ errMsg.classList.remove("show"); }
    function validEmail(v){ return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v); }
    form.addEventListener("submit", function (e) {
      e.preventDefault(); clearErr();
      var first = form.first_name.value.trim(), last = form.last_name.value.trim(), email = form.email.value.trim(), phone = form.phone.value.trim();
      [form.first_name, form.last_name, form.email].forEach(function (el){ el.classList.remove("invalid"); });
      var bad = false;
      if (!first) { form.first_name.classList.add("invalid"); bad = true; }
      if (!last) { form.last_name.classList.add("invalid"); bad = true; }
      if (!validEmail(email)) { form.email.classList.add("invalid"); bad = true; }
      if (bad) { showErr("נא למלא שם פרטי, שם משפחה ואימייל תקין."); return; }
      btn.disabled = true; btn.textContent = "שולח…";
      var payload = { system: CONFIG.systemId, first_name: first, last_name: last, email: email, phone: phone, company_website: form.company_website.value };
      fetch(CONFIG.endpoint, { method: "POST", headers: { "Content-Type": "text/plain;charset=utf-8" }, body: JSON.stringify(payload) })
        .then(function (res){ if (!res.ok) throw new Error("bad status " + res.status); document.getElementById("formView").style.display = "none"; document.getElementById("successView").style.display = "block"; })
        .catch(function (){ btn.disabled = false; btn.textContent = "שליחת פרטים"; showErr("השליחה נכשלה. אפשר לפנות אלינו ישירות במייל: " + CONFIG.fallbackEmail); });
    });
  })();
</script>
</body>
</html>
"""


def render(sys):
    def feats(items):
        return "".join(
            f'<div class="feature"><div class="ico"><svg viewBox="0 0 24 24">{ICONS[i]}</svg></div>'
            f"<h3>{t}</h3><p>{p}</p></div>"
            for (i, t, p) in items
        )

    def stats(items):
        return "".join(f'<div class="stat"><b>{b}</b><span>{s}</span></div>' for (b, s) in items)

    def bens(items):
        return "".join(
            f'<div class="benefit"><span class="chk">✓</span><div><b>{b}</b> <span>{s}</span></div></div>'
            for (b, s) in items
        )

    html = TEMPLATE
    repl = {
        "TITLE": sys["title"], "META_DESC": sys["meta_desc"],
        "OG_TITLE": sys.get("og_title", sys["brand"]), "OG_DESC": sys.get("og_desc", sys["meta_desc"]),
        "ACCENT": sys["accent"], "ACCENT2": sys["accent2"], "BG": sys["bg"], "BG_SOFT": sys["bg_soft"],
        "EMOJI": sys["emoji"], "BRAND": sys["brand"], "BADGE": sys["badge"],
        "KICKER": sys["kicker"], "H1": sys["h1"], "LEAD": sys["lead"],
        "CTA1": sys.get("cta1", "לשמוע עוד →"), "CTA2": sys.get("cta2", "מה זה עושה"),
        "STATS": stats(sys["stats"]), "FEAT_H": sys["feat_h"], "FEAT_SUB": sys["feat_sub"],
        "FEATURES": feats(sys["features"]), "BEN_H": sys["ben_h"], "BEN_SUB": sys["ben_sub"],
        "BENEFITS": bens(sys["benefits"]),
        "FORM_H": sys.get("form_h", "מתעניינים? נשמח לספר עוד"),
        "FORM_SUB": sys.get("form_sub", "השאירו פרטים ונחזור אליכם."),
        "FOOTER": sys["footer"], "SYSTEM_ID": sys["id"], "ENDPOINT": ENDPOINT, "FALLBACK": FALLBACK_EMAIL,
    }
    for k, v in repl.items():
        html = html.replace(f"%%{k}%%", v)
    return html


SYSTEMS = [
    {
        "id": "sendmsg", "emoji": "💬", "brand": "SendMSG",
        "accent": "#6d5efc", "accent2": "#22d3ee", "bg": "#0b0d1a", "bg_soft": "#121424",
        "repo_path": "/Users/Avishai/Developer/SendMSG/public/landing.html", "shared_host": False,
        "title": "SendMSG — כל התקשורת היוצאת בערוץ אחד חכם",
        "meta_desc": "SendMSG מאחדת וואטסאפ, אימייל ותוכן סושיאל למרכז בקרה אחד — עם יצירת תוכן מבוססת AI ובקרה אנושית על כל שליחה.",
        "badge": "תקשורת יוצאת חכמה · מבית PandaTech",
        "kicker": "פנייה יזומה בקנה מידה — בלי לאבד את המגע האישי",
        "h1": 'כל התקשורת היוצאת שלך<br /><span class="grad">בערוץ אחד חכם</span>',
        "lead": "SendMSG מאחדת וואטסאפ, אימייל ותוכן סושיאל למרכז בקרה יחיד — עם יצירת תוכן מבוססת AI, סנכרון ל-Pipedrive, ובקרה אנושית על כל שליחה.",
        "cta1": "לשמוע עוד →", "cta2": "מה המערכת עושה",
        "stats": [("רב-ערוצי", "וואטסאפ · מייל · סושיאל"), ("AI + אישור אנושי", "תוכן חכם, שליטה מלאה"), ("Pipedrive", "מסתנכרן אוטומטית")],
        "feat_h": "מה SendMSG עושה", "feat_sub": "פנייה יזומה חכמה, ממותגת ומבוקרת.",
        "features": [
            ("bubble", "תקשורת רב-ערוצית מאוחדת", "וואטסאפ, אימייל וסושיאל בממשק ניהול אחד — במקום לקפוץ בין מערכות."),
            ("users", 'סוכנת AI "הילה"', "מיתוג אחיד לכל הודעה יוצאת, וגילוי AI שקוף בפנייה הראשונה."),
            ("link", "סנכרון עם Pipedrive", "ניהול מועמדים, עובדים ולקוחות — מסתנכרן אוטומטית עם ה-CRM."),
            ("target", "התאמת AI חכמה", "מדרגת עובדים למשרות (0–100) ומפעילה פנייה יזומה ממוקדת."),
            ("pen", "יצירת תוכן מבוססת AI", "פוסטים לסושיאל, ניוזלטרים, פודקאסטים וסרטוני אוואטר — בלחיצה."),
            ("shieldcheck", "שליטה מלאה", "תור אישורים אנושי, בקרת קצב שליחה וניהול opt-out/הרשמה."),
        ],
        "ben_h": "למה זה עובד", "ben_sub": "קנה מידה בלי לאבד את האישי ואת השליטה.",
        "benefits": [
            ("סקייל אמיתי.", "פנייה יזומה להרבה אנשים, בלי צוות ענק."),
            ("מגע אישי.", "כל הודעה ממותגת ומותאמת, לא דיוור גנרי."),
            ("אישור אנושי.", "שום דבר לא יוצא בלי שאדם אישר."),
            ("ערוץ אחד.", "כל התקשורת היוצאת במקום אחד."),
            ("תוכן ב-AI.", "מפוסט ועד פודקאסט — נוצר אוטומטית."),
            ("בטוח.", "בקרת קצב ו-opt-out מובנים."),
        ],
        "form_h": "רוצים לשמוע עוד?", "form_sub": "השאירו פרטים ונחזור אליכם עם הדגמה.",
        "footer": "© SendMSG · תקשורת יוצאת חכמה · מבית PandaTech",
    },
    {
        "id": "pandoosh", "emoji": "🐼", "brand": "Pandoosh",
        "accent": "#14b8a6", "accent2": "#34d399", "bg": "#06140f", "bg_soft": "#0b1a15",
        "repo_path": "/Users/Avishai/Developer/Pandoosh/landing/index.html", "shared_host": True,
        "title": "Pandoosh — קונסיירז' ה-HR של העובד, בוואטסאפ",
        "meta_desc": "פנדוש הוא קונסיירז' HR חכם בוואטסאפ: עונה מיד על נהלים ומדיניות, ומטפל בכל השאר מקצה לקצה — בלי להפנות אף עובד החוצה.",
        "badge": "קונסיירז' HR בוואטסאפ · מבית PandaTech",
        "kicker": "לשכת השירות הדיגיטלית של העובד — ערוץ אחד לכל דבר",
        "h1": 'כל שאלה של עובד,<br /><span class="grad">נענית בוואטסאפ</span>',
        "lead": "פנדוש הוא קונסיירז' HR חכם שחי בוואטסאפ של העובדים: עונה מיד על נהלים ומדיניות מתוך מאגר הידע, ומטפל בכל השאר בעצמו — אוסף פרטים, מנתב לבעל התפקיד, ועוקב עד שהתשובה חוזרת.",
        "cta1": "לשמוע עוד →", "cta2": "איך זה עובד",
        "stats": [("24/7", "מענה מיידי, בכל שעה"), ("ערוץ אחד", "הכל בוואטסאפ של העובד"), ("אפס הפניות", "פנדוש סופג ומחזיר תשובה")],
        "feat_h": "מה פנדוש עושה", "feat_sub": "חוויית עובד אחידה, ועומס נמוך על ה-HR.",
        "features": [
            ("bubble", "מענה עצמי מיידי", "שאלות נהלים ומדיניות נענות לבד ומיד, מתוך מאגר הידע הארגוני."),
            ("route", "ניתוב חכם לבעלי תפקיד", "איסוף פרטים בשיחה, מעקב SLA, תזכורות והסלמה — עד שהתשובה חוזרת."),
            ("lock", "זיהוי עובד ואימות OTP", "כל שיחה מבודדת ומאובטחת לעובד בודד."),
            ("grid", "פאנל ניהול מלא", "דשבורד, ניהול נושאים, מאגר ידע ולוח בקשות (Kanban)."),
            ("refresh", "סנכרון ידע אוטומטי", "קבצים מ-Google Drive/Dropbox, וניהול מסמכי עובד עם כללי ציות."),
            ("spark", "שיפור-עצמי יומי", "מזהה פערי ידע ומעשיר את בסיס הידע אוטומטית."),
        ],
        "ben_h": "למה זה משנה", "ben_sub": "פחות רדיפה אחרי תשובות, יותר ראש שקט.",
        "benefits": [
            ("אף עובד לא מופנה החוצה.", "פנדוש סופג הכל ומחזיר תשובה."),
            ("מיידי.", "מענה על נהלים תוך שניות, 24/7."),
            ("עומס HR יורד.", "השגרתי נענה לבד; אנשים מטפלים בחריג."),
            ("מאובטח.", "אימות OTP ובידוד שיחה לכל עובד."),
            ("מתועד.", "Audit trail מלא לכל פנייה."),
            ("משתפר לבד.", "לומד מפערי ידע ומעשיר את עצמו."),
        ],
        "footer": "© Pandoosh · קונסיירז' HR בוואטסאפ · מבית PandaTech",
    },
    {
        "id": "argus", "emoji": "🛡️", "brand": "Argus",
        "accent": "#2f6fb3", "accent2": "#38bdf8", "bg": "#070d15", "bg_soft": "#0c141f",
        "repo_path": "/Users/Avishai/Developer/Argus/landing/index.html", "shared_host": True,
        "title": "Argus — ראיות קבילות לעמידה ב-IEC 60880",
        "meta_desc": "Argus הוא מנתח סטטי לתוכנת בקרה גרעינית (קטגוריה A) שמייצר חבילת ראיות חתומה וקבילה לרגולטור — עם עקיבות מלאה מהתקן ועד כל ממצא.",
        "badge": "ניתוח סטטי · תוכנת בטיחות גרעינית · IEC 60880",
        "kicker": "ראיות קבילות לרגולטור — לא רק אזהרות",
        "h1": 'הוכחת עמידה ב-IEC 60880,<br /><span class="grad">דטרמיניסטית ומתועדת</span>',
        "lead": "Argus הוא מנתח סטטי ייעודי לתוכנת בקרה גרעינית בקטגוריית הבטיחות הגבוהה ביותר (Category A). הוא מייצר חבילת ראיות חתומה וקבילה לרגולטור — עם עקיבות מלאה מסעיף התקן ועד כל ממצא והחלטה.",
        "cta1": "לשמוע עוד →", "cta2": "מה הוא עושה",
        "stats": [("Category A", "רמת הבטיחות הגבוהה ביותר"), ("94 כללים", "ממופים לסעיפי IEC 60880"), ("Air-gapped", "מנותק-רשת, אפס telemetry")],
        "feat_h": "מה Argus עושה", "feat_sub": "מהוכחת קונפורמיות ידנית ויקרה — למסלול דטרמיניסטי.",
        "features": [
            ("shieldcheck", "ניתוח סטטי רב-שכבתי", "תחביר, זרימת נתונים, ממשק חומרה וקונקרנטיות — מול 94 כללים ממופים ל-IEC 60880."),
            ("file", "חבילת ראיות חתומה", "manifest + SHA256 מוכנים למסירה למעריך רגולטורי."),
            ("trace", "מטריצת עקיבות מלאה", "מסעיף תקן → כלל → ממצא → החלטה, כולל זיהוי פערים."),
            ("chart", "דיווח בארבעה מצבים", "CI, מפתח, סוקר ורגולטור — ופלט SARIF תקני."),
            ("wifioff", "מנותק-רשת לחלוטין", "אפס CDN/telemetry, עם RBAC לחמישה תפקידים."),
            ("lock", "audit-log חתום", "שרשרת-hash: שום ממצא לא נמחק — רק מסווג ומתועד."),
        ],
        "ben_h": "למה זה משנה", "ben_sub": "שקוף, ניתן להסמכה, וניתן לחזרה.",
        "benefits": [
            ("דטרמיניסטי.", "אותו קלט → אותו פלט, byte-for-byte."),
            ("מוכן לרגולטור.", "חבילת ראיות חתומה, לא רק דוח."),
            ("שום דבר לא מושתק.", "סינון = סיווג מתועד, לא מחיקה."),
            ("Air-gapped.", "פועל בסביבה מנותקת-רשת."),
            ("עקיב.", "מהתקן ועד כל ממצא והחלטה."),
            ("Legacy.", "baseline מבוקר לאימוץ קוד קיים."),
        ],
        "form_h": "רוצים לשמוע עוד?", "form_sub": "השאירו פרטים ונחזור אליכם עם מידע והדגמה.",
        "footer": "© Argus · ניתוח סטטי לבטיחות גרעינית · IEC 60880",
    },
    {
        "id": "pandavista", "emoji": "🌐", "brand": "PandaVista",
        "accent": "#4f46e5", "accent2": "#22d3ee", "bg": "#0a0a18", "bg_soft": "#101025",
        "repo_path": "/Users/Avishai/Developer/PandaVista/landing/index.html", "shared_host": True,
        "title": "PandaVista — תוכן שמדורג בגוגל וגם ב-AI",
        "meta_desc": "PandaVista היא פלטפורמת תוכן רב-דיירית: עריכה דו-לשונית ללא קוד, שער סודיות מובנה, ושכבת SEO/GEO לנראות במנועי חיפוש וב-AI.",
        "badge": "תוכן · SEO · GEO · מבית PandaTech",
        "kicker": "אתר שמנהל את עצמו",
        "h1": 'תוכן דו-לשוני שמדורג —<br /><span class="grad">בגוגל וגם ב-AI</span>',
        "lead": "PandaVista היא פלטפורמת תוכן רב-דיירית לבנייה, ניהול וקידום של אתרי תוכן: עריכה דו-לשונית ללא קוד, שער סודיות מובנה שחוסם מידע רגיש, ושכבת SEO/GEO כאזרח מדרגה ראשונה.",
        "cta1": "לשמוע עוד →", "cta2": "מה זה עושה",
        "stats": [("עברית + אנגלית", "פרסום דו-לשוני ללא קוד"), ("SEO + GEO", "נראות בחיפוש וב-AI"), ("Multi-tenant", "בידוד דיירים מלא")],
        "feat_h": "מה PandaVista עושה", "feat_sub": "מפרסום תוכן ועד נראות — בלי מפתחים.",
        "features": [
            ("pen", "עריכה ופרסום דו-לשוני", "עברית ואנגלית, בלי שורת קוד — שומרים, והתוכן עולה לאוויר."),
            ("shield", "שער סודיות אוטומטי", "חוסם שמות לקוחות ומידע מסווג עוד לפני תור האישורים."),
            ("chart", "מנוע SEO + GEO", "נראות במנועי חיפוש וגם במנועי AI, עם מדדים חיים."),
            ("pie", "מנוע אינפוגרפיקה", "הופך נתונים לתרשימי SVG ויזואליים ומוכנים."),
            ("spark", "סוכני AI לניסוח טיוטות", "מנסחים תוכן אוטומטית — עם תור אישורים אנושי לכל פריט."),
            ("layers", "ניהול רב-דיירי", "תפקידים, הזמנות, וחיבור אתרים חיצוניים."),
        ],
        "ben_h": "למה זה עובד", "ben_sub": "פרסום מהיר, בטוח, ובר-שליטה.",
        "benefits": [
            ("בלי קוד.", "צוות שיווק מפרסם לבד."),
            ("בטוח כברירת מחדל.", "מידע רגיש נחסם לפני פרסום."),
            ("נראות כפולה.", "גם בגוגל וגם במנועי AI."),
            ("אישור אנושי.", "שום פריט לא עולה בלי אישור."),
            ("רב-דיירי.", "אתר לכל לקוח, מבודד."),
            ("דו-לשוני.", "עברית ואנגלית מהיום הראשון."),
        ],
        "footer": "© PandaVista · תוכן, SEO ו-GEO · מבית PandaTech",
    },
    {
        "id": "personal-assistant", "emoji": "🌅", "brand": "העוזר האישי",
        "accent": "#e0a458", "accent2": "#f59e0b", "bg": "#14100a", "bg_soft": "#1c160d",
        "repo_path": "/Users/Avishai/Developer/עוזר אישי/landing/index.html", "shared_host": True,
        "title": "העוזר האישי — כל מה שחשוב היום, במקום אחד",
        "meta_desc": "העוזר האישי אוסף את היום שלך ממקום אחד — יומן, Pipedrive ומיילים — ומריץ רוטינת בוקר אישית לפני שצוללים למשימות.",
        "badge": "הכנה יומית ושבועית · אישי",
        "kicker": "רוטינת בוקר, הכנה לפגישות, וראש שקט",
        "h1": 'כל מה שחשוב היום —<br /><span class="grad">במקום אחד, כל בוקר</span>',
        "lead": "העוזר האישי אוסף את היום שלך ממקום אחד: פגישות מהיומן, דילים ואנשי קשר מ-Pipedrive, ומיילים שדורשים מעקב — ומריץ איתך רוטינת בוקר אישית לפני שצוללים למשימות.",
        "cta1": "לשמוע עוד →", "cta2": "מה הוא עושה",
        "stats": [("כל יום 17:00", "הכנה ליום הבא"), ("שבת 20:00", "תמונת שבוע מלאה"), ("אישי לגמרי", "מחובר לרצון, לא רק למחויבות")],
        "feat_h": "מה העוזר האישי עושה", "feat_sub": "שום דבר לא נופל בין הכיסאות.",
        "features": [
            ("refresh", "סריקה יומית ושבועית", "Calendar, Pipedrive, Gmail ו-Outlook — הכל במקום אחד."),
            ("sun", "רוטינת בוקר", "כתיבה חופשית, בדיקת מטרות, ו'מה בא לי לעשות היום'."),
            ("check", "ניהול משימות חי", "ב-Google Sheet, עם ארכוב אוטומטי כשמסמנים Done."),
            ("users", "הכנה ממוקדת", "לפגישות ולדילים שצריך לקדם היום ומחר."),
            ("target", "מעקב מטרות", "ארוכות-טווח ורבעוניות, עם snapshot יומי."),
            ("calendar", "תכנון שבועי מלא", "כל שבת, והרצה ידנית בכל רגע."),
        ],
        "ben_h": "למה זה עובד", "ben_sub": "מחובר לרצון, לא רק לרשימת מטלות.",
        "benefits": [
            ("שום דבר לא נופל.", "משימות, פגישות ודילים במקום אחד."),
            ("ראש שקט.", "היום מסודר עוד לפני שהתחיל."),
            ("אישי.", "מה שכתבת נשמר מילה-במילה."),
            ("גמיש.", "אפשר לדלג בכל שלב."),
            ("תמונה שבועית.", "כל שבת — פגישות, יעדים ודילים."),
            ("מרובה-מקורות.", "יומן, CRM ומיילים יחד."),
        ],
        "form_h": "רוצים עוזר אישי כזה?", "form_sub": "השאירו פרטים ונחזור אליכם.",
        "footer": "© העוזר האישי · הכנה יומית ושבועית",
    },
    {
        "id": "weavz", "emoji": "🧭", "brand": "Weavz",
        "accent": "#5b8def", "accent2": "#22d3ee", "bg": "#0e1116", "bg_soft": "#141922",
        "repo_path": "/Users/Avishai/Developer/Weavs/landing/index.html", "shared_host": True,
        "title": "Weavz — ניווט בחיים: נתיב, קצב, וחיבור",
        "meta_desc": "Weavz היא אפליקציית מובייל לניווט בחיים: מתווים נתיבים אל יעדי החיים, רואים מפת ניווט חיה, ופוגשים אנשים שנעים לאותו כיוון.",
        "badge": "ניווט בחיים · אפליקציית מובייל",
        "kicker": "התווה את הנתיב שלך, ופגוש את מי שנע לאותו כיוון",
        "h1": 'ניווט בחיים —<br /><span class="grad">נתיב, קצב, וחיבור</span>',
        "lead": "Weavz היא אפליקציית מובייל לניווט בחיים: מתווים 3–5 נתיבים אל יעדי החיים, רואים אותם כמפת ניווט חיה בזהות רכבת-תחתית, ופוגשים אנשים שנעים לאותו כיוון.",
        "cta1": "רוצה גישה מוקדמת →", "cta2": "מה זה עושה",
        "stats": [("iOS + Android", "אפליקציית מובייל"), ("3–5 נתיבים", "אל יעדי החיים שלך"), ("פרטיות by-default", "אנונימי עד הסכמה")],
        "feat_h": "מה Weavz עושה", "feat_sub": "מסע אישי, בטוח ומחובר.",
        "features": [
            ("map", "מפת ניווט חיה", "בזהות רכבת-תחתית, ל-3–5 נתיבי חיים."),
            ("check", "פירוק יעדים אוטומטי", "לאבני דרך ולצעדים ברי-ביצוע."),
            ("link", '"אריגה" חברתית', "התאמה לאנשים שנעים לאותו כיוון בחיים."),
            ("activity", "ניטור קצב", "סטטוס חי ונדנוד יומי עדין."),
            ("users", "שיירות ומנטורים", "פורומים וחוכמה ממי שכבר עבר את הדרך."),
            ("eyeoff", "פרטיות by-default", "בידוד מלא, אנונימיות עד opt-in, מיקום גס בלבד."),
        ],
        "ben_h": "למה זה שונה", "ben_sub": "לא עוד רשימת מטלות — מסע עם אנשים.",
        "benefits": [
            ("בהירות.", "רואים את נתיבי החיים על מפה אחת."),
            ("בר-ביצוע.", "כל יעד מפורק לצעדים קטנים."),
            ("חיבורים אמיתיים.", "פוגשים מי שנע לאותו כיוון."),
            ("עדין.", "נדנוד יומי, בלי לחץ."),
            ("קהילה.", "שיירות, מנטורים וחוכמה מושאלת."),
            ("פרטי.", "אנונימי עד שאתה בוחר להיחשף."),
        ],
        "form_h": "רוצים גישה מוקדמת?", "form_sub": "השאירו פרטים ונעדכן אתכם כשנפתח.",
        "footer": "© Weavz · ניווט בחיים 🧭",
    },
]


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("  wrote", path)


def main():
    # DIST_ONLY=1 → only (re)generate dist/ for the shared static host. Used in CI
    # (GitHub Actions), where the sibling product repos are NOT checked out, so
    # writing to their absolute paths is impossible/pointless.
    dist_only = os.environ.get("DIST_ONLY") == "1"
    for sys in SYSTEMS:
        print(sys["id"])
        html = render(sys)
        # Only write into a product repo when that repo actually exists locally
        # (skip in CI / on a machine without the sibling checkout).
        repo_root = os.path.dirname(os.path.dirname(sys["repo_path"]))
        if not dist_only and os.path.isdir(repo_root):
            write(sys["repo_path"], html)
        elif not dist_only:
            print("  skip repo (not found):", sys["repo_path"])
        if sys.get("shared_host"):
            write(os.path.join(HERE, "dist", sys["id"], "index.html"), html)
    print("done:", len(SYSTEMS), "systems", "(dist-only)" if dist_only else "")


if __name__ == "__main__":
    main()
