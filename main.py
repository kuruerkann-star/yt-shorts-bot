import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import json
import os
import subprocess
import webbrowser
from pathlib import Path
from typing import Optional, List, Dict

CONFIG_FILE = "config.json"


def load_config() -> Dict:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "api_key": "",
        "client_secrets": "",
        "channel_name": "",
        "region_code": "TR",
        "language": "tr",
        "output_dir": "output_videos",
        "video_duration": 30,
        "auto_tts": False,
        "ai_provider": "openai",
        "ai_api_key": "",
    }


def save_config(cfg: Dict):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("YouTube Shorts Bot")
        self.geometry("1150x860")
        self.minsize(950, 700)
        self.configure(bg="#0f0f1a")
        self.config_data = load_config()
        self.trending_results: List[Dict] = []
        self.selected_video: Optional[Dict] = None
        self.created_video_path: Optional[str] = None

        self._setup_styles()
        self._build_ui()

    def _setup_styles(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        bg = "#0f0f1a"
        fg = "#ffffff"
        accent = "#ff3c78"
        entry_bg = "#1a1a2e"
        ai_color = "#7c3aed"
        s.configure(".", background=bg, foreground=fg, font=("Segoe UI", 10))
        s.configure("TFrame", background=bg)
        s.configure("TLabel", background=bg, foreground=fg)
        s.configure("TLabelframe", background=bg, foreground=accent, bordercolor=accent)
        s.configure("TLabelframe.Label", background=bg, foreground=accent, font=("Segoe UI", 10, "bold"))
        s.configure("AI.TLabelframe", background=bg, foreground=ai_color, bordercolor=ai_color)
        s.configure("AI.TLabelframe.Label", background=bg, foreground=ai_color, font=("Segoe UI", 10, "bold"))
        s.configure("TNotebook", background=bg, borderwidth=0)
        s.configure("TNotebook.Tab", background="#1a1a2e", foreground=fg, padding=[14, 6])
        s.map("TNotebook.Tab", background=[("selected", accent)], foreground=[("selected", fg)])
        s.configure("TEntry", fieldbackground=entry_bg, foreground=fg, insertcolor=fg)
        s.configure("TCombobox", fieldbackground=entry_bg, foreground=fg, background=entry_bg)
        s.map("TCombobox", fieldbackground=[("readonly", entry_bg)])
        s.configure("Accent.TButton", background=accent, foreground=fg,
                    font=("Segoe UI", 10, "bold"), padding=[12, 6])
        s.map("Accent.TButton", background=[("active", "#ff6090")])
        s.configure("AI.TButton", background=ai_color, foreground=fg,
                    font=("Segoe UI", 10, "bold"), padding=[12, 6])
        s.map("AI.TButton", background=[("active", "#9d5cff")])
        s.configure("Green.TButton", background="#16a34a", foreground=fg,
                    font=("Segoe UI", 10, "bold"), padding=[12, 6])
        s.map("Green.TButton", background=[("active", "#22c55e")])
        s.configure("TButton", background="#1a1a2e", foreground=fg, padding=[10, 5])
        s.map("TButton", background=[("active", "#2a2a4e")])
        s.configure("TCheckbutton", background=bg, foreground=fg)
        s.configure("Horizontal.TProgressbar", troughcolor="#1a1a2e", background=accent)
        s.configure("TScrollbar", background="#1a1a2e", troughcolor=bg, arrowcolor=fg)
        s.configure("Treeview", background="#1a1a2e", foreground=fg,
                    fieldbackground="#1a1a2e", rowheight=28)
        s.configure("Treeview.Heading", background="#0f0f1a", foreground=accent,
                    font=("Segoe UI", 9, "bold"))
        s.map("Treeview", background=[("selected", accent)])

    def _build_ui(self):
        header = ttk.Frame(self)
        header.pack(fill="x", padx=0, pady=0)
        tk.Label(header, text="YouTube Shorts Bot",
                 font=("Segoe UI", 18, "bold"), bg="#0f0f1a", fg="#ff3c78").pack(side="left", padx=18, pady=10)
        tk.Label(header, text="Trend Shorts bul  |  AI ile video olustur  |  YouTube'a yukle",
                 font=("Segoe UI", 9), bg="#0f0f1a", fg="#888").pack(side="left", padx=4)

        sep = tk.Frame(self, height=2, bg="#ff3c78")
        sep.pack(fill="x")

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=0, pady=0)

        self.tab_search = ttk.Frame(nb)
        self.tab_create = ttk.Frame(nb)
        self.tab_upload = ttk.Frame(nb)
        self.tab_settings = ttk.Frame(nb)

        nb.add(self.tab_search, text="  Trend Ara  ")
        nb.add(self.tab_create, text="  Video Olustur  ")
        nb.add(self.tab_upload, text="  YouTube'a Yukle  ")
        nb.add(self.tab_settings, text="  Ayarlar  ")

        self._build_search_tab()
        self._build_create_tab()
        self._build_upload_tab()
        self._build_settings_tab()

        self.status_var = tk.StringVar(value="Hazir")
        status_bar = tk.Label(self, textvariable=self.status_var,
                              bg="#1a1a2e", fg="#aaa", anchor="w", padx=10,
                              font=("Segoe UI", 9))
        status_bar.pack(fill="x", side="bottom")

    def _build_search_tab(self):
        p = ttk.Frame(self.tab_search)
        p.pack(fill="both", expand=True, padx=14, pady=10)

        top = ttk.LabelFrame(p, text="Arama Kriterleri", padding=10)
        top.pack(fill="x", pady=(0, 8))

        ttk.Label(top, text="Arama kelimesi:").grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.search_query = ttk.Entry(top, width=40)
        self.search_query.grid(row=0, column=1, sticky="ew", padx=(0, 12))

        ttk.Label(top, text="Sonuc sayisi:").grid(row=0, column=2, sticky="w", padx=(0, 6))
        self.result_count = ttk.Combobox(top, values=["5", "10", "15", "20", "25"], width=5, state="readonly")
        self.result_count.set("10")
        self.result_count.grid(row=0, column=3, padx=(0, 12))

        self.trend_mode = tk.BooleanVar(value=False)
        ttk.Checkbutton(top, text="Gunun trendleri", variable=self.trend_mode).grid(
            row=0, column=4, padx=(0, 12))

        ttk.Button(top, text="Ara", style="Accent.TButton", command=self._do_search).grid(
            row=0, column=5, padx=(0, 4))
        top.columnconfigure(1, weight=1)

        tree_frame = ttk.LabelFrame(p, text="Sonuclar", padding=6)
        tree_frame.pack(fill="both", expand=True)

        cols = ("title", "channel", "views", "likes", "url")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="browse")
        self.tree.heading("title", text="Baslik")
        self.tree.heading("channel", text="Kanal")
        self.tree.heading("views", text="Izlenme")
        self.tree.heading("likes", text="Begeni")
        self.tree.heading("url", text="URL")
        self.tree.column("title", width=350, minwidth=200)
        self.tree.column("channel", width=150, minwidth=100)
        self.tree.column("views", width=110, minwidth=80, anchor="e")
        self.tree.column("likes", width=100, minwidth=70, anchor="e")
        self.tree.column("url", width=220, minwidth=150)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.tree.bind("<Double-1>", self._open_url)

        btn_row = ttk.Frame(p)
        btn_row.pack(fill="x", pady=(6, 0))
        ttk.Button(btn_row, text="Secileni Video'ya Aktar", command=self._use_selected).pack(side="left", padx=(0, 8))
        ttk.Button(btn_row, text="URL'yi Ac", command=self._open_url).pack(side="left")

        self.search_progress = ttk.Progressbar(p, mode="indeterminate")
        self.search_progress.pack(fill="x", pady=(6, 0))

    def _build_create_tab(self):
        p = ttk.Frame(self.tab_create)
        p.pack(fill="both", expand=True, padx=14, pady=10)

        # --- AI Paneli ---
        ai_frame = ttk.LabelFrame(p, text="  Yapay Zeka ile Icerik Olustur", padding=10, style="AI.TLabelframe")
        ai_frame.pack(fill="x", pady=(0, 8))

        ttk.Label(ai_frame, text="Konu / istek:", foreground="#c4b5fd").grid(
            row=0, column=0, sticky="w", padx=(0, 8))
        self.ai_prompt = ttk.Entry(ai_frame, width=55)
        self.ai_prompt.insert(0, "Para kazanma yollari hakkinda viral bir shorts videosu")
        self.ai_prompt.grid(row=0, column=1, sticky="ew", padx=(0, 10))

        ttk.Label(ai_frame, text="Saglayici:").grid(row=0, column=2, sticky="w", padx=(0, 6))
        self.ai_provider_var = tk.StringVar(value=self.config_data.get("ai_provider", "openai"))
        ai_provider_combo = ttk.Combobox(ai_frame, textvariable=self.ai_provider_var,
                                          values=["openai", "gemini", "nim"], width=8, state="readonly")
        ai_provider_combo.grid(row=0, column=3, padx=(0, 10))
        ai_provider_combo.bind("<<ComboboxSelected>>", self._on_provider_change)

        ttk.Button(ai_frame, text="AI ile Olustur", style="AI.TButton",
                   command=self._do_ai_generate).grid(row=0, column=4)
        ai_frame.columnconfigure(1, weight=1)

        nim_row = ttk.Frame(ai_frame)
        nim_row.grid(row=1, column=0, columnspan=5, sticky="w", pady=(6, 0))
        self.nim_label = ttk.Label(nim_row, text="NIM Model:", foreground="#c4b5fd")
        self.nim_label.pack(side="left", padx=(0, 8))
        from ai_helper import NIM_MODELS
        self.nim_model_var = tk.StringVar(value=self.config_data.get("nim_model", NIM_MODELS[0]))
        self.nim_model_combo = ttk.Combobox(nim_row, textvariable=self.nim_model_var,
                                             values=NIM_MODELS, width=42, state="readonly")
        self.nim_model_combo.pack(side="left")
        self._on_provider_change()

        self.ai_status = ttk.Label(ai_frame, text="", foreground="#c4b5fd", font=("Segoe UI", 9))
        self.ai_status.grid(row=2, column=0, columnspan=5, sticky="w", pady=(4, 0))

        self.ai_context_label = ttk.Label(ai_frame,
            text="Ipucu: Trend Ara sekmesinden bir video sec — AI o videonun verisini referans alacak.",
            foreground="#666", font=("Segoe UI", 8))
        self.ai_context_label.grid(row=3, column=0, columnspan=5, sticky="w")

        # --- Video Bilgileri ---
        meta = ttk.LabelFrame(p, text="Video Bilgileri", padding=10)
        meta.pack(fill="x", pady=(0, 8))

        ttk.Label(meta, text="Baslik:").grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.vid_title = ttk.Entry(meta, width=60)
        self.vid_title.grid(row=0, column=1, columnspan=3, sticky="ew", pady=2)

        ttk.Label(meta, text="Kanal adi:").grid(row=1, column=0, sticky="w", padx=(0, 8))
        self.vid_channel = ttk.Entry(meta, width=30)
        self.vid_channel.insert(0, self.config_data.get("channel_name", ""))
        self.vid_channel.grid(row=1, column=1, sticky="ew", pady=2)

        ttk.Label(meta, text="Sure (sn):").grid(row=1, column=2, sticky="w", padx=(10, 6))
        self.vid_duration = ttk.Combobox(meta, values=["15", "20", "25", "30", "45", "55"],
                                         width=6, state="readonly")
        self.vid_duration.set(str(self.config_data.get("video_duration", 30)))
        self.vid_duration.grid(row=1, column=3, sticky="w", pady=2)
        meta.columnconfigure(1, weight=1)

        content_frame = ttk.LabelFrame(p, text="Icerik (her satir bir metin satiri)", padding=8)
        content_frame.pack(fill="both", expand=True, pady=(0, 8))
        self.vid_content = scrolledtext.ScrolledText(content_frame, height=7,
                                                      bg="#1a1a2e", fg="white",
                                                      insertbackground="white",
                                                      font=("Segoe UI", 10),
                                                      relief="flat", borderwidth=0)
        self.vid_content.pack(fill="both", expand=True)

        opt_row = ttk.Frame(p)
        opt_row.pack(fill="x", pady=(0, 6))
        self.tts_var = tk.BooleanVar(value=self.config_data.get("auto_tts", False))
        ttk.Checkbutton(opt_row, text="TTS sesi ekle (gTTS gerekli)", variable=self.tts_var).pack(side="left")

        btn_row = ttk.Frame(p)
        btn_row.pack(fill="x")
        ttk.Button(btn_row, text="Video Olustur", style="Accent.TButton",
                   command=self._do_create).pack(side="left", padx=(0, 10))
        self.preview_btn = ttk.Button(btn_row, text="Videoyu Izle", style="Green.TButton",
                                       command=self._preview_video, state="disabled")
        self.preview_btn.pack(side="left", padx=(0, 10))
        self.create_path_label = ttk.Label(btn_row, text="", foreground="#aaa")
        self.create_path_label.pack(side="left")

        self.create_progress = ttk.Progressbar(p, mode="determinate", maximum=100)
        self.create_progress.pack(fill="x", pady=(8, 0))

        self.create_log = scrolledtext.ScrolledText(p, height=5, bg="#1a1a2e", fg="#ccc",
                                                     font=("Consolas", 9), state="disabled",
                                                     relief="flat")
        self.create_log.pack(fill="x", pady=(6, 0))

    def _build_upload_tab(self):
        p = ttk.Frame(self.tab_upload)
        p.pack(fill="both", expand=True, padx=14, pady=10)

        file_frame = ttk.LabelFrame(p, text="Video Dosyasi", padding=10)
        file_frame.pack(fill="x", pady=(0, 8))
        ttk.Label(file_frame, text="Dosya:").grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.upload_path = ttk.Entry(file_frame, width=55)
        self.upload_path.grid(row=0, column=1, sticky="ew", padx=(0, 8))
        ttk.Button(file_frame, text="Goz At", command=self._browse_video).grid(row=0, column=2)
        ttk.Button(file_frame, text="Olusturulan Videoyu Kullan",
                   command=self._use_created_video).grid(row=0, column=3, padx=(8, 0))
        file_frame.columnconfigure(1, weight=1)

        meta_frame = ttk.LabelFrame(p, text="Video Meta Bilgileri", padding=10)
        meta_frame.pack(fill="x", pady=(0, 8))

        ttk.Label(meta_frame, text="Baslik:").grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.up_title = ttk.Entry(meta_frame, width=60)
        self.up_title.grid(row=0, column=1, columnspan=3, sticky="ew", pady=2)

        ttk.Label(meta_frame, text="Aciklama:").grid(row=1, column=0, sticky="nw", padx=(0, 8))
        self.up_desc = scrolledtext.ScrolledText(meta_frame, height=4, bg="#1a1a2e", fg="white",
                                                  insertbackground="white", font=("Segoe UI", 10),
                                                  relief="flat")
        self.up_desc.grid(row=1, column=1, columnspan=3, sticky="ew", pady=2)
        self.up_desc.insert("1.0", "#Shorts #viral #trending")

        ttk.Label(meta_frame, text="Etiketler (virgul ile):").grid(row=2, column=0, sticky="w", padx=(0, 8))
        self.up_tags = ttk.Entry(meta_frame, width=40)
        self.up_tags.grid(row=2, column=1, sticky="ew", pady=2)

        ttk.Label(meta_frame, text="Gizlilik:").grid(row=2, column=2, sticky="w", padx=(10, 6))
        self.up_privacy = ttk.Combobox(meta_frame, values=["public", "unlisted", "private"],
                                       width=10, state="readonly")
        self.up_privacy.set("public")
        self.up_privacy.grid(row=2, column=3, pady=2)
        meta_frame.columnconfigure(1, weight=1)

        auth_frame = ttk.LabelFrame(p, text="YouTube Kimlik Dogrulama", padding=10)
        auth_frame.pack(fill="x", pady=(0, 8))
        ttk.Button(auth_frame, text="Google Hesabi ile Giris Yap",
                   command=self._do_auth).pack(side="left", padx=(0, 10))
        self.auth_status = ttk.Label(auth_frame, text="Giris yapilmadi", foreground="#ff6666")
        self.auth_status.pack(side="left")

        btn_row = ttk.Frame(p)
        btn_row.pack(fill="x")
        ttk.Button(btn_row, text="YouTube'a Yukle", style="Accent.TButton",
                   command=self._do_upload).pack(side="left", padx=(0, 10))
        self.up_result = ttk.Label(btn_row, text="", foreground="#44ff88")
        self.up_result.pack(side="left")

        self.up_progress = ttk.Progressbar(p, mode="determinate", maximum=100)
        self.up_progress.pack(fill="x", pady=(8, 0))

    def _build_settings_tab(self):
        p = ttk.Frame(self.tab_settings)
        p.pack(fill="both", expand=True, padx=20, pady=16)

        ttk.Label(p, text="YouTube Data API v3 Anahtari:", font=("Segoe UI", 10, "bold")).grid(
            row=0, column=0, sticky="w", pady=4)
        self.cfg_api_key = ttk.Entry(p, width=55, show="*")
        self.cfg_api_key.insert(0, self.config_data.get("api_key", ""))
        self.cfg_api_key.grid(row=0, column=1, sticky="ew", pady=4, padx=(8, 0))

        ttk.Label(p, text="OAuth Client Secrets JSON yolu:", font=("Segoe UI", 10, "bold")).grid(
            row=1, column=0, sticky="w", pady=4)
        self.cfg_secrets = ttk.Entry(p, width=55)
        self.cfg_secrets.insert(0, self.config_data.get("client_secrets", ""))
        self.cfg_secrets.grid(row=1, column=1, sticky="ew", pady=4, padx=(8, 0))
        ttk.Button(p, text="Goz At", command=lambda: self._browse_file(self.cfg_secrets)).grid(
            row=1, column=2, padx=6)

        ttk.Label(p, text="Kanal adi (@ olmadan):").grid(row=2, column=0, sticky="w", pady=4)
        self.cfg_channel = ttk.Entry(p, width=30)
        self.cfg_channel.insert(0, self.config_data.get("channel_name", ""))
        self.cfg_channel.grid(row=2, column=1, sticky="w", pady=4, padx=(8, 0))

        ttk.Label(p, text="Bolge kodu:").grid(row=3, column=0, sticky="w", pady=4)
        self.cfg_region = ttk.Combobox(p, values=["TR", "US", "GB", "DE", "FR", "JP"], width=8, state="readonly")
        self.cfg_region.set(self.config_data.get("region_code", "TR"))
        self.cfg_region.grid(row=3, column=1, sticky="w", pady=4, padx=(8, 0))

        ttk.Label(p, text="Cikti klasoru:").grid(row=4, column=0, sticky="w", pady=4)
        self.cfg_outdir = ttk.Entry(p, width=40)
        self.cfg_outdir.insert(0, self.config_data.get("output_dir", "output_videos"))
        self.cfg_outdir.grid(row=4, column=1, sticky="w", pady=4, padx=(8, 0))

        sep = tk.Frame(p, height=1, bg="#2a2a4e")
        sep.grid(row=5, column=0, columnspan=3, sticky="ew", pady=12)

        tk.Label(p, text="Yapay Zeka Ayarlari", font=("Segoe UI", 11, "bold"),
                 bg="#0f0f1a", fg="#7c3aed").grid(row=6, column=0, columnspan=3, sticky="w", pady=(0, 6))

        ttk.Label(p, text="AI Saglayici:").grid(row=7, column=0, sticky="w", pady=4)
        self.cfg_ai_provider = ttk.Combobox(p, values=["openai", "gemini", "nim"],
                                             width=12, state="readonly")
        self.cfg_ai_provider.set(self.config_data.get("ai_provider", "openai"))
        self.cfg_ai_provider.grid(row=7, column=1, sticky="w", pady=4, padx=(8, 0))

        ttk.Label(p, text="AI API Anahtari:", font=("Segoe UI", 10, "bold")).grid(
            row=8, column=0, sticky="w", pady=4)
        self.cfg_ai_key = ttk.Entry(p, width=55, show="*")
        self.cfg_ai_key.insert(0, self.config_data.get("ai_api_key", ""))
        self.cfg_ai_key.grid(row=8, column=1, sticky="ew", pady=4, padx=(8, 0))

        from ai_helper import NIM_MODELS
        ttk.Label(p, text="NIM Model:").grid(row=9, column=0, sticky="w", pady=4)
        self.cfg_nim_model = ttk.Combobox(p, values=NIM_MODELS, width=45, state="readonly")
        self.cfg_nim_model.set(self.config_data.get("nim_model", NIM_MODELS[0]))
        self.cfg_nim_model.grid(row=9, column=1, sticky="w", pady=4, padx=(8, 0))

        ai_info = ttk.Label(p,
            text="OpenAI: platform.openai.com/api-keys   |   Gemini: aistudio.google.com/apikey   |   NIM: build.nvidia.com",
            foreground="#666", font=("Segoe UI", 8))
        ai_info.grid(row=10, column=1, sticky="w", padx=(8, 0))

        ttk.Button(p, text="Ayarlari Kaydet", style="Accent.TButton",
                   command=self._save_settings).grid(row=11, column=0, columnspan=2,
                                                      sticky="w", pady=14)
        p.columnconfigure(1, weight=1)

    def _log_create(self, msg: str):
        self.create_log.configure(state="normal")
        self.create_log.insert("end", msg + "\n")
        self.create_log.see("end")
        self.create_log.configure(state="disabled")

    def _set_status(self, msg: str):
        self.status_var.set(msg)

    def _do_search(self):
        api_key = self.config_data.get("api_key", "").strip()
        if not api_key:
            messagebox.showwarning("API Anahtari", "Lutfen Ayarlar sekmesinden API anahtarini girin.")
            return

        def worker():
            self.search_progress.start(12)
            self._set_status("Arama yapiliyor...")
            try:
                from youtube_api import YouTubeAPI
                api = YouTubeAPI(api_key)
                n = int(self.result_count.get())
                q = self.search_query.get().strip()
                region = self.config_data.get("region_code", "TR")
                lang = self.config_data.get("language", "tr")

                if self.trend_mode.get():
                    results = api.get_trending_videos(region_code=region, max_results=n)
                else:
                    results = api.search_trending_shorts(query=q, max_results=n,
                                                         region_code=region, language=lang)
                self.trending_results = results
                self.after(0, self._populate_tree, results)
                self._set_status(f"{len(results)} sonuc bulundu.")
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Hata", str(e)))
                self._set_status("Hata olustu.")
            finally:
                self.after(0, self.search_progress.stop)

        threading.Thread(target=worker, daemon=True).start()

    def _populate_tree(self, results: List[Dict]):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for v in results:
            self.tree.insert("", "end", values=(
                v["title"],
                v["channel"],
                f"{v['view_count']:,}",
                f"{v['like_count']:,}",
                v["url"],
            ))

    def _on_tree_select(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        idx = self.tree.index(sel[0])
        if 0 <= idx < len(self.trending_results):
            self.selected_video = self.trending_results[idx]

    def _open_url(self, _event=None):
        if self.selected_video:
            webbrowser.open(self.selected_video.get("url", ""))

    def _use_selected(self):
        if not self.selected_video:
            messagebox.showinfo("Bilgi", "Lutfen bir video secin.")
            return
        v = self.selected_video
        self.vid_title.delete(0, "end")
        self.vid_title.insert(0, v.get("title", ""))
        self.vid_content.delete("1.0", "end")
        desc = v.get("description", "")
        sentences = [s.strip() for s in desc.replace("\n", ". ").split(".") if len(s.strip()) > 15]
        self.vid_content.insert("1.0", "\n".join(sentences[:6]))
        self.up_title.delete(0, "end")
        self.up_title.insert(0, v.get("title", ""))
        tags = v.get("tags", [])
        self.up_tags.delete(0, "end")
        self.up_tags.insert(0, ", ".join(tags[:8]))
        self._set_status("Video bilgileri aktarildi.")

    def _on_provider_change(self, _event=None):
        is_nim = self.ai_provider_var.get() == "nim"
        state = "normal" if is_nim else "disabled"
        self.nim_label.configure(foreground="#c4b5fd" if is_nim else "#444")
        self.nim_model_combo.configure(state="readonly" if is_nim else "disabled")

    def _do_ai_generate(self):
        prompt = self.ai_prompt.get().strip()
        if not prompt:
            messagebox.showwarning("Eksik", "Lutfen bir konu girin.")
            return
        ai_key = self.config_data.get("ai_api_key", "").strip()
        if not ai_key:
            messagebox.showwarning("AI Anahtari", "Ayarlar sekmesinden AI API anahtarini girin.")
            return
        provider = self.ai_provider_var.get()
        nim_model = self.nim_model_var.get()
        video_context = dict(self.selected_video) if self.selected_video else None

        status_parts = [f"[{provider.upper()}]"]
        if provider == "nim":
            status_parts.append(f"({nim_model.split('/')[-1]})")
        if video_context:
            status_parts.append(f"Referans: '{video_context.get('title', '')[:40]}...'")
        self.ai_status.configure(
            text="  ".join(status_parts) + "  —  AI icerik olusturuyor...",
            foreground="#c4b5fd"
        )
        self._set_status("AI ile icerik olusturuluyor...")

        def worker():
            try:
                from ai_helper import AIHelper
                helper = AIHelper(provider=provider, api_key=ai_key, nim_model=nim_model)
                result = helper.generate_video_content(prompt, video_context=video_context)

                def apply():
                    self.vid_title.delete(0, "end")
                    self.vid_title.insert(0, result.get("title", ""))
                    self.vid_content.delete("1.0", "end")
                    self.vid_content.insert("1.0", "\n".join(result.get("content_lines", [])))
                    self.up_title.delete(0, "end")
                    self.up_title.insert(0, result.get("title", ""))
                    self.up_desc.delete("1.0", "end")
                    desc = result.get("description", "")
                    tags = result.get("hashtags", "")
                    self.up_desc.insert("1.0", f"{desc}\n\n{tags}")
                    self.ai_status.configure(
                        text="AI icerik basariyla olusturuldu!",
                        foreground="#44ff88"
                    )
                    self._set_status("AI icerik olusturuldu.")

                self.after(0, apply)
            except Exception as e:
                self.after(0, lambda: self.ai_status.configure(
                    text=f"Hata: {str(e)[:90]}", foreground="#ff6666"))
                self.after(0, lambda: self._set_status("AI hatasi: " + str(e)))

        threading.Thread(target=worker, daemon=True).start()

    def _do_create(self):
        title = self.vid_title.get().strip()
        if not title:
            messagebox.showwarning("Eksik Bilgi", "Lutfen bir baslik girin.")
            return
        content = self.vid_content.get("1.0", "end").strip()
        channel = self.vid_channel.get().strip()
        duration = int(self.vid_duration.get())
        out_dir = self.config_data.get("output_dir", "output_videos")
        use_tts = self.tts_var.get()

        self.create_progress["value"] = 0
        self.create_log.configure(state="normal")
        self.create_log.delete("1.0", "end")
        self.create_log.configure(state="disabled")
        self.created_video_path = None
        self.create_path_label.configure(text="")
        self.preview_btn.configure(state="disabled")

        def worker():
            try:
                from video_creator import VideoCreator
                creator = VideoCreator(output_dir=out_dir)

                def cb(cur, total, msg):
                    pct = int(cur / max(total, 1) * 100)
                    self.after(0, lambda: self.create_progress.configure(value=pct))
                    self.after(0, lambda: self._log_create(msg))
                    self.after(0, lambda: self._set_status(msg))

                video_data = dict(self.selected_video) if self.selected_video else {}
                video_data["title"] = title
                path = creator.create_video(
                    video_data=video_data,
                    custom_title=title,
                    custom_content=content,
                    channel_name=channel,
                    duration=duration,
                    callback=cb,
                )

                if use_tts:
                    self.after(0, lambda: self._log_create("TTS sesi ekleniyor..."))
                    tts_text = title + ". " + content.replace("\n", ". ")
                    path = creator.add_tts_audio(path, tts_text)
                    self.after(0, lambda: self._log_create("TTS tamamlandi."))

                self.created_video_path = path
                self.after(0, lambda: self.create_path_label.configure(
                    text=f"Kaydedildi: {Path(path).name}", foreground="#44ff88"))
                self.after(0, lambda: self.create_progress.configure(value=100))
                self.after(0, lambda: self._set_status("Video olusturuldu: " + path))
                self.after(0, lambda: self._log_create(f"Basari! Dosya: {path}"))
                self.after(0, lambda: self.preview_btn.configure(state="normal"))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Hata", str(e)))
                self.after(0, lambda: self._set_status("Hata: " + str(e)))
                self.after(0, lambda: self._log_create("HATA: " + str(e)))

        threading.Thread(target=worker, daemon=True).start()

    def _preview_video(self):
        if not self.created_video_path or not os.path.exists(self.created_video_path):
            messagebox.showinfo("Bilgi", "Once bir video olusturun.")
            return
        os.startfile(self.created_video_path)

    def _browse_video(self):
        path = filedialog.askopenfilename(filetypes=[("MP4 Dosyalari", "*.mp4"), ("Tum Dosyalar", "*.*")])
        if path:
            self.upload_path.delete(0, "end")
            self.upload_path.insert(0, path)

    def _use_created_video(self):
        if self.created_video_path:
            self.upload_path.delete(0, "end")
            self.upload_path.insert(0, self.created_video_path)
        else:
            messagebox.showinfo("Bilgi", "Henuz olusturulmus bir video yok.")

    def _do_auth(self):
        secrets = self.config_data.get("client_secrets", "").strip()
        if not secrets:
            messagebox.showwarning("Eksik Bilgi", "Ayarlar sekmesinden Client Secrets dosya yolunu girin.")
            return

        def worker():
            try:
                from youtube_uploader import YouTubeUploader
                uploader = YouTubeUploader(secrets)
                uploader.authenticate()
                self.after(0, lambda: self.auth_status.configure(
                    text="Giris basarili!", foreground="#44ff88"))
                self.after(0, lambda: self._set_status("YouTube kimlik dogrulama basarili."))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Kimlik Dogrulama Hatasi", str(e)))
                self.after(0, lambda: self.auth_status.configure(
                    text="Hata: " + str(e)[:60], foreground="#ff6666"))

        threading.Thread(target=worker, daemon=True).start()

    def _do_upload(self):
        path = self.upload_path.get().strip()
        title = self.up_title.get().strip()
        desc = self.up_desc.get("1.0", "end").strip()
        tags_raw = self.up_tags.get().strip()
        tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
        privacy = self.up_privacy.get()
        secrets = self.config_data.get("client_secrets", "").strip()

        if not path or not os.path.exists(path):
            messagebox.showwarning("Eksik", "Gecerli bir video dosyasi secin.")
            return
        if not title:
            messagebox.showwarning("Eksik", "Baslik alanini doldurun.")
            return
        if not secrets:
            messagebox.showwarning("Eksik", "Ayarlar sekmesinden Client Secrets yolunu girin.")
            return

        self.up_progress["value"] = 0
        self.up_result.configure(text="")

        def worker():
            try:
                from youtube_uploader import YouTubeUploader
                uploader = YouTubeUploader(secrets)
                url = uploader.upload_short(
                    video_path=path,
                    title=title,
                    description=desc,
                    tags=tags,
                    privacy=privacy,
                    callback=lambda pct: self.after(0, lambda: self.up_progress.configure(value=pct)),
                )
                if url:
                    self.after(0, lambda: self.up_result.configure(
                        text=f"Yuklendi: {url}", foreground="#44ff88"))
                    self.after(0, lambda: self._set_status("Video yuklendi: " + url))
                    self.after(0, lambda: webbrowser.open(url))
                else:
                    self.after(0, lambda: self.up_result.configure(
                        text="Yukleme basarisiz.", foreground="#ff6666"))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Yukleme Hatasi", str(e)))
                self.after(0, lambda: self._set_status("Hata: " + str(e)))

        threading.Thread(target=worker, daemon=True).start()

    def _save_settings(self):
        self.config_data["api_key"] = self.cfg_api_key.get().strip()
        self.config_data["client_secrets"] = self.cfg_secrets.get().strip()
        self.config_data["channel_name"] = self.cfg_channel.get().strip()
        self.config_data["region_code"] = self.cfg_region.get()
        self.config_data["output_dir"] = self.cfg_outdir.get().strip()
        self.config_data["ai_provider"] = self.cfg_ai_provider.get()
        self.config_data["ai_api_key"] = self.cfg_ai_key.get().strip()
        self.config_data["nim_model"] = self.cfg_nim_model.get()
        save_config(self.config_data)
        self.vid_channel.delete(0, "end")
        self.vid_channel.insert(0, self.config_data["channel_name"])
        messagebox.showinfo("Kaydedildi", "Ayarlar basariyla kaydedildi.")

    def _browse_file(self, entry: ttk.Entry):
        path = filedialog.askopenfilename(filetypes=[("JSON Dosyalari", "*.json"), ("Tum Dosyalar", "*.*")])
        if path:
            entry.delete(0, "end")
            entry.insert(0, path)


if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    app = App()
    app.mainloop()
