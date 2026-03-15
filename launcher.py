"""
SoundLaunch — Launcher
"""
import sys, os, socket, threading, webbrowser, time, logging
from pathlib import Path

def base_path():
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent

def data_path():
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).parent

BASE = base_path()
DATA = data_path()
PORT = 7878

(DATA / 'data').mkdir(exist_ok=True)
(DATA / 'static' / 'images').mkdir(parents=True, exist_ok=True)

# Redirect stdout/stderr before uvicorn touches them
log_file = DATA / 'soundlaunch.log'
try:
    _log = open(log_file, 'w', encoding='utf-8', buffering=1)
    sys.stdout = _log
    sys.stderr = _log
except Exception:
    pass

logging.disable(logging.CRITICAL)
for _n in ['uvicorn','uvicorn.error','uvicorn.access','fastapi']:
    _lg = logging.getLogger(_n)
    _lg.handlers.clear()
    _lg.addHandler(logging.NullHandler())
    _lg.propagate = False

os.environ['SL_DATA_PATH']   = str(DATA)
os.environ['SL_STATIC_PATH'] = str(BASE / 'static')
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))

# ── GUI log sink ─────────────────────────────────────────────────────────────
_gui_log_cb = None   # set after GUI is created

class _GuiLogHandler(logging.Handler):
    def emit(self, record):
        if _gui_log_cb:
            try: _gui_log_cb(self.format(record))
            except Exception: pass

def _log_to_gui(msg):
    if _gui_log_cb:
        try: _gui_log_cb(msg)
        except Exception: pass

# ── Network ──────────────────────────────────────────────────────────────────
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'

# ── Server ───────────────────────────────────────────────────────────────────
_server    = None
_srv_ready = threading.Event()
_srv_error = None

def _run_server():
    global _server, _srv_error
    try:
        _log_to_gui('uvicorn import ediliyor...')
        import uvicorn
        import uvicorn.config as uvc
        uvc.LOGGING_CONFIG = {'version':1,'disable_existing_loggers':False,'handlers':{},'loggers':{}}
        _log_to_gui('server.py import ediliyor...')
        from server import app
        _log_to_gui(f'Server başlatılıyor — port {PORT}...')
        cfg = uvicorn.Config(app, host='0.0.0.0', port=PORT,
                             log_config=None, log_level='critical', access_log=False)
        _server = uvicorn.Server(cfg)
        _srv_ready.set()
        _log_to_gui('Server çalışıyor.')
        _server.run()
    except Exception as e:
        _srv_error = str(e)
        _log_to_gui(f'HATA: {e}')
        _srv_ready.set()

def start_server():
    threading.Thread(target=_run_server, daemon=True).start()
    _srv_ready.wait(timeout=10)
    if _srv_error:
        return False, _srv_error
    for _ in range(16):
        time.sleep(0.5)
        try:
            s = socket.create_connection(('127.0.0.1', PORT), timeout=1)
            s.close()
            return True, None
        except OSError:
            continue
    return False, f'Port {PORT} açılmadı.'

def stop_server():
    global _server
    if _server:
        _server.should_exit = True

