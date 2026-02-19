"""
AL Window Profile CSV Generator - Streamlit Web App v2.5
Single-view layout — no sidebar, everything visible at once.
Supports insert-at-position and reordering.
"""

import streamlit as st
import pandas as pd
import csv
from datetime import date
from io import StringIO

# ── Page config ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="AL Window Profile Generator",
    page_icon="🪟",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Hide sidebar completely ─────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="collapsedControl"] { display: none; }
    section[data-testid="stSidebar"] { display: none; }
    .block-container { padding-top: 1.5rem; padding-bottom: 1rem; max-width: 1600px; }
    div[data-testid="stMetric"] {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 12px 16px;
    }
    div[data-testid="stMetric"] label { font-size: 0.8rem; color: #64748B; }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] { font-size: 1.6rem; color: #1E40AF; }
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
if 'windows' not in st.session_state:
    st.session_state.windows = []
if 'dealer' not in st.session_state:
    st.session_state.dealer = ''
if 'tag' not in st.session_state:
    st.session_state.tag = ''
if 'color' not in st.session_state:
    st.session_state.color = '4 Black'


def renumber_windows():
    """Renumber all windows sequentially after any insert/delete/move."""
    for i, w in enumerate(st.session_state.windows, 1):
        w['number'] = i


# ════════════════════════════════════════════════════════════════════
#  CSV GENERATION LOGIC  (v2.5 — 'Top' → 'TOP' fix applied)
# ════════════════════════════════════════════════════════════════════
def gen_fixed_lite(window, color, colorcode, today, start_id):
    rows = []
    wm, hm = window['width_mm'], window['height_mm']
    pos = window['number']
    code = get_profile_code(color, 'fixed')
    desc = PROFILE_DESCRIPTIONS[code]

    if window['width'] < 14.5:
        orient = 'TOP/BOTTOM'
        ktnbar = int(round((wm + 2 * 25.4) * 10))
    else:
        orient = 'UPRIGHT'
        ktnbar = int(round((hm + 25.4) * 10))

    for i in range(2):
        rows.append([
            start_id + i, 1, 1, 1, ktnbar, 90, 90,
            code, desc,
            int(round(wm * 10)), int(round(hm * 10)),
            0, 0, orient, 0, 0, pos, 0, 0,
            st.session_state.dealer, today, 'Z MF_UPRIGHT_FIXED',
            0, colorcode, color, code, st.session_state.tag,
            '', '', '', '', '', ''
        ])
    return rows


def gen_sliding_xo(window, color, colorcode, today, start_id):
    rows = []
    wm, hm = window['width_mm'], window['height_mm']
    pos = window['number']

    fc  = get_profile_code(color, 'fixed')
    mc  = get_profile_code(color, 'moving')
    stc = get_profile_code(color, 'sash_top_bottom')
    smc = get_profile_code(color, 'sash_moving')
    spc = get_profile_code(color, 'sash_pull')

    upright_k = int(round((hm + 25.4) * 10))
    sash_tb_k = int(round(((wm / 2) + 0.625 * 25.4) * 10))
    sash_up_k = int(round((hm - 4.8125 * 25.4) * 10))

    wd = int(round(wm * 10))
    ht = int(round(hm * 10))

    profiles = [
        (fc,  PROFILE_DESCRIPTIONS[fc],  'UPRIGHT', upright_k, 'Z MF_UPRIGHT FIXED SLIDING'),
        (mc,  PROFILE_DESCRIPTIONS[mc],  'UPRIGHT', upright_k, 'Z MF_UPRIGHT MOVING SLIDING'),
        (stc, PROFILE_DESCRIPTIONS[stc], 'BOTTOM',  sash_tb_k, 'Z SASH TOP'),
        (stc, PROFILE_DESCRIPTIONS[stc], 'TOP',     sash_tb_k, 'Z SASH BOTTOM'),
        (smc, PROFILE_DESCRIPTIONS[smc], 'LEFT',    sash_up_k, 'Z AL SASH UPRIGHT MOVING XO'),
        (spc, PROFILE_DESCRIPTIONS[spc], 'RIGHT',   sash_up_k, 'Z SASH PULL UPRIGHT'),
    ]

    for i, (code, desc, orient, ktnbar, nccode) in enumerate(profiles):
        rows.append([
            start_id + i, 1, 1, 1, ktnbar, 90, 90,
            code, desc, wd, ht, 0, 0, orient, 0, 0, pos, 0, 0,
            st.session_state.dealer, today, nccode,
            0, colorcode, color, code, st.session_state.tag,
            '', '', '', '', '', ''
        ])
    return rows


def gen_sliding_ox(window, color, colorcode, today, start_id):
    rows = []
    wm, hm = window['width_mm'], window['height_mm']
    pos = window['number']

    fc  = get_profile_code(color, 'fixed')
    mc  = get_profile_code(color, 'moving')
    stc = get_profile_code(color, 'sash_top_bottom')
    smc = get_profile_code(color, 'sash_moving')
    spc = get_profile_code(color, 'sash_pull')

    upright_k = int(round((hm + 25.4) * 10))
    sash_tb_k = int(round(((wm / 2) + 0.625 * 25.4) * 10))
    sash_up_k = int(round((hm - 4.8125 * 25.4) * 10))

    wd = int(round(wm * 10))
    ht = int(round(hm * 10))

    # FIX v2.5: 'Top' → 'TOP' (case consistency)
    # OX orientation pattern is intentionally NOT swapped (confirmed correct)
    profiles = [
        (fc,  PROFILE_DESCRIPTIONS[fc],  'UPRIGHT', upright_k, 'Z MF_UPRIGHT FIXED SLIDING OX'),
        (mc,  PROFILE_DESCRIPTIONS[mc],  'UPRIGHT', upright_k, 'Z MF_UPRIGHT MOVING SLIDING OX'),
        (stc, PROFILE_DESCRIPTIONS[stc], 'TOP',     sash_tb_k, 'Z SASH TOP'),
        (stc, PROFILE_DESCRIPTIONS[stc], 'BOTTOM',  sash_tb_k, 'Z SASH BOTTOM'),
        (smc, PROFILE_DESCRIPTIONS[smc], 'LEFT',    sash_up_k, 'Z AL SASH UPRIGHT MOVING OX'),
        (spc, PROFILE_DESCRIPTIONS[spc], 'RIGHT',   sash_up_k, 'Z SASH PULL UPRIGHT'),
    ]

    for i, (code, desc, orient, ktnbar, nccode) in enumerate(profiles):
        rows.append([
            start_id + i, 1, 1, 1, ktnbar, 90, 90,
            code, desc, wd, ht, 0, 0, orient, 0, 0, pos, 0, 0,
            st.session_state.dealer, today, nccode,
            0, colorcode, color, code, st.session_state.tag,
            '', '', '', '', '', ''
        ])
    return rows


def generate_csv():
    if not st.session_state.windows:
        return None

    color     = st.session_state.color
    colorcode = COLOR_CODES[color]['colorcode']
    today     = date.today().strftime('%Y-%m-%d')

    rows   = []
    row_id = 1

    for window in st.session_state.windows:
        wtype = window['type']
        if wtype == 'Fixed Lite':
            new_rows = gen_fixed_lite(window, color, colorcode, today, row_id)
        elif wtype == 'Sliding Window XO':
            new_rows = gen_sliding_xo(window, color, colorcode, today, row_id)
        elif wtype == 'Sliding Window OX':
            new_rows = gen_sliding_ox(window, color, colorcode, today, row_id)
        else:
            continue
        rows.extend(new_rows)
        row_id += len(new_rows)

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(CSV_HEADER)
    writer.writerows(rows)
    return output.getvalue()


# ════════════════════════════════════════════════════════════════════
#  UI LAYOUT
# ════════════════════════════════════════════════════════════════════

# ── Header ──────────────────────────────────────────────────────────
st.markdown("""
<div style="background:#1E293B; padding:16px 24px; border-radius:10px; margin-bottom:16px;">
    <span style="color:#FFFFFF; font-size:1.4rem; font-weight:700;">🪟 Window Profile Generator</span>
    <span style="color:#94A3B8; font-size:0.85rem; margin-left:12px;">AL Profile CSV Tool  •  v2.5</span>
</div>
""", unsafe_allow_html=True)

# ── Three-column layout ────────────────────────────────────────────
col_left, col_mid, col_right = st.columns([3, 5, 2.5], gap="medium")

# ─── LEFT: Project Info + Add Windows ──────────────────────────────
with col_left:
    st.markdown("**Project Info**")
    st.session_state.dealer = st.text_input(
        "Dealer", value=st.session_state.dealer,
        label_visibility="collapsed", placeholder="Dealer name"
    )
    st.session_state.tag = st.text_input(
        "Tag", value=st.session_state.tag,
        label_visibility="collapsed", placeholder="Tag / Project ID"
    )
    st.session_state.color = st.selectbox(
        "Color", list(COLOR_CODES.keys()),
        index=list(COLOR_CODES.keys()).index(st.session_state.color),
        label_visibility="collapsed"
    )

    st.divider()
    st.markdown("**Add Windows**")

    with st.form("add_window_form", clear_on_submit=True):
        window_type = st.selectbox("Type", ["Fixed Lite", "Sliding Window XO", "Sliding Window OX"])

        fc1, fc2 = st.columns(2)
        with fc1:
            width_str = st.text_input("Width (in)", value="", placeholder="e.g. 43.6875")
        with fc2:
            height_str = st.text_input("Height (in)", value="", placeholder="e.g. 64.9375")

        qc1, qc2 = st.columns(2)
        with qc1:
            quantity = st.number_input("Qty", min_value=1, max_value=100, value=1)
        with qc2:
            max_pos = len(st.session_state.windows) + 1
            insert_at = st.number_input(
                "Insert at pos#",
                min_value=1, max_value=max_pos, value=max_pos,
                help="Where to insert. Default = end of list."
            )

        submitted = st.form_submit_button("Add Window(s)", type="primary", use_container_width=True)

        if submitted:
            # Validate width
            try:
                width = float(width_str) if width_str.strip() else 0.0
            except ValueError:
                width = -1.0

            # Validate height
            try:
                height = float(height_str) if height_str.strip() else 0.0
            except ValueError:
                height = -1.0

            if width <= 0 or height <= 0:
                st.error("Enter valid positive numbers for width and height")
            else:
                narrow = []
                insert_idx = insert_at - 1  # 0-based

                for i in range(quantity):
                    new_win = {
                        'number': 0,  # renumber below
                        'width': width, 'height': height,
                        'width_mm': round(width * 25.4, 2),
                        'height_mm': round(height * 25.4, 2),
                        'type': window_type
                    }
                    st.session_state.windows.insert(insert_idx + i, new_win)

                    if window_type == 'Fixed Lite' and width < 14.5:
                        narrow.append(insert_at + i)

                renumber_windows()

                st.success(f"Added {quantity} window(s) at position {insert_at}")
                if narrow:
                    st.warning(
                        f"Window(s) at pos {', '.join(map(str, narrow))} "
                        f"< 14.5\" — uses TOP/BOTTOM + width+2\""
                    )
                st.rerun()

    # ── Action buttons ──────────────────────────────────────────────
    ac1, ac2 = st.columns(2)
    with ac1:
        if st.button("📋 Duplicate Last", use_container_width=True,
                     disabled=len(st.session_state.windows) == 0):
            last = st.session_state.windows[-1].copy()
            st.session_state.windows.append(last)
            renumber_windows()
            st.rerun()
    with ac2:
        if st.button("🗑️ Clear All", use_container_width=True,
                     disabled=len(st.session_state.windows) == 0):
            st.session_state.windows = []
            st.rerun()


# ─── CENTER: Window List + Reorder ─────────────────────────────────
with col_mid:
    st.markdown("**Window List**")

    if st.session_state.windows:
        df = pd.DataFrame(st.session_state.windows)
        df['profiles'] = df['type'].apply(lambda t: 2 if t == 'Fixed Lite' else 6)
        df = df[['number', 'type', 'width', 'height', 'width_mm', 'height_mm', 'profiles']]
        df.columns = ['Pos', 'Type', 'W (in)', 'H (in)', 'W (mm)', 'H (mm)', 'Profiles']

        st.dataframe(df, use_container_width=True, hide_index=True, height=380)

        # ── Reorder / Delete row ────────────────────────────────────
        st.caption("Manage windows")
        rc1, rc2, rc3, rc4 = st.columns([2, 1, 1, 1])
        with rc1:
            sel_num = st.number_input(
                "Window #", min_value=1,
                max_value=len(st.session_state.windows), step=1, value=1,
                label_visibility="collapsed"
            )
        with rc2:
            if st.button("⬆️ Up", use_container_width=True, disabled=sel_num <= 1):
                idx = sel_num - 1
                w = st.session_state.windows
                w[idx], w[idx - 1] = w[idx - 1], w[idx]
                renumber_windows()
                st.rerun()
        with rc3:
            if st.button("⬇️ Down", use_container_width=True,
                         disabled=sel_num >= len(st.session_state.windows)):
                idx = sel_num - 1
                w = st.session_state.windows
                w[idx], w[idx + 1] = w[idx + 1], w[idx]
                renumber_windows()
                st.rerun()
        with rc4:
            if st.button("🗑️ Del", use_container_width=True):
                st.session_state.windows.pop(sel_num - 1)
                renumber_windows()
                st.rerun()
    else:
        st.info("Add windows using the form on the left")


# ─── RIGHT: Summary + Generate ─────────────────────────────────────
with col_right:
    st.markdown("**Summary**")

    n_windows  = len(st.session_state.windows)
    n_profiles = sum(2 if w['type'] == 'Fixed Lite' else 6 for w in st.session_state.windows)
    n_fixed    = sum(1 for w in st.session_state.windows if w['type'] == 'Fixed Lite')
    n_xo       = sum(1 for w in st.session_state.windows if w['type'] == 'Sliding Window XO')
    n_ox       = sum(1 for w in st.session_state.windows if w['type'] == 'Sliding Window OX')

    st.metric("Windows", n_windows)
    st.metric("Profiles", n_profiles)

    mc1, mc2, mc3 = st.columns(3)
    with mc1:
        st.metric("Fixed", n_fixed)
    with mc2:
        st.metric("XO", n_xo)
    with mc3:
        st.metric("OX", n_ox)

    st.divider()
    st.markdown("**Settings**")
    st.caption(f"Dealer: {st.session_state.dealer or '—'}")
    st.caption(f"Tag: {st.session_state.tag or '—'}")
    st.caption(f"Color: {st.session_state.color}")

    st.divider()

    if st.button("📊 Generate CSV", type="primary", use_container_width=True,
                 disabled=n_windows == 0):
        if not st.session_state.dealer or not st.session_state.tag:
            st.error("Fill in Dealer and Tag first")
        else:
            csv_data = generate_csv()
            if csv_data:
                st.success(f"{n_windows} windows → {n_profiles} profiles")
                st.download_button(
                    label="⬇️ Download CSV",
                    data=csv_data,
                    file_name=f"{st.session_state.tag}_windows.csv",
                    mime="text/csv",
                    use_container_width=True
                )

# ── Footer ──────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; color:#94A3B8; padding:12px 0 4px; font-size:0.75rem;'>
    AL Window Profile CSV Generator v2.5 • Streamlit
</div>
""", unsafe_allow_html=True)
