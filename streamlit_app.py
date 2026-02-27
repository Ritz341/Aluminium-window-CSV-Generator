"""
AL Window Profile CSV Generator — Streamlit v2.6
Click-to-select rows, move-to-position, import CSV, summary panels.
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
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    [data-testid="collapsedControl"] { display: none; }
    section[data-testid="stSidebar"] { display: none; }

    .block-container {
        padding: 0.6rem 1.5rem 0.6rem 1.5rem;
        max-width: 1800px;
        font-family: 'JetBrains Mono', 'Consolas', monospace;
    }

    /* dark header */
    .app-header {
        background: linear-gradient(135deg, #1A1A2E 0%, #16213E 100%);
        padding: 12px 22px;
        border-radius: 8px;
        margin-bottom: 10px;
        display: flex; align-items: baseline; gap: 14px;
        border-bottom: 3px solid #F5A623;
    }
    .app-header h1 {
        color: #F5A623; font-family: 'JetBrains Mono', monospace;
        font-size: 1.15rem; font-weight: 700; margin: 0; letter-spacing: 0.02em;
    }
    .app-header span { color: #7F8C8D; font-size: 0.72rem; }

    /* section labels */
    .sec-label {
        font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; font-weight: 600;
        text-transform: uppercase; letter-spacing: 0.1em; color: #F5A623;
        border-bottom: 1px solid #2C3E6B; padding-bottom: 4px; margin-bottom: 8px;
    }

    /* metrics */
    div[data-testid="stMetric"] {
        background: #16213E; border: 1px solid #2C3E6B; border-radius: 6px;
        padding: 6px 10px; border-left: 3px solid #F5A623;
    }
    div[data-testid="stMetric"] label {
        font-family: 'JetBrains Mono', monospace; font-size: 0.6rem;
        text-transform: uppercase; letter-spacing: 0.08em; color: #7F8C8D;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace; font-size: 1.2rem;
        font-weight: 600; color: #00D2FF;
    }

    /* selection hint */
    .sel-hint {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.68rem; color: #F5A623; padding: 4px 0; font-weight: 600;
    }
    .sel-none { font-size: 0.68rem; color: #7F8C8D; padding: 4px 0; }

    /* table */
    div[data-testid="stDataFrame"] { border: 1px solid #2C3E6B; border-radius: 6px; }

    /* info box */
    .info-box {
        background: #16213E; border: 1px solid #2C3E6B; border-radius: 6px;
        padding: 10px 14px; margin: 6px 0; font-size: 0.72rem;
        font-family: 'JetBrains Mono', monospace; color: #7F8C8D;
        line-height: 1.6;
    }
    .info-box b { color: #00D2FF; }
    .info-box .amber { color: #F5A623; }

    .app-footer {
        text-align: center; color: #7F8C8D;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.58rem; padding: 6px 0 2px; letter-spacing: 0.05em;
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
defaults = {'windows': [], 'dealer': '', 'tag': '', 'color': '4 Black', 'msg': ''}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


def renumber():
    for i, w in enumerate(st.session_state.windows, 1):
        w['number'] = i


# ════════════════════════════════════════════════════════════════════
#  CSV GENERATION (v2.6)
# ════════════════════════════════════════════════════════════════════

def _row(sid, ktnbar, code, desc, wm10, hm10, orient, pos, nccode, today, color, colorcode, tag):
    return [
        sid, 1, 1, 1, ktnbar, 90, 90, code, desc, wm10, hm10,
        0, 0, orient, 0, 0, pos, 0, 0,
        st.session_state.dealer, today, nccode,
        0, colorcode, color, code, tag,
        '', '', '', '', '', ''
    ]


def gen_fixed_lite(w, color, cc, today, sid):
    tag = f"FXLITE_{st.session_state.tag}"
    wm, hm, pos = w['width_mm'], w['height_mm'], w['number']
    code = get_profile_code(color, 'fixed')
    desc = PROFILE_DESCRIPTIONS[code]
    wm10, hm10 = int(round(wm * 10)), int(round(hm * 10))
    if w['height'] < 14.5:
        o, k = 'TOP/BOTTOM', int(round((wm + 2 * 25.4) * 10))
    else:
        o, k = 'UPRIGHT', int(round((hm + 25.4) * 10))
    return [_row(sid + i, k, code, desc, wm10, hm10, o, pos, 'Z MF_UPRIGHT_FIXED', today, color, cc, tag) for i in range(2)]


def gen_sliding_xo(w, color, cc, today, sid):
    tag = f"XO_{st.session_state.tag}"
    wm, hm, pos = w['width_mm'], w['height_mm'], w['number']
    wm10, hm10 = int(round(wm * 10)), int(round(hm * 10))
    fc, mc = get_profile_code(color, 'fixed'), get_profile_code(color, 'moving')
    stc = get_profile_code(color, 'sash_top_bottom')
    smc, spc = get_profile_code(color, 'sash_moving'), get_profile_code(color, 'sash_pull')
    uk = int(round((hm + 25.4) * 10))
    sk = int(round(((wm / 2) + 0.625 * 25.4) * 10))
    vk = int(round((hm - 4.8125 * 25.4) * 10))
    P = PROFILE_DESCRIPTIONS
    specs = [
        (fc, P[fc], 'UPRIGHT', uk, 'Z MF_UPRIGHT FIXED SLIDING'),
        (mc, P[mc], 'UPRIGHT', uk, 'Z MF_UPRIGHT MOVING SLIDING'),
        (stc, P[stc], 'BOTTOM', sk, 'Z SASH TOP'),
        (stc, P[stc], 'TOP', sk, 'Z SASH BOTTOM'),
        (smc, P[smc], 'LEFT', vk, 'Z AL SASH UPRIGHT MOVING XO'),
        (spc, P[spc], 'RIGHT', vk, 'Z SASH PULL UPRIGHT'),
    ]
    return [_row(sid + i, k, c, d, wm10, hm10, o, pos, nc, today, color, cc, tag) for i, (c, d, o, k, nc) in enumerate(specs)]


def gen_sliding_ox(w, color, cc, today, sid):
    tag = f"OX_{st.session_state.tag}"
    wm, hm, pos = w['width_mm'], w['height_mm'], w['number']
    wm10, hm10 = int(round(wm * 10)), int(round(hm * 10))
    fc, mc = get_profile_code(color, 'fixed'), get_profile_code(color, 'moving')
    stc = get_profile_code(color, 'sash_top_bottom')
    smc, spc = get_profile_code(color, 'sash_moving'), get_profile_code(color, 'sash_pull')
    uk = int(round((hm + 25.4) * 10))
    sk = int(round(((wm / 2) + 0.625 * 25.4) * 10))
    vk = int(round((hm - 4.8125 * 25.4) * 10))
    P = PROFILE_DESCRIPTIONS
    specs = [
        (fc, P[fc], 'UPRIGHT', uk, 'Z MF_UPRIGHT FIXED SLIDING OX'),
        (mc, P[mc], 'UPRIGHT', uk, 'Z MF_UPRIGHT MOVING SLIDING OX'),
        (stc, P[stc], 'TOP', sk, 'Z SASH TOP'),
        (stc, P[stc], 'BOTTOM', sk, 'Z SASH BOTTOM'),
        (smc, P[smc], 'LEFT', vk, 'Z AL SASH UPRIGHT MOVING OX'),
        (spc, P[spc], 'RIGHT', vk, 'Z SASH PULL UPRIGHT'),
    ]
    return [_row(sid + i, k, c, d, wm10, hm10, o, pos, nc, today, color, cc, tag) for i, (c, d, o, k, nc) in enumerate(specs)]


GENERATORS = {'Fixed Lite': gen_fixed_lite, 'Sliding Window XO': gen_sliding_xo, 'Sliding Window OX': gen_sliding_ox}


def generate_csv():
    if not st.session_state.windows:
        return None
    color = st.session_state.color
    cc = COLOR_CODES[color]['colorcode']
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
    writer = csv.writer(out)
    writer.writerow(CSV_HEADER)
    writer.writerows(rows)
    return out.getvalue()


def import_csv_data(uploaded):
    """Parse an uploaded CSV back into window list."""
    try:
        content = uploaded.read().decode('utf-8')
        reader = csv.reader(StringIO(content))
        header = next(reader)
        rows = list(reader)
        if not rows:
            return False, 'CSV is empty'

        seen = {}
        for row in rows:
            pos = int(row[16])
            if pos not in seen:
                w_mm = int(row[9]) / 10.0
                h_mm = int(row[10]) / 10.0
                nc = row[21]
                if 'SLIDING OX' in nc or 'MOVING OX' in nc:
                    wtype = 'Sliding Window OX'
                elif 'SLIDING' in nc or 'MOVING' in nc:
                    wtype = 'Sliding Window XO'
                else:
                    wtype = 'Fixed Lite'
                seen[pos] = {
                    'number': pos,
                    'width': round(w_mm / 25.4, 4),
                    'height': round(h_mm / 25.4, 4),
                    'width_mm': w_mm,
                    'height_mm': h_mm,
                    'type': wtype
                }
        st.session_state.windows = [seen[k] for k in sorted(seen.keys())]

        # extract dealer / tag
        st.session_state.dealer = rows[0][19]
        raw_tag = rows[0][27]
        for prefix in ['FXLITE_', 'XO_', 'OX_']:
            if raw_tag.startswith(prefix):
                raw_tag = raw_tag[len(prefix):]
                break
        st.session_state.tag = raw_tag
        renumber()
        return True, f'Imported {len(st.session_state.windows)} windows'
    except Exception as e:
        return False, str(e)


# ════════════════════════════════════════════════════════════════════
#  LAYOUT
# ════════════════════════════════════════════════════════════════════

# ── Header ──────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <h1>▣ WINDOW PROFILE GENERATOR</h1>
    <span>v2.6 &nbsp;•&nbsp; AL PROFILE CSV</span>
</div>
""", unsafe_allow_html=True)

