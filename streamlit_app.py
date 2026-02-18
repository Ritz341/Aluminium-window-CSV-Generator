#!/usr/bin/env python3
"""
AL Window Profile CSV Generator v2.5
Single-window GUI (1920×1080) — no sidebar, everything visible at once.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
from datetime import date
from typing import List
import os


class WindowProfileGenerator:
    """Main application class for window profile CSV generation"""

    CSV_HEADER = [
        'id', 'ksn', 'ksnbar', 'ktn', 'ktnbar', 'l', 'r', 'code', 'info',
        'width', 'height', 'trolley', 'box', 'orientation', 'reinf', 'reinfbar',
        'pos', 'prono', 'offno', 'customer', 'date', 'nccode', 'isfix', 'colorcode',
        'colorinfo', 'mainprofile', 'subcust', 'image', 'DATA1', 'DATA2', 'DATA3',
        'DATA4', 'DATA5'
    ]

    COLOR_CODES = {
        '1 White':     {'code': 883009, 'colorcode': '1'},
        '2 Driftwood': {'code': 883011, 'colorcode': '2'},
        '4 Black':     {'code': 883008, 'colorcode': '4'}
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

    # ── colour → profile code map ──────────────────────────────────
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

    def get_profile_code(self, profile_type: str) -> int:
        return self.COLOR_PROFILE_MAP[self.color.get()][profile_type]

    # ================================================================
    #  INIT
    # ================================================================
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("AL Window Profile CSV Generator  v2.5")
        self.root.geometry("1920x1080")
        self.root.minsize(1280, 720)

        # ── palette ─────────────────────────────────────────────────
        self.C = {
            'bg':       '#F0F2F5',
            'card':     '#FFFFFF',
            'primary':  '#2563EB',
            'primary_hover': '#1D4ED8',
            'success':  '#16A34A',
            'danger':   '#DC2626',
            'text':     '#1E293B',
            'text2':    '#64748B',
            'border':   '#CBD5E1',
            'accent':   '#3B82F6',
            'row_alt':  '#F8FAFC',
            'header_bg':'#1E293B',
        }

        self.root.configure(bg=self.C['bg'])

        # ── data ────────────────────────────────────────────────────
        self.windows: list = []
        self.dealer      = tk.StringVar()
        self.tag         = tk.StringVar()
        self.color       = tk.StringVar(value='4 Black')
        self.window_type = tk.StringVar(value='Fixed Lite')
        self.status_var  = tk.StringVar(value='Ready')

        self._setup_styles()
        self._build_ui()

    # ================================================================
    #  STYLES
    # ================================================================
    def _setup_styles(self):
        s = ttk.Style()
        s.theme_use('clam')

        s.configure('.', background=self.C['bg'], font=('Segoe UI', 10))

        # frames
        s.configure('Card.TFrame',   background=self.C['card'])
        s.configure('Header.TFrame', background=self.C['header_bg'])

        # labels
        s.configure('Title.TLabel',   background=self.C['header_bg'], foreground='#FFFFFF',
                    font=('Segoe UI', 16, 'bold'))
        s.configure('Subtitle.TLabel', background=self.C['header_bg'], foreground='#94A3B8',
                    font=('Segoe UI', 10))
        s.configure('Section.TLabel', background=self.C['card'], foreground=self.C['text'],
                    font=('Segoe UI', 12, 'bold'))
        s.configure('Field.TLabel',   background=self.C['card'], foreground=self.C['text'],
                    font=('Segoe UI', 10))
        s.configure('Info.TLabel',    background=self.C['card'], foreground=self.C['text2'],
                    font=('Segoe UI', 9))
        s.configure('Stat.TLabel',    background=self.C['card'], foreground=self.C['primary'],
                    font=('Segoe UI', 20, 'bold'))
        s.configure('StatLabel.TLabel', background=self.C['card'], foreground=self.C['text2'],
                    font=('Segoe UI', 9))
        s.configure('Status.TLabel',  background=self.C['bg'], foreground=self.C['text2'],
                    font=('Segoe UI', 9))

        # buttons
        s.configure('Primary.TButton',   font=('Segoe UI', 10, 'bold'), padding=(16, 8))
        s.configure('Secondary.TButton', font=('Segoe UI', 10),         padding=(12, 6))
        s.configure('Generate.TButton',  font=('Segoe UI', 11, 'bold'), padding=(24, 10))
        s.configure('Danger.TButton',    font=('Segoe UI', 10),         padding=(12, 6))

        # entry / combo
        s.configure('Modern.TEntry', padding=6)
        s.configure('Modern.TCombobox', padding=6)

        # treeview
        s.configure('Treeview', rowheight=28, font=('Segoe UI', 10),
                    background=self.C['card'], fieldbackground=self.C['card'],
                    foreground=self.C['text'])
        s.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'),
                    background=self.C['header_bg'], foreground='#FFFFFF', padding=6)
        s.map('Treeview', background=[('selected', self.C['accent'])],
              foreground=[('selected', '#FFFFFF')])

    # ================================================================
    #  BUILD UI
    # ================================================================
    def _build_ui(self):
        # weight the root
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)   # main area grows

        # ── 1  HEADER BAR ──────────────────────────────────────────
        hdr = ttk.Frame(self.root, style='Header.TFrame', padding=(20, 12))
        hdr.grid(row=0, column=0, sticky='ew')
        hdr.columnconfigure(1, weight=1)

        ttk.Label(hdr, text='Window Profile Generator', style='Title.TLabel')\
            .grid(row=0, column=0, sticky='w')
        ttk.Label(hdr, text='AL Profile CSV Tool  •  v2.5', style='Subtitle.TLabel')\
            .grid(row=0, column=1, sticky='w', padx=(12, 0))

        # ── 2  MAIN BODY (3-column) ───────────────────────────────
        body = ttk.Frame(self.root, style='TFrame')
        body.grid(row=1, column=0, sticky='nsew', padx=16, pady=(12, 0))
        body.columnconfigure(0, weight=0, minsize=340)   # left  – inputs
        body.columnconfigure(1, weight=1)                 # mid   – window list
        body.columnconfigure(2, weight=0, minsize=240)    # right – stats
        body.rowconfigure(0, weight=1)

        self._build_left_panel(body)
        self._build_center_panel(body)
        self._build_right_panel(body)

        # ── 3  FOOTER / STATUS ────────────────────────────────────
        foot = ttk.Frame(self.root, padding=(20, 6))
        foot.grid(row=2, column=0, sticky='ew')
        ttk.Label(foot, textvariable=self.status_var, style='Status.TLabel')\
            .pack(side='left')

    # ── LEFT PANEL ──────────────────────────────────────────────────
    def _build_left_panel(self, parent):
        left = ttk.Frame(parent, style='Card.TFrame', padding=16)
        left.grid(row=0, column=0, sticky='nsew', padx=(0, 8))
        left.columnconfigure(1, weight=1)

        r = 0
        # -- section: project info
        ttk.Label(left, text='Project Info', style='Section.TLabel')\
            .grid(row=r, column=0, columnspan=2, sticky='w', pady=(0, 10)); r += 1

        for label_text, var in [('Dealer', self.dealer), ('Tag', self.tag)]:
            ttk.Label(left, text=label_text, style='Field.TLabel')\
                .grid(row=r, column=0, sticky='w', pady=4)
            ttk.Entry(left, textvariable=var, style='Modern.TEntry')\
                .grid(row=r, column=1, sticky='ew', padx=(8, 0), pady=4)
            r += 1

        ttk.Label(left, text='Color', style='Field.TLabel')\
            .grid(row=r, column=0, sticky='w', pady=4)
        ttk.Combobox(left, textvariable=self.color,
                     values=list(self.COLOR_CODES.keys()),
                     state='readonly', style='Modern.TCombobox')\
            .grid(row=r, column=1, sticky='ew', padx=(8, 0), pady=4); r += 1

        # separator
        sep = ttk.Separator(left, orient='horizontal')
        sep.grid(row=r, column=0, columnspan=2, sticky='ew', pady=14); r += 1

        # -- section: add windows
        ttk.Label(left, text='Add Windows', style='Section.TLabel')\
            .grid(row=r, column=0, columnspan=2, sticky='w', pady=(0, 10)); r += 1

        ttk.Label(left, text='Type', style='Field.TLabel')\
            .grid(row=r, column=0, sticky='w', pady=4)
        ttk.Combobox(left, textvariable=self.window_type,
                     values=['Fixed Lite', 'Sliding Window XO', 'Sliding Window OX'],
                     state='readonly', style='Modern.TCombobox')\
            .grid(row=r, column=1, sticky='ew', padx=(8, 0), pady=4); r += 1

        # width / height side-by-side
        dim_frame = ttk.Frame(left, style='Card.TFrame')
        dim_frame.grid(row=r, column=0, columnspan=2, sticky='ew', pady=4); r += 1
        dim_frame.columnconfigure(1, weight=1)
        dim_frame.columnconfigure(3, weight=1)

        ttk.Label(dim_frame, text='W (in)', style='Field.TLabel')\
            .grid(row=0, column=0, sticky='w')
        self.width_entry = ttk.Entry(dim_frame, width=10, style='Modern.TEntry')
        self.width_entry.grid(row=0, column=1, sticky='ew', padx=(4, 12))

        ttk.Label(dim_frame, text='H (in)', style='Field.TLabel')\
            .grid(row=0, column=2, sticky='w')
        self.height_entry = ttk.Entry(dim_frame, width=10, style='Modern.TEntry')
        self.height_entry.grid(row=0, column=3, sticky='ew', padx=(4, 0))

        # quantity
        qty_frame = ttk.Frame(left, style='Card.TFrame')
        qty_frame.grid(row=r, column=0, columnspan=2, sticky='ew', pady=4); r += 1
        qty_frame.columnconfigure(1, weight=1)

        ttk.Label(qty_frame, text='Qty', style='Field.TLabel')\
            .grid(row=0, column=0, sticky='w')
        self.quantity_entry = ttk.Entry(qty_frame, width=6, style='Modern.TEntry')
        self.quantity_entry.insert(0, '1')
        self.quantity_entry.grid(row=0, column=1, sticky='w', padx=(8, 0))

        # buttons
        btn1 = ttk.Frame(left, style='Card.TFrame')
        btn1.grid(row=r, column=0, columnspan=2, sticky='ew', pady=(12, 4)); r += 1

        ttk.Button(btn1, text='Add Window(s)', command=self.add_window,
                   style='Primary.TButton').pack(fill='x')

        btn2 = ttk.Frame(left, style='Card.TFrame')
        btn2.grid(row=r, column=0, columnspan=2, sticky='ew', pady=2); r += 1
        ttk.Button(btn2, text='Duplicate Last', command=self.duplicate_last,
                   style='Secondary.TButton').pack(side='left', fill='x', expand=True, padx=(0, 4))
        ttk.Button(btn2, text='Clear Fields', command=self.clear_fields,
                   style='Secondary.TButton').pack(side='left', fill='x', expand=True)

        btn3 = ttk.Frame(left, style='Card.TFrame')
        btn3.grid(row=r, column=0, columnspan=2, sticky='ew', pady=2); r += 1
        ttk.Button(btn3, text='Delete Selected', command=self.delete_selected,
                   style='Danger.TButton').pack(side='left', fill='x', expand=True, padx=(0, 4))
        ttk.Button(btn3, text='Clear All', command=self.clear_windows,
                   style='Danger.TButton').pack(side='left', fill='x', expand=True)

        # spacer pushes generate to bottom
        left.rowconfigure(r, weight=1); r += 1

        # generate button at bottom of left panel
        ttk.Button(left, text='Generate CSV', command=self.generate_csv,
                   style='Generate.TButton')\
            .grid(row=r, column=0, columnspan=2, sticky='ew', pady=(10, 0))

        # bind Enter on entries
        self.width_entry.bind('<Return>', lambda e: self.height_entry.focus())
        self.height_entry.bind('<Return>', lambda e: self.quantity_entry.focus())
        self.quantity_entry.bind('<Return>', lambda e: self.add_window())

    # ── CENTER PANEL ────────────────────────────────────────────────
    def _build_center_panel(self, parent):
        center = ttk.Frame(parent, style='Card.TFrame', padding=16)
        center.grid(row=0, column=1, sticky='nsew', padx=8)
        center.columnconfigure(0, weight=1)
        center.rowconfigure(1, weight=1)

        ttk.Label(center, text='Window List', style='Section.TLabel')\
            .grid(row=0, column=0, sticky='w', pady=(0, 8))

        # treeview
        tree_wrap = ttk.Frame(center, style='Card.TFrame')
        tree_wrap.grid(row=1, column=0, sticky='nsew')
        tree_wrap.columnconfigure(0, weight=1)
        tree_wrap.rowconfigure(0, weight=1)

        cols = ('number', 'type', 'width_in', 'height_in', 'width_mm', 'height_mm', 'profiles')
        self.tree = ttk.Treeview(tree_wrap, columns=cols, show='headings', selectmode='extended')

        headings = {'number': '#', 'type': 'Type', 'width_in': 'Width (in)',
                    'height_in': 'Height (in)', 'width_mm': 'Width (mm)',
                    'height_mm': 'Height (mm)', 'profiles': 'Profiles'}
        widths   = {'number': 50, 'type': 160, 'width_in': 100, 'height_in': 100,
                    'width_mm': 110, 'height_mm': 110, 'profiles': 70}

        for c in cols:
            self.tree.heading(c, text=headings[c])
            anchor = tk.W if c == 'type' else tk.CENTER
            self.tree.column(c, width=widths[c], anchor=anchor, minwidth=widths[c])

        vsb = ttk.Scrollbar(tree_wrap, orient='vertical', command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_wrap, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        # info line below tree
        self.tree_info = ttk.Label(center, text='No windows added yet', style='Info.TLabel')
        self.tree_info.grid(row=2, column=0, sticky='w', pady=(6, 0))

    # ── RIGHT PANEL ─────────────────────────────────────────────────
    def _build_right_panel(self, parent):
        right = ttk.Frame(parent, style='Card.TFrame', padding=16)
        right.grid(row=0, column=2, sticky='nsew', padx=(8, 0))
        right.columnconfigure(0, weight=1)

        ttk.Label(right, text='Summary', style='Section.TLabel')\
            .grid(row=0, column=0, sticky='w', pady=(0, 16))

        # stat cards
        self._stat_windows = self._make_stat(right, 1, '0', 'Windows')
        self._stat_profiles = self._make_stat(right, 2, '0', 'Profiles')
        self._stat_type_fixed = self._make_stat(right, 3, '0', 'Fixed Lite')
        self._stat_type_xo = self._make_stat(right, 4, '0', 'Sliding XO')
        self._stat_type_ox = self._make_stat(right, 5, '0', 'Sliding OX')

        ttk.Separator(right, orient='horizontal')\
            .grid(row=6, column=0, sticky='ew', pady=16)

        # preview section header
        ttk.Label(right, text='Current Settings', style='Section.TLabel')\
            .grid(row=7, column=0, sticky='w', pady=(0, 8))

        self._setting_labels = {}
        for i, key in enumerate(['Dealer', 'Tag', 'Color']):
            lbl = ttk.Label(right, text=f'{key}: —', style='Info.TLabel')
            lbl.grid(row=8 + i, column=0, sticky='w', pady=2)
            self._setting_labels[key] = lbl

        # live update traces
        self.dealer.trace_add('write', lambda *_: self._update_settings_display())
        self.tag.trace_add('write', lambda *_: self._update_settings_display())
        self.color.trace_add('write', lambda *_: self._update_settings_display())

    def _make_stat(self, parent, row, value, label):
        """Create a stat number + label pair, return the value label for updates."""
        f = ttk.Frame(parent, style='Card.TFrame')
        f.grid(row=row, column=0, sticky='ew', pady=4)
        val_lbl = ttk.Label(f, text=value, style='Stat.TLabel')
        val_lbl.pack(anchor='w')
        ttk.Label(f, text=label, style='StatLabel.TLabel').pack(anchor='w')
        return val_lbl

    # ================================================================
    #  HELPERS
    # ================================================================
    def _update_stats(self):
        n = len(self.windows)
        profiles = sum(2 if w['type'] == 'Fixed Lite' else 6 for w in self.windows)
        fixed = sum(1 for w in self.windows if w['type'] == 'Fixed Lite')
        xo    = sum(1 for w in self.windows if w['type'] == 'Sliding Window XO')
        ox    = sum(1 for w in self.windows if w['type'] == 'Sliding Window OX')

        self._stat_windows.config(text=str(n))
        self._stat_profiles.config(text=str(profiles))
        self._stat_type_fixed.config(text=str(fixed))
        self._stat_type_xo.config(text=str(xo))
        self._stat_type_ox.config(text=str(ox))

        if n == 0:
            self.tree_info.config(text='No windows added yet')
        else:
            self.tree_info.config(text=f'{n} window(s)  •  {profiles} profile row(s)')

    def _update_settings_display(self):
        self._setting_labels['Dealer'].config(text=f'Dealer: {self.dealer.get() or "—"}')
        self._setting_labels['Tag'].config(text=f'Tag: {self.tag.get() or "—"}')
        self._setting_labels['Color'].config(text=f'Color: {self.color.get()}')

    def _refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        for w in self.windows:
            prof = 2 if w['type'] == 'Fixed Lite' else 6
            self.tree.insert('', 'end', values=(
                w['number'], w['type'], w['width'], w['height'],
                w['width_mm'], w['height_mm'], prof
            ))
        self._update_stats()

    # ================================================================
    #  ACTIONS
    # ================================================================
    def add_window(self):
        try:
            width = float(self.width_entry.get())
            height = float(self.height_entry.get())
            if width <= 0 or height <= 0:
                messagebox.showerror('Error', 'Width and height must be positive numbers')
                return
        except ValueError:
            messagebox.showerror('Error', 'Please enter valid numbers for width and height')
            return

        try:
            quantity = int(self.quantity_entry.get())
            if quantity <= 0:
                messagebox.showerror('Error', 'Quantity must be positive')
                return
            if quantity > 100:
                if not messagebox.askyesno('Confirm', f'Add {quantity} windows? That seems high.'):
                    return
        except ValueError:
            messagebox.showerror('Error', 'Quantity must be a valid integer')
            return

        width_mm  = round(width * 25.4, 2)
        height_mm = round(height * 25.4, 2)
        wtype     = self.window_type.get()
        narrow    = []

        for _ in range(quantity):
            num = len(self.windows) + 1
            self.windows.append({
                'number': num, 'width': width, 'height': height,
                'width_mm': width_mm, 'height_mm': height_mm, 'type': wtype
            })
            if wtype == 'Fixed Lite' and width < 14.5:
                narrow.append(num)

        if narrow:
            messagebox.showinfo(
                'Narrow Fixed Lite',
                f"Window(s) {', '.join(map(str, narrow))} are < 14.5\" wide.\n\n"
                "• Orientation → TOP/BOTTOM\n"
                "• Calculation → width + 2\"\n"
                "This is expected for narrow windows."
            )

        self._refresh_tree()
        self.quantity_entry.select_range(0, tk.END)
        self.quantity_entry.focus()
        self.status_var.set(f'Added {quantity} {wtype} window(s)  —  total: {len(self.windows)}')

    def duplicate_last(self):
        if not self.windows:
            messagebox.showwarning('Warning', 'No windows to duplicate')
            return
        last = self.windows[-1]
        num = len(self.windows) + 1
        self.windows.append({**last, 'number': num})
        self._refresh_tree()
        self.status_var.set(f'Duplicated window  —  total: {len(self.windows)}')

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning('Warning', 'Select window(s) to delete')
            return
        nums_to_del = set()
        for item_id in sel:
            nums_to_del.add(self.tree.item(item_id)['values'][0])
        self.windows = [w for w in self.windows if w['number'] not in nums_to_del]
        for i, w in enumerate(self.windows, 1):
            w['number'] = i
        self._refresh_tree()
        self.status_var.set(f'Deleted {len(nums_to_del)} window(s)  —  {len(self.windows)} remaining')

    def clear_windows(self):
        if self.windows and messagebox.askyesno('Confirm', 'Clear ALL windows?'):
            self.windows.clear()
            self._refresh_tree()
            self.status_var.set('All windows cleared')

    def clear_fields(self):
        self.width_entry.delete(0, tk.END)
        self.height_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)
        self.quantity_entry.insert(0, '1')
        self.width_entry.focus()
        self.status_var.set('Fields cleared')

    # ================================================================
    #  CSV GENERATION  (logic unchanged from v2.4)
    # ================================================================
    def generate_csv(self):
        if not self.windows:
            messagebox.showerror('Error', 'Add at least one window first')
            return
        if not self.dealer.get() or not self.tag.get():
            messagebox.showerror('Error', 'Please fill in Dealer and Tag')
            return

        filename = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=[('CSV files', '*.csv'), ('All files', '*.*')],
            initialfile=f"{self.tag.get()}_windows.csv"
        )
        if not filename:
            return

        try:
            rows = self._generate_all_rows()
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(self.CSV_HEADER)
                writer.writerows(rows)

            profile_count = len(rows)
            messagebox.showinfo(
                'Success',
                f"CSV generated!\n\n"
                f"File: {os.path.basename(filename)}\n"
                f"Windows: {len(self.windows)}\n"
                f"Profiles: {profile_count}"
            )
            self.status_var.set(f'Saved: {os.path.basename(filename)}  ({profile_count} rows)')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to generate CSV:\n{e}')

    def _generate_all_rows(self) -> List[list]:
        colorcode = self.COLOR_CODES[self.color.get()]['colorcode']
        today     = date.today().strftime('%Y-%m-%d')

        rows   = []
        row_id = 1
        for w in self.windows:
            wtype = w['type']
            if wtype == 'Fixed Lite':
                new_rows = self._gen_fixed_lite(w, colorcode, today, row_id)
            elif wtype == 'Sliding Window XO':
                new_rows = self._gen_sliding_xo(w, colorcode, today, row_id)
            elif wtype == 'Sliding Window OX':
                new_rows = self._gen_sliding_ox(w, colorcode, today, row_id)
            else:
                continue
            rows.extend(new_rows)
            row_id += len(new_rows)
        return rows

    # ── Fixed Lite ──────────────────────────────────────────────────
    def _gen_fixed_lite(self, w, colorcode, today, start_id) -> List[list]:
        rows = []
        width_mm, height_mm = w['width_mm'], w['height_mm']
        pos  = w['number']
        code = self.get_profile_code('fixed')
        desc = self.PROFILE_DESCRIPTIONS[code]

        if w['width'] < 14.5:
            orient = 'TOP/BOTTOM'
            ktnbar = int(round((width_mm + 2 * 25.4) * 10))
        else:
            orient = 'UPRIGHT'
            ktnbar = int(round((height_mm + 25.4) * 10))

        for i in range(2):
            rows.append([
                start_id + i, 1, 1, 1, ktnbar, 90, 90,
                code, desc,
                int(round(width_mm * 10)), int(round(height_mm * 10)),
                0, 0, orient, 0, 0, pos, 0, 0,
                self.dealer.get(), today, 'Z MF_UPRIGHT_FIXED',
                0, colorcode, self.color.get(), code, self.tag.get(),
                '', '', '', '', '', ''
            ])
        return rows

    # ── Sliding XO ──────────────────────────────────────────────────
    def _gen_sliding_xo(self, w, colorcode, today, start_id) -> List[list]:
        rows = []
        wm, hm = w['width_mm'], w['height_mm']
        pos    = w['number']
        color  = self.color.get()
        dealer = self.dealer.get()
        tag    = self.tag.get()

        fc  = self.get_profile_code('fixed')
        mc  = self.get_profile_code('moving')
        stc = self.get_profile_code('sash_top_bottom')
        smc = self.get_profile_code('sash_moving')
        spc = self.get_profile_code('sash_pull')

        upright_k = int(round((hm + 25.4) * 10))
        sash_tb_k = int(round(((wm / 2) + 0.625 * 25.4) * 10))
        sash_up_k = int(round((hm - 4.8125 * 25.4) * 10))

        wd = int(round(wm * 10))
        ht = int(round(hm * 10))

        profiles = [
            (fc,  self.PROFILE_DESCRIPTIONS[fc],  'UPRIGHT', upright_k, 'Z MF_UPRIGHT FIXED SLIDING'),
            (mc,  self.PROFILE_DESCRIPTIONS[mc],  'UPRIGHT', upright_k, 'Z MF_UPRIGHT MOVING SLIDING'),
            (stc, self.PROFILE_DESCRIPTIONS[stc], 'BOTTOM',  sash_tb_k, 'Z SASH TOP'),
            (stc, self.PROFILE_DESCRIPTIONS[stc], 'TOP',     sash_tb_k, 'Z SASH BOTTOM'),
            (smc, self.PROFILE_DESCRIPTIONS[smc], 'LEFT',    sash_up_k, 'Z AL SASH UPRIGHT MOVING XO'),
            (spc, self.PROFILE_DESCRIPTIONS[spc], 'RIGHT',   sash_up_k, 'Z SASH PULL UPRIGHT'),
        ]

        for i, (code, desc, orient, ktnbar, nccode) in enumerate(profiles):
            rows.append([
                start_id + i, 1, 1, 1, ktnbar, 90, 90,
                code, desc, wd, ht, 0, 0, orient, 0, 0, pos, 0, 0,
                dealer, today, nccode,
                0, colorcode, color, code, tag,
                '', '', '', '', '', ''
            ])
        return rows

    # ── Sliding OX ──────────────────────────────────────────────────
    def _gen_sliding_ox(self, w, colorcode, today, start_id) -> List[list]:
        rows = []
        wm, hm = w['width_mm'], w['height_mm']
        pos    = w['number']
        color  = self.color.get()
        dealer = self.dealer.get()
        tag    = self.tag.get()

        fc  = self.get_profile_code('fixed')
        mc  = self.get_profile_code('moving')
        stc = self.get_profile_code('sash_top_bottom')
        smc = self.get_profile_code('sash_moving')
        spc = self.get_profile_code('sash_pull')

        upright_k = int(round((hm + 25.4) * 10))
        sash_tb_k = int(round(((wm / 2) + 0.625 * 25.4) * 10))
        sash_up_k = int(round((hm - 4.8125 * 25.4) * 10))

        wd = int(round(wm * 10))
        ht = int(round(hm * 10))

        profiles = [
            (fc,  self.PROFILE_DESCRIPTIONS[fc],  'UPRIGHT', upright_k, 'Z MF_UPRIGHT FIXED SLIDING OX'),
            (mc,  self.PROFILE_DESCRIPTIONS[mc],  'UPRIGHT', upright_k, 'Z MF_UPRIGHT MOVING SLIDING OX'),
            (stc, self.PROFILE_DESCRIPTIONS[stc], 'Top',     sash_tb_k, 'Z SASH TOP'),
            (stc, self.PROFILE_DESCRIPTIONS[stc], 'BOTTOM',  sash_tb_k, 'Z SASH BOTTOM'),
            (smc, self.PROFILE_DESCRIPTIONS[smc], 'LEFT',    sash_up_k, 'Z AL SASH UPRIGHT MOVING OX'),
            (spc, self.PROFILE_DESCRIPTIONS[spc], 'RIGHT',   sash_up_k, 'Z SASH PULL UPRIGHT'),
        ]

        for i, (code, desc, orient, ktnbar, nccode) in enumerate(profiles):
            rows.append([
                start_id + i, 1, 1, 1, ktnbar, 90, 90,
                code, desc, wd, ht, 0, 0, orient, 0, 0, pos, 0, 0,
                dealer, today, nccode,
                0, colorcode, color, code, tag,
                '', '', '', '', '', ''
            ])
        return rows


# ════════════════════════════════════════════════════════════════════
def main():
    root = tk.Tk()
    WindowProfileGenerator(root)
    root.mainloop()


if __name__ == '__main__':
    main()
