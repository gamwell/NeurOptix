import sys
import multiprocessing as mp
import time
from agent import Agent, CONFIG

if __name__ == "__main__":
    mp.freeze_support()

    print("="*50)
    print("  OptiCPU-RAM — Pipeline IA")
    print("="*50)
    print("  1. Lancer l'agent autonome")
    print("  2. Quitter")
    print("="*50)

    choix = input("\nTon choix (1 ou 2) : ").strip()

    if choix == "1":
        agent = Agent()
        for cycle in range(1, CONFIG["cycles"] + 1):
            agent.cycle = cycle
            print(f"\n--- CYCLE {cycle}/{CONFIG['cycles']} ---")
            etat     = agent.observer()
            decision = agent.decider(etat)
            print(f"  CPU {etat['cpu']:.1f}% · {decision}")
            perf     = agent.agir()
            print(f"  Temps : {perf['temps']}s · score : {perf['resultat']:.2f}")
            agent.apprendre(perf)
            time.sleep(CONFIG["sleep_cycle"])
        agent.rapport()

    else:
        print("Au revoir !")

    input("\nAppuie sur Entrée pour quitter...")
