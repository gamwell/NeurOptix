import tkinter as tk
from tkinter import ttk
import multiprocessing as mp
import threading
import psutil
import time
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
from agent import Agent, CONFIG

# ==============================
# APPLICATION GUI
# ==============================
class OptiCPUApp:
    def __init__(self, root):
        self.root       = root
        self.root.title("OptiCPU-RAM")
        self.root.geometry("480x720")
        self.root.resizable(False, False)
        self.root.configure(bg="#0d0f14")

        self.agent        = None
        self.running      = False
        self.monitor_on   = True
        self.workers_var  = tk.IntVar(value=4)

        self._build_ui()
        self._start_monitor()

    # --------------------------
    # CONSTRUCTION UI
    # --------------------------
    def _build_ui(self):
        BG   = "#0d0f14"
        SURF = "#13161e"
        BDR  = "#252a38"
        TXT  = "#e8eaf0"
        MUT  = "#7a7f94"
        BLUE = "#38bdf8"
        GRN  = "#4ade80"

        # TITRE
        tk.Label(self.root, text="OptiCPU-RAM",
                 bg=BG, fg=TXT,
                 font=("Courier New", 20, "bold")).pack(pady=(20,2))
        tk.Label(self.root, text="Pipeline IA · i5-9500 · Python 3.12",
                 bg=BG, fg=MUT,
                 font=("Courier New", 9)).pack(pady=(0,16))

        # CADRE MONITORING
        frame_mon = tk.Frame(self.root, bg=SURF,
                             highlightbackground=BDR,
                             highlightthickness=1)
        frame_mon.pack(fill="x", padx=20, pady=4)

        tk.Label(frame_mon, text="MONITORING SYSTÈME",
                 bg=SURF, fg=MUT,
                 font=("Courier New", 8, "bold")).pack(anchor="w", padx=12, pady=(10,4))

        # CPU
        f_cpu = tk.Frame(frame_mon, bg=SURF)
        f_cpu.pack(fill="x", padx=12, pady=2)
        tk.Label(f_cpu, text="CPU", bg=SURF, fg=BLUE,
                 font=("Courier New", 10, "bold"), width=5,
                 anchor="w").pack(side="left")
        self.cpu_bar = ttk.Progressbar(f_cpu, length=260,
                                        mode="determinate", maximum=100)
        self.cpu_bar.pack(side="left", padx=8)
        self.cpu_lbl = tk.Label(f_cpu, text="0.0%", bg=SURF, fg=TXT,
                                 font=("Courier New", 10), width=6)
        self.cpu_lbl.pack(side="left")

        # RAM
        f_ram = tk.Frame(frame_mon, bg=SURF)
        f_ram.pack(fill="x", padx=12, pady=(2,10))
        tk.Label(f_ram, text="RAM", bg=SURF, fg=GRN,
                 font=("Courier New", 10, "bold"), width=5,
                 anchor="w").pack(side="left")
        self.ram_bar = ttk.Progressbar(f_ram, length=260,
                                        mode="determinate", maximum=100)
        self.ram_bar.pack(side="left", padx=8)
        self.ram_lbl = tk.Label(f_ram, text="0.0%", bg=SURF, fg=TXT,
                                 font=("Courier New", 10), width=6)
        self.ram_lbl.pack(side="left")

        # CADRE CONFIG
        frame_cfg = tk.Frame(self.root, bg=SURF,
                              highlightbackground=BDR,
                              highlightthickness=1)
        frame_cfg.pack(fill="x", padx=20, pady=4)

        tk.Label(frame_cfg, text="CONFIGURATION",
                 bg=SURF, fg=MUT,
                 font=("Courier New", 8, "bold")).pack(anchor="w", padx=12, pady=(10,4))

        f_w = tk.Frame(frame_cfg, bg=SURF)
        f_w.pack(fill="x", padx=12, pady=(0,10))
        tk.Label(f_w, text="Workers :", bg=SURF, fg=TXT,
                 font=("Courier New", 10)).pack(side="left")
        for w in [1, 2, 3, 4]:
            tk.Radiobutton(f_w, text=str(w),
                           variable=self.workers_var, value=w,
                           bg=SURF, fg=TXT,
                           selectcolor="#1a1e28",
                           activebackground=SURF,
                           font=("Courier New", 10)).pack(side="left", padx=8)

        # CADRE RÉSULTATS
        frame_res = tk.Frame(self.root, bg=SURF,
                              highlightbackground=BDR,
                              highlightthickness=1)
        frame_res.pack(fill="x", padx=20, pady=4)

        tk.Label(frame_res, text="RÉSULTATS",
                 bg=SURF, fg=MUT,
                 font=("Courier New", 8, "bold")).pack(anchor="w", padx=12, pady=(10,4))

        self.status_lbl = tk.Label(frame_res,
                                    text="En attente...",
                                    bg=SURF, fg=MUT,
                                    font=("Courier New", 10))
        self.status_lbl.pack(anchor="w", padx=12)

        self.cycle_lbl = tk.Label(frame_res,
                                   text="Cycle — / —",
                                   bg=SURF, fg=TXT,
                                   font=("Courier New", 10))
        self.cycle_lbl.pack(anchor="w", padx=12)

        self.time_lbl = tk.Label(frame_res,
                                  text="Temps : —",
                                  bg=SURF, fg=TXT,
                                  font=("Courier New", 10))
        self.time_lbl.pack(anchor="w", padx=12)

        self.score_lbl = tk.Label(frame_res,
                                   text="Score : —",
                                   bg=SURF, fg=GRN,
                                   font=("Courier New", 10))
        self.score_lbl.pack(anchor="w", padx=12, pady=(0,10))

        # LOG
        frame_log = tk.Frame(self.root, bg=SURF,
                              highlightbackground=BDR,
                              highlightthickness=1)
        frame_log.pack(fill="x", padx=20, pady=4)

        tk.Label(frame_log, text="LOG",
                 bg=SURF, fg=MUT,
                 font=("Courier New", 8, "bold")).pack(anchor="w", padx=12, pady=(8,4))

        self.log = tk.Text(frame_log, height=6,
                            bg="#0a0c10", fg="#7a7f94",
                            font=("Courier New", 9),
                            relief="flat", state="disabled",
                            insertbackground="white")
        self.log.pack(fill="x", padx=12, pady=(0,10))

        # BOUTONS
        frame_btn = tk.Frame(self.root, bg=BG)
        frame_btn.pack(pady=12)

        self.btn_start = tk.Button(frame_btn,
                                    text="▶  Lancer l'agent",
                                    command=self._lancer,
                                    bg="#1a3a5c", fg="#38bdf8",
                                    font=("Courier New", 11, "bold"),
                                    relief="flat", padx=20, pady=8,
                                    cursor="hand2")
        self.btn_start.pack(side="left", padx=8)

        self.btn_stop = tk.Button(frame_btn,
                                   text="■  Arrêter",
                                   command=self._arreter,
                                   bg="#2a1a1a", fg="#ef4444",
                                   font=("Courier New", 11, "bold"),
                                   relief="flat", padx=20, pady=8,
                                   cursor="hand2",
                                   state="disabled")
        self.btn_stop.pack(side="left", padx=8)

    # --------------------------
    # MONITORING TEMPS RÉEL
    # --------------------------
    def _start_monitor(self):
        def loop():
            while self.monitor_on:
                cpu = psutil.cpu_percent(interval=0.5)
                ram = psutil.virtual_memory().percent
                self.cpu_bar["value"] = cpu
                self.ram_bar["value"] = ram
                self.cpu_lbl.config(text=f"{cpu:.1f}%")
                self.ram_lbl.config(text=f"{ram:.1f}%")
        threading.Thread(target=loop, daemon=True).start()

    # --------------------------
    # LOG
    # --------------------------
    def _log(self, msg):
        self.log.config(state="normal")
        self.log.insert("end", f"→ {msg}\n")
        self.log.see("end")
        self.log.config(state="disabled")

    # --------------------------
    # LANCER L'AGENT
    # --------------------------
    def _lancer(self):
        if self.running:
            return
        self.running = True
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        CONFIG["max_workers"] = self.workers_var.get()
        threading.Thread(target=self._run_agent, daemon=True).start()

    def _run_agent(self):
        self.agent = Agent()
        self._log(f"Agent démarré · {CONFIG['max_workers']} workers")

        for cycle in range(1, CONFIG["cycles"] + 1):
            if not self.running:
                break
            self.agent.cycle = cycle
            self.cycle_lbl.config(text=f"Cycle {cycle} / {CONFIG['cycles']}")
            self.status_lbl.config(text="En cours...")

            etat     = self.agent.observer()
            decision = self.agent.decider(etat)
            self._log(f"Cycle {cycle} · CPU {etat['cpu']:.1f}%")
            self._log(decision)

            perf = self.agent.agir()
            self.agent.apprendre(perf)

            self.time_lbl.config(text=f"Temps : {perf['temps']}s")
            self.score_lbl.config(text=f"Score : {perf['resultat']:.2f}")
            self._log(f"Résultat : {perf['temps']}s · {perf['resultat']:.2f}")

            time.sleep(CONFIG["sleep_cycle"])

        self.status_lbl.config(text="Terminé ✓")
        self._log("Agent terminé")
        self.running = False
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")

    # --------------------------
    # ARRÊTER
    # --------------------------
    def _arreter(self):
        self.running = False
        self.monitor_on = False
        self._log("Arrêt demandé...")
        self.btn_stop.config(state="disabled")

# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    mp.freeze_support()
    root = tk.Tk()
    app  = OptiCPUApp(root)
    root.mainloop()


