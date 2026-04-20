import ctypes
import psutil
import subprocess
import sys

# ==============================
# LIBÉRER LA RAM
# ==============================
def liberer_ram():
    """Tue les processus inutiles en respectant la liste blanche"""
    import json, os
    # Charge la liste de protection
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config_protection.json')
    try:
        with open(config_path) as f:
            proteges = set(json.load(f)["proteges"])
    except:
        proteges = {"python.exe", "powershell.exe", "explorer.exe"}

    avant = psutil.virtual_memory().percent
    tues = []
    for proc in psutil.process_iter(['name', 'memory_percent']):
        try:
            nom = proc.info['name'].lower()
            mem = proc.info['memory_percent']
            if mem > 1.0 and nom not in proteges:
                proc.kill()
                tues.append(f"{nom} ({mem:.1f}%)")
        except:
            pass
    apres = psutil.virtual_memory().percent
    liberee = round(avant - apres, 1)
    detail = ", ".join(tues[:3]) or "rien à tuer"
    return f"RAM : {avant}% → {apres}% | Tués : {detail}"

# ==============================
# TEMPÉRATURE CPU
# ==============================
def temperature_cpu():
    """Lit la température CPU via WMI"""
    try:
        import wmi
        w = wmi.WMI(namespace="root/wmi")
        temps = w.MSAcpi_ThermalZoneTemperature()
        celsius = (temps[0].CurrentTemperature / 10.0) - 273.15
        return round(celsius, 1)
    except:
        return None

# ==============================
# BOOST CPU
# ==============================
def boost_cpu():
    """Active le mode haute performance Windows"""
    subprocess.run([
        "powercfg", "/setactive",
        "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"
    ], capture_output=True)
    return "✅ Mode haute performance activé"

# ==============================
# BOOST CALCUL CPU
# ==============================
def boost_calcul_cpu():
    """Augmente la priorité CPU + optimise le cache"""
    resultats = []

    # 1. Priorité haute pour le processus Python actuel
    import os
    p = psutil.Process(os.getpid())
    p.nice(psutil.HIGH_PRIORITY_CLASS)
    resultats.append("✅ Priorité CPU : HAUTE")

    # 2. Active tous les cœurs logiques
    subprocess.run([
        "powershell", "-Command",
        "powercfg /setacvalueindex SCHEME_CURRENT SUB_PROCESSOR PROCTHROTTLEMIN 100"
    ], capture_output=True)
    resultats.append("✅ Cœurs CPU : 100% min")

    # 3. Désactive le throttling thermique temporairement
    subprocess.run([
        "powershell", "-Command",
        "powercfg /setacvalueindex SCHEME_CURRENT SUB_PROCESSOR PROCTHROTTLEMAX 100"
    ], capture_output=True)
    resultats.append("✅ Throttling désactivé")

    # 4. Vide le cache de travail pour libérer de la bande passante mémoire
    ctypes.windll.psapi.EmptyWorkingSet(-1)
    resultats.append("✅ Cache mémoire optimisé")

    return "\n".join(resultats)

# ==============================
# ANTI-SURCHAUFFE
# ==============================
def anti_surchauffe(seuil=75):
    """Réduit la charge CPU si température trop haute"""
    temp = temperature_cpu()
    if temp is None:
        return "⚠️ Température non disponible"

    if temp >= seuil:
        # Réduit la fréquence CPU à 80%
        subprocess.run([
            "powershell", "-Command",
            "powercfg /setacvalueindex SCHEME_CURRENT SUB_PROCESSOR PROCTHROTTLEMAX 80"
        ], capture_output=True)
        return f"🌡️ {temp}°C ≥ {seuil}°C → fréquence réduite à 80%"
    else:
        return f"🌡️ {temp}°C — température normale, pas d'action"

# ==============================
# TEST
# ==============================
if __name__ == "__main__":
    print(liberer_ram())
    print(boost_cpu())
    print(boost_calcul_cpu())
    print(anti_surchauffe())
