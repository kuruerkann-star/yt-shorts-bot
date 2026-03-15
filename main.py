import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import json
import os
from pathlib import Path
from typing import Optional, Dict

from video_processor import ANIMAL_COLORS, TARGET_COLORS, SOURCE_ANIMALS
from animal_overlays import ANIMAL_DRAWERS

CONFIG_FILE = "config.json"


def load_config() -> Dict:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "output_dir": "output_videos",
        "sensitivity": 15,
        "confidence": 35,
    }


def save_config(cfg: Dict):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hayvan Video Düzenleyici")
        self.geometry("900x720")
        self.minsize(780, 580)
        self.configure(bg="#0f0f1a")
        self.config_data = load_config()
        self.downloaded_path: Optional[str] = None
        self.output_path: Optional[str] = None
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
        s.configure("TScale", background=BG, troughcolor=ENT)

    def _build_ui(self):
        hdr = ttk.Frame(self)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Hayvan Video Düzenleyici",
                 font=("Segoe UI", 17, "bold"), bg="#0f0f1a", fg="#ff3c78"
                 ).pack(side="left", padx=18, pady=10)
        tk.Label(hdr, text="YouTube URL → renk değiştir veya hayvan değiştir",
                 font=("Segoe UI", 9), bg="#0f0f1a", fg="#666"
                 ).pack(side="left")
        tk.Frame(self, height=2, bg="#ff3c78").pack(fill="x")

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)

        self.tab_color   = ttk.Frame(nb)
        self.tab_replace = ttk.Frame(nb)
        self.tab_cfg     = ttk.Frame(nb)
        nb.add(self.tab_color,   text="  Renk Değiştir  ")
        nb.add(self.tab_replace, text="  Hayvan Değiştir  ")
        nb.add(self.tab_cfg,     text="  Ayarlar  ")

        self._build_url_section(self.tab_color,   tag="color")
        self._build_url_section(self.tab_replace, tag="replace")
        self._build_color_tab()
        self._build_replace_tab()
        self._build_settings_tab()

        self.status_var = tk.StringVar(value="Hazır")
        tk.Label(self, textvariable=self.status_var, bg="#1a1a2e", fg="#aaa",
                 anchor="w", padx=10, font=("Segoe UI", 9)
                 ).pack(fill="x", side="bottom")

    # ---- URL bölümü (her sekmeye ayrı) ----
    def _build_url_section(self, parent, tag: str):
        url_frame = ttk.LabelFrame(parent, text="YouTube URL", padding=10)
        url_frame.pack(fill="x", padx=16, pady=(12, 0))

        ttk.Label(url_frame, text="URL:").grid(row=0, column=0, sticky="w", padx=(0, 8))
        entry = ttk.Entry(url_frame, width=56)
        entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        ttk.Button(url_frame, text="Videoyu İndir", style="Accent.TButton",
                   command=lambda t=tag: self._download(t)).grid(row=0, column=2)
        url_frame.columnconfigure(1, weight=1)

        dl_lbl = ttk.Label(url_frame, text="", foreground="#aaa", font=("Segoe UI", 8))
        dl_lbl.grid(row=1, column=0, columnspan=3, sticky="w", pady=(4, 0))

        setattr(self, f"_{tag}_url_entry", entry)
        setattr(self, f"_{tag}_dl_lbl",   dl_lbl)
        setattr(self, f"_{tag}_dl_path",  None)

    # ---- Renk değiştir sekmesi ----
    def _build_color_tab(self):
        p = ttk.Frame(self.tab_color)
        p.pack(fill="both", expand=True, padx=16, pady=8)

        cf = ttk.LabelFrame(p, text="Renk Ayarları", padding=10)
        cf.pack(fill="x", pady=(0, 8))

        ttk.Label(cf, text="Hayvan Rengi:").grid(row=0, column=0, sticky="w", padx=(0,10), pady=4)
        self.color_animal_combo = ttk.Combobox(cf, values=list(ANIMAL_COLORS.keys()),
                                               width=22, state="readonly")
        self.color_animal_combo.set(list(ANIMAL_COLORS.keys())[0])
        self.color_animal_combo.grid(row=0, column=1, sticky="w", pady=4)

        ttk.Label(cf, text="Yeni Renk:").grid(row=0, column=2, sticky="w", padx=(20,10), pady=4)
        self.color_target_combo = ttk.Combobox(cf, values=list(TARGET_COLORS.keys()),
                                               width=14, state="readonly")
        self.color_target_combo.set("Mavi")
        self.color_target_combo.grid(row=0, column=3, sticky="w", pady=4)

        ttk.Label(cf, text="Hassasiyet:").grid(row=1, column=0, sticky="w", padx=(0,10), pady=4)
        self.sens_var = tk.IntVar(value=self.config_data.get("sensitivity", 15))
        ttk.Scale(cf, from_=5, to=40, variable=self.sens_var,
                  orient="horizontal", length=160).grid(row=1, column=1, sticky="w")
        sens_lbl = ttk.Label(cf, text=str(self.sens_var.get()), foreground="#aaa", width=3)
        sens_lbl.grid(row=1, column=2, sticky="w", padx=(8,0))
        self.sens_var.trace_add("write", lambda *_: sens_lbl.configure(text=str(self.sens_var.get())))

        self._build_action_row(p, tag="color", cmd=self._process_color)

    # ---- Hayvan değiştir sekmesi ----
    def _build_replace_tab(self):
        p = ttk.Frame(self.tab_replace)
        p.pack(fill="both", expand=True, padx=16, pady=8)

        rf = ttk.LabelFrame(p, text="Hayvan Ayarları", padding=10)
        rf.pack(fill="x", pady=(0, 8))

        ttk.Label(rf, text="Videodaki Hayvan:").grid(row=0, column=0, sticky="w", padx=(0,10), pady=4)
        self.src_animal_combo = ttk.Combobox(rf, values=list(SOURCE_ANIMALS.keys()),
                                             width=20, state="readonly")
        self.src_animal_combo.set("Kedi")
        self.src_animal_combo.grid(row=0, column=1, sticky="w", pady=4)

        ttk.Label(rf, text="Yerine Koy:").grid(row=0, column=2, sticky="w", padx=(20,10), pady=4)
        self.tgt_animal_combo = ttk.Combobox(rf, values=list(ANIMAL_DRAWERS.keys()),
                                             width=14, state="readonly")
        self.tgt_animal_combo.set("Tavşan")
        self.tgt_animal_combo.grid(row=0, column=3, sticky="w", pady=4)

        ttk.Label(rf, text="Güven Eşiği:").grid(row=1, column=0, sticky="w", padx=(0,10), pady=4)
        self.conf_var = tk.IntVar(value=self.config_data.get("confidence", 35))
        ttk.Scale(rf, from_=10, to=80, variable=self.conf_var,
                  orient="horizontal", length=160).grid(row=1, column=1, sticky="w")
        conf_lbl = ttk.Label(rf, text=f"%{self.conf_var.get()}", foreground="#aaa", width=4)
        conf_lbl.grid(row=1, column=2, sticky="w", padx=(8,0))
        self.conf_var.trace_add("write", lambda *_: conf_lbl.configure(text=f"%{self.conf_var.get()}"))

        ttk.Label(rf, text="Düşük = daha fazla tespit, yüksek = daha az yanlış",
                  foreground="#555", font=("Segoe UI", 8)
                  ).grid(row=2, column=0, columnspan=4, sticky="w", pady=(2,0))

        self._build_action_row(p, tag="replace", cmd=self._process_replace)

    def _build_action_row(self, parent, tag: str, cmd):
        btn_row = ttk.Frame(parent)
        btn_row.pack(fill="x", pady=(0, 6))
        ttk.Button(btn_row, text="İşlemi Başlat", style="Accent.TButton",
                   command=cmd).pack(side="left", padx=(0, 10))
        preview_btn = ttk.Button(btn_row, text="▶  İzle", style="Green.TButton",
                                 state="disabled",
                                 command=lambda: self._preview(tag))
        preview_btn.pack(side="left")
        setattr(self, f"_{tag}_preview_btn", preview_btn)

        progress = ttk.Progressbar(parent, mode="determinate", maximum=100)
        progress.pack(fill="x", pady=(0, 4))
        setattr(self, f"_{tag}_progress", progress)

        log = scrolledtext.ScrolledText(parent, height=7, bg="#1a1a2e", fg="#ccc",
                                        font=("Consolas", 8), state="disabled", relief="flat")
        log.pack(fill="both", expand=True)
        setattr(self, f"_{tag}_log", log)
        setattr(self, f"_{tag}_out_path", None)

    def _build_settings_tab(self):
        p = ttk.Frame(self.tab_cfg)
        p.pack(fill="both", expand=True, padx=24, pady=20)
        ttk.Label(p, text="Çıktı klasörü:").grid(row=0, column=0, sticky="w", pady=8)
        self.cfg_outdir = ttk.Entry(p, width=48)
        self.cfg_outdir.insert(0, self.config_data.get("output_dir", "output_videos"))
        self.cfg_outdir.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=8)
        ttk.Button(p, text="Kaydet", style="Accent.TButton",
                   command=self._save_settings).grid(row=1, column=0, columnspan=2, sticky="w", pady=10)
        p.columnconfigure(1, weight=1)

    # ---- Yardımcılar ----
    def _set_status(self, msg: str):
        self.status_var.set(msg)

    def _log(self, tag: str, msg: str):
        box: scrolledtext.ScrolledText = getattr(self, f"_{tag}_log")
        box.configure(state="normal")
        box.insert("end", msg + "\n")
        box.see("end")
        box.configure(state="disabled")

    def _preview(self, tag: str):
        path = getattr(self, f"_{tag}_out_path")
        if path and os.path.exists(path):
            os.startfile(path)

    # ---- İndirme ----
    def _download(self, tag: str):
        entry: ttk.Entry = getattr(self, f"_{tag}_url_entry")
        lbl:   ttk.Label = getattr(self, f"_{tag}_dl_lbl")
        url = entry.get().strip()
        if not url:
            messagebox.showwarning("Eksik", "Bir YouTube URL'si girin.")
            return
        setattr(self, f"_{tag}_dl_path", None)
        lbl.configure(text="İndiriliyor...", foreground="#aaa")
        self._set_status("Video indiriliyor...")

        def worker():
            try:
                from video_processor import download_video
                out_dir = self.config_data.get("output_dir", "output_videos")

                def cb(c, t, m):
                    self.after(0, lambda: lbl.configure(text=m))
                    self.after(0, lambda: self._set_status(m))

                path = download_video(url, out_dir, callback=cb)
                setattr(self, f"_{tag}_dl_path", path)
                name = Path(path).name
                self.after(0, lambda: lbl.configure(
                    text=f"İndirildi: {name}", foreground="#44ff88"))
                self.after(0, lambda: self._set_status("Video indirildi."))
            except Exception as e:
                self.after(0, lambda: lbl.configure(
                    text=f"Hata: {str(e)[:80]}", foreground="#ff6666"))
                self.after(0, lambda: self._set_status("İndirme hatası."))

        threading.Thread(target=worker, daemon=True).start()

    # ---- Renk işleme ----
    def _process_color(self):
        path = getattr(self, "_color_dl_path")
        if not path or not os.path.exists(path):
            messagebox.showwarning("Video Yok", "Önce videoyu indirin.")
            return
        animal_color = self.color_animal_combo.get()
        target_color = self.color_target_combo.get()
        sensitivity  = self.sens_var.get()
        self._run_processing(
            tag="color",
            src=path,
            out=path.replace(".mp4", f"_{target_color}.mp4"),
            fn=lambda src, out, cb: __import__("video_processor").process_video(
                src, out, animal_color, target_color, sensitivity, cb),
        )

    # ---- Hayvan değiştirme ----
    def _process_replace(self):
        path = getattr(self, "_replace_dl_path")
        if not path or not os.path.exists(path):
            messagebox.showwarning("Video Yok", "Önce videoyu indirin.")
            return
        src_animal = self.src_animal_combo.get()
        tgt_animal = self.tgt_animal_combo.get()
        confidence = self.conf_var.get() / 100.0
        self._run_processing(
            tag="replace",
            src=path,
            out=path.replace(".mp4", f"_{tgt_animal}.mp4"),
            fn=lambda src, out, cb: __import__("video_processor").replace_animal(
                src, out, src_animal, tgt_animal, confidence, cb),
        )

    def _run_processing(self, tag: str, src: str, out: str, fn):
        progress: ttk.Progressbar = getattr(self, f"_{tag}_progress")
        preview_btn: ttk.Button   = getattr(self, f"_{tag}_preview_btn")
        progress["value"] = 0
        log: scrolledtext.ScrolledText = getattr(self, f"_{tag}_log")
        log.configure(state="normal"); log.delete("1.0", "end"); log.configure(state="disabled")
        setattr(self, f"_{tag}_out_path", None)
        preview_btn.configure(state="disabled")
        self._set_status("İşleniyor...")

        def worker():
            try:
                def cb(cur, total, msg):
                    pct = int(cur / max(total, 1) * 100)
                    self.after(0, lambda: progress.configure(value=pct))
                    self.after(0, lambda: self._log(tag, msg))
                    self.after(0, lambda: self._set_status(msg))

                result = fn(src, out, cb)
                setattr(self, f"_{tag}_out_path", result)
                self.after(0, lambda: progress.configure(value=100))
                self.after(0, lambda: self._log(tag, f"Tamamlandi → {result}"))
                self.after(0, lambda: self._set_status("Hazır: " + result))
                self.after(0, lambda: preview_btn.configure(state="normal"))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Hata", str(e)))
                self.after(0, lambda: self._log(tag, "HATA: " + str(e)))
                self.after(0, lambda: self._set_status("Hata oluştu."))

        threading.Thread(target=worker, daemon=True).start()

    def _save_settings(self):
        self.config_data["output_dir"]  = self.cfg_outdir.get().strip()
        self.config_data["sensitivity"] = self.sens_var.get()
        self.config_data["confidence"]  = self.conf_var.get()
        save_config(self.config_data)
        messagebox.showinfo("Kaydedildi", "Ayarlar kaydedildi.")


if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    App().mainloop()
