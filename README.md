# panda-brochures — דפי נחיתה שיווקיים (ברושורים) משותפים

מקור-אמת אחד לדפי הנחיתה השיווקיים של מערכות PandaTech שמשתמשות בתבנית
משותפת, וגם **האתר הסטטי המשותף** שמארח את המערכות שאין להן פרונטאנד web
(נתיב לכל מערכת: `/pandoosh`, `/argus`, `/pandavista`, `/personal-assistant`,
`/weavz`).

היכולת מקבילה למסך העזרה: כמו שהעזרה מתעדכנת עם יכולות המערכת, גם הברושור
מתעדכן (כלל חובה ב-`CLAUDE.md` הגלובלי של אבישי). הדפוס המלא + נקודת הקצה
המשותפת מתועדים ב-`PandaPower/docs/MARKETING_BROCHURE.md`.

## איך זה עובד

- `generate.py` — תבנית HTML אחת + תוכן לכל מערכת. מריצים ומייצר:
  1. את הברושור **בתוך הריפו של כל מערכת** (`public/landing.html` למערכות web,
     `landing/index.html` לשאר).
  2. עותק ל-`dist/<id>/index.html` כאן — האתר הסטטי המשותף.
- כל הברושורים שולחים לידים לנקודת קצה משותפת אחת ב-**SendMSG** (מערכת השיווק):
  `POST https://send-msg-zeta.vercel.app/api/public/leads`
  → טבלת `leads` + התראת מייל (Resend), וכשיש טלפון מקודם ללקוח פוטנציאלי
  לפניית הילה (בשער אישור). מסך ניהול: `/leads` ב-SendMSG.
- הברושורים עצמאיים: אין מהם מעבר אל המערכת עצמה.

## עדכון / הוספת מערכת

```bash
python3 generate.py
```

לעדכון תוכן: ערוך את הרשומה של המערכת ב-`SYSTEMS` בתוך `generate.py` והרץ מחדש.
להוספת מערכת חדשה: הוסף רשומה ל-`SYSTEMS` (כולל `id`, `repo_path`,
`shared_host`), **ורשום את ה-`id`** ב-`KNOWN_SYSTEMS`/`SYSTEM_LABELS` בקובץ
`SendMSG/lib/leads/systems.ts` (אחרת ה-endpoint ידחה את הליד).

## חלוקת אחסון

| מערכת | אחסון | כתובת |
|-------|-------|-------|
| PandaPower | פרונטאנד עצמי (Vercel) | `/landing.html` |
| PandaSkill | פרונטאנד עצמי (Vercel) | `/landing.html` |
| SendMSG | פרונטאנד עצמי (Vercel) | `/landing.html` |
| Pandoosh, Argus, PandaVista, העוזר האישי, Weavz | האתר המשותף כאן (`dist/`) | `/<id>` |

## פריסה אוטומטית (ברירת מחדל) — GitHub Pages

פריסה אוטומטית מוגדרת ב-`.github/workflows/deploy.yml`: **דחיפה/מיזוג ל-`main`
מפרסמת את `dist/` ל-GitHub Pages אוטומטית**, ללא מפתחות/סודות (משתמש ב-
`GITHUB_TOKEN` המובנה + OIDC — אין Service Account ואין מפתח JSON ב-repo,
בהתאם לכלל ה-CI/CD הגלובלי). ה-workflow גם מריץ `DIST_ONLY=1 python3 generate.py`
כדי ש-Pages תמיד תואם לתבנית.

הפעלה חד-פעמית לאחר יצירת ה-repo ב-GitHub:

```bash
gh repo create panda-brochures --public --source=. --remote=origin --push
gh api -X POST repos/{owner}/panda-brochures/pages -f build_type=workflow  # מפעיל Pages (מקור: GitHub Actions)
```

או ידנית: Settings → Pages → Build and deployment → Source: **GitHub Actions**.
לאחר מכן כל `git push` ל-`main` מפרסם. הכתובת: `https://<owner>.github.io/panda-brochures/`
(קישורי ה-hub יחסיים, כך שהם עובדים גם תחת נתיב-בסיס וגם בדומיין שורש).

### חלופות (הוסטינג סטטי אחר)
- **Vercel**: `vercel deploy --prod` (משתמש ב-`vercel.json` → מגיש `dist/` עם `cleanUrls`).
- **Netlify**: `netlify deploy --prod` (משתמש ב-`netlify.toml`).
