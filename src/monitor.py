import psutil
import time
import os

# --- CONFIG ---
INTERVAL = 0.5      # mesure toutes les 0.5 secondes
DUREE    = 30       # surveille pendant 30 secondes

def get_stats():
    cpu     = psutil.cpu_percent(interval=None, percpu=True)  # par cœur
    ram     = psutil.virtual_memory()
    return cpu, ram

def afficher_barre(valeur, max_val=100, largeur=20):
    """Affiche une barre de progression ASCII"""
    rempli = int((valeur / max_val) * largeur)
    barre  = "█" * rempli + "░" * (largeur - rempli)
    return f"[{barre}] {valeur:5.1f}%"

def afficher_stats():
    cpu_cores, ram = get_stats()

    # Efface l'écran
    os.system("clear")

    print("=" * 50)
    print("  📊 MONITORING OptiCPU-RAM  ")
    print("=" * 50)

    # CPU par cœur
    print("\n🖥️  CPU i5-9500 (6 cœurs) :")
    for i, usage in enumerate(cpu_cores):
        print(f"  Cœur {i+1} : {afficher_barre(usage)}")

    cpu_global = sum(cpu_cores) / len(cpu_cores)
    print(f"\n  Moyenne : {afficher_barre(cpu_global)}")

    # Seuil thermique
    if cpu_global > 75:
        print("  ⚠️  CHARGE ÉLEVÉE - workers réduits")
    elif cpu_global > 50:
        print("  🟡 Charge modérée")
    else:
        print("  ✅ Charge normale")

    # RAM
    print(f"\n💾 RAM :")
    print(f"  Utilisée : {afficher_barre(ram.percent)}")
    print(f"  Détail   : {ram.used // 1024**2} Mo / {ram.total // 1024**2} Mo")
    print(f"  Libre    : {ram.available // 1024**2} Mo")

    print("\n" + "=" * 50)
    print("  Ctrl+C pour arrêter")
    print("=" * 50)

# --- MAIN ---
if __name__ == "__main__":
    print("Démarrage du monitoring...")
    time.sleep(1)
    try:
        while True:
            afficher_stats()
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        print("\n\n✅ Monitoring arrêté.")