# ── Stats bar ───────────────────────────────────────────────────────
n_win = len(st.session_state.windows)
n_prof = sum(2 if w['type'] == 'Fixed Lite' else 6 for w in st.session_state.windows)
n_fl = sum(1 for w in st.session_state.windows if w['type'] == 'Fixed Lite')
n_xo = sum(1 for w in st.session_state.windows if w['type'] == 'Sliding Window XO')
n_ox = sum(1 for w in st.session_state.windows if w['type'] == 'Sliding Window OX')

m1, m2, m3, m4, m5, m6 = st.columns([1, 1, 1, 1, 1, 2.5])
m1.metric("Windows", n_win)
m2.metric("Profiles", n_prof)
m3.metric("Fixed", n_fl)
m4.metric("XO", n_xo)
m5.metric("OX", n_ox)
with m6:
    info_parts = []
    d = st.session_state.dealer or '---'
    t = st.session_state.tag or '---'
    st.markdown(
        f'<div class="info-box">'
        f'<b>DEALER:</b> {d.upper()} &nbsp;|&nbsp; '
        f'<b>TAG:</b> {t.upper()} &nbsp;|&nbsp; '
        f'<span class="amber">{st.session_state.color}</span> &nbsp;|&nbsp; '
        f'{date.today().strftime("%Y-%m-%d")}'
        f'</div>', unsafe_allow_html=True)