# ── GUI ──────────────────────────────────────────────────────────────────────
def run_gui(url):
    global _gui_log_cb
    import tkinter as tk
    from tkinter import font as tkf

    BG      = '#0a0a0a'
    BG1     = '#111111'
    BG2     = '#181818'
    BG3     = '#222222'
    GREEN   = '#22c55e'
    GREEN2  = '#16a34a'
    BLUE    = '#3b82f6'
    AMBER   = '#f59e0b'
    RED     = '#ef4444'
    T1      = '#f0f0f0'
    T2      = '#888888'
    T3      = '#444444'
    T4      = '#2a2a2a'

    root = tk.Tk()
    root.title('SoundLaunch')
    root.geometry('480x580')
    root.resizable(False, False)
    root.configure(bg=BG)

    # Icon
    try:
        icon_path = BASE / 'static' / 'icon.png'
        if icon_path.exists():
            img = tk.PhotoImage(file=str(icon_path))
            root.iconphoto(True, img)
    except Exception:
        pass

    # ── HEADER ───────────────────────────────────────────────────────────────
    hdr = tk.Frame(root, bg=BG1, height=64)
    hdr.pack(fill='x')
    hdr.pack_propagate(False)

    hdr_c = tk.Frame(hdr, bg=BG1)
    hdr_c.place(relx=.5, rely=.5, anchor='center')
    tk.Label(hdr_c, text='SL▸', font=('Segoe UI', 20, 'bold'),
             fg=GREEN, bg=BG1).pack(side='left', padx=(0,8))
    tk.Label(hdr_c, text='SoundLaunch', font=('Segoe UI', 14),
             fg=T2, bg=BG1).pack(side='left')

    # Separator
    tk.Frame(root, bg=BG3, height=1).pack(fill='x')

    # ── STATUS ROW ───────────────────────────────────────────────────────────
    st_row = tk.Frame(root, bg=BG, pady=14)
    st_row.pack(fill='x', padx=28)

    st_dot_canvas = tk.Canvas(st_row, width=10, height=10, bg=BG,
                              highlightthickness=0)
    st_dot_canvas.pack(side='left', padx=(0,7))
    st_dot = st_dot_canvas.create_oval(1,1,9,9, fill=GREEN, outline='')

    st_txt = tk.Label(st_row, text='Server aktif',
                      font=('Segoe UI', 11, 'bold'), fg=GREEN, bg=BG)
    st_txt.pack(side='left')

    sp_txt = tk.Label(st_row, text='',
                      font=('Segoe UI', 9), fg=T3, bg=BG)
    sp_txt.pack(side='right')

    # Dot pulse
    pulse_on = [True]
    def _pulse():
        if not pulse_on[0]: return
        try:
            c = st_dot_canvas.itemcget(st_dot, 'fill')
            st_dot_canvas.itemconfig(st_dot, fill=GREEN2 if c==GREEN else GREEN)
            root.after(900, _pulse)
        except Exception: pass
    _pulse()

    # ── URL CARD ─────────────────────────────────────────────────────────────
    card = tk.Frame(root, bg=BG2, padx=0, pady=0)
    card.pack(fill='x', padx=28, pady=(0,0))

    tk.Label(card, text='Telefonunda tarayıcıya yaz:',
             font=('Segoe UI', 9), fg=T3, bg=BG2,
             pady=10).pack(anchor='w', padx=16)

    url_row = tk.Frame(card, bg=BG3)
    url_row.pack(fill='x', padx=16, pady=(0,14))

    url_entry = tk.Entry(url_row, font=('Consolas', 13, 'bold'),
                         fg=BLUE, bg=BG3, bd=0,
                         readonlybackground=BG3,
                         state='readonly')
    url_entry.config(state='normal')
    url_entry.insert(0, '  ' + url)
    url_entry.config(state='readonly')
    url_entry.pack(side='left', fill='x', expand=True, ipady=10, padx=(6,0))

    copy_var = tk.StringVar(value='Kopyala')
    def do_copy():
        root.clipboard_clear()
        root.clipboard_append(url)
        copy_var.set('✓')
        root.after(2000, lambda: copy_var.set('Kopyala'))

    copy_btn = tk.Button(url_row, textvariable=copy_var,
                         font=('Segoe UI', 10), fg=T2, bg='#2c2c2c',
                         activeforeground=T1, activebackground='#383838',
                         bd=0, padx=16, pady=10, cursor='hand2',
                         relief='flat', command=do_copy)
    copy_btn.pack(side='right')

    # ── INFO PILLS ───────────────────────────────────────────────────────────
    pills = tk.Frame(root, bg=BG)
    pills.pack(fill='x', padx=28, pady=(10,0))

    def pill(parent, label, value, vc):
        f = tk.Frame(parent, bg=BG2, padx=14, pady=10)
        f.pack(side='left', expand=True, fill='x', padx=(0,8))
        tk.Label(f, text=label, font=('Segoe UI', 8),
                 fg=T3, bg=BG2).pack(anchor='w')
        tk.Label(f, text=value, font=('Consolas', 12, 'bold'),
                 fg=vc, bg=BG2).pack(anchor='w', pady=(2,0))

    ip = get_local_ip()
    pill(pills, 'IP Adresi', ip, T1)
    pill(pills, 'Port', str(PORT), AMBER)

    # ── ACTION BUTTONS ───────────────────────────────────────────────────────
    bf = tk.Frame(root, bg=BG)
    bf.pack(fill='x', padx=28, pady=(14,0))

    open_btn = tk.Button(bf, text='🌐  Tarayıcıda Aç',
                         font=('Segoe UI', 11, 'bold'),
                         fg='#000', bg=GREEN,
                         activeforeground='#000', activebackground=GREEN2,
                         bd=0, pady=11, cursor='hand2', relief='flat',
                         command=lambda: webbrowser.open(url))
    open_btn.pack(side='left', fill='x', expand=True)

    def do_quit():
        pulse_on[0] = False
        stop_server()
        root.destroy()
        sys.exit(0)

    quit_btn = tk.Button(bf, text='Kapat',
                         font=('Segoe UI', 11), fg=RED, bg='#1e1e1e',
                         activeforeground=T1, activebackground='#2c2c2c',
                         bd=0, pady=11, cursor='hand2', relief='flat',
                         command=do_quit)
    quit_btn.pack(side='right', fill='x', expand=True, padx=(8,0))

    def on_enter_open(e): open_btn.config(bg=GREEN2)
    def on_leave_open(e): open_btn.config(bg=GREEN)
    def on_enter_quit(e): quit_btn.config(bg='#2c2c2c', fg=T1)
    def on_leave_quit(e): quit_btn.config(bg='#1e1e1e', fg=RED)
    open_btn.bind('<Enter>', on_enter_open)
    open_btn.bind('<Leave>', on_leave_open)
    quit_btn.bind('<Enter>', on_enter_quit)
    quit_btn.bind('<Leave>', on_leave_quit)

    # ── LOG PANEL ────────────────────────────────────────────────────────────
    tk.Frame(root, bg=BG3, height=1).pack(fill='x', padx=28, pady=(16,0))

    log_hdr = tk.Frame(root, bg=BG)
    log_hdr.pack(fill='x', padx=28, pady=(8,4))
    tk.Label(log_hdr, text='L O G', font=('Segoe UI', 8, 'bold'),
             fg=T3, bg=BG).pack(side='left')
    log_clear_btn = tk.Button(log_hdr, text='Temizle',
                              font=('Segoe UI', 8), fg=T3, bg=BG,
                              activeforeground=T2, activebackground=BG,
                              bd=0, cursor='hand2', relief='flat')
    log_clear_btn.pack(side='right')

    log_frame = tk.Frame(root, bg=BG2, padx=0, pady=0)
    log_frame.pack(fill='both', expand=True, padx=28, pady=(0,16))

    log_text = tk.Text(log_frame,
                       font=('Consolas', 9),
                       fg='#4ade80', bg='#0d0d0d',
                       insertbackground=GREEN,
                       selectbackground='#1e3a1e',
                       bd=0, padx=10, pady=8,
                       state='disabled',
                       wrap='word',
                       cursor='arrow')
    log_text.pack(side='left', fill='both', expand=True)

    log_sb = tk.Scrollbar(log_frame, orient='vertical',
                          command=log_text.yview,
                          bg=BG2, troughcolor=BG2,
                          activebackground=BG3, width=8)
    log_sb.pack(side='right', fill='y')
    log_text.config(yscrollcommand=log_sb.set)

    # Color tags
    log_text.tag_config('err',  foreground='#ef4444')
    log_text.tag_config('warn', foreground='#f59e0b')
    log_text.tag_config('ok',   foreground='#4ade80')
    log_text.tag_config('info', foreground='#888')
    log_text.tag_config('ts',   foreground='#333')

    def append_log(msg):
        import datetime
        ts = datetime.datetime.now().strftime('%H:%M:%S')
        msg = str(msg).strip()
        if not msg: return

        tag = 'info'
        if any(w in msg.upper() for w in ['HATA','ERROR','FAIL','EXCEPTION','TRACEBACK']):
            tag = 'err'
        elif any(w in msg.upper() for w in ['WARN','WARNING']):
            tag = 'warn'
        elif any(w in msg.upper() for w in ['AKTIF','ÇALIŞIYOR','HAZIR','BAŞLATILDI','OK','BAĞLI']):
            tag = 'ok'

        log_text.config(state='normal')
        log_text.insert('end', f'[{ts}] ', 'ts')
        log_text.insert('end', msg + '\n', tag)
        log_text.config(state='disabled')
        log_text.see('end')

    def clear_log():
        log_text.config(state='normal')
        log_text.delete('1.0', 'end')
        log_text.config(state='disabled')

    log_clear_btn.config(command=clear_log)

    # Wire up the global log callback
    _gui_log_cb = lambda msg: root.after(0, append_log, msg)

    # Initial log messages
    append_log(f'SoundLaunch başlatıldı.')
    append_log(f'Adres: {url}')
    append_log(f'Veri dizini: {DATA}')

    # ── Soundpad poller ──────────────────────────────────────────────────────
    def check_soundpad():
        try:
            import urllib.request, json
            with urllib.request.urlopen(
                f'http://127.0.0.1:{PORT}/api/status', timeout=2
            ) as r:
                data = json.loads(r.read())
                if data.get('connected'):
                    sp_txt.config(text='● Soundpad bağlı', fg=GREEN)
                else:
                    code = data.get('error_code', '')
                    sp_txt.config(
                        text='○ Soundpad kapalı',
                        fg=AMBER
                    )
        except Exception:
            pass
        root.after(5000, check_soundpad)

    root.after(2000, check_soundpad)

    # ── File log tail ────────────────────────────────────────────────────────
    _last_pos = [0]
    def tail_log_file():
        try:
            with open(log_file, 'r', encoding='utf-8', errors='replace') as f:
                f.seek(_last_pos[0])
                new = f.read()
                _last_pos[0] = f.tell()
            if new.strip():
                for line in new.splitlines():
                    if line.strip():
                        append_log(line)
        except Exception:
            pass
        root.after(1000, tail_log_file)

    root.after(1500, tail_log_file)

    root.protocol('WM_DELETE_WINDOW', do_quit)
    root.mainloop()

