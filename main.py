import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import json
import os
from pathlib import Path
from typing import Optional, Dict

from video_processor import ANIMAL_COLORS, TARGET_COLORS

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
    }


def save_config(cfg: Dict):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hayvan Renk Değiştirici")
        self.geometry("860x680")
        self.minsize(760, 560)
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
        tk.Label(hdr, text="Hayvan Renk Değiştirici",
                 font=("Segoe UI", 17, "bold"), bg="#0f0f1a", fg="#ff3c78"
                 ).pack(side="left", padx=18, pady=10)
        tk.Label(hdr, text="YouTube URL yapıştır → hayvan rengini seç → değiştir",
                 font=("Segoe UI", 9), bg="#0f0f1a", fg="#666"
                 ).pack(side="left")
        tk.Frame(self, height=2, bg="#ff3c78").pack(fill="x")

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)

        self.tab_main = ttk.Frame(nb)
        self.tab_cfg  = ttk.Frame(nb)
        nb.add(self.tab_main, text="  Renk Değiştir  ")
        nb.add(self.tab_cfg,  text="  Ayarlar  ")

        self._build_main_tab()
        self._build_settings_tab()

        self.status_var = tk.StringVar(value="Hazır")
        tk.Label(self, textvariable=self.status_var, bg="#1a1a2e", fg="#aaa",
                 anchor="w", padx=10, font=("Segoe UI", 9)
                 ).pack(fill="x", side="bottom")

    def _build_main_tab(self):
        p = ttk.Frame(self.tab_main)
        p.pack(fill="both", expand=True, padx=16, pady=12)

        # URL
        url_frame = ttk.LabelFrame(p, text="YouTube URL", padding=10)
        url_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(url_frame, text="URL:").grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.url_entry = ttk.Entry(url_frame, width=58)
        self.url_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        ttk.Button(url_frame, text="Videoyu İndir", style="Accent.TButton",
                   command=self._download).grid(row=0, column=2)
        url_frame.columnconfigure(1, weight=1)
        self.dl_status = ttk.Label(url_frame, text="", foreground="#aaa",
                                   font=("Segoe UI", 8))
        self.dl_status.grid(row=1, column=0, columnspan=3, sticky="w", pady=(4, 0))

        # Renk ayarlari
        color_frame = ttk.LabelFrame(p, text="Renk Ayarları", padding=10)
        color_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(color_frame, text="Hayvan Rengi:").grid(row=0, column=0, sticky="w", padx=(0, 10), pady=4)
        self.animal_combo = ttk.Combobox(color_frame, values=list(ANIMAL_COLORS.keys()),
                                         width=22, state="readonly")
        self.animal_combo.set(list(ANIMAL_COLORS.keys())[0])
        self.animal_combo.grid(row=0, column=1, sticky="w", pady=4)

        ttk.Label(color_frame, text="Yeni Renk:").grid(row=0, column=2, sticky="w", padx=(20, 10), pady=4)
        self.target_combo = ttk.Combobox(color_frame, values=list(TARGET_COLORS.keys()),
                                          width=14, state="readonly")
        self.target_combo.set("Mavi")
        self.target_combo.grid(row=0, column=3, sticky="w", pady=4)

        ttk.Label(color_frame, text="Hassasiyet:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=4)
        self.sens_var = tk.IntVar(value=self.config_data.get("sensitivity", 15))
        sens_scale = ttk.Scale(color_frame, from_=5, to=40, variable=self.sens_var,
                               orient="horizontal", length=160)
        sens_scale.grid(row=1, column=1, sticky="w", pady=4)
        sens_lbl = ttk.Label(color_frame, text="15", foreground="#aaa", width=3)
        sens_lbl.grid(row=1, column=2, sticky="w", padx=(8, 0))
        self.sens_var.trace_add("write", lambda *_: sens_lbl.configure(
            text=str(self.sens_var.get())))

        # Islem
        btn_row = ttk.Frame(p)
        btn_row.pack(fill="x", pady=(0, 6))
        ttk.Button(btn_row, text="Rengi Değiştir", style="Accent.TButton",
                   command=self._process).pack(side="left", padx=(0, 10))
        self.preview_btn = ttk.Button(btn_row, text="▶  İzle", style="Green.TButton",
                                      state="disabled", command=self._preview)
        self.preview_btn.pack(side="left")

        self.progress = ttk.Progressbar(p, mode="determinate", maximum=100)
        self.progress.pack(fill="x", pady=(6, 4))

        self.log_box = scrolledtext.ScrolledText(p, height=6, bg="#1a1a2e", fg="#ccc",
                                                  font=("Consolas", 8), state="disabled",
                                                  relief="flat")
        self.log_box.pack(fill="both", expand=True)

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

    def _set_status(self, msg: str):
        self.status_var.set(msg)

    def _log(self, msg: str):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def _preview(self):
        if self.output_path and os.path.exists(self.output_path):
            os.startfile(self.output_path)

    def _download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Eksik", "Bir YouTube URL'si girin.")
            return
        self.downloaded_path = None
        self.dl_status.configure(text="İndiriliyor...", foreground="#aaa")
        self._set_status("Video indiriliyor...")

        def worker():
            try:
                from video_processor import download_video
                out_dir = self.config_data.get("output_dir", "output_videos")

                def cb(cur, total, msg):
                    self.after(0, lambda: self.dl_status.configure(text=msg))
                    self.after(0, lambda: self._set_status(msg))

                path = download_video(url, out_dir, callback=cb)
                self.downloaded_path = path
                self.after(0, lambda: self.dl_status.configure(
                    text=f"İndirildi: {Path(path).name}", foreground="#44ff88"))
                self.after(0, lambda: self._set_status("Video indirildi."))
            except Exception as e:
                self.after(0, lambda: self.dl_status.configure(
                    text=f"Hata: {str(e)[:80]}", foreground="#ff6666"))
                self.after(0, lambda: self._set_status("İndirme hatası."))

        threading.Thread(target=worker, daemon=True).start()

    def _process(self):
        if not self.downloaded_path or not os.path.exists(self.downloaded_path):
            messagebox.showwarning("Video Yok", "Önce bir YouTube URL'si indirin.")
            return

        animal_color = self.animal_combo.get()
        target_color = self.target_combo.get()
        sensitivity  = self.sens_var.get()

        self.progress["value"] = 0
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")
        self.output_path = None
        self.preview_btn.configure(state="disabled")
        self._set_status("İşleniyor...")

        def worker():
            try:
                from video_processor import process_video
                src = self.downloaded_path
                out = src.replace(".mp4", f"_{target_color}.mp4")

                def cb(cur, total, msg):
                    pct = int(cur / max(total, 1) * 100)
                    self.after(0, lambda: self.progress.configure(value=pct))
                    self.after(0, lambda: self._log(msg))
                    self.after(0, lambda: self._set_status(msg))

                path = process_video(src, out, animal_color, target_color, sensitivity, cb)
                self.output_path = path
                self.after(0, lambda: self.progress.configure(value=100))
                self.after(0, lambda: self._log(f"Tamamlandi → {path}"))
                self.after(0, lambda: self._set_status("Hazır: " + path))
                self.after(0, lambda: self.preview_btn.configure(state="normal"))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Hata", str(e)))
                self.after(0, lambda: self._log("HATA: " + str(e)))
                self.after(0, lambda: self._set_status("Hata oluştu."))

        threading.Thread(target=worker, daemon=True).start()

    def _save_settings(self):
        self.config_data["output_dir"] = self.cfg_outdir.get().strip()
        self.config_data["sensitivity"] = self.sens_var.get()
        save_config(self.config_data)
        messagebox.showinfo("Kaydedildi", "Ayarlar kaydedildi.")


if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    App().mainloop()