# show status message
if st.session_state.msg:
    st.success(st.session_state.msg)
    st.session_state.msg = ''

# ── Main body ───────────────────────────────────────────────────────
col_input, col_list = st.columns([1, 2.6], gap="medium")

# ─── LEFT: Inputs ──────────────────────────────────────────────────
with col_input:
    st.markdown('<div class="sec-label">// PROJECT SETUP</div>', unsafe_allow_html=True)
    pc1, pc2 = st.columns(2)
    with pc1:
        st.session_state.dealer = st.text_input("Dealer", value=st.session_state.dealer, placeholder="Dealer name")
    with pc2:
        st.session_state.tag = st.text_input("Tag", value=st.session_state.tag, placeholder="Project tag")
    st.session_state.color = st.selectbox(
        "Color", list(COLOR_CODES.keys()),
        index=list(COLOR_CODES.keys()).index(st.session_state.color)
    )

    st.markdown('<div class="sec-label">// ADD WINDOWS</div>', unsafe_allow_html=True)

    with st.form("add_form", clear_on_submit=True):
        window_type = st.selectbox("Type", ["Fixed Lite", "Sliding Window XO", "Sliding Window OX"])
        wc1, wc2, wc3 = st.columns([2, 2, 1])
        with wc1:
            width_str = st.text_input("W (in)", value="", placeholder="43.6875")
        with wc2:
            height_str = st.text_input("H (in)", value="", placeholder="64.9375")
        with wc3:
            quantity = st.number_input("Qty", min_value=1, max_value=100, value=1)

        if st.form_submit_button("➕  ADD WINDOW(S)", type="primary", use_container_width=True):
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
            elif window_type == 'Fixed Lite' and height < 12.75:
                st.error(f"Height {height}\" is below 12.75\" minimum — cannot run on machine")
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
                    if window_type == 'Fixed Lite' and height < 14.5:
                        narrow.append(num)
                renumber()
                if narrow:
                    st.warning(f"Pos {', '.join(map(str, narrow))}: height < 14.5\" → TOP/BOTTOM, ktnbar = width+2\"")
                st.rerun()

    # Quick actions
    qa1, qa2 = st.columns(2)
    with qa1:
        if st.button("📋 Dup Last", use_container_width=True, disabled=n_win == 0):
            st.session_state.windows.append({**st.session_state.windows[-1]})
            renumber()
            st.rerun()
    with qa2:
        if st.button("🗑 Clear All", use_container_width=True, disabled=n_win == 0):
            st.session_state.windows = []
            st.rerun()

    # Import CSV
    st.markdown('<div class="sec-label">// IMPORT / EXPORT</div>', unsafe_allow_html=True)

    uploaded = st.file_uploader("Import existing CSV", type=['csv'], label_visibility='collapsed')
    if uploaded is not None:
        ok, msg = import_csv_data(uploaded)
        if ok:
            st.session_state.msg = msg
            st.rerun()
        else:
            st.error(msg)

    if st.button("📊  GENERATE CSV", type="primary", use_container_width=True, disabled=n_win == 0):
        if not st.session_state.dealer or not st.session_state.tag:
            st.error("Fill in Dealer and Tag")
        else:
            csv_data = generate_csv()
            if csv_data:
                st.success(f"{n_win} windows → {n_prof} profiles")
                st.download_button("⬇️  DOWNLOAD CSV", data=csv_data,
                                   file_name=f"{st.session_state.tag}_windows.csv",
                                   mime="text/csv", use_container_width=True)

    # Formulas reference (collapsible)
    with st.expander("📐 FORMULAS REFERENCE"):
        st.markdown("""
**Fixed Lite (height ≥ 14.5"):**
- Orientation: UPRIGHT
- ktnbar = (height + 1") × 10

**Fixed Lite (height < 14.5", min 12.75"):**
- Orientation: TOP/BOTTOM
- ktnbar = (width + 2") × 10

**Sliding XO / OX:**
- Main frame upright: (height + 1") × 10
- Sash top/bottom: ((width/2) + 0.625") × 10
- Sash upright: (height - 4.8125") × 10
        """)


