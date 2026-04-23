import re

with open(r'd:\project_final\pages\admin.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace the entire <style> block again
start_str = "st.markdown(\"\"\"\n<style>"
end_str = "</style>\n\"\"\", unsafe_allow_html=True)"

new_style = """st.markdown(\"\"\"
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

* { box-sizing: border-box; }

[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at top left, #ffffff 0%, #f1f5f9 60%, #e2e8f0 100%);
}
[data-testid="stHeader"] { background: transparent !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #070b14 0%, #0f172a 100%) !important;
    border-right: 1px solid rgba(15,23,42,0.15) !important;
}
[data-testid="stSidebar"] * { font-family: 'DM Sans', sans-serif !important; }

/* ── Main area ── */
.block-container { padding: 2.5rem 3rem !important; max-width: 1400px !important; }

/* ── Top bar ── */
.admin-topbar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 0 1.5rem 0; border-bottom: 2px solid rgba(15, 23, 42, 0.05); margin-bottom: 2.5rem;
}
.admin-brand { font-family: 'DM Serif Display', Georgia, serif; font-size: 1.8rem; background: linear-gradient(135deg, #0f172a, #4338ca); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.admin-brand span { font-family: 'DM Sans', sans-serif; font-size: 0.72rem; letter-spacing: 2.5px; text-transform: uppercase; display: block; margin-top: 0px; -webkit-text-fill-color: #64748b; font-weight: 700; }
.admin-badge { background: rgba(99, 102, 241, 0.08); border: 1px solid rgba(99, 102, 241, 0.2); border-radius: 20px; padding: 4px 14px; font-family: 'DM Sans', sans-serif; font-size: 0.75rem; color: #4338ca; letter-spacing: 1px; text-transform: uppercase; font-weight: 700; box-shadow: 0 0 10px rgba(99,102,241,0.1); }

/* ── Stat cards ── */
.stat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 2.5rem; }
.stat-card {
    background: rgba(255, 255, 255, 0.65); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.8); border-radius: 16px; padding: 1.6rem 1.8rem;
    position: relative; overflow: hidden; transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1); box-shadow: 0 8px 32px rgba(15, 23, 42, 0.03), inset 0 2px 4px rgba(255,255,255,0.7);
}
.stat-card:hover { transform: translateY(-4px); box-shadow: 0 12px 40px rgba(15, 23, 42, 0.06), inset 0 2px 4px rgba(255,255,255,1); }
.stat-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, var(--accent, #6366f1), transparent); opacity: 0.8; }
.stat-icon { font-size: 1.6rem; margin-bottom: 0.8rem; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1)); }
.stat-value { font-family: 'DM Serif Display', Georgia, serif; font-size: 2.2rem; color: #0f172a; line-height: 1; margin-bottom: 4px; }
.stat-label { font-family: 'DM Sans', sans-serif; font-size: 0.75rem; color: #475569; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 700; }
.stat-sub { font-family: 'DM Sans', sans-serif; font-size: 0.75rem; margin-top: 6px; font-weight: 600; }
.stat-up { color: #10b981; } .stat-dn { color: #ef4444; }

/* ── Section headers ── */
.section-hdr { font-family: 'DM Sans', sans-serif; font-size: 0.75rem; font-weight: 800; letter-spacing: 2.5px; text-transform: uppercase; color: #334155; padding-bottom: 12px; border-bottom: 2px solid rgba(15, 23, 42, 0.04); margin-bottom: 1.5rem; }

/* ── Table override ── */
.stDataFrame, [data-testid="stDataFrame"] { background: rgba(255, 255, 255, 0.5) !important; backdrop-filter: blur(10px) !important; border-radius: 16px !important; border: 1px solid rgba(255, 255, 255, 0.6) !important; overflow: hidden !important; box-shadow: 0 4px 16px rgba(15, 23, 42, 0.02) !important; }
[data-testid="stDataFrame"] * { font-family: 'DM Sans', sans-serif !important; font-size: 0.85rem !important; color: #334155 !important; }
[data-testid="stDataFrame"] th { background: rgba(255, 255, 255, 0.8) !important; color: #1e293b !important; font-size: 0.72rem !important; letter-spacing: 1px !important; text-transform: uppercase !important; border-bottom: 1px solid rgba(15, 23, 42, 0.05) !important; font-weight: 800 !important; }

/* ── Panel card ── */
.panel-card { background: rgba(255, 255, 255, 0.65); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.8); border-radius: 16px; padding: 1.8rem 2rem; margin-bottom: 1.2rem; box-shadow: 0 8px 32px rgba(15, 23, 42, 0.03), inset 0 2px 4px rgba(255,255,255,0.7); }

/* ── Buttons ── */
.stButton > button:first-child { background: linear-gradient(135deg, #1e293b, #0f172a) !important; color: #ffffff !important; border: none !important; border-radius: 10px !important; font-family: 'DM Sans', sans-serif !important; font-size: 0.9rem !important; font-weight: 700 !important; padding: 0.6rem 1.4rem !important; box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15), inset 0 1px 1px rgba(255,255,255,0.1) !important; transition: all 0.25s cubic-bezier(0.25, 0.8, 0.25, 1) !important; }
.stButton > button:first-child:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 16px rgba(15, 23, 42, 0.2) !important; }
.stButton > button[kind="secondary"] { background: rgba(239, 68, 68, 0.08) !important; backdrop-filter: blur(5px) !important; color: #ef4444 !important; border: 1px solid rgba(239, 68, 68, 0.2) !important; border-radius: 10px !important; font-family: 'DM Sans', sans-serif !important; font-size: 0.85rem !important; font-weight: 700 !important; box-shadow: none !important;}
.stButton > button[kind="secondary"]:hover { background: rgba(239, 68, 68, 0.15) !important; transform: translateY(-1px) !important; }

/* ── Inputs ── */
.stTextInput > div > div > input, .stSelectbox > div > div { background: rgba(255, 255, 255, 0.8) !important; border: 1px solid rgba(15, 23, 42, 0.08) !important; border-radius: 10px !important; color: #0f172a !important; font-family: 'DM Sans', sans-serif !important; font-size: 0.95rem !important; box-shadow: inset 0 2px 4px rgba(15, 23, 42, 0.01) !important; transition: all 0.2s !important; padding: 0.65rem 0.8rem !important; }
.stTextInput > div > div > input:focus { border-color: #6366f1 !important; background: #ffffff !important; box-shadow: 0 0 0 3px rgba(99,102,241,0.15), inset 0 2px 4px rgba(15, 23, 42, 0.01) !important; }
.stTextInput > label, .stSelectbox > label { color: #475569 !important; font-family: 'DM Sans', sans-serif !important; font-size: 0.78rem !important; font-weight: 700 !important; letter-spacing: 0.5px !important; text-transform: uppercase !important; margin-bottom: 0.4rem !important; }

/* ── Alerts ── */
.stSuccess > div { background: rgba(220, 252, 231, 0.8) !important; backdrop-filter: blur(10px) !important; border: 1px solid rgba(134, 239, 172, 0.5) !important; border-radius: 12px !important; color: #166534 !important; font-family: 'DM Sans', sans-serif !important; box-shadow: 0 4px 12px rgba(22, 101, 52, 0.05) !important; font-weight: 600 !important; }
.stError > div { background: rgba(254, 226, 226, 0.8) !important; backdrop-filter: blur(10px) !important; border: 1px solid rgba(252, 165, 165, 0.5) !important; border-radius: 12px !important; color: #991b1b !important; font-family: 'DM Sans', sans-serif !important; box-shadow: 0 4px 12px rgba(153, 27, 27, 0.05) !important; font-weight: 600 !important; }
.stWarning > div { background: rgba(254, 249, 195, 0.8) !important; backdrop-filter: blur(10px) !important; border: 1px solid rgba(253, 224, 71, 0.5) !important; border-radius: 12px !important; color: #854d0e !important; font-family: 'DM Sans', sans-serif !important; box-shadow: 0 4px 12px rgba(133, 77, 14, 0.05) !important; font-weight: 600 !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { background: rgba(226, 232, 240, 0.6) !important; backdrop-filter: blur(10px) !important; border-radius: 14px !important; padding: 6px !important; border: 1px solid rgba(255, 255, 255, 0.5) !important; gap: 4px !important; box-shadow: inset 0 2px 4px rgba(15, 23, 42, 0.02) !important; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: #64748b !important; font-family: 'DM Sans', sans-serif !important; font-size: 0.88rem !important; font-weight: 600 !important; border-radius: 10px !important; padding: 0.5rem 1.4rem !important; border: none !important; transition: all 0.2s !important; }
.stTabs [aria-selected="true"] { background: #ffffff !important; color: #0f172a !important; box-shadow: 0 2px 8px rgba(15, 23, 42, 0.08) !important; font-weight: 700 !important; }

/* ── Search / filter ── */
.filter-row { display: flex; gap: 10px; align-items: flex-end; margin-bottom: 1rem; }

/* ── User row card ── */
.user-row { display: flex; align-items: center; justify-content: space-between; background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.8); border-radius: 12px; padding: 1.2rem 1.6rem; margin-bottom: 12px; transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1); box-shadow: 0 4px 12px rgba(15, 23, 42, 0.02); }
.user-row:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06); border-color: #cbd5e1; background: #ffffff; }
.user-avatar { width: 42px; height: 42px; border-radius: 50%; background: linear-gradient(135deg, #e0e7ff, #c7d2fe); border: 2px solid #ffffff; display: flex; align-items: center; justify-content: center; font-family: 'DM Sans', sans-serif; font-size: 1rem; font-weight: 800; color: #4338ca; flex-shrink: 0; margin-right: 16px; box-shadow: 0 2px 6px rgba(67, 56, 202, 0.15); }
.user-info { flex: 1; }
.user-name { font-family: 'DM Sans', sans-serif; font-size: 1rem; font-weight: 800; color: #0f172a; }
.user-meta { font-family: 'DM Sans', sans-serif; font-size: 0.78rem; color: #64748b; margin-top: 4px; }
.user-mono { font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #94a3b8; }

/* ── Log/Activity (if any) ── */
.log-row { display: flex; gap: 12px; align-items: flex-start; padding: 8px 0; border-bottom: 1px solid #e2e8f0; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 6px; }
::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
</style>
\"\"\", unsafe_allow_html=True)"""

parts = text.split(start_str)
if len(parts) >= 2:
    text = text[:text.rfind(start_str)] + new_style + text[text.rfind(end_str) + len(end_str):]
else:
    print("Could not find style block")

with open(r'd:\project_final\pages\admin.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("done premium override")
