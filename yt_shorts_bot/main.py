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

        self.tab_merge = ttk.Frame(nb)
        self.tab_audio = ttk.Frame(nb)
        self.tab_tts   = ttk.Frame(nb)
        nb.add(self.tab_merge, text="  Video Birleştir  ")
        nb.add(self.tab_audio, text="  Müzik Ekle  ")
        nb.add(self.tab_tts,   text="  Ses Üret  ")

        self._build_merge_tab()
        self._build_audio_tab()
        self._build_tts_tab()

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


    # ── Ses Üret (TTS) ──────────────────────────────────────────────────────
    def _build_tts_tab(self):
        p = ttk.Frame(self.tab_tts)
        p.pack(fill="both", expand=True, padx=16, pady=12)

        # Metin girişi
        tf = ttk.LabelFrame(p, text="Seslendirilecek Metin", padding=10)
        tf.pack(fill="both", expand=True, pady=(0, 8))
        self._tts_text = tk.Text(
            tf, height=8, bg="#1a1a2e", fg="#fff", insertbackground="#fff",
            font=("Segoe UI", 11), relief="flat", wrap="word")
        self._tts_text.pack(fill="both", expand=True)
        self._tts_text.insert("1.0", "Merhaba! Bu bir test sesidir.")

        # Ayarlar
        af = ttk.LabelFrame(p, text="Ses Ayarları", padding=10)
        af.pack(fill="x", pady=(0, 8))

        ttk.Label(af, text="Dil:").grid(row=0, column=0, sticky="w", padx=(0, 8))
        self._tts_lang = ttk.Combobox(af, width=18, state="readonly", values=[
            "Türkçe (tr)", "İngilizce (en)", "Almanca (de)",
            "Fransızca (fr)", "İspanyolca (es)", "Japonca (ja)"])
        self._tts_lang.set("Türkçe (tr)")
        self._tts_lang.grid(row=0, column=1, sticky="w", pady=4, padx=(0, 20))

        ttk.Label(af, text="Hız:").grid(row=0, column=2, sticky="w", padx=(0, 8))
        self._tts_slow = tk.BooleanVar(value=False)
        ttk.Checkbutton(af, text="Yavaş oku",
                        variable=self._tts_slow).grid(row=0, column=3, sticky="w")

        ttk.Label(af, text="Çıktı:").grid(row=1, column=0, sticky="w", padx=(0, 8))
        self._tts_out_entry = ttk.Entry(af, width=50)
        self._tts_out_entry.insert(0, "output_videos/tts_output.mp3")
        self._tts_out_entry.grid(row=1, column=1, columnspan=3, sticky="ew", pady=4)
        af.columnconfigure(1, weight=1)

        # Aksiyon satırı
        act = ttk.Frame(p)
        act.pack(fill="x", pady=(0, 6))
        ttk.Button(act, text="Ses Üret", style="Green.TButton",
                   command=self._tts_generate).pack(side="left", padx=(0, 8))
        self._tts_play_btn = ttk.Button(act, text="▶  Dinle", state="disabled",
                                         command=self._tts_play)
        self._tts_play_btn.pack(side="left", padx=(0, 6))
        self._tts_use_btn = ttk.Button(act, text="→  Müzik Ekle'ye Gönder",
                                        state="disabled",
                                        command=self._tts_send_to_audio)
        self._tts_use_btn.pack(side="left", padx=(0, 6))
        self._tts_save_btn = ttk.Button(act, text="Masaüstüne İndir",
                                         state="disabled",
                                         command=self._tts_save_desktop)
        self._tts_save_btn.pack(side="left")

        self._tts_progress = ttk.Progressbar(p, mode="indeterminate")
        self._tts_progress.pack(fill="x", pady=(0, 4))

        self._tts_status = tk.StringVar(value="")
        tk.Label(p, textvariable=self._tts_status, bg="#0f0f1a",
                 fg="#aaa", font=("Segoe UI", 9), anchor="w"
                 ).pack(fill="x")

        self._tts_out_path = None

    _TTS_LANG_MAP = {
        "Türkçe (tr)": "tr",
        "İngilizce (en)": "en",
        "Almanca (de)": "de",
        "Fransızca (fr)": "fr",
        "İspanyolca (es)": "es",
        "Japonca (ja)": "ja",
    }

    def _tts_generate(self):
        text = self._tts_text.get("1.0", "end").strip()
        if not text:
            messagebox.showwarning("Boş Metin", "Seslendirilecek metin girin.")
            return
        lang    = self._TTS_LANG_MAP.get(self._tts_lang.get(), "tr")
        slow    = self._tts_slow.get()
        out_path = self._tts_out_entry.get().strip() or "output_videos/tts_output.mp3"
        os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)

        self._tts_play_btn.configure(state="disabled")
        self._tts_use_btn.configure(state="disabled")
        self._tts_save_btn.configure(state="disabled")
        self._tts_out_path = None
        self._tts_progress.start(10)
        self._tts_status.set("Ses üretiliyor...")
        self.status_var.set("TTS çalışıyor...")

        def worker():
            try:
                from gtts import gTTS
                tts = gTTS(text=text, lang=lang, slow=slow)
                tts.save(out_path)
                def _done():
                    self._tts_out_path = os.path.abspath(out_path)
                    self._tts_progress.stop()
                    self._tts_progress["value"] = 100
                    self._tts_status.set(f"Tamamlandı → {self._tts_out_path}")
                    self.status_var.set("Ses üretildi.")
                    self._tts_play_btn.configure(state="normal")
                    self._tts_use_btn.configure(state="normal")
                    self._tts_save_btn.configure(state="normal")
                self.after(0, _done)
            except Exception as e:
                def _err(msg=str(e)):
                    self._tts_progress.stop()
                    self._tts_status.set("HATA: " + msg)
                    self.status_var.set("Hata oluştu.")
                    messagebox.showerror("TTS Hatası", msg)
                self.after(0, _err)

        threading.Thread(target=worker, daemon=True).start()

    def _tts_play(self):
        if self._tts_out_path and os.path.exists(self._tts_out_path):
            os.startfile(self._tts_out_path)

    def _tts_send_to_audio(self):
        if not self._tts_out_path or not os.path.exists(self._tts_out_path):
            return
        self._audio_source_var.set("local")
        self._audio_toggle()
        self._audio_local_entry.delete(0, "end")
        self._audio_local_entry.insert(0, self._tts_out_path)
        # Ses Ekle sekmesine geç (index 1)
        for w in self.winfo_children():
            if isinstance(w, ttk.Notebook):
                w.select(1)
                break
        self.status_var.set("Müzik dosyası Müzik Ekle sekmesine gönderildi.")

    def _tts_save_desktop(self):
        import shutil
        path = self._tts_out_path
        if not path or not os.path.exists(path):
            messagebox.showerror("Dosya Yok", "Önce ses üretin.")
            return
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        base, ext = os.path.splitext(os.path.basename(path))
        dest = os.path.join(desktop, os.path.basename(path))
        c = 1
        while os.path.exists(dest):
            dest = os.path.join(desktop, f"{base}_{c}{ext}"); c += 1
        shutil.copy2(path, dest)
        messagebox.showinfo("Kaydedildi", f"Masaüstüne kaydedildi:\n{dest}")


if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    App().mainloop()