# ─── RIGHT: Clickable Table + Actions ──────────────────────────────
with col_list:
    st.markdown('<div class="sec-label">// WINDOW LIST — click row to select</div>', unsafe_allow_html=True)

    if st.session_state.windows:
        df = pd.DataFrame(st.session_state.windows)
        df['profiles'] = df['type'].apply(lambda t: 2 if t == 'Fixed Lite' else 6)
        display_df = df[['number', 'type', 'width', 'height', 'width_mm', 'height_mm', 'profiles']]
        display_df.columns = ['POS', 'TYPE', 'W (in)', 'H (in)', 'W (mm)', 'H (mm)', 'PROFILES']

        # Clickable dataframe
        event = st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            height=min(38 + 28 * len(st.session_state.windows), 460),
            on_select="rerun",
            selection_mode="single-row",
            key="window_table"
        )

        selected_rows = event.selection.rows if event.selection.rows else []
        sel_idx = selected_rows[0] if selected_rows else None

        # Selection info
        if sel_idx is not None:
            w = st.session_state.windows[sel_idx]
            st.markdown(
                f'<div class="sel-hint">▶ POS {w["number"]} — '
                f'{w["type"].upper()}  {w["width"]}" × {w["height"]}"</div>',
                unsafe_allow_html=True)
        else:
            st.markdown('<div class="sel-none">Click a row to select</div>', unsafe_allow_html=True)

        # ── Action buttons — row 1: move ────────────────────────────
        ac1, ac2, ac3, ac4, ac5 = st.columns([1, 1, 0.6, 0.8, 1])
        with ac1:
            if st.button("⬆️ UP", use_container_width=True, disabled=(sel_idx is None or sel_idx == 0)):
                i = sel_idx
                w = st.session_state.windows
                w[i - 1], w[i] = w[i], w[i - 1]
                renumber()
                st.rerun()
        with ac2:
            if st.button("⬇️ DOWN", use_container_width=True, disabled=(sel_idx is None or sel_idx >= n_win - 1)):
                i = sel_idx
                w = st.session_state.windows
                w[i], w[i + 1] = w[i + 1], w[i]
                renumber()
                st.rerun()
        with ac3:
            move_to = st.text_input("TO#", value="", placeholder="#", label_visibility="collapsed",
                                    key="moveto_input")
        with ac3:            move_to = st.text_input("TO#", value="", placeholder="#", label_visibility="collapsed",                                    key="moveto_input")        with ac4:            if st.button("GO", use_container_width=True, disabled=sel_idx is None):                try:                    target = int(move_to) - 1                    if target < 0 or target >= n_win:                        raise ValueError                    if sel_idx is not None and sel_idx != target:                        item = st.session_state.windows.pop(sel_idx)                        st.session_state.windows.insert(target, item)                        renumber()                        st.rerun()                except (ValueError, TypeError):                    st.error(f"Enter 1-{n_win}")        with ac5:            st.markdown(f'<div class="sel-none" style="padding-top:8px">MOVE TO POS</div>',                        unsafe_allow_html=True)        # ── Action buttons — row 2: edit ────────────────────────────        bc1, bc2, bc3, bc4 = st.columns(4)        with bc1:            if st.button("󓋠DUP", use_container_width=True, disabled=sel_idx is None):                dup = {**st.session_state.windows[sel_idx]}                st.session_state.windows.insert(sel_idx + 1, dup)                renumber()                st.rerun()        with bc2:            if st.button("󗑠DEL", use_container_width=True, disabled=sel_idx is None):                st.session_state.windows.pop(sel_idx)                renumber()                st.rerun()        with bc3:            if st.button("󔄠NEW", use_container_width=True):                st.session_state.windows = []                st.session_state.dealer = ''                st.session_state.tag = ''                st.rerun()        with bc4:            # Summary            if st.button("󓊠SUMMARY", use_container_width=True, disabled=n_win == 0):                st.session_state['show_summary'] = not st.session_state.get('show_summary', False)        # Summary panel
  if st.session_state.get('show_summary', False) and n_win > 0:            st.markdown(                f'<div class="info-box">'                f'<span class="amber">// PROFILE SUMMARY</span><br>'                f'<b>TOTAL WINDOWS:</b> {n_win}<br>'                f'<b>TOTAL PROFILES:</b> {n_prof}<br>'                f'FIXED LITE: {n_fl} ({n_fl*2} profiles) &nbsp;|&nbsp; '                f'SLIDING XO: {n_xo} ({n_xo*6} profiles) &nbsp;|&nbsp; '                f'SLIDING OX: {n_ox} ({n_ox*6} profiles)<br>'                f'<b>DEALER:</b> {st.session_state.dealer} &nbsp;|&nbsp; '                f'<b>TAG:</b> {st.session_state.tag} &nbsp;|&nbsp; '                f'<span class="amber">{st.session_state.color}</span>'                f'</div>', unsafe_allow_html=True)    else:        st.info(" ← Add windows using the form, or import an existing CSV") # ── Footer ────────────────────────────────────────────────────────── st.markdown('<div class="app-footer">AL WINDOW PROFILE CSV GENERATOR v2.6</div>', unsafe_allow_html=True)