"""
AL Window Profile CSV Generator — Streamlit v2.5
Clean single-view layout. No sidebar.
"""

import streamlit as st
import pandas as pd
import csv
from datetime import date
from io import StringIO

# ── Page config ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="Window Profile Generator",
    page_icon="🪟",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Theme ───────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    [data-testid="collapsedControl"] { display: none; }
    section[data-testid="stSidebar"] { display: none; }

    .block-container {
        padding: 1rem 2rem 1rem 2rem;
        max-width: 1800px;
        font-family: 'DM Sans', sans-serif;
    }

    /* header bar */
    .app-header {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        padding: 18px 28px;
        border-radius: 12px;
        margin-bottom: 20px;
        display: flex;
        align-items: baseline;
        gap: 14px;
        border-bottom: 3px solid #F59E0B;
    }
    .app-header h1 {
        color: #F8FAFC;
        font-family: 'DM Sans', sans-serif;
        font-size: 1.35rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .app-header span {
        color: #64748B;
        font-size: 0.8rem;
        font-family: 'JetBrains Mono', monospace;
    }

    /* section labels */
    .sec-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #94A3B8;
        border-bottom: 1px solid #E2E8F0;
        padding-bottom: 6px;
        margin-bottom: 12px;
    }

    /* metrics */
    div[data-testid="stMetric"] {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 10px 14px;
        border-left: 3px solid #F59E0B;
    }
    div[data-testid="stMetric"] label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.65rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #64748B;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.4rem;
        font-weight: 500;
        color: #0F172A;
    }

    /* table styling */
    div[data-testid="stDataFrame"] {
        border: 1px solid #E2E8F0;
        border-radius: 8px;
    }

    /* footer */
    .app-footer {
        text-align: center;
        color: #94A3B8;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.65rem;
        padding: 10px 0 2px;
        letter-spacing: 0.05em;
    }
