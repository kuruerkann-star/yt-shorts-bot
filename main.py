import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import json
import os
import webbrowser
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
        "ai_provider": "openai",
        "ai_api_key": "",
        "channel_name": "",
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
        self.geometry("960x780")
        self.minsize(860, 650)
        self.configure(bg="#0f0f1a")
        self.config_data = load_config()
        self.fetched_video: Optional[Dict] = None
        self.created_video_path: Optional[str] = None
        self._setup_styles()
        self._build_ui()

    # ------------------------------------------------------------------ styles
    def _setup_styles(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        BG, FG = "#0f0f1a", "#ffffff"
        ACC = "#ff3c78"
        AI  = "#7c3aed"
        ENT = "#1a1a2e"
        s.configure(".", background=BG, foreground=FG, font=("Segoe UI", 10))
        s.configure("TFrame", background=BG)
        s.configure("TLabel", background=BG, foreground=FG)
        s.configure("TLabelframe", background=BG, foreground=ACC, bordercolor=ACC)
        s.configure("TLabelframe.Label", background=BG, foreground=ACC,
                    font=("Segoe UI", 10, "bold"))
        s.configure("AI.TLabelframe", background=BG, foreground=AI, bordercolor=AI)
        s.configure("AI.TLabelframe.Label", background=BG, foreground=AI,
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
        s.configure("AI.TButton", background=AI, foreground=FG,
                    font=("Segoe UI", 10, "bold"), padding=[12, 6])
        s.map("AI.TButton", background=[("active", "#9d5cff")])
        s.configure("Green.TButton", background="#16a34a", foreground=FG,
                    font=("Segoe UI", 10, "bold"), padding=[12, 6])
        s.map("Green.TButton", background=[("active", "#22c55e")])
        s.configure("TButton", background=ENT, foreground=FG, padding=[10, 5])
        s.map("TButton", background=[("active", "#2a2a4e")])
        s.configure("TCheckbutton", background=BG, foreground=FG)
        s.configure("Horizontal.TProgressbar", troughcolor=ENT, background=ACC)
        s.configure("TScrollbar", background=ENT, troughcolor=BG, arrowcolor=FG)

    # ------------------------------------------------------------------ layout
    def _build_ui(self):
        hdr = ttk.Frame(self)
        hdr.pack(fill="x")
        tk.Label(hdr, text="YouTube Shorts Bot",
                 font=("Segoe UI", 17, "bold"), bg="#0f0f1a", fg="#ff3c78"
                 ).pack(side="left", padx=18, pady=10)
        tk.Label(hdr, text="URL yapıştır veya hikaye yaz → AI script oluştursun → video çıksın",
                 font=("Segoe UI", 9), bg="#0f0f1a", fg="#666"
                 ).pack(side="left")
        tk.Frame(self, height=2, bg="#ff3c78").pack(fill="x")

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)

        self.tab_url   = ttk.Frame(nb)
        self.tab_story = ttk.Frame(nb)
        self.tab_cfg   = ttk.Frame(nb)

        nb.add(self.tab_url,   text="  YouTube URL  ")
        nb.add(self.tab_story, text="  Hikaye / Metin  ")
        nb.add(self.tab_cfg,   text="  Ayarlar  ")

        self._build_url_tab()
        self._build_story_tab()
        self._build_settings_tab()

        self.status_var = tk.StringVar(value="Hazır")
        tk.Label(self, textvariable=self.status_var, bg="#1a1a2e", fg="#aaa",
                 anchor="w", padx=10, font=("Segoe UI", 9)
                 ).pack(fill="x", side="bottom")

    # ------------------------------------------------------------------ URL tab
    def _build_url_tab(self):
        p = ttk.Frame(self.tab_url)
        p.pack(fill="both", expand=True, padx=16, pady=12)

        # URL girisi
        url_frame = ttk.LabelFrame(p, text="YouTube URL", padding=10)
        url_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(url_frame, text="URL:").grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.url_entry = ttk.Entry(url_frame, width=60)
        self.url_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        ttk.Button(url_frame, text="Video Bilgisini Getir",
                   command=self._fetch_url).grid(row=0, column=2)
        url_frame.columnconfigure(1, weight=1)

        # Getirilen bilgi
        self.info_frame = ttk.LabelFrame(p, text="Video Bilgisi", padding=8)
        self.info_frame.pack(fill="x", pady=(0, 10))
        self.info_title   = self._info_row(self.info_frame, "Başlık :", 0)
        self.info_channel = self._info_row(self.info_frame, "Kanal  :", 1)
        self.info_views   = self._info_row(self.info_frame, "İzlenme:", 2)
        self.info_tags    = self._info_row(self.info_frame, "Etiket :", 3)
        self.info_frame.columnconfigure(1, weight=1)

        # AI + video olustur (paylasimli)
        self._build_ai_and_create(p, source="url")

    # ------------------------------------------------------------------ story tab
    def _build_story_tab(self):
        p = ttk.Frame(self.tab_story)
        p.pack(fill="both", expand=True, padx=16, pady=12)

        story_frame = ttk.LabelFrame(p, text="Hikaye / Metin", padding=10)
        story_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(story_frame,
                  text="Anlatmak istediginiz hikayeyi, konuyu veya script'i buraya yazin:",
                  foreground="#aaa").pack(anchor="w", pady=(0, 6))
        self.story_text = scrolledtext.ScrolledText(
            story_frame, height=8, bg="#1a1a2e", fg="white",
            insertbackground="white", font=("Segoe UI", 10), relief="flat")
        self.story_text.pack(fill="x")

        self._build_ai_and_create(p, source="story")

    # ------------------------------------------------------------------ shared AI + create panel
    def _build_ai_and_create(self, parent, source: str):
        prefix = source  # "url" or "story"

        # AI paneli
        ai_frame = ttk.LabelFrame(parent, text="  Yapay Zeka (OpenAI / Gemini)",
                                   padding=10, style="AI.TLabelframe")
        ai_frame.pack(fill="x", pady=(0, 8))

        ttk.Label(ai_frame, text="Ne tarz video olsun?",
                  foreground="#c4b5fd").grid(row=0, column=0, sticky="w", padx=(0, 8))
        prompt_entry = ttk.Entry(ai_frame, width=48)
        prompt_entry.insert(0, "Viral, merak uyandiran, izleyiciyi ekrana kilitleyen" if source == "url"
                            else "Hikayeyi akici, etkili bir Shorts videosuna donustur")
        prompt_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))

        ttk.Button(ai_frame, text="AI ile Script Oluştur", style="AI.TButton",
                   command=lambda: self._do_ai(source, prompt_entry)
                   ).grid(row=0, column=2)
        ai_frame.columnconfigure(1, weight=1)

        ai_status = ttk.Label(ai_frame, text="", foreground="#c4b5fd",
                              font=("Segoe UI", 8))
        ai_status.grid(row=1, column=0, columnspan=3, sticky="w", pady=(4, 0))

        # Script duzenleme
        edit_frame = ttk.LabelFrame(parent, text="Video Başlık & İçerik (düzenleyebilirsiniz)", padding=8)
        edit_frame.pack(fill="both", expand=True, pady=(0, 8))

        ttk.Label(edit_frame, text="Başlık:").grid(row=0, column=0, sticky="w", padx=(0, 8))
        title_entry = ttk.Entry(edit_frame, width=65)
        title_entry.grid(row=0, column=1, sticky="ew", pady=(0, 6))
        edit_frame.columnconfigure(1, weight=1)

        content_box = scrolledtext.ScrolledText(
            edit_frame, height=6, bg="#1a1a2e", fg="white",
            insertbackground="white", font=("Segoe UI", 10), relief="flat")
        content_box.grid(row=1, column=0, columnspan=2, sticky="nsew")
        edit_frame.rowconfigure(1, weight=1)

        # Video ayarlari
        opt_row = ttk.Frame(parent)
        opt_row.pack(fill="x", pady=(0, 6))

        ttk.Label(opt_row, text="Kanal adı:").pack(side="left", padx=(0, 6))
        ch_entry = ttk.Entry(opt_row, width=20)
        ch_entry.insert(0, self.config_data.get("channel_name", ""))
        ch_entry.pack(side="left", padx=(0, 16))

        ttk.Label(opt_row, text="Süre (sn):").pack(side="left", padx=(0, 6))
        dur_combo = ttk.Combobox(opt_row, values=["15","20","25","30","45","55"],
                                  width=5, state="readonly")
        dur_combo.set(str(self.config_data.get("video_duration", 30)))
        dur_combo.pack(side="left")

        # Butonlar
        btn_row = ttk.Frame(parent)
        btn_row.pack(fill="x")

        progress = ttk.Progressbar(parent, mode="determinate", maximum=100)
        progress.pack(fill="x", pady=(8, 0))

        log_box = scrolledtext.ScrolledText(parent, height=4, bg="#1a1a2e", fg="#ccc",
                                             font=("Consolas", 8), state="disabled", relief="flat")
        log_box.pack(fill="x", pady=(4, 0))

        preview_btn = ttk.Button(btn_row, text="▶  Videoyu İzle",
                                  style="Green.TButton", state="disabled",
                                  command=lambda: self._preview())
        ttk.Button(btn_row, text="Video Oluştur", style="Accent.TButton",
                   command=lambda: self._do_create(
                       title_entry, content_box, ch_entry, dur_combo,
                       progress, log_box, preview_btn)
                   ).pack(side="left", padx=(0, 10))
        preview_btn.pack(side="left")

        # Referanslari sakla
        setattr(self, f"_{prefix}_ai_status",   ai_status)
        setattr(self, f"_{prefix}_title",        title_entry)
        setattr(self, f"_{prefix}_content",      content_box)
        setattr(self, f"_{prefix}_progress",     progress)
        setattr(self, f"_{prefix}_log",          log_box)
        setattr(self, f"_{prefix}_preview_btn",  preview_btn)

    # ------------------------------------------------------------------ settings
    def _build_settings_tab(self):
        p = ttk.Frame(self.tab_cfg)
        p.pack(fill="both", expand=True, padx=24, pady=20)

        from ai_helper import AIHelper

        rows = [
            ("AI Sağlayıcı:", "cfg_provider",  "combo", ["openai","gemini"]),
            ("AI API Anahtarı:", "cfg_ai_key",  "entry_secret", None),
            ("Kanal adı:", "cfg_channel",       "entry", None),
            ("Çıktı klasörü:", "cfg_outdir",    "entry", None),
        ]
        widgets = {}
        for i, (label, key, kind, values) in enumerate(rows):
            ttk.Label(p, text=label, font=("Segoe UI", 10, "bold") if "API" in label else None
                      ).grid(row=i, column=0, sticky="w", pady=5)
            if kind == "combo":
                w = ttk.Combobox(p, values=values, width=46, state="readonly")
                w.set(self.config_data.get(key.replace("cfg_", "").replace("provider","ai_provider")
                                           .replace("nim_model","nim_model")
                                           .replace("channel","channel_name")
                                           .replace("outdir","output_dir"), values[0] if values else ""))
            elif kind == "entry_secret":
                w = ttk.Entry(p, width=50, show="*")
                w.insert(0, self.config_data.get("ai_api_key", ""))
            else:
                w = ttk.Entry(p, width=50)
                field = {"cfg_channel": "channel_name", "cfg_outdir": "output_dir"}.get(key, key)
                w.insert(0, self.config_data.get(field, ""))
            w.grid(row=i, column=1, sticky="ew", pady=5, padx=(10, 0))
            widgets[key] = w

        self._cfg_widgets = widgets

        ttk.Label(p, text="OpenAI → platform.openai.com/api-keys\n"
                          "Gemini → aistudio.google.com/apikey",
                  foreground="#555", font=("Segoe UI", 8), justify="left"
                  ).grid(row=len(rows), column=1, sticky="w", padx=(10, 0), pady=(4, 12))

        ttk.Button(p, text="Kaydet", style="Accent.TButton",
                   command=self._save_settings
                   ).grid(row=len(rows)+1, column=0, columnspan=2, sticky="w")
        p.columnconfigure(1, weight=1)

    # ------------------------------------------------------------------ helpers
    def _info_row(self, parent, label: str, row: int) -> ttk.Label:
        ttk.Label(parent, text=label, foreground="#888").grid(
            row=row, column=0, sticky="w", padx=(0, 10), pady=2)
        val = ttk.Label(parent, text="—", foreground="#eee", wraplength=700, justify="left")
        val.grid(row=row, column=1, sticky="w", pady=2)
        return val

    def _set_status(self, msg: str):
        self.status_var.set(msg)

    def _log(self, box: scrolledtext.ScrolledText, msg: str):
        box.configure(state="normal")
        box.insert("end", msg + "\n")
        box.see("end")
        box.configure(state="disabled")

    def _preview(self):
        if self.created_video_path and os.path.exists(self.created_video_path):
            os.startfile(self.created_video_path)

    # ------------------------------------------------------------------ fetch URL
    def _fetch_url(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Eksik", "Bir YouTube URL'si girin.")
            return
        self._set_status("Video bilgisi getiriliyor...")

        def worker():
            try:
                from youtube_fetcher import YouTubeFetcher
                info = YouTubeFetcher().get_video_info(url)
                self.fetched_video = info
                def update():
                    self.info_title.configure(text=info["title"])
                    self.info_channel.configure(text=info["channel"])
                    self.info_views.configure(text=f"{info['view_count']:,}")
                    tags = ", ".join(info["tags"][:8]) if info["tags"] else "—"
                    self.info_tags.configure(text=tags)
                    self._set_status("Video bilgisi alındı.")
                self.after(0, update)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Hata", str(e)))
                self.after(0, lambda: self._set_status("Hata: " + str(e)))

        threading.Thread(target=worker, daemon=True).start()

    # ------------------------------------------------------------------ AI generate
    def _do_ai(self, source: str, prompt_entry: ttk.Entry):
        prompt  = prompt_entry.get().strip()
        ai_key  = self.config_data.get("ai_api_key", "").strip()
        provider = self.config_data.get("ai_provider", "openai")

        if not ai_key:
            messagebox.showwarning("API Anahtarı", "Ayarlar sekmesinden AI API anahtarınızı girin.")
            return

        if source == "url" and not self.fetched_video:
            messagebox.showwarning("URL Gerekli", "Önce bir YouTube URL'si getirin.")
            return

        video_context = None
        if source == "url":
            video_context = self.fetched_video
        else:
            story = self.story_text.get("1.0", "end").strip()
            if not story:
                messagebox.showwarning("Boş", "Hikaye/metin alanını doldurun.")
                return
            prompt = f"Asagidaki hikaye/metni viral bir Shorts videosuna donustur:\n\n{story}\n\nEk istek: {prompt}"

        status_lbl: ttk.Label = getattr(self, f"_{source}_ai_status")
        status_lbl.configure(text=f"[{provider.upper()}] script oluşturuluyor...", foreground="#c4b5fd")
        self._set_status("AI script oluşturuluyor...")

        def worker():
            try:
                from ai_helper import AIHelper
                result = AIHelper(provider=provider, api_key=ai_key
                                  ).generate_video_content(prompt, video_context=video_context)

                title_w: ttk.Entry = getattr(self, f"_{source}_title")
                content_w: scrolledtext.ScrolledText = getattr(self, f"_{source}_content")

                def apply():
                    title_w.delete(0, "end")
                    title_w.insert(0, result.get("title", ""))
                    content_w.delete("1.0", "end")
                    content_w.insert("1.0", "\n".join(result.get("content_lines", [])))
                    status_lbl.configure(text="Script hazır!", foreground="#44ff88")
                    self._set_status("AI script oluşturuldu.")

                self.after(0, apply)
            except Exception as e:
                self.after(0, lambda: status_lbl.configure(
                    text=f"Hata: {str(e)[:80]}", foreground="#ff6666"))
                self.after(0, lambda: self._set_status("AI hatası: " + str(e)))

        threading.Thread(target=worker, daemon=True).start()

    # ------------------------------------------------------------------ create video
    def _do_create(self, title_w, content_w, ch_w, dur_w, progress, log_box, preview_btn):
        title   = title_w.get().strip()
        content = content_w.get("1.0", "end").strip()
        channel = ch_w.get().strip()
        duration = int(dur_w.get())
        out_dir  = self.config_data.get("output_dir", "output_videos")

        if not title:
            messagebox.showwarning("Eksik", "Başlık alanı boş olamaz.")
            return
        if not content:
            messagebox.showwarning("Eksik", "İçerik alanı boş olamaz.")
            return

        progress["value"] = 0
        log_box.configure(state="normal"); log_box.delete("1.0", "end"); log_box.configure(state="disabled")
        self.created_video_path = None
        preview_btn.configure(state="disabled")

        def worker():
            try:
                from video_creator import VideoCreator
                creator = VideoCreator(output_dir=out_dir)

                def cb(cur, total, msg):
                    pct = int(cur / max(total, 1) * 100)
                    self.after(0, lambda: progress.configure(value=pct))
                    self.after(0, lambda: self._log(log_box, msg))
                    self.after(0, lambda: self._set_status(msg))

                video_data = dict(self.fetched_video) if self.fetched_video else {}
                video_data["title"] = title
                path = creator.create_video(
                    video_data=video_data,
                    custom_title=title,
                    custom_content=content,
                    channel_name=channel,
                    duration=duration,
                    callback=cb,
                )
                self.created_video_path = path
                self.after(0, lambda: progress.configure(value=100))
                self.after(0, lambda: self._log(log_box, f"Tamamlandi → {path}"))
                self.after(0, lambda: self._set_status("Video hazır: " + path))
                self.after(0, lambda: preview_btn.configure(state="normal"))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Hata", str(e)))
                self.after(0, lambda: self._log(log_box, "HATA: " + str(e)))
                self.after(0, lambda: self._set_status("Hata: " + str(e)))

        threading.Thread(target=worker, daemon=True).start()

    # ------------------------------------------------------------------ save settings
    def _save_settings(self):
        w = self._cfg_widgets
        cfg_map = {
            "cfg_provider":  "ai_provider",
            "cfg_ai_key":    "ai_api_key",
            "cfg_channel":   "channel_name",
            "cfg_outdir":    "output_dir",
        }
        for wkey, cfgkey in cfg_map.items():
            widget = w[wkey]
            self.config_data[cfgkey] = widget.get().strip()
        save_config(self.config_data)
        messagebox.showinfo("Kaydedildi", "Ayarlar kaydedildi.")


if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    App().mainloop()
