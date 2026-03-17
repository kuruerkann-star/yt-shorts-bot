import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import os
from pathlib import Path


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Video Araçları")
        self.geometry("860x660")
        self.minsize(720, 520)
        self.configure(bg="#0f0f1a")
        self._setup_styles()
        self._build_ui()

    def _setup_styles(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        BG, FG = "#0f0f1a", "#ffffff"
        ACC = "#ff3c78"
        ENT = "#1a1a2e"
        s.configure(".", background=BG, foreground=FG, font=("Segoe UI", 10))
        s.configure("TFrame", background=BG)
        s.configure("TLabel", background=BG, foreground=FG)
        s.configure("TLabelframe", background=BG, foreground=ACC, bordercolor=ACC)
        s.configure("TLabelframe.Label", background=BG, foreground=ACC,
                    font=("Segoe UI", 10, "bold"))
        s.configure("TNotebook", background=BG, borderwidth=0)
        s.configure("TNotebook.Tab", background=ENT, foreground=FG, padding=[18, 8])
        s.map("TNotebook.Tab",
              background=[("selected", ACC)], foreground=[("selected", FG)])
        s.configure("TEntry", fieldbackground=ENT, foreground=FG, insertcolor=FG)
        s.configure("TCombobox", fieldbackground=ENT, foreground=FG, background=ENT)
        s.map("TCombobox", fieldbackground=[("readonly", ENT)])
        s.configure("Accent.TButton", background=ACC, foreground=FG,
                    font=("Segoe UI", 10, "bold"), padding=[12, 6])
        s.map("Accent.TButton", background=[("active", "#ff6090")])
        s.configure("Green.TButton", background="#16a34a", foreground=FG,
                    font=("Segoe UI", 10, "bold"), padding=[12, 6])
        s.map("Green.TButton", background=[("active", "#22c55e")])
        s.configure("TButton", background=ENT, foreground=FG, padding=[10, 5])
        s.map("TButton", background=[("active", "#2a2a4e")])
        s.configure("Horizontal.TProgressbar", troughcolor=ENT, background=ACC)

    def _build_ui(self):
        hdr = ttk.Frame(self)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Video Araçları",
                 font=("Segoe UI", 17, "bold"), bg="#0f0f1a", fg="#ff3c78"
                 ).pack(side="left", padx=18, pady=10)
        tk.Label(hdr, text="Video Birleştir  •  Ses Ekle",
                 font=("Segoe UI", 9), bg="#0f0f1a", fg="#666"
                 ).pack(side="left")
        tk.Frame(self, height=2, bg="#ff3c78").pack(fill="x")

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)

        self.tab_merge  = ttk.Frame(nb)
        self.tab_audio  = ttk.Frame(nb)
        self.tab_trends = ttk.Frame(nb)
        nb.add(self.tab_merge,  text="  Video Birleştir  ")
        nb.add(self.tab_audio,  text="  Müzik Ekle  ")
        nb.add(self.tab_trends, text="  Trend Shorts  ")

        self._build_merge_tab()
        self._build_audio_tab()
        self._build_trends_tab()

        self.status_var = tk.StringVar(value="Hazır")
        tk.Label(self, textvariable=self.status_var, bg="#1a1a2e", fg="#aaa",
                 anchor="w", padx=10, font=("Segoe UI", 9)
                 ).pack(fill="x", side="bottom")

    # ── Video Birleştir ──────────────────────────────────────────────────────
    def _build_merge_tab(self):
        p = ttk.Frame(self.tab_merge)
        p.pack(fill="both", expand=True, padx=16, pady=12)

        lf = ttk.LabelFrame(p, text="Birleştirilecek Videolar (Sırayla)", padding=10)
        lf.pack(fill="both", expand=True, pady=(0, 8))

        list_frame = ttk.Frame(lf)
        list_frame.pack(fill="both", expand=True)

        self._merge_listbox = tk.Listbox(
            list_frame, bg="#1a1a2e", fg="#fff", selectbackground="#ff3c78",
            font=("Segoe UI", 9), height=8, relief="flat", activestyle="none")
        self._merge_listbox.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(list_frame, orient="vertical",
                           command=self._merge_listbox.yview)
        sb.pack(side="right", fill="y")
        self._merge_listbox.configure(yscrollcommand=sb.set)

        btn_row = ttk.Frame(lf)
        btn_row.pack(fill="x", pady=(6, 0))
        ttk.Button(btn_row, text="+ Video Ekle",
                   command=self._merge_add_file).pack(side="left", padx=(0, 6))
        ttk.Button(btn_row, text="Yukarı ↑",
                   command=self._merge_move_up).pack(side="left", padx=(0, 6))
        ttk.Button(btn_row, text="Aşağı ↓",
                   command=self._merge_move_down).pack(side="left", padx=(0, 6))
        ttk.Button(btn_row, text="Sil",
                   command=self._merge_remove).pack(side="left")

        ef = ttk.LabelFrame(p, text="Geçiş Efekti Ayarları", padding=10)
        ef.pack(fill="x", pady=(0, 8))

        ttk.Label(ef, text="Efekt:").grid(row=0, column=0, sticky="w", padx=(0, 8))
        from video_editor import TRANSITIONS
        self._merge_effect_cb = ttk.Combobox(ef, values=TRANSITIONS,
                                              width=20, state="readonly")
        self._merge_effect_cb.set(TRANSITIONS[0])
        self._merge_effect_cb.grid(row=0, column=1, sticky="w", pady=4)

        ttk.Label(ef, text="Süre (sn):").grid(row=0, column=2, sticky="w", padx=(16, 8))
        self._merge_dur_var = tk.StringVar(value="0.5")
        ttk.Spinbox(ef, from_=0.1, to=2.0, increment=0.1,
                    textvariable=self._merge_dur_var, width=6
                    ).grid(row=0, column=3, sticky="w", pady=4)

        ttk.Label(ef, text="Çıktı:").grid(row=1, column=0, sticky="w", padx=(0, 8))
        self._merge_out_entry = ttk.Entry(ef, width=48)
        self._merge_out_entry.insert(0, "output_videos/merged_output.mp4")
        self._merge_out_entry.grid(row=1, column=1, columnspan=3, sticky="ew", pady=4)
        ef.columnconfigure(1, weight=1)

        act = ttk.Frame(p)
        act.pack(fill="x", pady=(0, 6))
        ttk.Button(act, text="Birleştir", style="Green.TButton",
                   command=self._merge_start).pack(side="left", padx=(0, 8))
        self._merge_preview_btn = ttk.Button(act, text="▶  İzle", state="disabled",
                                              command=self._merge_preview)
        self._merge_preview_btn.pack(side="left", padx=(0, 6))
        self._merge_save_btn = ttk.Button(act, text="Masaüstüne İndir", state="disabled",
                                           command=self._merge_save_desktop)
        self._merge_save_btn.pack(side="left")

        self._merge_progress = ttk.Progressbar(p, mode="determinate", maximum=100)
        self._merge_progress.pack(fill="x", pady=(0, 4))
        self._merge_log = scrolledtext.ScrolledText(
            p, height=5, bg="#1a1a2e", fg="#ccc",
            font=("Consolas", 8), state="disabled", relief="flat")
        self._merge_log.pack(fill="both", expand=False)
        self._merge_out_path = None

    def _merge_add_file(self):
        paths = filedialog.askopenfilenames(
            title="Video Seç",
            filetypes=[("Video", "*.mp4 *.avi *.mov *.mkv *.webm"), ("Tümü", "*.*")])
        for p in paths:
            self._merge_listbox.insert("end", p)

    def _merge_move_up(self):
        sel = self._merge_listbox.curselection()
        if not sel or sel[0] == 0:
            return
        i = sel[0]; val = self._merge_listbox.get(i)
        self._merge_listbox.delete(i)
        self._merge_listbox.insert(i - 1, val)
        self._merge_listbox.selection_set(i - 1)

    def _merge_move_down(self):
        sel = self._merge_listbox.curselection()
        if not sel or sel[0] == self._merge_listbox.size() - 1:
            return
        i = sel[0]; val = self._merge_listbox.get(i)
        self._merge_listbox.delete(i)
        self._merge_listbox.insert(i + 1, val)
        self._merge_listbox.selection_set(i + 1)

    def _merge_remove(self):
        sel = self._merge_listbox.curselection()
        if sel:
            self._merge_listbox.delete(sel[0])

    def _merge_preview(self):
        path = self._merge_out_path
        if path:
            path = os.path.abspath(path)
            if os.path.exists(path):
                os.startfile(path)
            else:
                messagebox.showerror("Bulunamadı", f"Dosya yok:\n{path}")

    def _merge_save_desktop(self):
        import shutil
        path = self._merge_out_path
        if not path or not os.path.exists(path):
            messagebox.showerror("Dosya Yok", "Önce video birleştirin.")
            return
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        base, ext = os.path.splitext(os.path.basename(path))
        dest = os.path.join(desktop, os.path.basename(path))
        c = 1
        while os.path.exists(dest):
            dest = os.path.join(desktop, f"{base}_{c}{ext}"); c += 1
        shutil.copy2(path, dest)
        messagebox.showinfo("Kaydedildi", f"Masaüstüne kaydedildi:\n{dest}")

    def _merge_log_msg(self, msg):
        self._merge_log.configure(state="normal")
        self._merge_log.insert("end", msg + "\n")
        self._merge_log.see("end")
        self._merge_log.configure(state="disabled")

    def _merge_start(self):
        paths = list(self._merge_listbox.get(0, "end"))
        if len(paths) < 2:
            messagebox.showwarning("Yetersiz Video", "En az 2 video ekleyin.")
            return
        effect   = self._merge_effect_cb.get()
        out_path = self._merge_out_entry.get().strip() or "output_videos/merged_output.mp4"
        try:
            dur = float(self._merge_dur_var.get())
        except ValueError:
            dur = 0.5
        os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
        self._merge_progress["value"] = 0
        self._merge_preview_btn.configure(state="disabled")
        self._merge_save_btn.configure(state="disabled")
        self._merge_out_path = None
        self._merge_log.configure(state="normal")
        self._merge_log.delete("1.0", "end")
        self._merge_log.configure(state="disabled")
        self.status_var.set("Videolar birleştiriliyor...")

        def cb(cur, total, msg):
            pct = int(cur / max(total, 1) * 100)
            self.after(0, lambda: self._merge_progress.configure(value=pct))
            self.after(0, lambda: self._merge_log_msg(msg))
            self.after(0, lambda: self.status_var.set(msg))

        def worker():
            try:
                from video_editor import merge_videos
                result = merge_videos(paths, out_path, transition=effect,
                                      transition_sec=dur, callback=cb)
                def _done(r=result):
                    self._merge_out_path = os.path.abspath(r)
                    self._merge_progress.configure(value=100)
                    self._merge_log_msg(f"Tamamlandı → {self._merge_out_path}")
                    self.status_var.set("Birleştirme tamamlandı.")
                    self._merge_preview_btn.configure(state="normal")
                    self._merge_save_btn.configure(state="normal")
                self.after(0, _done)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Hata", str(e)))
                self.after(0, lambda: self._merge_log_msg("HATA: " + str(e)))
                self.after(0, lambda: self.status_var.set("Hata oluştu."))
        threading.Thread(target=worker, daemon=True).start()

    # ── Ses Ekle ────────────────────────────────────────────────────────────
    def _build_audio_tab(self):
        p = ttk.Frame(self.tab_audio)
        p.pack(fill="both", expand=True, padx=16, pady=12)

        vf = ttk.LabelFrame(p, text="Video Dosyası", padding=10)
        vf.pack(fill="x", pady=(0, 8))
        self._audio_video_entry = ttk.Entry(vf, width=60)
        self._audio_video_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ttk.Button(vf, text="Seç...",
                   command=self._audio_pick_video).pack(side="left")

        sf = ttk.LabelFrame(p, text="Müzik Kaynağı", padding=10)
        sf.pack(fill="x", pady=(0, 8))

        self._audio_source_var = tk.StringVar(value="youtube")
        rb = ttk.Frame(sf)
        rb.pack(anchor="w", pady=(0, 6))
        ttk.Radiobutton(rb, text="YouTube URL", variable=self._audio_source_var,
                        value="youtube", command=self._audio_toggle).pack(side="left", padx=(0, 20))
        ttk.Radiobutton(rb, text="Yerel Dosya", variable=self._audio_source_var,
                        value="local", command=self._audio_toggle).pack(side="left")

        self._audio_yt_frame = ttk.Frame(sf)
        self._audio_yt_frame.pack(fill="x")
        ttk.Label(self._audio_yt_frame, text="URL:").pack(side="left", padx=(0, 8))
        self._audio_yt_entry = ttk.Entry(self._audio_yt_frame, width=60)
        self._audio_yt_entry.pack(side="left", fill="x", expand=True)

        self._audio_local_frame = ttk.Frame(sf)
        ttk.Label(self._audio_local_frame, text="Dosya:").pack(side="left", padx=(0, 8))
        self._audio_local_entry = ttk.Entry(self._audio_local_frame, width=50)
        self._audio_local_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ttk.Button(self._audio_local_frame, text="Seç...",
                   command=self._audio_pick_local).pack(side="left")

        opt = ttk.Frame(sf)
        opt.pack(fill="x", pady=(8, 0))
        ttk.Label(opt, text="Müzik seviyesi:").pack(side="left", padx=(0, 6))
        self._audio_vol_var = tk.StringVar(value="1.0")
        ttk.Spinbox(opt, from_=0.1, to=3.0, increment=0.1,
                    textvariable=self._audio_vol_var, width=5).pack(side="left", padx=(0, 16))
        self._audio_loop_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(opt, text="Müzik döngüye girsin",
                        variable=self._audio_loop_var).pack(side="left")

        of = ttk.LabelFrame(p, text="Çıktı Dosyası", padding=10)
        of.pack(fill="x", pady=(0, 8))
        self._audio_out_entry = ttk.Entry(of, width=60)
        self._audio_out_entry.insert(0, "output_videos/video_with_audio.mp4")
        self._audio_out_entry.pack(side="left", fill="x", expand=True)

        act = ttk.Frame(p)
        act.pack(fill="x", pady=(0, 6))
        ttk.Button(act, text="Müzik Ekle", style="Green.TButton",
                   command=self._audio_start).pack(side="left", padx=(0, 8))
        self._audio_preview_btn = ttk.Button(act, text="▶  İzle", state="disabled",
                                              command=self._audio_preview)
        self._audio_preview_btn.pack(side="left", padx=(0, 6))
        self._audio_save_btn = ttk.Button(act, text="Masaüstüne İndir", state="disabled",
                                           command=self._audio_save_desktop)
        self._audio_save_btn.pack(side="left")

        self._audio_progress = ttk.Progressbar(p, mode="determinate", maximum=100)
        self._audio_progress.pack(fill="x", pady=(0, 4))
        self._audio_log = scrolledtext.ScrolledText(
            p, height=6, bg="#1a1a2e", fg="#ccc",
            font=("Consolas", 8), state="disabled", relief="flat")
        self._audio_log.pack(fill="both", expand=True)
        self._audio_out_path = None

    def _audio_toggle(self):
        if self._audio_source_var.get() == "youtube":
            self._audio_local_frame.pack_forget()
            self._audio_yt_frame.pack(fill="x")
        else:
            self._audio_yt_frame.pack_forget()
            self._audio_local_frame.pack(fill="x")

    def _audio_pick_video(self):
        path = filedialog.askopenfilename(
            title="Video Seç",
            filetypes=[("Video", "*.mp4 *.avi *.mov *.mkv *.webm"), ("Tümü", "*.*")])
        if path:
            self._audio_video_entry.delete(0, "end")
            self._audio_video_entry.insert(0, path)

    def _audio_pick_local(self):
        path = filedialog.askopenfilename(
            title="Ses Dosyası Seç",
            filetypes=[("Ses", "*.mp3 *.wav *.aac *.ogg *.m4a"), ("Tümü", "*.*")])
        if path:
            self._audio_local_entry.delete(0, "end")
            self._audio_local_entry.insert(0, path)

    def _audio_log_msg(self, msg):
        self._audio_log.configure(state="normal")
        self._audio_log.insert("end", msg + "\n")
        self._audio_log.see("end")
        self._audio_log.configure(state="disabled")

    def _audio_preview(self):
        path = self._audio_out_path
        if path and os.path.exists(path):
            os.startfile(path)

    def _audio_save_desktop(self):
        import shutil
        path = self._audio_out_path
        if not path or not os.path.exists(path):
            messagebox.showerror("Dosya Yok", "Önce ses ekleyin.")
            return
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        base, ext = os.path.splitext(os.path.basename(path))
        dest = os.path.join(desktop, os.path.basename(path))
        c = 1
        while os.path.exists(dest):
            dest = os.path.join(desktop, f"{base}_{c}{ext}"); c += 1
        shutil.copy2(path, dest)
        messagebox.showinfo("Kaydedildi", f"Masaüstüne kaydedildi:\n{dest}")

    def _audio_start(self):
        video_path = self._audio_video_entry.get().strip()
        if not video_path or not os.path.exists(video_path):
            messagebox.showwarning("Video Yok", "Geçerli bir video dosyası seçin.")
            return
        source  = self._audio_source_var.get()
        yt_url  = self._audio_yt_entry.get().strip()
        local_f = self._audio_local_entry.get().strip()
        out_path = self._audio_out_entry.get().strip() or "output_videos/video_with_audio.mp4"
        try:
            volume = float(self._audio_vol_var.get())
        except ValueError:
            volume = 1.0
        loop = self._audio_loop_var.get()

        if source == "youtube" and not yt_url:
            messagebox.showwarning("URL Eksik", "YouTube URL'si girin.")
            return
        if source == "local" and (not local_f or not os.path.exists(local_f)):
            messagebox.showwarning("Dosya Yok", "Geçerli bir ses dosyası seçin.")
            return

        os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
        self._audio_progress["value"] = 0
        self._audio_preview_btn.configure(state="disabled")
        self._audio_save_btn.configure(state="disabled")
        self._audio_out_path = None
        self._audio_log.configure(state="normal")
        self._audio_log.delete("1.0", "end")
        self._audio_log.configure(state="disabled")
        self.status_var.set("Müzik ekleniyor...")

        def cb(cur, total, msg):
            pct = int(cur / max(total, 1) * 100)
            self.after(0, lambda: self._audio_progress.configure(value=pct))
            self.after(0, lambda: self._audio_log_msg(msg))
            self.after(0, lambda: self.status_var.set(msg))

        def worker():
            try:
                from video_editor import download_youtube_audio, add_audio_to_video
                audio_file = local_f
                if source == "youtube":
                    audio_file = download_youtube_audio(
                        yt_url, "output_videos/audio_cache", callback=cb)
                result = add_audio_to_video(video_path, audio_file, out_path,
                                            volume=volume, loop_audio=loop, callback=cb)
                def _done(r=result):
                    self._audio_out_path = os.path.abspath(r)
                    self._audio_progress.configure(value=100)
                    self._audio_log_msg(f"Tamamlandı → {self._audio_out_path}")
                    self.status_var.set("Müzik ekleme tamamlandı.")
                    self._audio_preview_btn.configure(state="normal")
                    self._audio_save_btn.configure(state="normal")
                self.after(0, _done)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Hata", str(e)))
                self.after(0, lambda: self._audio_log_msg("HATA: " + str(e)))
                self.after(0, lambda: self.status_var.set("Hata oluştu."))
        threading.Thread(target=worker, daemon=True).start()


    # ── Trend Shorts ─────────────────────────────────────────────────────────
    def _build_trends_tab(self):
        from trends_fetcher import CATEGORIES
        p = ttk.Frame(self.tab_trends)
        p.pack(fill="both", expand=True, padx=16, pady=12)

        # Üst kontrol satırı
        ctrl = ttk.Frame(p)
        ctrl.pack(fill="x", pady=(0, 8))

        ttk.Label(ctrl, text="Kategori:").pack(side="left", padx=(0, 8))
        self._tr_cat = ttk.Combobox(ctrl, values=list(CATEGORIES.keys()),
                                    width=18, state="readonly")
        self._tr_cat.set("Genel Trend")
        self._tr_cat.pack(side="left", padx=(0, 8))
        self._tr_cat.bind("<<ComboboxSelected>>", self._tr_on_cat)

        ttk.Label(ctrl, text="Özel arama:").pack(side="left", padx=(0, 6))
        self._tr_search = ttk.Entry(ctrl, width=28)
        self._tr_search.pack(side="left", padx=(0, 8))
        self._tr_search.configure(state="disabled")

        ttk.Label(ctrl, text="Sonuç:").pack(side="left", padx=(0, 4))
        self._tr_count = ttk.Combobox(ctrl, values=["10","20","30","50"],
                                      width=5, state="readonly")
        self._tr_count.set("20")
        self._tr_count.pack(side="left", padx=(0, 8))

        ttk.Button(ctrl, text="Ara 🔍", style="Green.TButton",
                   command=self._tr_fetch).pack(side="left")

        # Tablo başlıkları
        cols = ("rank","title","views","channel","duration","url")
        hdr  = ttk.Frame(p)
        hdr.pack(fill="x")
        self._tr_tree = ttk.Treeview(
            p, columns=cols, show="headings",
            selectmode="browse", height=16)

        for col, txt, w in [
            ("rank",     "#",         40),
            ("title",    "Başlık",   320),
            ("views",    "İzlenme",   90),
            ("channel",  "Kanal",    160),
            ("duration", "Süre",      55),
            ("url",      "URL",        0),
        ]:
            self._tr_tree.heading(col, text=txt)
            self._tr_tree.column(col, width=w, minwidth=w,
                                 stretch=(col == "title"))

        self._tr_tree.column("url", width=0, minwidth=0, stretch=False)
        vsb = ttk.Scrollbar(p, orient="vertical",
                            command=self._tr_tree.yview)
        self._tr_tree.configure(yscrollcommand=vsb.set)
        self._tr_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # Satır renklendirme
        self._tr_tree.tag_configure("odd",  background="#1a1a2e")
        self._tr_tree.tag_configure("even", background="#16213e")
        self._tr_tree.bind("<Double-1>", self._tr_open_url)

        # Alt butonlar
        bot = ttk.Frame(p)
        bot.pack(fill="x", pady=(6, 0), side="bottom")
        ttk.Button(bot, text="▶  Tarayıcıda Aç",
                   command=self._tr_open_url).pack(side="left", padx=(0, 8))
        ttk.Button(bot, text="⬇  URL'yi Müzik Ekle'ye Kopyala",
                   command=self._tr_copy_to_audio).pack(side="left", padx=(0, 8))
        ttk.Button(bot, text="⬇  İndir (MP4)",
                   command=self._tr_download).pack(side="left")

        self._tr_progress = ttk.Progressbar(p, mode="determinate", maximum=100)
        self._tr_progress.pack(fill="x", pady=(4, 0), side="bottom")

        self._tr_results = []

    def _tr_on_cat(self, _=None):
        if self._tr_cat.get() == "Özel Arama":
            self._tr_search.configure(state="normal")
        else:
            self._tr_search.configure(state="disabled")

    def _tr_fetch(self):
        from trends_fetcher import CATEGORIES, fetch_trending
        cat = self._tr_cat.get()
        query = CATEGORIES.get(cat)
        if query is None:
            custom = self._tr_search.get().strip()
            if not custom:
                messagebox.showwarning("Arama Boş", "Özel arama terimi girin.")
                return
            query = f"ytsearchdate40:{custom} #shorts"

        max_r = int(self._tr_count.get())

        # Listeyi temizle
        for row in self._tr_tree.get_children():
            self._tr_tree.delete(row)
        self._tr_results = []
        self._tr_progress["value"] = 0
        self.status_var.set("Trend shortlar aranıyor...")

        def cb(cur, total, msg):
            pct = int(cur / max(total, 1) * 100)
            self.after(0, lambda: self._tr_progress.configure(value=pct))
            self.after(0, lambda: self.status_var.set(msg))

        def worker():
            try:
                from trends_fetcher import fmt_num
                results = fetch_trending(query, max_r, callback=cb)
                def _done(res=results):
                    self._tr_results = res
                    for i, r in enumerate(res):
                        dur = f"{r['duration']//60}:{r['duration']%60:02d}"
                        tag = "odd" if i % 2 else "even"
                        self._tr_tree.insert("", "end", iid=str(i),
                            values=(i+1, r["title"], fmt_num(r["views"]),
                                    r["channel"], dur, r["url"]),
                            tags=(tag,))
                    self._tr_progress.configure(value=100)
                    self.status_var.set(
                        f"{len(res)} trend short listelendi — çift tıklayarak aç")
                self.after(0, _done)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Hata", str(e)))
                self.after(0, lambda: self.status_var.set("Hata oluştu."))

        threading.Thread(target=worker, daemon=True).start()

    def _tr_selected_url(self):
        sel = self._tr_tree.selection()
        if not sel:
            messagebox.showinfo("Seçim Yok", "Listeden bir video seçin.")
            return None
        idx = int(sel[0])
        return self._tr_results[idx]["url"] if idx < len(self._tr_results) else None

    def _tr_open_url(self, _=None):
        url = self._tr_selected_url()
        if url:
            import webbrowser
            webbrowser.open(url)

    def _tr_copy_to_audio(self):
        url = self._tr_selected_url()
        if not url:
            return
        # Müzik Ekle sekmesine geç ve URL'yi yapıştır
        self._audio_source_var.set("youtube")
        self._audio_toggle()
        self._audio_yt_entry.delete(0, "end")
        self._audio_yt_entry.insert(0, url)
        for w in self.winfo_children():
            if isinstance(w, ttk.Notebook):
                w.select(1)
                break
        self.status_var.set("URL Müzik Ekle sekmesine kopyalandı.")

    def _tr_download(self):
        url = self._tr_selected_url()
        if not url:
            return
        out_dir = "output_videos"
        os.makedirs(out_dir, exist_ok=True)
        self.status_var.set("Video indiriliyor...")
        self._tr_progress["value"] = 0

        def worker():
            try:
                import yt_dlp
                ydl_opts = {
                    "format": "bestvideo[ext=mp4][vcodec^=avc]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                    "outtmpl": f"{out_dir}/%(title).60s.%(ext)s",
                    "quiet": True,
                    "merge_output_format": "mp4",
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    title = info.get("title","video")
                self.after(0, lambda: self.status_var.set(
                    f"İndirildi: {title[:50]}"))
                self.after(0, lambda: self._tr_progress.configure(value=100))
                self.after(0, lambda: messagebox.showinfo(
                    "İndirildi", f"Video indirildi:\noutput_videos klasörüne kaydedildi."))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Hata", str(e)))
                self.after(0, lambda: self.status_var.set("İndirme hatası."))

        threading.Thread(target=worker, daemon=True).start()


if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    App().mainloop()