</style>
""", unsafe_allow_html=True)

# ── Constants ───────────────────────────────────────────────────────
CSV_HEADER = [
    'id', 'ksn', 'ksnbar', 'ktn', 'ktnbar', 'l', 'r', 'code', 'info',
    'width', 'height', 'trolley', 'box', 'orientation', 'reinf', 'reinfbar',
    'pos', 'prono', 'offno', 'customer', 'date', 'nccode', 'isfix', 'colorcode',
    'colorinfo', 'mainprofile', 'subcust', 'image', 'DATA1', 'DATA2', 'DATA3',
    'DATA4', 'DATA5'
]

COLOR_CODES = {
    '4 Black':     {'code': 883008, 'colorcode': '4'},
    '1 White':     {'code': 883009, 'colorcode': '1'},
    '2 Driftwood': {'code': 883011, 'colorcode': '2'}
}

PROFILE_DESCRIPTIONS = {
    883008: 'Main Frame - Upright (Fixed) -BL',
    883009: 'Main Frame - Upright (Fixed) - WH',
    883011: 'Main Frame - Upright (Fixed) - DR',
    883048: 'Main Frame - Upright (Moving) -BL',
    883049: 'Main Frame - Upright (Moving) -WH',
    883051: 'Main Frame - Upright (Moving) -DR',
    883013: 'Main Frame - Top/Bottom (Fixed Lite) -BL',
    883014: 'Main Frame - Top/Bottom (Fixed Lite) -WH',
    883016: 'Main Frame - Top/Bottom (Fixed Lite) -DR',
    883068: 'Sash - Top/Bottom -BL',
    883069: 'Sash - Top/Bottom -WH',
    883071: 'Sash - Top/Bottom -DR',
    883053: 'Sash - Upright (Pull) -BL',
    883054: 'Sash - Upright (Pull) -WH',
    883056: 'Sash - Upright (Pull) -DR',
    883058: 'Sash - Upright (Moving Interlock) -BL',
    883059: 'Sash - Upright (Moving Interlock) -WH',
    883061: 'Sash - Upright (Moving Interlock) -DR'
}

COLOR_PROFILE_MAP = {
    '1 White': {
        'fixed': 883009, 'moving': 883049, 'top_bottom': 883014,
        'sash_top_bottom': 883069, 'sash_pull': 883054, 'sash_moving': 883059
    },
    '2 Driftwood': {
        'fixed': 883011, 'moving': 883051, 'top_bottom': 883016,
        'sash_top_bottom': 883071, 'sash_pull': 883056, 'sash_moving': 883061
    },
    '4 Black': {
        'fixed': 883008, 'moving': 883048, 'top_bottom': 883013,
        'sash_top_bottom': 883068, 'sash_pull': 883053, 'sash_moving': 883058
    }
}


def get_profile_code(color_choice, profile_type):
    return COLOR_PROFILE_MAP[color_choice][profile_type]


# ── Session state ───────────────────────────────────────────────────
for key, default in [('windows', []), ('dealer', ''), ('tag', ''), ('color', '4 Black')]:
    if key not in st.session_state:
        st.session_state[key] = default


def renumber():
    for i, w in enumerate(st.session_state.windows, 1):
        w['number'] = i


# ════════════════════════════════════════════════════════════════════
#  CSV GENERATION  (v2.5 — 'Top' → 'TOP' fix)
# ════════════════════════════════════════════════════════════════════

def _row(sid, ktnbar, code, desc, wm10, hm10, orient, pos, nccode, today, color, colorcode):
    return [
        sid, 1, 1, 1, ktnbar, 90, 90, code, desc, wm10, hm10,
        0, 0, orient, 0, 0, pos, 0, 0,
        st.session_state.dealer, today, nccode,
        0, colorcode, color, code, st.session_state.tag,
        '', '', '', '', '', ''
    ]


def gen_fixed_lite(w, color, cc, today, sid):
    wm, hm, pos = w['width_mm'], w['height_mm'], w['number']
    code = get_profile_code(color, 'fixed')
    desc = PROFILE_DESCRIPTIONS[code]
    wm10, hm10 = int(round(wm * 10)), int(round(hm * 10))
    if w['width'] < 14.5:
        o, k = 'TOP/BOTTOM', int(round((wm + 2 * 25.4) * 10))
    else:
        o, k = 'UPRIGHT', int(round((hm + 25.4) * 10))
    return [_row(sid + i, k, code, desc, wm10, hm10, o, pos, 'Z MF_UPRIGHT_FIXED', today, color, cc) for i in range(2)]


def gen_sliding_xo(w, color, cc, today, sid):
    wm, hm, pos = w['width_mm'], w['height_mm'], w['number']
    wm10, hm10 = int(round(wm * 10)), int(round(hm * 10))
    fc, mc = get_profile_code(color, 'fixed'), get_profile_code(color, 'moving')
    stc = get_profile_code(color, 'sash_top_bottom')
    smc, spc = get_profile_code(color, 'sash_moving'), get_profile_code(color, 'sash_pull')
    uk = int(round((hm + 25.4) * 10))
    sk = int(round(((wm / 2) + 0.625 * 25.4) * 10))
    svk = int(round((hm - 4.8125 * 25.4) * 10))
    P = PROFILE_DESCRIPTIONS
    specs = [
        (fc,  P[fc],  'UPRIGHT', uk,  'Z MF_UPRIGHT FIXED SLIDING'),
        (mc,  P[mc],  'UPRIGHT', uk,  'Z MF_UPRIGHT MOVING SLIDING'),
        (stc, P[stc], 'BOTTOM',  sk,  'Z SASH TOP'),
        (stc, P[stc], 'TOP',     sk,  'Z SASH BOTTOM'),
        (smc, P[smc], 'LEFT',    svk, 'Z AL SASH UPRIGHT MOVING XO'),
        (spc, P[spc], 'RIGHT',   svk, 'Z SASH PULL UPRIGHT'),
    ]
    return [_row(sid + i, k, c, d, wm10, hm10, o, pos, nc, today, color, cc) for i, (c, d, o, k, nc) in enumerate(specs)]


def gen_sliding_ox(w, color, cc, today, sid):
    wm, hm, pos = w['width_mm'], w['height_mm'], w['number']
    wm10, hm10 = int(round(wm * 10)), int(round(hm * 10))
    fc, mc = get_profile_code(color, 'fixed'), get_profile_code(color, 'moving')
    stc = get_profile_code(color, 'sash_top_bottom')
    smc, spc = get_profile_code(color, 'sash_moving'), get_profile_code(color, 'sash_pull')
    uk = int(round((hm + 25.4) * 10))
    sk = int(round(((wm / 2) + 0.625 * 25.4) * 10))
    svk = int(round((hm - 4.8125 * 25.4) * 10))
    P = PROFILE_DESCRIPTIONS
    # v2.5 fix: 'Top' → 'TOP'
    specs = [
        (fc,  P[fc],  'UPRIGHT', uk,  'Z MF_UPRIGHT FIXED SLIDING OX'),
        (mc,  P[mc],  'UPRIGHT', uk,  'Z MF_UPRIGHT MOVING SLIDING OX'),
        (stc, P[stc], 'TOP',     sk,  'Z SASH TOP'),
        (stc, P[stc], 'BOTTOM',  sk,  'Z SASH BOTTOM'),
        (smc, P[smc], 'LEFT',    svk, 'Z AL SASH UPRIGHT MOVING OX'),
        (spc, P[spc], 'RIGHT',   svk, 'Z SASH PULL UPRIGHT'),
    ]
    return [_row(sid + i, k, c, d, wm10, hm10, o, pos, nc, today, color, cc) for i, (c, d, o, k, nc) in enumerate(specs)]


GENERATORS = {'Fixed Lite': gen_fixed_lite, 'Sliding Window XO': gen_sliding_xo, 'Sliding Window OX': gen_sliding_ox}


def generate_csv():
    if not st.session_state.windows:
        return None
    color = st.session_state.color
    cc    = COLOR_CODES[color]['colorcode']
    today = date.today().strftime('%Y-%m-%d')
    rows, rid = [], 1
    for w in st.session_state.windows:
        gen = GENERATORS.get(w['type'])
        if not gen:
            continue
        new = gen(w, color, cc, today, rid)
        rows.extend(new)
        rid += len(new)
    out = StringIO()
    csv.writer(out).writerow(CSV_HEADER)
    csv.writer(out).writerows(rows)
    return out.getvalue()


# ════════════════════════════════════════════════════════════════════
#  LAYOUT
# ════════════════════════════════════════════════════════════════════

# ── Header ──────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <h1>🪟 Window Profile Generator</h1>
    <span>v2.5  •  AL PROFILE CSV</span>
</div>
""", unsafe_allow_html=True)

