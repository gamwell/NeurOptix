import ctypes
import psutil
import subprocess
import sys

# ==============================
# LIBÉRER LA RAM
# ==============================
def liberer_ram():
    """Tue les processus inutiles en arrière-plan"""
    # Processus à ignorer (système + notre app)
    protéges = {"system", "svchost.exe", "explorer.exe", 
                "python.exe", "powershell.exe", "msys2.exe"}
    avant = psutil.virtual_memory().percent
    tues = []
    for proc in psutil.process_iter(['name', 'memory_percent']):
        try:
            nom = proc.info['name'].lower()
            mem = proc.info['memory_percent']
            # Tue les processus qui consomment >1% RAM et non protégés
            if mem > 1.0 and nom not in protéges:
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
# TEST
# ==============================
if __name__ == "__main__":
    print(liberer_ram())
    temp = temperature_cpu()
    print(f"Température CPU : {temp}°C" if temp else "Température : non disponible")
    print(boost_cpu())
