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

class OptiCPUApp:
    def __init__(self, root):
        self.root      = root
        self.root.title("NeurOptix")
        self.root.geometry("480x820")
        self.root.resizable(False, False)
        self.root.configure(bg="#0d0f14")
        self.agent       = None
        self.running     = False
        self.monitor_on  = True
        self.workers_var = tk.IntVar(value=4)
        self._build_ui()
        self._start_monitor()

    def _build_ui(self):
        BG   = "#0d0f14"
        SURF = "#13161e"
        BDR  = "#252a38"
        TXT  = "#e8eaf0"
        MUT  = "#7a7f94"
        BLUE = "#38bdf8"
        GRN  = "#4ade80"

        # TITRE
        tk.Label(self.root, text="NeurOptix",
                 bg=BG, fg=TXT,
                 font=("Courier New", 20, "bold")).pack(pady=(20,2))
        tk.Label(self.root, text="Pipeline IA · i5-9500 · Python 3.12",
                 bg=BG, fg=MUT,
                 font=("Courier New", 9)).pack(pady=(0,16))

        # MONITORING
        frame_mon = tk.Frame(self.root, bg=SURF,
                             highlightbackground=BDR, highlightthickness=1)
        frame_mon.pack(fill="x", padx=20, pady=4)
        tk.Label(frame_mon, text="MONITORING SYSTÈME",
                 bg=SURF, fg=MUT,
                 font=("Courier New", 8, "bold")).pack(anchor="w", padx=12, pady=(10,4))

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
        # OPTIMISATION
        frame_opt = tk.Frame(self.root, bg=SURF,
                             highlightbackground=BDR, highlightthickness=1)
        frame_opt.pack(fill="x", padx=20, pady=4)
        tk.Label(frame_opt, text="OPTIMISATION",
                 bg=SURF, fg=MUT,
                 font=("Courier New", 8, "bold")).pack(anchor="w", padx=12, pady=(10,4))
        f_btns = tk.Frame(frame_opt, bg=SURF)
        f_btns.pack(fill="x", padx=12, pady=(0,10))
        self.btn_ram = tk.Button(f_btns, text="🧹 RAM",
                 bg="#1e293b", fg=TXT, font=("Courier New", 10, "bold"),
                 relief="flat", cursor="hand2", command=self._liberer_ram)
        self.btn_ram.pack(side="left", padx=4, pady=2, ipadx=8, ipady=4)
        self.btn_boost = tk.Button(f_btns, text="⚡ Boost",
                 bg="#1e293b", fg=TXT, font=("Courier New", 10, "bold"),
                 relief="flat", cursor="hand2", command=self._boost_cpu)
        self.btn_boost.pack(side="left", padx=4, pady=2, ipadx=8, ipady=4)
        self.btn_temp = tk.Button(f_btns, text="🌡️ Temp",
                 bg="#1e293b", fg=TXT, font=("Courier New", 10, "bold"),
                 relief="flat", cursor="hand2", command=self._check_temp)
        self.btn_temp.pack(side="left", padx=4, pady=2, ipadx=8, ipady=4)

        # CONFIG
        frame_cfg = tk.Frame(self.root, bg=SURF,
                              highlightbackground=BDR, highlightthickness=1)
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

        # RÉSULTATS
        frame_res = tk.Frame(self.root, bg=SURF,
                              highlightbackground=BDR, highlightthickness=1)
        frame_res.pack(fill="x", padx=20, pady=4)
        tk.Label(frame_res, text="RÉSULTATS",
                 bg=SURF, fg=MUT,
                 font=("Courier New", 8, "bold")).pack(anchor="w", padx=12, pady=(10,4))
        self.status_lbl = tk.Label(frame_res, text="En attente...",
                                    bg=SURF, fg=MUT,
                                    font=("Courier New", 10))
        self.status_lbl.pack(anchor="w", padx=12)
        self.cycle_lbl = tk.Label(frame_res, text="Cycle — / —",
                                   bg=SURF, fg=TXT,
                                   font=("Courier New", 10))
        self.cycle_lbl.pack(anchor="w", padx=12)
        self.time_lbl = tk.Label(frame_res, text="Temps : —",
                                  bg=SURF, fg=TXT,
                                  font=("Courier New", 10))
        self.time_lbl.pack(anchor="w", padx=12)
        self.score_lbl = tk.Label(frame_res, text="Score : —",
                                   bg=SURF, fg=GRN,
                                   font=("Courier New", 10))
        self.score_lbl.pack(anchor="w", padx=12, pady=(0,10))

        # LOG
        frame_log = tk.Frame(self.root, bg=SURF,
                              highlightbackground=BDR, highlightthickness=1)
        frame_log.pack(fill="x", padx=20, pady=4)
        tk.Label(frame_log, text="LOG",
                 bg=SURF, fg=MUT,
                 font=("Courier New", 8, "bold")).pack(anchor="w", padx=12, pady=(8,4))
        self.log = tk.Text(frame_log, height=5,
                            bg="#0a0c10", fg="#7a7f94",
                            font=("Courier New", 9),
                            relief="flat", state="disabled",
                            insertbackground="white")
        self.log.pack(fill="x", padx=12, pady=(0,10))

        # ANALYSE IA
        frame_ia = tk.Frame(self.root, bg=SURF,
                             highlightbackground=BDR, highlightthickness=1)
        frame_ia.pack(fill="x", padx=20, pady=4)
        tk.Label(frame_ia, text="ANALYSE IA LOCALE (Phi3:mini)",
                 bg=SURF, fg=MUT,
                 font=("Courier New", 8, "bold")).pack(anchor="w", padx=12, pady=(8,4))
        self.ia_text = tk.Text(frame_ia, height=5,
                                bg="#0a0c10", fg="#a78bfa",
                                font=("Courier New", 9),
                                relief="flat", state="disabled",
                                wrap="word")
        self.ia_text.pack(fill="x", padx=12, pady=(0,10))

        # BOUTONS
        # LIGNE 1 : Lancer + Arrêter
        frame_btn1 = tk.Frame(self.root, bg=BG)
        frame_btn1.pack(pady=(12,4))
        self.btn_start = tk.Button(frame_btn1, text="▶  Lancer l'agent", command=self._lancer, bg="#1a3a5c", fg="#38bdf8", font=("Courier New", 11, "bold"), relief="flat", padx=20, pady=8, cursor="hand2")
        self.btn_start.pack(side="left", padx=8)
        self.btn_stop = tk.Button(frame_btn1, text="■  Arrêter", command=self._arreter, bg="#2a1a1a", fg="#ef4444", font=("Courier New", 11, "bold"), relief="flat", padx=20, pady=8, cursor="hand2", state="disabled")
        self.btn_stop.pack(side="left", padx=8)

        # LIGNE 2 : Analyse IA
        frame_btn2 = tk.Frame(self.root, bg=BG)
        frame_btn2.pack(pady=(0,12))
        self.btn_ia = tk.Button(frame_btn2, text="🧠  Analyse IA (Phi3:mini)", command=self._analyser_ia, bg="#2a1535", fg="#a78bfa", font=("Courier New", 11, "bold"), relief="flat", padx=20, pady=8, cursor="hand2", state="disabled")
        self.btn_ia.pack()

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

    def _log(self, msg):
        self.log.config(state="normal")
        self.log.insert("end", f"→ {msg}\n")
        self.log.see("end")
        self.log.config(state="disabled")

    def _lancer(self):
        if self.running:
            return
        self.running = True
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.btn_ia.config(state="disabled")
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
        self.btn_ia.config(state="normal")

    def _afficher_ia(self, texte):
        self.ia_text.config(state="normal")
        self.ia_text.delete("1.0", "end")
        self.ia_text.insert("end", texte)
        self.ia_text.config(state="disabled")

    def _analyser_ia(self):
        if not self.agent or not self.agent.historique:
            self._afficher_ia("Lance d'abord l'agent pour avoir des données.")
            return
        self.btn_ia.config(state="disabled", text="Analyse...")
        self._afficher_ia("Analyse en cours...")

        def run():
            sys.path.insert(0, os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "src"))
            from neuroptix_ai import analyser_avec_ia
            historique = [
                {"workers": h["workers"],
                 "temps"  : h["temps"],
                 "score"  : h["resultat"]}
                for h in self.agent.historique
            ]
            conseil = analyser_avec_ia(historique)
            self._afficher_ia(conseil)
            self.btn_ia.config(state="normal", text="Analyse IA")

        threading.Thread(target=run, daemon=True).start()
    def _liberer_ram(self):
        self.btn_ram.config(state="disabled", text="...")
        def run():
            from optimizer_v2 import liberer_ram
            resultat = liberer_ram()
            self._log(resultat)
            self.btn_ram.config(state="normal", text="🧹 RAM")
        threading.Thread(target=run, daemon=True).start()

    def _boost_cpu(self):
        self.btn_boost.config(state="disabled", text="...")
        def run():
            from optimizer_v2 import boost_cpu, boost_calcul_cpu
            self._log(boost_cpu())
            self._log(boost_calcul_cpu())
            self.btn_boost.config(state="normal", text="⚡ Boost")
        threading.Thread(target=run, daemon=True).start()

    def _check_temp(self):
        from optimizer_v2 import anti_surchauffe
        resultat = anti_surchauffe()
        self._log(resultat)

    def _arreter(self):
        self.running = False
        self._log("Arrêt demandé...")
        self.btn_stop.config(state="disabled")

    def _arreter(self):
        self.running = False
        self._log("Arrêt demandé...")
        self.btn_stop.config(state="disabled")

if __name__ == "__main__":
    mp.freeze_support()
    root = tk.Tk()
    app  = OptiCPUApp(root)
    root.mainloop()

