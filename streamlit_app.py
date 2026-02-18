"""
AL Window Profile CSV Generator - Streamlit Web App
Modern web interface for generating window profile CSV files
"""

import streamlit as st
import pandas as pd
import csv
from datetime import date
from io import StringIO
import base64

# Page config
st.set_page_config(
    page_title="AL Window Profile Generator",
    page_icon="🪟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    h1 {
        color: #1E3A8A;
        padding-bottom: 1rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #D1FAE5;
        border: 1px solid #34D399;
        margin: 1rem 0;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #FEF3C7;
        border: 1px solid #FBBF24;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Constants
CSV_HEADER = [
    'id', 'ksn', 'ksnbar', 'ktn', 'ktnbar', 'l', 'r', 'code', 'info', 
    'width', 'height', 'trolley', 'box', 'orientation', 'reinf', 'reinfbar', 
    'pos', 'prono', 'offno', 'customer', 'date', 'nccode', 'isfix', 'colorcode', 
    'colorinfo', 'mainprofile', 'subcust', 'image', 'DATA1', 'DATA2', 'DATA3', 
    'DATA4', 'DATA5'
]

COLOR_CODES = {
    '4 Black': {'code': 883008, 'colorcode': '4'},
    '1 White': {'code': 883009, 'colorcode': '1'},
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

# Initialize session state
if 'windows' not in st.session_state:
    st.session_state.windows = []

def get_profile_code(color_choice, profile_type):
    """Get the correct profile code based on color and profile type"""
    color_map = {
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
    return color_map[color_choice][profile_type]

def generate_fixed_lite_profiles(window, color, colorcode, today, start_id):
    """Generate profiles for Fixed Lite window"""
    rows = []
    width_mm = window['width_mm']
    height_mm = window['height_mm']
    width_inches = window['width']
    pos = window['number']
    
    # Check if narrow window
    if width_inches < 14.5:
        code = get_profile_code(color, 'fixed')
        description = PROFILE_DESCRIPTIONS[code]
        orientation = 'TOP/BOTTOM'
        ktnbar = int(round((width_mm + (2 * 25.4)) * 10))
    else:
        code = get_profile_code(color, 'fixed')
        description = PROFILE_DESCRIPTIONS[code]
        orientation = 'UPRIGHT'
        ktnbar = int(round((height_mm + 25.4) * 10))
    
    for i in range(2):
        row = [
            start_id + i, 1, 1, 1, ktnbar, 90, 90, code, description,
            int(round(width_mm * 10)), int(round(height_mm * 10)),
            0, 0, orientation, 0, 0, pos, 0, 0,
            st.session_state.dealer, today, 'Z MF_UPRIGHT_FIXED',
            0, colorcode, color, code, st.session_state.tag,
            '', '', '', '', '', ''
        ]
        rows.append(row)
    
    return rows

def generate_sliding_xo_profiles(window, color, colorcode, today, start_id):
    """Generate profiles for Sliding XO window"""
    rows = []
    width_mm = window['width_mm']
    height_mm = window['height_mm']
    pos = window['number']
    
    fixed_code = get_profile_code(color, 'fixed')
    moving_code = get_profile_code(color, 'moving')
    sash_tb_code = get_profile_code(color, 'sash_top_bottom')
    sash_moving_code = get_profile_code(color, 'sash_moving')
    sash_pull_code = get_profile_code(color, 'sash_pull')
    
    profiles = [
        (fixed_code, PROFILE_DESCRIPTIONS[fixed_code], 'UPRIGHT', 
         int(round((height_mm + 25.4) * 10)), 'Z MF_UPRIGHT FIXED SLIDING'),
        (moving_code, PROFILE_DESCRIPTIONS[moving_code], 'UPRIGHT',
         int(round((height_mm + 25.4) * 10)), 'Z MF_UPRIGHT MOVING SLIDING'),
        (sash_tb_code, PROFILE_DESCRIPTIONS[sash_tb_code], 'BOTTOM',
         int(round(((width_mm / 2) + (0.625 * 25.4)) * 10)), 'Z SASH TOP'),
        (sash_tb_code, PROFILE_DESCRIPTIONS[sash_tb_code], 'TOP',
         int(round(((width_mm / 2) + (0.625 * 25.4)) * 10)), 'Z SASH BOTTOM'),
        (sash_moving_code, PROFILE_DESCRIPTIONS[sash_moving_code], 'LEFT',
         int(round((height_mm - (4.9375 * 25.4)) * 10)), 'Z AL SASH UPRIGHT MOVING XO'),
        (sash_pull_code, PROFILE_DESCRIPTIONS[sash_pull_code], 'RIGHT',
         int(round((height_mm - (4.9375 * 25.4)) * 10)), 'Z SASH PULL UPRIGHT')
    ]
    
    for i, (code, desc, orient, ktnbar, nccode) in enumerate(profiles):
        row = [
            start_id + i, 1, 1, 1, ktnbar, 90, 90, code, desc,
            int(round(width_mm * 10)), int(round(height_mm * 10)),
            0, 0, orient, 0, 0, pos, 0, 0,
            st.session_state.dealer, today, nccode,
            0, colorcode, color, code, st.session_state.tag,
            '', '', '', '', '', ''
        ]
        rows.append(row)
    
    return rows

def generate_sliding_ox_profiles(window, color, colorcode, today, start_id):
    """Generate profiles for Sliding OX window"""
    rows = []
    width_mm = window['width_mm']
    height_mm = window['height_mm']
    pos = window['number']
    
    fixed_code = get_profile_code(color, 'fixed')
    moving_code = get_profile_code(color, 'moving')
    sash_tb_code = get_profile_code(color, 'sash_top_bottom')
    sash_moving_code = get_profile_code(color, 'sash_moving')
    sash_pull_code = get_profile_code(color, 'sash_pull')
    
    profiles = [
        (fixed_code, PROFILE_DESCRIPTIONS[fixed_code], 'UPRIGHT',
         int(round((height_mm + 25.4) * 10)), 'Z MF_UPRIGHT FIXED SLIDING OX'),
        (moving_code, PROFILE_DESCRIPTIONS[moving_code], 'UPRIGHT',
         int(round((height_mm + 25.4) * 10)), 'Z MF_UPRIGHT MOVING SLIDING OX'),
        (sash_tb_code, PROFILE_DESCRIPTIONS[sash_tb_code], 'Top',
         int(round(((width_mm / 2) + (0.625 * 25.4)) * 10)), 'Z SASH TOP'),
        (sash_tb_code, PROFILE_DESCRIPTIONS[sash_tb_code], 'BOTTOM',
         int(round(((width_mm / 2) + (0.625 * 25.4)) * 10)), 'Z SASH BOTTOM'),
        (sash_moving_code, PROFILE_DESCRIPTIONS[sash_moving_code], 'LEFT',
         int(round((height_mm - (4.9375 * 25.4)) * 10)), 'Z AL SASH UPRIGHT MOVING OX'),
        (sash_pull_code, PROFILE_DESCRIPTIONS[sash_pull_code], 'RIGHT',
         int(round((height_mm - (4.9375 * 25.4)) * 10)), 'Z SASH PULL UPRIGHT')
    ]
    
    for i, (code, desc, orient, ktnbar, nccode) in enumerate(profiles):
        row = [
            start_id + i, 1, 1, 1, ktnbar, 90, 90, code, desc,
            int(round(width_mm * 10)), int(round(height_mm * 10)),
            0, 0, orient, 0, 0, pos, 0, 0,
            st.session_state.dealer, today, nccode,
            0, colorcode, color, code, st.session_state.tag,
            '', '', '', '', '', ''
        ]
        rows.append(row)
    
    return rows

def generate_csv():
    """Generate CSV data from windows"""
    if not st.session_state.windows:
        return None
    
    color = st.session_state.color
    colorcode = COLOR_CODES[color]['colorcode']
    today = date.today().strftime('%Y-%m-%d')
    
    rows = []
    row_id = 1
    
    for window in st.session_state.windows:
        if window['type'] == 'Fixed Lite':
            window_rows = generate_fixed_lite_profiles(window, color, colorcode, today, row_id)
        elif window['type'] == 'Sliding Window XO':
            window_rows = generate_sliding_xo_profiles(window, color, colorcode, today, row_id)
        elif window['type'] == 'Sliding Window OX':
            window_rows = generate_sliding_ox_profiles(window, color, colorcode, today, row_id)
        else:
            continue
        
        rows.extend(window_rows)
        row_id += len(window_rows)
    
    # Create CSV
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(CSV_HEADER)
    writer.writerows(rows)
    
    return output.getvalue()

# Main App
st.title("🪟 AL Window Profile CSV Generator")
st.markdown("**Professional window profile generation tool**")

# Sidebar for project info
with st.sidebar:
    st.header("📋 Project Information")
    st.session_state.dealer = st.text_input("Dealer Name", value=st.session_state.get('dealer', ''))
    st.session_state.tag = st.text_input("Tag / Project ID", value=st.session_state.get('tag', ''))
    st.session_state.color = st.selectbox("Color", list(COLOR_CODES.keys()))
    
    st.divider()
    st.markdown(f"**Total Windows:** {len(st.session_state.windows)}")
    
    if st.session_state.windows:
        profile_count = sum([
            2 if w['type'] == 'Fixed Lite' else 6 
            for w in st.session_state.windows
        ])
        st.markdown(f"**Total Profiles:** {profile_count}")

# Main content area
col1, col2 = st.columns([2, 3])

with col1:
    st.subheader("➕ Add Windows")
    
    with st.form("add_window_form", clear_on_submit=True):
        width = st.number_input("Width (inches)", min_value=0.0, step=0.0625, format="%.4f")
        height = st.number_input("Height (inches)", min_value=0.0, step=0.0625, format="%.4f")
        
        col_a, col_b = st.columns(2)
        with col_a:
            quantity = st.number_input("Quantity", min_value=1, max_value=100, value=1)
        with col_b:
            window_type = st.selectbox("Type", ["Fixed Lite", "Sliding Window XO", "Sliding Window OX"])
        
        submitted = st.form_submit_button("Add Window(s)", type="primary", use_container_width=True)
        
        if submitted:
            if width <= 0 or height <= 0:
                st.error("Width and height must be greater than 0!")
            else:
                # Add windows
                narrow_windows = []
                for i in range(quantity):
                    window_num = len(st.session_state.windows) + 1
                    window_data = {
                        'number': window_num,
                        'width': width,
                        'height': height,
                        'width_mm': round(width * 25.4, 2),
                        'height_mm': round(height * 25.4, 2),
                        'type': window_type
                    }
                    st.session_state.windows.append(window_data)
                    
                    if window_type == 'Fixed Lite' and width < 14.5:
                        narrow_windows.append(window_num)
                
                st.success(f"✅ Added {quantity} window(s)!")
                
                if narrow_windows:
                    st.warning(f"⚠️ Window(s) {', '.join(map(str, narrow_windows))} are < 14.5\" wide.\n\n"
                             f"These will use TOP/BOTTOM orientation with width + 2\" calculation.")
                
                st.rerun()
    
    # Quick actions
    st.divider()
    col_clear, col_last = st.columns(2)
    
    with col_clear:
        if st.button("🗑️ Clear All", use_container_width=True):
            st.session_state.windows = []
            st.rerun()
    
    with col_last:
        if st.button("📋 Duplicate Last", use_container_width=True, disabled=len(st.session_state.windows) == 0):
            if st.session_state.windows:
                last = st.session_state.windows[-1].copy()
                last['number'] = len(st.session_state.windows) + 1
                st.session_state.windows.append(last)
                st.rerun()

with col2:
    st.subheader("📊 Windows List")
    
    if st.session_state.windows:
        # Create DataFrame for display
        df = pd.DataFrame(st.session_state.windows)
        df = df[['number', 'width', 'height', 'width_mm', 'height_mm', 'type']]
        df.columns = ['#', 'Width (in)', 'Height (in)', 'Width (mm)', 'Height (mm)', 'Type']
        
        # Display table
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            height=400
        )
        
        # Delete specific window
        st.divider()
        delete_num = st.number_input("Delete window #", min_value=1, max_value=len(st.session_state.windows), step=1)
        if st.button("🗑️ Delete Selected Window", use_container_width=True):
            st.session_state.windows = [w for w in st.session_state.windows if w['number'] != delete_num]
            # Renumber
            for i, window in enumerate(st.session_state.windows, 1):
                window['number'] = i
            st.rerun()
    else:
        st.info("👆 Add windows using the form on the left")

# Generate CSV section
st.divider()
st.subheader("📥 Generate CSV File")

col_gen1, col_gen2, col_gen3 = st.columns([2, 1, 1])

with col_gen1:
    if st.button("📊 Generate CSV", type="primary", use_container_width=True, disabled=len(st.session_state.windows) == 0):
        if not st.session_state.dealer or not st.session_state.tag:
            st.error("⚠️ Please fill in Dealer and Tag in the sidebar!")
        else:
            csv_data = generate_csv()
            if csv_data:
                # Show success and download button
                st.success("✅ CSV Generated Successfully!")
                
                # Count profiles
                profile_count = sum([2 if w['type'] == 'Fixed Lite' else 6 for w in st.session_state.windows])
                
                st.info(f"📊 **{len(st.session_state.windows)} windows** → **{profile_count} profiles**")
                
                # Download button
                filename = f"{st.session_state.tag}_windows.csv"
                st.download_button(
                    label="⬇️ Download CSV File",
                    data=csv_data,
                    file_name=filename,
                    mime="text/csv",
                    use_container_width=True
                )

with col_gen2:
    st.metric("Windows", len(st.session_state.windows))

with col_gen3:
    if st.session_state.windows:
        profile_count = sum([2 if w['type'] == 'Fixed Lite' else 6 for w in st.session_state.windows])
        st.metric("Profiles", profile_count)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <small>AL Window Profile CSV Generator v2.3 • Streamlit Web App</small>
</div>
""", unsafe_allow_html=True)