# ── Stats bar (top, always visible) ────────────────────────────────
n_win = len(st.session_state.windows)
n_prof = sum(2 if w['type'] == 'Fixed Lite' else 6 for w in st.session_state.windows)
n_fl = sum(1 for w in st.session_state.windows if w['type'] == 'Fixed Lite')
n_xo = sum(1 for w in st.session_state.windows if w['type'] == 'Sliding Window XO')
n_ox = sum(1 for w in st.session_state.windows if w['type'] == 'Sliding Window OX')

m1, m2, m3, m4, m5, m6, m7 = st.columns([1, 1, 1, 1, 1, 2, 2])
m1.metric("Windows", n_win)
m2.metric("Profiles", n_prof)
m3.metric("Fixed", n_fl)
m4.metric("XO", n_xo)
m5.metric("OX", n_ox)
with m6:
    st.caption(f"Dealer: **{st.session_state.dealer or '—'}**")
    st.caption(f"Tag: **{st.session_state.tag or '—'}**")
with m7:
    st.caption(f"Color: **{st.session_state.color}**")
    st.caption(f"Date: **{date.today().strftime('%Y-%m-%d')}**")

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ── Main body: left input | right table ────────────────────────────
col_input, col_list = st.columns([1, 2.4], gap="large")

# ─── LEFT: Project Info + Add Form ─────────────────────────────────
with col_input:
    st.markdown('<div class="sec-label">Project Setup</div>', unsafe_allow_html=True)

    pc1, pc2 = st.columns(2)
    with pc1:
        st.session_state.dealer = st.text_input("Dealer", value=st.session_state.dealer, placeholder="Dealer name")
    with pc2:
        st.session_state.tag = st.text_input("Tag / ID", value=st.session_state.tag, placeholder="Project tag")

    st.session_state.color = st.selectbox(
        "Color", list(COLOR_CODES.keys()),
        index=list(COLOR_CODES.keys()).index(st.session_state.color)
    )

    st.markdown('<div class="sec-label" style="margin-top:16px">Add Windows</div>', unsafe_allow_html=True)

    with st.form("add_form", clear_on_submit=True):
        window_type = st.selectbox("Window Type", ["Fixed Lite", "Sliding Window XO", "Sliding Window OX"])

        wc1, wc2, wc3 = st.columns([2, 2, 1])
        with wc1:
            width_str = st.text_input("Width (in)", value="", placeholder="43.6875")
        with wc2:
            height_str = st.text_input("Height (in)", value="", placeholder="64.9375")
        with wc3:
            quantity = st.number_input("Qty", min_value=1, max_value=100, value=1)

        add_btn = st.form_submit_button("➕  Add Window(s)", type="primary", use_container_width=True)

        if add_btn:
            try:
                width = float(width_str) if width_str.strip() else 0.0
            except ValueError:
                width = -1.0
            try:
                height = float(height_str) if height_str.strip() else 0.0
            except ValueError:
                height = -1.0

            if width <= 0 or height <= 0:
                st.error("Enter valid width and height")
            else:
                narrow = []
                for _ in range(quantity):
                    num = len(st.session_state.windows) + 1
                    st.session_state.windows.append({
                        'number': num,
                        'width': width, 'height': height,
                        'width_mm': round(width * 25.4, 2),
                        'height_mm': round(height * 25.4, 2),
                        'type': window_type
                    })
                    if window_type == 'Fixed Lite' and width < 14.5:
                        narrow.append(num)
                renumber()
                if narrow:
                    st.warning(f"Pos {', '.join(map(str, narrow))}: narrow (<14.5\") → TOP/BOTTOM + width+2\"")
                st.rerun()

    # quick actions
    qa1, qa2 = st.columns(2)
    with qa1:
        if st.button("📋 Duplicate Last", use_container_width=True, disabled=n_win == 0):
            st.session_state.windows.append({**st.session_state.windows[-1]})
            renumber()
            st.rerun()
    with qa2:
        if st.button("🗑️ Clear All", use_container_width=True, disabled=n_win == 0):
            st.session_state.windows = []
            st.rerun()

    # generate
    st.markdown('<div class="sec-label" style="margin-top:16px">Output</div>', unsafe_allow_html=True)
    if st.button("📊  Generate CSV", type="primary", use_container_width=True, disabled=n_win == 0):
        if not st.session_state.dealer or not st.session_state.tag:
            st.error("Fill in Dealer and Tag")
        else:
            csv_data = generate_csv()
            if csv_data:
                st.success(f"{n_win} windows → {n_prof} profiles")
                st.download_button("⬇️  Download CSV", data=csv_data,
                                   file_name=f"{st.session_state.tag}_windows.csv",
                                   mime="text/csv", use_container_width=True)


