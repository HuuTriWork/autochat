import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import requests
import json
import threading
import time
import random
from tkinter import Menu
import webbrowser

try:
    from ttkthemes import ThemedStyle
    HAS_THEMES = True
except ImportError:
    HAS_THEMES = False

class SciFiDiscordTokenManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Chat Discord - SubinDev")
        self.root.configure(bg="#0a0a12")
        
        try:
            self.root.iconbitmap('nebula.ico')
        except:
            pass
            
        self.root.state('zoomed')

        self.primary_color = "#00a8ff"  
        self.secondary_color = "#9c27b0"  
        self.bg_color = "#0a0a12"  
        self.panel_bg = "#12121a"  
        self.text_color = "#e0e0e0"
        self.success_color = "#00e676"  
        self.error_color = "#ff3d00"  
        self.warning_color = "#ffab00"  
        self.highlight_color = "#4a148c" 
        
        self.title_font = ("Orbitron", 14, "bold")
        self.header_font = ("Orbitron", 10, "bold")
        self.body_font = ("Roboto", 9)
        self.code_font = ("Consolas", 9)
        
        self.is_chat_running = False
        self.chat_thread = None
        self.content_source = tk.StringVar(value="manual")
        self.send_mode = tk.StringVar(value="first")
        
        self.style = ttk.Style()
        if HAS_THEMES:
            self.style.theme_use('black')
        else:
            self.style.theme_use('clam')
            self.configure_custom_styles()
        
        self.main_container = tk.Frame(root, bg=self.primary_color, bd=0)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.main_frame = ttk.Frame(self.main_container, style='Dark.TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        self.create_header()
        self.create_main_panels()
        self.create_token_table()
        self.create_control_buttons()
        self.create_chat_controls()
        
        self.tokens = []
        self.selected_tokens = []
        
        if hasattr(self, 'message_count_entry'):
            self.message_count_entry.insert(0, "0")
        if hasattr(self, 'min_delay_entry'):
            self.min_delay_entry.insert(0, "1")
        if hasattr(self, 'max_delay_entry'):
            self.max_delay_entry.insert(0, "3")
    
    def configure_custom_styles(self):
        self.style.configure('.', background=self.bg_color, foreground=self.text_color)
        
        self.style.configure('Dark.TFrame', background=self.panel_bg)
        self.style.configure('Panel.TFrame', background=self.panel_bg, borderwidth=2, relief="solid")
        self.style.configure('Border.TFrame', background=self.primary_color)
        
        self.style.configure('Title.TLabel', 
                           font=self.title_font, 
                           background=self.bg_color, 
                           foreground=self.primary_color)
        self.style.configure('Header.TLabel', 
                           font=self.header_font, 
                           background=self.panel_bg, 
                           foreground=self.text_color)
        self.style.configure('Normal.TLabel', 
                           font=self.body_font, 
                           background=self.panel_bg, 
                           foreground=self.text_color)
        
        button_styles = {
            'Primary.TButton': {'bg': self.primary_color, 'fg': 'white'},
            'Secondary.TButton': {'bg': self.secondary_color, 'fg': 'white'},
            'Success.TButton': {'bg': self.success_color, 'fg': 'white'},
            'Danger.TButton': {'bg': self.error_color, 'fg': 'white'},
            'Warning.TButton': {'bg': self.warning_color, 'fg': 'black'}
        }
        
        for style, colors in button_styles.items():
            self.style.configure(style,
                background=colors['bg'],
                foreground=colors['fg'],
                font=self.header_font,
                padding=8,
                relief="flat",
                borderwidth=0,
                focuscolor=colors['bg']
            )
            self.style.map(style,
                background=[('active', self.adjust_color(colors['bg'], 20)), 
                          ('pressed', self.adjust_color(colors['bg'], -20))],
                relief=[('pressed', 'sunken'), ('active', 'raised')]
            )
        
        self.style.configure('TEntry',
            fieldbackground="#1e1e2a",
            foreground=self.text_color,
            insertcolor=self.primary_color,
            bordercolor=self.primary_color,
            lightcolor=self.primary_color,
            darkcolor=self.primary_color,
            padding=5,
            relief="solid"
        )
        
        self.style.configure('TNotebook', background=self.bg_color)
        self.style.configure('TNotebook.Tab',
            background=self.bg_color,
            foreground=self.text_color,
            padding=(15, 5),
            font=self.header_font
        )
        self.style.map('TNotebook.Tab',
            background=[('selected', self.primary_color)],
            foreground=[('selected', 'white')]
        )
        
        self.style.configure('Treeview',
            background="#1e1e2a",
            foreground=self.text_color,
            fieldbackground="#1e1e2a",
            rowheight=25,
            font=self.body_font
        )
        self.style.configure('Treeview.Heading',
            background=self.primary_color,
            foreground='white',
            font=self.header_font,
            relief="flat"
        )
        self.style.map('Treeview',
            background=[('selected', self.highlight_color)],
            foreground=[('selected', 'white')]
        )
        
        self.style.configure('Vertical.TScrollbar',
            background=self.bg_color,
            troughcolor=self.bg_color,
            arrowcolor=self.primary_color,
            bordercolor=self.bg_color,
            relief="flat"
        )
    
    def adjust_color(self, color, amount):
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        rgb = tuple(max(0, min(255, x + amount)) for x in rgb)
        return '#%02x%02x%02x' % rgb
    
    def create_header(self):
        header_frame = ttk.Frame(self.main_frame, style='Dark.TFrame')
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        title_label = ttk.Label(header_frame, 
                               text="Auto Chat Discord - SubinDev", 
                               style='Title.TLabel')
        title_label.pack(side=tk.LEFT)
        
        version_frame = ttk.Frame(header_frame, style='Panel.TFrame')
        version_frame.pack(side=tk.RIGHT, padx=5)
        ttk.Label(version_frame, 
                 text="v1.0", 
                 style='Header.TLabel').pack(padx=5, pady=2)
        
        self.create_decorative_line(header_frame)
    
    def create_decorative_line(self, parent):
        line_frame = ttk.Frame(parent, height=2, style='Border.TFrame')
        line_frame.pack(fill=tk.X, pady=5)
        
        for i in range(30):
            dot = ttk.Label(line_frame, text="•", 
                           foreground=self.primary_color, 
                           background=self.bg_color,
                           font=("Arial", 14))
            dot.pack(side=tk.LEFT, padx=1)
    
    def create_main_panels(self):
        main_panel = ttk.Frame(self.main_frame, style='Dark.TFrame')
        main_panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.left_panel = ttk.Frame(main_panel, style='Panel.TFrame')
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        right_container = ttk.Frame(main_panel, style='Dark.TFrame')
        right_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)
        
        self.right_canvas = tk.Canvas(right_container, 
                                     bg=self.panel_bg, 
                                     highlightthickness=0,
                                     width=450)  
        right_scrollbar = ttk.Scrollbar(right_container, 
                                       orient=tk.VERTICAL, 
                                       command=self.right_canvas.yview)
        
        self.right_panel = ttk.Frame(self.right_canvas, style='Panel.TFrame')
        self.right_panel.bind('<Configure>', 
                            lambda e: self.right_canvas.configure(
                                scrollregion=self.right_canvas.bbox("all")))
        
        self.right_canvas.create_window((0, 0), 
                                      window=self.right_panel, 
                                      anchor="nw", 
                                      width=430)
        self.right_canvas.configure(yscrollcommand=right_scrollbar.set)
        
        self.right_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        right_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.right_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    
    def create_token_table(self):
        table_frame = ttk.Frame(self.left_panel, style='Dark.TFrame')
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.tree = ttk.Treeview(table_frame, 
                                columns=('selected', 'stt', 'username', 'token', 'status', 'channel_id'), 
                                show='headings', 
                                selectmode='extended',
                                style='Custom.Treeview')
        
        columns = [
            ('selected', '', 30, tk.CENTER),
            ('stt', 'ID', 50, tk.CENTER),
            ('username', 'Username', 150, tk.CENTER),
            ('token', 'Token', 250, tk.CENTER),
            ('status', 'Status', 80, tk.CENTER),
            ('channel_id', 'Channel ID', 150, tk.CENTER)
        ]
        
        for col_id, text, width, anchor in columns:
            self.tree.heading(col_id, text=text, anchor=anchor)
            self.tree.column(col_id, width=width, anchor=anchor)
        
        y_scroll = ttk.Scrollbar(table_frame, 
                                orient=tk.VERTICAL, 
                                command=self.tree.yview,
                                style='Vertical.TScrollbar')
        x_scroll = ttk.Scrollbar(table_frame, 
                                orient=tk.HORIZONTAL, 
                                command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        y_scroll.grid(row=0, column=1, sticky='ns')
        x_scroll.grid(row=1, column=0, sticky='ew')
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        self.tree.tag_configure('selected', background=self.highlight_color)
        self.tree.bind('<Button-1>', self.on_tree_click)
        
        self.token_menu = Menu(self.tree, 
                             tearoff=0,
                             bg="#1e1e2a",
                             fg=self.text_color,
                             activebackground=self.primary_color,
                             activeforeground='white',
                             bd=0)
        self.token_menu.add_command(label="Change Channel ID", command=self.change_channel_id_for_selected)
        self.tree.bind("<Button-3>", self.show_token_menu)
    
    def create_control_buttons(self):
        button_frame = ttk.Frame(self.left_panel, style='Dark.TFrame')
        button_frame.pack(fill=tk.X, pady=(5, 0), padx=5)
        
        buttons = [
            ('Add Token', self.add_token_dialog, 'Primary.TButton'),
            ('Delete', self.delete_tokens, 'Danger.TButton'),
            ('Check', self.check_tokens, 'Warning.TButton'),
            ('Save', self.save_tokens, 'Success.TButton'),
            ('Load', self.load_tokens, 'Secondary.TButton'),
            ('Select All', self.select_all, 'Primary.TButton'),
            ('Deselect All', self.deselect_all, 'Secondary.TButton')
        ]
        
        for i, (text, command, style) in enumerate(buttons):
            btn = ttk.Button(button_frame, 
                           text=text, 
                           command=command, 
                           style=style)
            btn.grid(row=0, column=i, padx=2, pady=2, sticky='ew')
            button_frame.grid_columnconfigure(i, weight=1)
    
    def create_chat_controls(self):
        self.notebook = ttk.Notebook(self.right_panel, style='TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        chat_tab = ttk.Frame(self.notebook, style='Panel.TFrame')
        self.notebook.add(chat_tab, text="Chat Control")
        
        settings_tab = ttk.Frame(self.notebook, style='Panel.TFrame')
        self.notebook.add(settings_tab, text="Settings")
        
        credits_tab = ttk.Frame(self.notebook, style='Panel.TFrame')
        self.notebook.add(credits_tab, text="Credits")
        
        self.build_chat_tab(chat_tab)
        self.build_settings_tab(settings_tab)
        self.build_credits_tab(credits_tab)
    
    def build_chat_tab(self, parent):
        source_frame = ttk.LabelFrame(parent, 
                                    text="Content Source", 
                                    style='Panel.TFrame',
                                    padding=(10, 5))
        source_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Radiobutton(source_frame, 
                       text="Manual Input", 
                       variable=self.content_source,
                       value="manual",
                       command=self.on_content_source_change,
                       style='Custom.TRadiobutton').pack(anchor=tk.W, padx=5, pady=2)
        
        ttk.Radiobutton(source_frame, 
                       text="Quote API", 
                       variable=self.content_source,
                       value="quote",
                       command=self.on_content_source_change,
                       style='Custom.TRadiobutton').pack(anchor=tk.W, padx=5, pady=2)
        
        self.message_frame = ttk.LabelFrame(parent, 
                                          text="Message Content", 
                                          style='Panel.TFrame',
                                          padding=(10, 5))
        self.message_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(self.message_frame, 
                 text="Separate messages with | character",
                 style='Normal.TLabel').pack(anchor=tk.W, pady=(0, 5))
        
        self.message_entry = tk.Text(self.message_frame, 
                                   height=4, 
                                   bg="#1e1e2a", 
                                   fg=self.text_color, 
                                   insertbackground=self.primary_color, 
                                   wrap=tk.WORD,
                                   relief="solid",
                                   bd=2)
        self.message_entry.pack(fill=tk.X, padx=5, pady=5)
        
        mode_frame = ttk.LabelFrame(parent, 
                                  text="Send Mode", 
                                  style='Panel.TFrame',
                                  padding=(10, 5))
        mode_frame.pack(fill=tk.X, padx=5, pady=5)
        
        modes = [
            ("Use first ID only", "first"),
            ("Sequential IDs", "sequential"), 
            ("Parallel send", "parallel")
        ]
        
        for text, value in modes:
            ttk.Radiobutton(mode_frame, 
                           text=text, 
                           variable=self.send_mode,
                           value=value,
                           style='Custom.TRadiobutton').pack(anchor=tk.W, padx=5, pady=2)
        
        settings_frame = ttk.LabelFrame(parent, 
                                      text="Timing Settings", 
                                      style='Panel.TFrame',
                                      padding=(10, 5))
        settings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.min_delay_entry = self.create_setting_entry(settings_frame, "Min delay (sec):", "1", 0)
        self.max_delay_entry = self.create_setting_entry(settings_frame, "Max delay (sec):", "3", 1)
        self.message_count_entry = self.create_setting_entry(settings_frame, "Message count:", "0", 2)
        self.change_channel_entry = self.create_setting_entry(settings_frame, "Change channel after:", "0", 3)
        self.auto_stop_entry = self.create_setting_entry(settings_frame, "Auto stop after (sec):", "0", 4)
        self.rest_time_entry = self.create_setting_entry(settings_frame, "Rest after (sec):", "0", 5)
        self.rest_duration_entry = self.create_setting_entry(settings_frame, "Rest duration (sec):", "0", 6)
        
        channel_frame = ttk.LabelFrame(parent, 
                                     text="Channel ID", 
                                     style='Panel.TFrame',
                                     padding=(10, 5))
        channel_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.chat_channel_entry = ttk.Entry(channel_frame, style='TEntry')
        self.chat_channel_entry.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(channel_frame, 
                 text="(Leave blank to use saved IDs)",
                 style='Normal.TLabel').pack(anchor=tk.W)
        
        button_frame = ttk.Frame(parent, style='Dark.TFrame')
        button_frame.pack(fill=tk.X, padx=5, pady=(5, 0))
        
        self.start_chat_btn = ttk.Button(button_frame, 
                                       text="Start Chat", 
                                       command=self.start_chat, 
                                       style='Success.TButton')
        self.stop_chat_btn = ttk.Button(button_frame, 
                                      text="Stop Chat", 
                                      command=self.stop_chat, 
                                      style='Danger.TButton')
        
        self.start_chat_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        self.stop_chat_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        self.stop_chat_btn.config(state=tk.DISABLED)
    
    def create_setting_entry(self, parent, label, default, row):
        frame = ttk.Frame(parent, style='Dark.TFrame')
        frame.grid(row=row, column=0, sticky='ew', pady=2)
        
        ttk.Label(frame, text=label, style='Normal.TLabel').pack(side=tk.LEFT, padx=5)
        entry = ttk.Entry(frame, width=8, style='TEntry')
        entry.pack(side=tk.LEFT)
        entry.insert(0, default)
        
        return entry
    
    def build_settings_tab(self, parent):
        token_frame = ttk.LabelFrame(parent, 
                                   text="Token Settings", 
                                   style='Panel.TFrame',
                                   padding=(10, 5))
        token_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(token_frame, 
                 text="Change channel IDs for selected tokens:",
                 style='Normal.TLabel').pack(anchor=tk.W, pady=(0, 5))
        
        entry_frame = ttk.Frame(token_frame, style='Dark.TFrame')
        entry_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.new_channel_entry = ttk.Entry(entry_frame, style='TEntry')
        self.new_channel_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        change_btn = ttk.Button(entry_frame, 
                              text="Apply", 
                              command=self.change_channel_ids,
                              style='Primary.TButton')
        change_btn.pack(side=tk.LEFT)
        
        ui_frame = ttk.LabelFrame(parent, 
                                text="UI Settings", 
                                style='Panel.TFrame',
                                padding=(10, 5))
        ui_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Checkbutton(ui_frame, 
                      text="Enable animations", 
                      style='Custom.TCheckbutton').pack(anchor=tk.W, padx=5, pady=2)
        
        ttk.Checkbutton(ui_frame, 
                      text="Show token preview", 
                      style='Custom.TCheckbutton').pack(anchor=tk.W, padx=5, pady=2)
    
    def build_credits_tab(self, parent):
        credits_frame = ttk.Frame(parent, style='Panel.TFrame')
        credits_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        logo_label = ttk.Label(credits_frame, 
                              text="Auto Chat Discord", 
                              style='Title.TLabel')
        logo_label.pack(pady=(20, 10))
        
        version_label = ttk.Label(credits_frame, 
                                text="Auto Chat Discord v1.0", 
                                style='Header.TLabel')
        version_label.pack(pady=(0, 20))
        
        credits_text = """
        Developed by: SubinDev
        
        Special thanks to:
        - The Discord API community
        - Open source contributors
        - Our beta testers
        
        © 2025 SubinDev.
        All rights reserved
        """
        
        text_label = ttk.Label(credits_frame, 
                             text=credits_text, 
                             style='Normal.TLabel',
                             justify=tk.CENTER)
        text_label.pack(pady=(0, 20))
        
        contact_btn = ttk.Button(credits_frame, 
                               text="Contact Support", 
                               command=lambda: webbrowser.open("mailto:"),
                               style='Primary.TButton')
        contact_btn.pack(pady=(0, 10))
    
    def _on_mousewheel(self, event):
        self.right_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def on_tree_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        column = self.tree.identify_column(event.x)
        
        if region == 'cell' and column == '#1':  
            item = self.tree.identify_row(event.y)
            current_value = self.tree.set(item, 'selected')
            new_value = '☑' if current_value != '☑' else '☐'
            self.tree.set(item, 'selected', new_value)
            
            token = self.tree.set(item, 'token')
            if new_value == '☑':
                if token not in self.selected_tokens:
                    self.selected_tokens.append(token)
            else:
                if token in self.selected_tokens:
                    self.selected_tokens.remove(token)
    
    def show_token_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.token_menu.post(event.x_root, event.y_root)
    
    def change_channel_id_for_selected(self):
        selected_items = self.tree.selection()
        if not selected_items:
            return
            
        new_channel_id = simpledialog.askstring("Change Channel ID", "Enter new channel ID:")
        if new_channel_id is not None:
            for item in selected_items:
                self.tree.set(item, 'channel_id', new_channel_id)
    
    def add_token_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Token")
        dialog.geometry("500x170")
        dialog.configure(bg=self.panel_bg)
        dialog.resizable(False, False)
        
        self.center_window(dialog)
        
        ttk.Label(dialog, text="Enter Discord Token:", style='Header.TLabel').pack(pady=(10, 5))
        
        token_frame = ttk.Frame(dialog, style='Dark.TFrame')
        token_frame.pack(fill=tk.X, padx=10)
        
        self.token_entry = ttk.Entry(token_frame, style='TEntry')
        self.token_entry.pack(fill=tk.X, expand=True, padx=5, pady=5)
        
        button_frame = ttk.Frame(dialog, style='Dark.TFrame')
        button_frame.pack(pady=(15, 10))
        
        dialog_buttons = [
            ("Add", lambda: self.add_token(dialog), 'Success.TButton'),
            ("Cancel", dialog.destroy, 'Danger.TButton'),
            ("Paste", self.paste_token, 'Primary.TButton'),
            ("Clear", self.clear_token_entry, 'Warning.TButton')
        ]
        
        for text, command, style in dialog_buttons:
            btn = ttk.Button(button_frame, 
                            text=text, 
                            command=command, 
                            style=style)
            btn.pack(side=tk.LEFT, padx=5)
        
        dialog.transient(self.root)
        dialog.grab_set()
        self.root.wait_window(dialog)
    
    def paste_token(self):
        try:
            self.token_entry.delete(0, tk.END)
            self.token_entry.insert(0, self.root.clipboard_get())
        except:
            pass
    
    def clear_token_entry(self):
        self.token_entry.delete(0, tk.END)
    
    def add_token(self, dialog):
        token = self.token_entry.get().strip()
        if not token:
            messagebox.showerror("Error", "Please enter a token!")
            return
        
        for item in self.tree.get_children():
            if self.tree.set(item, 'token') == token:
                messagebox.showerror("Error", "Token already exists!")
                return
        
        stt = len(self.tree.get_children()) + 1
        self.tree.insert('', tk.END, values=('☐', stt, 'Checking...', token, 'Checking...', ''))
        
        threading.Thread(target=self.check_single_token, args=(token, stt), daemon=True).start()
        
        dialog.destroy()
    
    def check_single_token(self, token, stt):
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get('https://discord.com/api/v9/users/@me', headers=headers)
            if response.status_code in [200, 201, 204]:
                user_data = response.json()
                try:
                    username = f"{user_data['username']}#{user_data['discriminator']}"
                except:
                    username = "Unknown User"
                status = "live"
                color = self.success_color
            else:
                username = "Unknown"
                status = "die" 
                color = self.error_color
        except Exception as e:
            username = "Unknown"
            status = "die"
            color = self.error_color
        
        self.root.after(0, self.update_token_status, token, stt, username, status, color)
    
    def update_token_status(self, token, stt, username, status, color):
        for item in self.tree.get_children():
            if self.tree.set(item, 'token') == token:
                self.tree.set(item, 'username', username)
                self.tree.set(item, 'status', status)
                self.tree.item(item, tags=(status,))
                self.tree.tag_configure(status, foreground=color)
                break
        
        self.update_stt_numbers()
    
    def update_stt_numbers(self):
        for i, item in enumerate(self.tree.get_children(), 1):
            self.tree.set(item, 'stt', i)
    
    def delete_tokens(self):
        selected_items = []
        for item in self.tree.get_children():
            if self.tree.set(item, 'selected') == '☑':
                selected_items.append(item)
        
        if not selected_items:
            messagebox.showwarning("Warning", "Please select at least one token to delete!")
            return
        
        for item in selected_items:
            token = self.tree.set(item, 'token')
            if token in self.selected_tokens:
                self.selected_tokens.remove(token)
            self.tree.delete(item)
        
        self.update_stt_numbers()
    
    def check_tokens(self):
        if not self.tree.get_children():
            messagebox.showwarning("Warning", "No tokens to check!")
            return
        
        for item in self.tree.get_children():
            token = self.tree.set(item, 'token')
            self.tree.set(item, 'username', 'Checking...')
            self.tree.set(item, 'status', 'Checking...')
            threading.Thread(target=self.check_single_token, args=(token, self.tree.set(item, 'stt')), daemon=True).start()
    
    def save_tokens(self):
        if not self.tree.get_children():
            messagebox.showwarning("Warning", "No tokens to save!")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save tokens"
        )
        
        if not file_path:
            return
        
        tokens_data = []
        for item in self.tree.get_children():
            tokens_data.append({
                'token': self.tree.set(item, 'token'),
                'username': self.tree.set(item, 'username'),
                'status': self.tree.set(item, 'status'),
                'channel_id': self.tree.set(item, 'channel_id')
            })
        
        try:
            with open(file_path, 'w') as f:
                json.dump(tokens_data, f, indent=4)
            messagebox.showinfo("Success", "Tokens saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {str(e)}")
    
    def load_tokens(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Load tokens"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r') as f:
                tokens_data = json.load(f)
            
            for item in self.tree.get_children():
                self.tree.delete(item)
            self.selected_tokens = []
            
            for data in tokens_data:
                stt = len(self.tree.get_children()) + 1
                status = data.get('status', 'die')
                color = self.success_color if status == 'live' else self.error_color
                
                self.tree.insert('', tk.END, values=(
                    '☐', 
                    stt, 
                    data.get('username', 'Unknown'), 
                    data['token'], 
                    status, 
                    data.get('channel_id', '')
                ))
                
                item = self.tree.get_children()[-1]
                self.tree.item(item, tags=(status,))
                self.tree.tag_configure(status, foreground=color)
            
            messagebox.showinfo("Success", "Tokens loaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")
    
    def select_all(self):
        for item in self.tree.get_children():
            self.tree.set(item, 'selected', '☑')
            token = self.tree.set(item, 'token')
            if token not in self.selected_tokens:
                self.selected_tokens.append(token)
    
    def deselect_all(self):
        for item in self.tree.get_children():
            self.tree.set(item, 'selected', '☐')
        self.selected_tokens = []
    
    def change_channel_ids(self):
        new_channel_ids = self.new_channel_entry.get().strip()
        if not new_channel_ids:
            messagebox.showwarning("Warning", "Please enter new channel IDs!")
            return
        
        channel_list = [cid.strip() for cid in new_channel_ids.split(',') if cid.strip()]
        
        for item in self.tree.get_children():
            if self.tree.set(item, 'selected') == '☑':
                self.tree.set(item, 'channel_id', ','.join(channel_list))
    
    def start_chat(self):
        if self.content_source.get() == "manual":
            messages = self.message_entry.get("1.0", tk.END).strip().split('|')
            messages = [msg.strip() for msg in messages if msg.strip()]
            
            if not messages:
                messagebox.showwarning("Warning", "Please enter chat content!")
                return
        else:
            messages = [""]
        
        try:
            min_delay = float(self.min_delay_entry.get())
            max_delay = float(self.max_delay_entry.get())
            if min_delay < 0 or max_delay < 0 or min_delay > max_delay:
                raise ValueError
        except:
            messagebox.showwarning("Warning", "Please enter valid delay (1-3 sec by default)!")
            return
        
        try:
            message_count = int(self.message_count_entry.get())
            if message_count < 0:
                raise ValueError
        except:
            messagebox.showwarning("Warning", "Please enter valid message count (0 = unlimited)!")
            return
        
        try:
            change_channel_after = int(self.change_channel_entry.get() or "0")
            if change_channel_after < 0:
                raise ValueError
        except:
            messagebox.showwarning("Warning", "Please enter valid channel change count (0 = don't change)!")
            return
        
        channel_id = self.chat_channel_entry.get().strip()
        if not channel_id:
            for item in self.tree.get_children():
                if self.tree.set(item, 'selected') == '☑' and self.tree.set(item, 'channel_id'):
                    channel_id = self.tree.set(item, 'channel_id')
                    break
        
        if not channel_id:
            messagebox.showwarning("Warning", "Please enter channel ID or set channel ID for token!")
            return
        
        tokens_to_use = []
        for item in self.tree.get_children():
            if self.tree.set(item, 'status') == 'live':
                token_channel = self.tree.set(item, 'channel_id') or channel_id
                tokens_to_use.append({
                    'token': self.tree.set(item, 'token'),
                    'channel_id': token_channel
                })
        
        if not tokens_to_use:
            messagebox.showwarning("Warning", "No live tokens available for chat!")
            return
        
        self.start_chat_btn.config(state=tk.DISABLED)
        self.stop_chat_btn.config(state=tk.NORMAL)
        self.is_chat_running = True
        
        self.chat_thread = threading.Thread(
            target=self.run_chat,
            args=(tokens_to_use, messages, min_delay, max_delay, message_count, channel_id, change_channel_after),
            daemon=True
        )
        self.chat_thread.start()
    
    def stop_chat(self):
        self.is_chat_running = False
        if self.chat_thread and self.chat_thread.is_alive():
            self.chat_thread.join(timeout=1)
        
        self.start_chat_btn.config(state=tk.NORMAL)
        self.stop_chat_btn.config(state=tk.DISABLED)
    
    def run_chat(self, tokens, messages, min_delay, max_delay, message_count, main_channel_id, change_channel_after):
        count = 0
        message_index = 0
        start_time = time.time()
        last_rest_time = start_time
        
        try:
            auto_stop_time = float(self.auto_stop_entry.get() or "0")
            rest_interval = float(self.rest_time_entry.get() or "0") 
            rest_duration = float(self.rest_duration_entry.get() or "0")
        except ValueError:
            auto_stop_time = 0
            rest_interval = 0
            rest_duration = 0
        
        while self.is_chat_running and (message_count == 0 or count < message_count):
            current_time = time.time()
            
            if auto_stop_time > 0 and (current_time - start_time) >= auto_stop_time:
                break
                
            if rest_interval > 0 and rest_duration > 0:
                if (current_time - last_rest_time) >= rest_interval:
                    time.sleep(rest_duration)
                    last_rest_time = time.time()
                    
                    if not self.is_chat_running:
                        break
            
            if not messages:
                break
                
            msg = messages[message_index % len(messages)]
            message_index += 1
            
            for token_data in tokens:
                if not self.is_chat_running:
                    break
                
                main_channel = self.chat_channel_entry.get().strip()
                if main_channel:
                    channel_ids = [main_channel]
                else:
                    channel_ids = token_data['channel_id'].split(',')
                
                if self.content_source.get() == "quote":
                    try:
                        response = requests.get('https://zenquotes.io/api/random')
                        if response.status_code == 200:
                            quote_data = response.json()[0]
                            msg = f"{quote_data['q']} - {quote_data['a']}"
                        else:
                            msg = messages[message_index % len(messages)]
                    except:
                        msg = messages[message_index % len(messages)]
                else:
                    msg = messages[message_index % len(messages)]
                
                if self.send_mode.get() == "parallel":
                    for channel_id in channel_ids:
                        self.send_message(token_data['token'], channel_id.strip(), msg)
                elif self.send_mode.get() == "first":
                    channel_id = channel_ids[0].strip()
                    self.send_message(token_data['token'], channel_id, msg)
                else: 
                    if change_channel_after > 0 and count > 0:
                        current_channel_index = (count // change_channel_after) % len(channel_ids)
                        channel_id = channel_ids[current_channel_index].strip()
                    else:
                        channel_id = channel_ids[0].strip()
                    self.send_message(token_data['token'], channel_id, msg)
                
                time.sleep(0.1)
            
            count += 1
            
            if self.is_chat_running and (message_count == 0 or count < message_count):
                delay = random.uniform(min_delay, max_delay)
                end_time = time.time() + delay
                while time.time() < end_time and self.is_chat_running:
                    time.sleep(0.1)
        
        self.root.after(0, self.stop_chat)
    
    def send_message(self, token, channel_id, message):
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }
        
        payload = {
            'content': message,
            'tts': False
        }
        
        try:
            response = requests.post(
                f'https://discord.com/api/v9/channels/{channel_id}/messages',
                headers=headers,
                json=payload,
                timeout=10
            )
            if response.status_code in [401, 403]:
                self.root.after(0, self.update_token_status, token, None, None, "die", self.error_color)
        except Exception as e:
            pass
    
    def center_window(self, window):
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')

    def on_content_source_change(self, *args):
        if self.content_source.get() == "quote":
            self.message_frame.pack_forget()
        else:
            self.message_frame.pack(fill=tk.X, pady=(0, 10))
        
if __name__ == "__main__":
    root = tk.Tk()
    app = SciFiDiscordTokenManager(root)
    root.mainloop()