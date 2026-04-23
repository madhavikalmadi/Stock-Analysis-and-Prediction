import re

with open(r'd:\project_final\pages\admin.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Replace the entire <style> block
start_str = "st.markdown(\"\"\"\n<style>"
end_str = "</style>\n\"\"\", unsafe_allow_html=True)"

new_style = """st.markdown(\"\"\"
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

* { box-sizing: border-box; }

[data-testid="stAppViewContainer"] { background: #f1f5f9; }
[data-testid="stHeader"] { background: transparent !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0f172a !important;
    border-right: 1px solid rgba(0,0,0,0.1) !important;
}
[data-testid="stSidebar"] * { font-family: 'DM Sans', sans-serif !important; }

/* ── Main area ── */
.block-container { padding: 2rem 2.5rem !important; max-width: 1400px !important; }

/* ── Top bar ── */
.admin-topbar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 0 1.8rem 0; border-bottom: 2px solid #e2e8f0; margin-bottom: 2rem;
}
.admin-brand { font-family: 'DM Serif Display', Georgia, serif; font-size: 1.6rem; color: #0f172a; }
.admin-brand span { font-family: 'DM Sans', sans-serif; font-size: 0.72rem; color: #64748b; letter-spacing: 2px; text-transform: uppercase; display: block; margin-top: -2px; }
.admin-badge { background: #e0e7ff; border: 1px solid #c7d2fe; border-radius: 20px; padding: 4px 14px; font-family: 'DM Sans', sans-serif; font-size: 0.75rem; color: #4338ca; letter-spacing: 1px; text-transform: uppercase; font-weight: 600; }

/* ── Stat cards ── */
.stat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 2rem; }
.stat-card {
    background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 1.2rem 1.4rem;
    position: relative; overflow: hidden; transition: box-shadow 0.2s; box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}
.stat-card:hover { box-shadow: 0 8px 12px -3px rgba(0,0,0,0.05); }
.stat-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: var(--accent, #f0c040); }
.stat-icon { font-size: 1.4rem; margin-bottom: 0.6rem; }
.stat-value { font-family: 'DM Serif Display', Georgia, serif; font-size: 2rem; color: #0f172a; line-height: 1; margin-bottom: 4px; }
.stat-label { font-family: 'DM Sans', sans-serif; font-size: 0.75rem; color: #64748b; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600; }
.stat-sub { font-family: 'DM Sans', sans-serif; font-size: 0.75rem; margin-top: 6px; font-weight: 500; }
.stat-up { color: #10b981; } .stat-dn { color: #ef4444; }

/* ── Section headers ── */
.section-hdr { font-family: 'DM Sans', sans-serif; font-size: 0.72rem; font-weight: 700; letter-spacing: 2.5px; text-transform: uppercase; color: #0f172a; padding-bottom: 10px; border-bottom: 2px solid #e2e8f0; margin-bottom: 1.2rem; }

/* ── Table override ── */
.stDataFrame, [data-testid="stDataFrame"] { background: #ffffff !important; border-radius: 12px !important; border: 1px solid #e2e8f0 !important; overflow: hidden !important; box-shadow: 0 1px 2px rgba(0,0,0,0.02) !important; }
[data-testid="stDataFrame"] * { font-family: 'DM Sans', sans-serif !important; font-size: 0.85rem !important; color: #334155 !important; }
[data-testid="stDataFrame"] th { background: #f8fafc !important; color: #475569 !important; font-size: 0.72rem !important; letter-spacing: 1px !important; text-transform: uppercase !important; border-bottom: 1px solid #e2e8f0 !important; }

/* ── Panel card ── */
.panel-card { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 1.4rem 1.6rem; margin-bottom: 1.2rem; box-shadow: 0 2px 5px rgba(0,0,0,0.02); }

/* ── Buttons ── */
.stButton > button:first-child { background: #0f172a !important; color: #ffffff !important; border: none !important; border-radius: 8px !important; font-family: 'DM Sans', sans-serif !important; font-size: 0.87rem !important; font-weight: 600 !important; padding: 0.5rem 1.2rem !important; box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important; transition: all 0.2s !important; }
.stButton > button:first-child:hover { background: #1e293b !important; transform: translateY(-1px) !important; box-shadow: 0 4px 8px rgba(0,0,0,0.12) !important; }
.stButton > button[kind="secondary"] { background: #fee2e2 !important; color: #ef4444 !important; border: 1px solid #fca5a5 !important; border-radius: 8px !important; font-family: 'DM Sans', sans-serif !important; font-size: 0.85rem !important; }
.stButton > button[kind="secondary"]:hover { background: #fecaca !important; }

/* ── Inputs ── */
.stTextInput > div > div > input, .stSelectbox > div > div { background: #ffffff !important; border: 1px solid #cbd5e1 !important; border-radius: 8px !important; color: #0f172a !important; font-family: 'DM Sans', sans-serif !important; font-size: 0.88rem !important; }
.stTextInput > div > div > input:focus { border-color: #3b82f6 !important; box-shadow: 0 0 0 3px rgba(59,130,246,0.1) !important; }
.stTextInput > label, .stSelectbox > label { color: #64748b !important; font-family: 'DM Sans', sans-serif !important; font-size: 0.78rem !important; font-weight: 600 !important; letter-spacing: 0.5px !important; text-transform: uppercase !important; }

/* ── Alerts ── */
.stSuccess > div { background: #dcfce7 !important; border: 1px solid #86efac !important; border-radius: 8px !important; color: #166534 !important; font-family: 'DM Sans', sans-serif !important; }
.stError > div { background: #fee2e2 !important; border: 1px solid #fca5a5 !important; border-radius: 8px !important; color: #991b1b !important; font-family: 'DM Sans', sans-serif !important; }
.stWarning > div { background: #fef9c3 !important; border: 1px solid #fde047 !important; border-radius: 8px !important; color: #854d0e !important; font-family: 'DM Sans', sans-serif !important; }
.stInfo > div { background: #e0e7ff !important; border: 1px solid #c7d2fe !important; border-radius: 8px !important; color: #3730a3 !important; font-family: 'DM Sans', sans-serif !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { background: #e2e8f0 !important; border-radius: 10px !important; padding: 4px !important; border: 1px solid #cbd5e1 !important; gap: 4px !important; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: #64748b !important; font-family: 'DM Sans', sans-serif !important; font-size: 0.85rem !important; font-weight: 600 !important; border-radius: 7px !important; padding: 0.4rem 1rem !important; border: none !important; }
.stTabs [aria-selected="true"] { background: #ffffff !important; color: #0f172a !important; box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important; }

/* ── Search / filter ── */
.filter-row { display: flex; gap: 10px; align-items: flex-end; margin-bottom: 1rem; }

/* ── User row card ── */
.user-row { display: flex; align-items: center; justify-content: space-between; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 0.8rem 1.2rem; margin-bottom: 8px; transition: border-color 0.2s; box-shadow: 0 1px 3px rgba(0,0,0,0.02); }
.user-row:hover { border-color: #cbd5e1; }
.user-avatar { width: 36px; height: 36px; border-radius: 50%; background: #e0e7ff; border: 1.5px solid #c7d2fe; display: flex; align-items: center; justify-content: center; font-family: 'DM Sans', sans-serif; font-size: 0.9rem; font-weight: 700; color: #4338ca; flex-shrink: 0; margin-right: 12px; }
.user-info { flex: 1; }
.user-name { font-family: 'DM Sans', sans-serif; font-size: 0.9rem; font-weight: 700; color: #0f172a; }
.user-meta { font-family: 'DM Sans', sans-serif; font-size: 0.74rem; color: #64748b; margin-top: 2px; }
.user-mono { font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #94a3b8; }

/* ── Activity log ── */
.log-row { display: flex; gap: 12px; align-items: flex-start; padding: 8px 0; border-bottom: 1px solid #e2e8f0; }
.log-dot { width: 8px; height: 8px; border-radius: 50%; background: #f0c040; margin-top: 5px; flex-shrink: 0; }
.log-text { font-family: 'DM Sans', sans-serif; font-size: 0.82rem; color: #475569; line-height: 1.4; }
.log-time { font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #94a3b8; margin-top: 2px; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
</style>
\"\"\", unsafe_allow_html=True)"""

idx_start = text.find(start_str)
idx_end = text.find(end_str) + len(end_str)
if idx_start != -1 and idx_end != -1:
    # also strip out previous CSS from character zero up to start_str if it occurs multiple times
    # wait there are TWO <style> blocks in admin.py, one inside the auth_guard and one main one.
    # The one after auth_guard starts on line ~95. Let's just split and replace the correct one.
    parts = text.split(start_str)
    # The last part should be the main one if we just replace the last occurrence
    text = text[:text.rfind(start_str)] + new_style + text[text.rfind(end_str) + len(end_str):]
else:
    print("Could not find style block")

# 2. Fix inline HTML table colors for light background
text = text.replace("color:#b0c8e0;", "color:#0f172a;")
text = text.replace("color:#3a5568;", "color:#64748b;")
text = text.replace("color:#f0c040;", "color:#0f172a;")

with open(r'd:\project_final\pages\admin.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("done")