# ─── RIGHT: Window List + Reorder ──────────────────────────────────
with col_list:
    st.markdown('<div class="sec-label">Window List</div>', unsafe_allow_html=True)

    if st.session_state.windows:
        df = pd.DataFrame(st.session_state.windows)
        df['profiles'] = df['type'].apply(lambda t: 2 if t == 'Fixed Lite' else 6)
        display_df = df[['number', 'type', 'width', 'height', 'width_mm', 'height_mm', 'profiles']]
        display_df.columns = ['Pos', 'Type', 'W (in)', 'H (in)', 'W (mm)', 'H (mm)', 'Profiles']

        st.dataframe(display_df, use_container_width=True, hide_index=True,
                     height=min(42 + 35 * len(st.session_state.windows), 520))

        # ── Reorder bar ─────────────────────────────────────────────
        st.markdown('<div class="sec-label" style="margin-top:8px">Reorder / Delete</div>', unsafe_allow_html=True)

        rc1, rc2, rc3, rc4 = st.columns([2.5, 1, 1, 1])
        with rc1:
            sel = st.number_input("Select window #", min_value=1,
                                  max_value=n_win, step=1, value=1,
                                  label_visibility="collapsed")
        with rc2:
            if st.button("⬆️ Move Up", use_container_width=True, disabled=(sel <= 1)):
                i = sel - 1
                w = st.session_state.windows
                w[i - 1], w[i] = w[i], w[i - 1]
                renumber()
                st.rerun()
        with rc3:
            if st.button("⬇️ Move Down", use_container_width=True, disabled=(sel >= n_win)):
                i = sel - 1
                w = st.session_state.windows
                w[i], w[i + 1] = w[i + 1], w[i]
                renumber()
                st.rerun()
        with rc4:
            if st.button("🗑️ Delete", use_container_width=True):
                st.session_state.windows.pop(sel - 1)
                renumber()
                st.rerun()
    else:
        st.info("← Add windows using the form")

# ── Footer ──────────────────────────────────────────────────────────
st.markdown('<div class="app-footer">AL Window Profile CSV Generator v2.5</div>', unsafe_allow_html=True)