# ── Splash ───────────────────────────────────────────────────────────────────
def show_splash():
    try:
        import tkinter as tk
        s = tk.Tk()
        s.overrideredirect(True)
        s.configure(bg='#0a0a0a')
        sw, sh = s.winfo_screenwidth(), s.winfo_screenheight()
        s.geometry(f'300x80+{(sw-300)//2}+{(sh-80)//2}')
        tk.Label(s, text='SL▸  SoundLaunch',
                 font=('Segoe UI', 14, 'bold'),
                 fg='#22c55e', bg='#0a0a0a').pack(expand=True)
        tk.Label(s, text='Başlatılıyor...',
                 font=('Segoe UI', 9), fg='#333', bg='#0a0a0a').pack()
        s.update()
        return s
    except Exception:
        return None

# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    splash = show_splash()
    ok, err = start_server()

    if splash:
        try: splash.destroy()
        except Exception: pass

    if not ok:
        try:
            import tkinter as tk
            from tkinter import messagebox
            r = tk.Tk(); r.withdraw()
            messagebox.showerror('SoundLaunch',
                f'Server başlatılamadı.\n\n{err}\n\n'
                f'Detay: {log_file}')
            r.destroy()
        except Exception:
            pass
        sys.exit(1)

    url = f'http://{get_local_ip()}:{PORT}'
    webbrowser.open(url)
    run_gui(url)
