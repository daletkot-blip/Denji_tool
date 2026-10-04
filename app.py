from flask import Flask, render_template_string, request
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Denji Tool - Free Fire</title>
    <style>
        :root {
            --bg-color: #0b0b0f;
            --card-bg: #13131c;
            --accent: #ff0055;
            --text-main: #ffffff;
            --text-muted: #7a7a8c;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, sans-serif; }
        
        body {
            background-color: var(--bg-color);
            color: var(--text-main);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 15px;
        }

        .container {
            width: 100%;
            max-width: 420px;
            background: var(--card-bg);
            border: 1px solid rgba(255, 255, 255, 0.07);
            border-radius: 18px;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.7);
            padding: 22px;
        }

        .simple-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }

        .logo-text {
            font-size: 16px;
            font-weight: 700;
            color: #fff;
            letter-spacing: 0.5px;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .logo-text span {
            color: var(--accent);
        }

        .logo-dot {
            width: 8px;
            height: 8px;
            background-color: var(--accent);
            border-radius: 50%;
            box-shadow: 0 0 8px var(--accent);
        }

        .search-box {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }

        input {
            flex: 1;
            padding: 11px 15px;
            background: #191924;
            border: 1px solid #28283d;
            color: #fff;
            border-radius: 10px;
            outline: none;
            font-size: 14px;
            transition: 0.2s;
        }

        input:focus {
            border-color: var(--accent);
        }

        button {
            background: var(--accent);
            color: #fff;
            border: none;
            padding: 0 20px;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
            font-size: 14px;
            transition: 0.2s;
        }

        button:active { opacity: 0.8; }

        .results-card {
            background: #171722;
            border-radius: 12px;
            padding: 16px;
        }

        .row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 9px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.03);
            font-size: 13.5px;
        }

        .row:last-child { border-bottom: none; }

        .label {
            color: var(--text-muted);
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .value {
            color: var(--text-main);
            font-weight: 500;
            direction: ltr;
            text-align: left;
        }

        .value.rtl {
            direction: rtl;
            text-align: right;
        }

        .name-box {
            margin-bottom: 10px;
            padding: 10px 12px;
            background: #101017;
            border-radius: 8px;
            border: 1px solid rgba(255, 0, 85, 0.2);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .bio-box {
            margin: 10px 0;
            padding: 10px 12px;
            background: #101017;
            border-radius: 8px;
            border: 1px dashed #28283d;
        }

        .bio-content {
            color: #b8b8cc;
            font-size: 13px;
            direction: rtl;
            text-align: right;
            word-break: break-all;
            margin-top: 4px;
        }

        /* تنسيق كلمة عرض المزيد الصغيرة والرمادية */
        .more-toggle {
            font-size: 12px;
            color: var(--text-muted);
            cursor: pointer;
            text-align: left;
            margin-top: 6px;
            transition: 0.2s;
            user-select: none;
        }
        .more-toggle:hover {
            color: var(--accent);
        }
        .hidden-section {
            display: none;
            margin-top: 8px;
            border-top: 1px dashed rgba(255, 255, 255, 0.05);
            padding-top: 8px;
        }

        .badge-active { color: #00ff88; }
        .badge-inactive { color: #ff4444; }

        .error-msg {
            background: rgba(255, 68, 68, 0.1);
            color: #ff4444;
            padding: 10px;
            border-radius: 8px;
            text-align: center;
            font-size: 13px;
        }

        .footer-credit {
            text-align: center;
            margin-top: 15px;
            font-size: 11px;
            color: var(--text-muted);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="simple-header">
            <div class="logo-text">Tool <span>Denji</span></div>
            <div class="logo-dot"></div>
        </div>
        
        <form method="POST">
            <div class="search-box">
                <input type="text" name="uid" placeholder="أدخل UID اللاعب..." required autocomplete="off" value="{{ uid if uid else '' }}">
                <button type="submit">بحث</button>
            </div>
        </form>

        {% if error %}
            <div class="error-msg">{{ error }}</div>
        {% endif %}

        {% if data %}
            {% set basic = data.get('basicInfo', {}) %}
            {% set social = data.get('socialInfo', {}) %}
            {% set clan = data.get('clanBasicInfo', {}) %}
            {% set captain = data.get('captainBasicInfo', {}) %}
            {% set pet = data.get('petInfo', {}) %}

            <div class="results-card">
                <div class="name-box">
                    <span style="color:var(--text-muted); font-size:13px;">👤 الاسم</span>
                    <span style="color:#ff77aa; font-weight:600; direction:rtl;">{{ basic.get('nickname', 'N/A') }}</span>
                </div>

                <div class="bio-box">
                    <span style="color:var(--text-muted); font-size:12px;">💬 البايو</span>
                    <div class="bio-content">{{ basic.get('signature', '') or social.get('signature', 'No Bio') }}</div>
                </div>

                <div class="row">
                    <span class="label">🆔 الـ UID</span>
                    <span class="value">{{ basic.get('accountId', '-') }}</span>
                </div>
                <div class="row">
                    <span class="label">🕒 آخر ظهور</span>
                    <span class="value">{{ format_time(basic.get('lastLoginAt'), '%Y-%m-%d %I:%M %p') }}</span>
                </div>
                <div class="row">
                    <span class="label">📅 تاريخ الإنشاء</span>
                    <span class="value">{{ format_time(basic.get('createAt'), '%Y-%m-%d') }}</span>
                </div>
                <div class="row">
                    <span class="label">⭐ اللفل</span>
                    <span class="value">{{ basic.get('level', 'N/A') }} <span style="color:var(--text-muted); font-size:11px;">({{ basic.get('exp', 'N/A') }})</span></span>
                </div>
                <div class="row">
                    <span class="label">🌍 السيرفر</span>
                    <span class="value">{{ basic.get('region', 'N/A') }}</span>
                </div>
                <div class="row">
                    <span class="label">❤️ اللايكات</span>
                    <span class="value">{{ basic.get('liked', '0') }}</span>
                </div>
                <div class="row">
                    <span class="label">🎫 الإليت باس</span>
                    <span class="value {% if basic.get('hasElitePass') %}badge-active{% else %}badge-inactive{% endif %}">{{ 'Yes [Active]' if basic.get('hasElitePass') else 'No [Inactive]' }}</span>
                </div>
                
                <!-- صف الكلان مع زر عرض المزيد -->
                <div class="row" style="flex-direction: column; align-items: stretch;">
                    <div style="display: flex; justify-content: space-between; width: 100%;">
                        <span class="label">🛡️ الكلان</span>
                        <span class="value rtl">{{ clan.get('clanName', 'No Clan') }}</span>
                    </div>
                    {% if clan and clan.get('clanName') %}
                    <div class="more-toggle" id="toggleText" onclick="toggleClanDetails()">عرض المزيد...</div>
                    <div id="clanDetails" class="hidden-section">
                        <div style="color: var(--accent); font-size: 12px; font-weight: bold; margin-bottom: 6px;">بيانات قائد الكلان:</div>
                        <div style="display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 5px;">
                            <span style="color: var(--text-muted);">اسم القائد:</span>
                            <span style="color: #fff; font-weight: 500;">{{ captain.get('nickname', 'غير معروف') }}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 5px;">
                            <span style="color: var(--text-muted);">مستوى القائد:</span>
                            <span style="color: #fff;">{{ captain.get('level', '-') }}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 5px;">
                            <span style="color: var(--text-muted);">لايكات القائد:</span>
                            <span style="color: #fff;">❤️ {{ captain.get('liked', 0) }}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; font-size: 13px;">
                            <span style="color: var(--text-muted);">آخر ظهور للقائد:</span>
                            <span style="color: #fff; direction: ltr;">{{ format_time(captain.get('lastLoginAt'), '%Y-%m-%d %I:%M %p') }}</span>
                        </div>
                    </div>
                    {% endif %}
                </div>

                <div class="row">
                    <span class="label">👥 مستوى الكلان</span>
                    <span class="value">{{ clan.get('clanLevel', 'N/A') }}</span>
                </div>
                <div class="row">
                    <span class="label">🐾 الحيوان</span>
                    <span class="value rtl">{{ pet.get('name', 'No Pet') if pet else 'No Pet' }}</span>
                </div>
            </div>
        {% endif %}

        <div class="footer-credit">⚡ Developed by Denji</div>
    </div>

    <script>
        function toggleClanDetails() {
            var section = document.getElementById('clanDetails');
            var toggle = document.getElementById('toggleText');
            if (section.style.display === 'block') {
                section.style.display = 'none';
                toggle.innerText = "عرض المزيد...";
            } else {
                section.style.display = 'block';
                toggle.innerText = "عرض أقل";
            }
        }
    </script>
</body>
</html>
"""

def format_time(timestamp_str, fmt):
    if not timestamp_str or not str(timestamp_str).isdigit():
        return "غير معروف"
    try:
        dt = datetime.utcfromtimestamp(int(timestamp_str)) + timedelta(hours=3)
        return dt.strftime(fmt)
    except Exception:
        return "غير معروف"

@app.route("/", methods=["GET", "POST"])
def index():
    data = None
    error = None
    uid = None
    if request.method == "POST":
        uid = request.form.get("uid").strip()
        if uid.isdigit():
            try:
                r = requests.get("http://de26.spaceify.eu:26080/info", params={"uid": uid}, timeout=20)
                if r.status_code == 200:
                    data = r.json()
                    if "basicInfo" not in data:
                        error = "فشل العثور على بيانات لهذا الـ UID."
                else:
                    error = "فشل الاتصال بالخادم، تأكد من صحة الـ UID."
            except Exception as e:
                error = f"حدث خطأ: {e}"
        else:
            error = "الرجاء إدخال أرقام صحيحة للـ UID."

    return render_template_string(HTML_TEMPLATE, data=data, error=error, uid=uid, format_time=format_time)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
      
