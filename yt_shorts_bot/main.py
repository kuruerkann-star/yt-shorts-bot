import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import json
import os
from pathlib import Path
from typing import Optional, Dict

CONFIG_FILE = "config.json"


def load_config() -> Dict:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "ai_provider": "grok",
        "ai_api_key": "",
        "output_dir": "output_videos",
        "video_duration": 30,
    }


def save_config(cfg: Dict):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("YouTube Shorts Bot")
        self.geometry("900x700")
        self.minsize(780, 560)
        self.configure(bg="#0f0f1a")
        self.config_data = load_config()
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
        s.configure("TNotebook.Tab", background=ENT, foreground=FG, padding=[16, 7])
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
        tk.Label(hdr, text="YouTube Shorts Bot",
                 font=("Segoe UI", 17, "bold"), bg="#0f0f1a", fg="#ff3c78"
                 ).pack(side="left", padx=18, pady=10)
        tk.Label(hdr, text="URL yapıştır veya hikaye yaz → AI ile video oluştur",
                 font=("Segoe UI", 9), bg="#0f0f1a", fg="#666"
                 ).pack(side="left")
        tk.Frame(self, height=2, bg="#ff3c78").pack(fill="x")

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)

        self.tab_url   = ttk.Frame(nb)
        self.tab_story = ttk.Frame(nb)
        self.tab_merge = ttk.Frame(nb)
        self.tab_cfg   = ttk.Frame(nb)
        nb.add(self.tab_url,   text="  YouTube URL  ")
        nb.add(self.tab_story, text="  Hikaye / Metin  ")
        nb.add(self.tab_merge, text="  Video Birleştir  ")
        nb.add(self.tab_cfg,   text="  Ayarlar  ")

        self._build_url_tab()
        self._build_story_tab()
        self._build_merge_tab()
        self._build_settings_tab()

        self.status_var = tk.StringVar(value="Hazır")
        tk.Label(self, textvariable=self.status_var, bg="#1a1a2e", fg="#aaa",
                 anchor="w", padx=10, font=("Segoe UI", 9)
                 ).pack(fill="x", side="bottom")

    # ── YouTube URL sekmesi ──────────────────────────────────────────────────
    def _build_url_tab(self):
        p = ttk.Frame(self.tab_url)
        p.pack(fill="both", expand=True, padx=16, pady=12)

        uf = ttk.LabelFrame(p, text="YouTube URL", padding=10)
        uf.pack(fill="x", pady=(0, 8))
        ttk.Label(uf, text="URL:").grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.url_entry = ttk.Entry(uf, width=60)
        self.url_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        ttk.Button(uf, text="Bilgi Getir", style="Accent.TButton",
                   command=self._fetch_url).grid(row=0, column=2)
        uf.columnconfigure(1, weight=1)
        self.url_info_lbl = ttk.Label(uf, text="", foreground="#aaa",
                                      font=("Segoe UI", 8), wraplength=700)
        self.url_info_lbl.grid(row=1, column=0, columnspan=3, sticky="w", pady=(4, 0))

        self._build_ai_panel(p, tag="url")
        self._build_action_row(p, tag="url")

    # ── Hikaye sekmesi ───────────────────────────────────────────────────────
    def _build_story_tab(self):
        p = ttk.Frame(self.tab_story)
        p.pack(fill="both", expand=True, padx=16, pady=12)

        sf = ttk.LabelFrame(p, text="Hikaye / Metin", padding=10)
        sf.pack(fill="x", pady=(0, 8))
        ttk.Label(sf, text="Oluşturmak istediğin video fikrini veya hikayeyi yaz:"
                  ).pack(anchor="w", pady=(0, 4))
        self.story_text = scrolledtext.ScrolledText(
            sf, height=5, bg="#1a1a2e", fg="#fff",
            font=("Segoe UI", 10), insertbackground="white", relief="flat")
        self.story_text.pack(fill="x")

        self._build_ai_panel(p, tag="story")
        self._build_action_row(p, tag="story")

    def _build_ai_panel(self, parent, tag: str):
        af = ttk.LabelFrame(parent, text="  Grok AI Ayarları", padding=10)
        af.pack(fill="x", pady=(0, 8))

        ttk.Label(af, text="Tarz / Prompt:").grid(row=0, column=0, sticky="w", padx=(0, 8))
        prompt_e = ttk.Entry(af, width=55)
        prompt_e.insert(0, "Viral, eğlenceli, 30 saniyelik Shorts videosu")
        prompt_e.grid(row=0, column=1, sticky="ew", pady=4)
        af.columnconfigure(1, weight=1)

        ttk.Label(af, text="Tema:").grid(row=1, column=0, sticky="w", padx=(0, 8))
        theme_cb = ttk.Combobox(af, values=[
            "dark", "neon", "minimal", "retro", "nature", "tech"
        ], width=14, state="readonly")
        theme_cb.set("dark")
        theme_cb.grid(row=1, column=1, sticky="w", pady=4)

        setattr(self, f"_{tag}_prompt_entry", prompt_e)
        setattr(self, f"_{tag}_theme_cb", theme_cb)

    def _build_action_row(self, parent, tag: str):
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=(0, 6))
        ttk.Button(row, text="AI ile Script Oluştur", style="Accent.TButton",
                   command=lambda t=tag: self._generate_script(t)).pack(side="left", padx=(0, 8))
        ttk.Button(row, text="Video Oluştur", style="Green.TButton",
                   command=lambda t=tag: self._create_video(t)).pack(side="left", padx=(0, 8))
        preview_btn = ttk.Button(row, text="▶  İzle", state="disabled",
                                 command=lambda t=tag: self._preview(t))
        preview_btn.pack(side="left")
        setattr(self, f"_{tag}_preview_btn", preview_btn)
        setattr(self, f"_{tag}_out_path", None)
        setattr(self, f"_{tag}_script", None)

        prog = ttk.Progressbar(parent, mode="determinate", maximum=100)
        prog.pack(fill="x", pady=(0, 4))
        setattr(self, f"_{tag}_progress", prog)

        log = scrolledtext.ScrolledText(parent, height=7, bg="#1a1a2e", fg="#ccc",
                                        font=("Consolas", 8), state="disabled", relief="flat")
        log.pack(fill="both", expand=True)
        setattr(self, f"_{tag}_log", log)

    # ── Video Birleştir sekmesi ──────────────────────────────────────────────
    def _build_merge_tab(self):
        p = ttk.Frame(self.tab_merge)
        p.pack(fill="both", expand=True, padx=16, pady=12)

        # Dosya listesi
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

        # Efekt ayarları
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
        dur_spin = ttk.Spinbox(ef, from_=0.1, to=2.0, increment=0.1,
                               textvariable=self._merge_dur_var, width=6)
        dur_spin.grid(row=0, column=3, sticky="w", pady=4)

        # Çıktı dosyası
        ttk.Label(ef, text="Çıktı:").grid(row=1, column=0, sticky="w", padx=(0, 8))
        self._merge_out_entry = ttk.Entry(ef, width=40)
        self._merge_out_entry.insert(0, "output_videos/merged_output.mp4")
        self._merge_out_entry.grid(row=1, column=1, columnspan=3, sticky="ew", pady=4)
        ef.columnconfigure(1, weight=1)

        # Aksiyon satırı
        act = ttk.Frame(p)
        act.pack(fill="x", pady=(0, 6))
        ttk.Button(act, text="Birleştir", style="Green.TButton",
                   command=self._merge_start).pack(side="left", padx=(0, 8))
        self._merge_preview_btn = ttk.Button(act, text="▶  İzle",
                                              state="disabled",
                                              command=self._merge_preview)
        self._merge_preview_btn.pack(side="left")

        self._merge_progress = ttk.Progressbar(p, mode="determinate", maximum=100)
        self._merge_progress.pack(fill="x", pady=(0, 4))

        self._merge_log = scrolledtext.ScrolledText(
            p, height=6, bg="#1a1a2e", fg="#ccc",
            font=("Consolas", 8), state="disabled", relief="flat")
        self._merge_log.pack(fill="both", expand=False)

        self._merge_out_path = None

    def _merge_add_file(self):
        from tkinter import filedialog
        paths = filedialog.askopenfilenames(
            title="Video Seç",
            filetypes=[("Video Dosyaları", "*.mp4 *.avi *.mov *.mkv *.webm"), ("Tümü", "*.*")])
        for p in paths:
            self._merge_listbox.insert("end", p)

    def _merge_move_up(self):
        sel = self._merge_listbox.curselection()
        if not sel or sel[0] == 0:
            return
        i = sel[0]
        val = self._merge_listbox.get(i)
        self._merge_listbox.delete(i)
        self._merge_listbox.insert(i - 1, val)
        self._merge_listbox.selection_set(i - 1)

    def _merge_move_down(self):
        sel = self._merge_listbox.curselection()
        if not sel or sel[0] == self._merge_listbox.size() - 1:
            return
        i = sel[0]
        val = self._merge_listbox.get(i)
        self._merge_listbox.delete(i)
        self._merge_listbox.insert(i + 1, val)
        self._merge_listbox.selection_set(i + 1)

    def _merge_remove(self):
        sel = self._merge_listbox.curselection()
        if sel:
            self._merge_listbox.delete(sel[0])

    def _merge_preview(self):
        path = self._merge_out_path
        if not path:
            return
        path = os.path.abspath(path)
        if os.path.exists(path):
            os.startfile(path)
        else:
            messagebox.showerror("Dosya Bulunamadı", f"Video dosyası bulunamadı:\n{path}")

    def _merge_log_msg(self, msg: str):
        self._merge_log.configure(state="normal")
        self._merge_log.insert("end", msg + "\n")
        self._merge_log.see("end")
        self._merge_log.configure(state="disabled")

    def _merge_start(self):
        paths = list(self._merge_listbox.get(0, "end"))
        if len(paths) < 2:
            messagebox.showwarning("Yetersiz Video", "En az 2 video ekleyin.")
            return

        effect    = self._merge_effect_cb.get()
        out_path  = self._merge_out_entry.get().strip() or "output_videos/merged_output.mp4"
        try:
            dur = float(self._merge_dur_var.get())
        except ValueError:
            dur = 0.5

        os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)

        self._merge_progress["value"] = 0
        self._merge_preview_btn.configure(state="disabled")
        self._merge_out_path = None
        self._merge_log.configure(state="normal")
        self._merge_log.delete("1.0", "end")
        self._merge_log.configure(state="disabled")
        self._set_status("Videolar birleştiriliyor...")

        def cb(cur, total, msg):
            pct = int(cur / max(total, 1) * 100)
            self.after(0, lambda: self._merge_progress.configure(value=pct))
            self.after(0, lambda: self._merge_log_msg(msg))
            self.after(0, lambda: self._set_status(msg))

        def worker():
            try:
                from video_editor import merge_videos
                result = merge_videos(paths, out_path,
                                      transition=effect,
                                      transition_sec=dur,
                                      callback=cb)
                def _done(r=result):
                    self._merge_out_path = os.path.abspath(r)
                    self._merge_progress.configure(value=100)
                    self._merge_log_msg(f"Tamamlandı → {self._merge_out_path}")
                    self._set_status("Birleştirme tamamlandı.")
                    self._merge_preview_btn.configure(state="normal")
                self.after(0, _done)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Hata", str(e)))
                self.after(0, lambda: self._merge_log_msg("HATA: " + str(e)))
                self.after(0, lambda: self._set_status("Hata oluştu."))
        threading.Thread(target=worker, daemon=True).start()

    # ── Ayarlar sekmesi ──────────────────────────────────────────────────────
    def _build_settings_tab(self):
        p = ttk.Frame(self.tab_cfg)
        p.pack(fill="both", expand=True, padx=24, pady=20)

        rows = [
            ("AI Sağlayıcı:",   "cfg_provider",  "combo", ["grok"]),
            ("AI API Anahtarı:", "cfg_ai_key",    "entry_secret", None),
            ("Çıktı klasörü:",  "cfg_outdir",    "entry", None),
            ("Video süresi (sn):", "cfg_duration","entry", None),
        ]
        for i, (lbl, attr, kind, opts) in enumerate(rows):
            ttk.Label(p, text=lbl).grid(row=i, column=0, sticky="w", pady=8)
            if kind == "combo":
                w = ttk.Combobox(p, values=opts, width=20, state="readonly")
                w.set(self.config_data.get("ai_provider", "grok"))
            elif kind == "entry_secret":
                w = ttk.Entry(p, width=48, show="*")
                w.insert(0, self.config_data.get("ai_api_key", ""))
            else:
                w = ttk.Entry(p, width=48)
                val = self.config_data.get(
                    "output_dir" if "klasör" in lbl else "video_duration", "")
                w.insert(0, str(val))
            w.grid(row=i, column=1, sticky="ew", padx=(10, 0), pady=8)
            setattr(self, attr, w)

        # Grok API key bilgisi
        info = ttk.LabelFrame(p, text="API Anahtarı Nereden Alınır?", padding=8)
        info.grid(row=len(rows), column=0, columnspan=2, sticky="ew", pady=(12, 0))
        ttk.Label(info, text="Grok → console.x.ai  (xAI — ücretsiz $25 kredi)",
                  foreground="#aaa", font=("Segoe UI", 9)).pack(anchor="w")

        ttk.Button(p, text="Kaydet", style="Accent.TButton",
                   command=self._save_settings).grid(
                   row=len(rows)+1, column=0, columnspan=2, sticky="w", pady=14)
        p.columnconfigure(1, weight=1)

    # ── Yardımcılar ──────────────────────────────────────────────────────────
    def _log(self, tag: str, msg: str):
        box: scrolledtext.ScrolledText = getattr(self, f"_{tag}_log")
        box.configure(state="normal")
        box.insert("end", msg + "\n")
        box.see("end")
        box.configure(state="disabled")

    def _set_status(self, msg: str):
        self.status_var.set(msg)

    def _preview(self, tag: str):
        path = getattr(self, f"_{tag}_out_path")
        if path and os.path.exists(path):
            os.startfile(path)

    def _get_ai(self):
        from ai_helper import AIHelper
        return AIHelper(
            provider=self.config_data.get("ai_provider", "grok"),
            api_key=self.config_data.get("ai_api_key", ""),
        )

    # ── URL bilgi getir ───────────────────────────────────────────────────────
    def _fetch_url(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Eksik", "Bir YouTube URL'si girin.")
            return
        self.url_info_lbl.configure(text="Bilgi getiriliyor...", foreground="#aaa")
        self._url_video_context = None

        def worker():
            try:
                from youtube_fetcher import get_video_info
                info = get_video_info(url)
                self._url_video_context = info
                txt = (f"✓  {info.get('title','?')}  |  "
                       f"{info.get('view_count',0):,} izlenme  |  "
                       f"{info.get('channel','?')}")
                self.after(0, lambda: self.url_info_lbl.configure(
                    text=txt, foreground="#44ff88"))
            except Exception as e:
                self.after(0, lambda: self.url_info_lbl.configure(
                    text=f"Hata: {e}", foreground="#ff6666"))
        threading.Thread(target=worker, daemon=True).start()

    # ── Script oluştur ───────────────────────────────────────────────────────
    def _generate_script(self, tag: str):
        ai_key = self.config_data.get("ai_api_key", "")
        if not ai_key:
            messagebox.showwarning("API Anahtarı Eksik",
                                   "Ayarlar sekmesinden AI API anahtarınızı girin.")
            return

        prompt_entry = getattr(self, f"_{tag}_prompt_entry")
        prompt = prompt_entry.get().strip()

        if tag == "story":
            story = self.story_text.get("1.0", "end").strip()
            if story:
                prompt = f"{prompt}\n\nHikaye/İçerik:\n{story}"

        video_context = getattr(self, "_url_video_context", None) if tag == "url" else None

        log = getattr(self, f"_{tag}_log")
        log.configure(state="normal"); log.delete("1.0", "end"); log.configure(state="disabled")
        self._log(tag, "AI script oluşturuluyor...")
        self._set_status("AI çalışıyor...")

        def worker():
            try:
                result = self._get_ai().generate_video_content(prompt, video_context)
                setattr(self, f"_{tag}_script", result)
                self.after(0, lambda: self._log(tag, f"Başlık: {result.get('title','')}"))
                self.after(0, lambda: self._log(tag, f"İçerik: {len(result.get('content_lines',[]))} satır"))
                self.after(0, lambda: self._log(tag, "Script hazır → 'Video Oluştur' butonuna bas."))
                self.after(0, lambda: self._set_status("Script hazır."))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("AI Hatası", str(e)))
                self.after(0, lambda: self._set_status("Hata."))
        threading.Thread(target=worker, daemon=True).start()

    # ── Video oluştur ────────────────────────────────────────────────────────
    def _create_video(self, tag: str):
        script = getattr(self, f"_{tag}_script")
        if not script:
            messagebox.showwarning("Script Yok", "Önce 'AI ile Script Oluştur' butonuna bas.")
            return

        theme    = getattr(self, f"_{tag}_theme_cb").get()
        duration = int(self.config_data.get("video_duration", 30))
        out_dir  = self.config_data.get("output_dir", "output_videos")
        progress: ttk.Progressbar = getattr(self, f"_{tag}_progress")
        preview_btn = getattr(self, f"_{tag}_preview_btn")
        progress["value"] = 0
        preview_btn.configure(state="disabled")
        setattr(self, f"_{tag}_out_path", None)
        self._set_status("Video oluşturuluyor...")

        def cb(cur, total, msg):
            pct = int(cur / max(total, 1) * 100)
            self.after(0, lambda: progress.configure(value=pct))
            self.after(0, lambda: self._log(tag, msg))
            self.after(0, lambda: self._set_status(msg))

        def worker():
            try:
                from video_creator import VideoCreator
                vc = VideoCreator(output_dir=out_dir)
                path = vc.create_video(
                    script,
                    custom_title=script.get("title", ""),
                    custom_content="\n".join(script.get("content_lines", [])),
                    channel_name=self.config_data.get("channel_name", ""),
                    duration=duration,
                    callback=cb,
                )
                setattr(self, f"_{tag}_out_path", path)
                self.after(0, lambda: progress.configure(value=100))
                self.after(0, lambda: self._log(tag, f"Tamamlandı → {path}"))
                self.after(0, lambda: self._set_status("Hazır: " + path))
                self.after(0, lambda: preview_btn.configure(state="normal"))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Hata", str(e)))
                self.after(0, lambda: self._log(tag, "HATA: " + str(e)))
                self.after(0, lambda: self._set_status("Hata oluştu."))
        threading.Thread(target=worker, daemon=True).start()

    def _save_settings(self):
        self.config_data["ai_provider"]   = self.cfg_provider.get()
        self.config_data["ai_api_key"]    = self.cfg_ai_key.get().strip()
        self.config_data["output_dir"]    = self.cfg_outdir.get().strip()
        try:
            self.config_data["video_duration"] = int(self.cfg_duration.get())
        except ValueError:
            self.config_data["video_duration"] = 30
        save_config(self.config_data)
        messagebox.showinfo("Kaydedildi", "Ayarlar kaydedildi.")


if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    App().mainloop()
