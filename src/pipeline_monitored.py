import zstandard as zstd
import multiprocessing as mp
import psutil
import random
import time
import threading
import os

# --- CONFIG i5-9500 ---
BATCH_SIZE   = 1000
MAX_WORKERS  = 4
CPU_LIMIT    = 75.0

# --- MONITORING (tourne en arrière-plan) ---
monitoring_actif = True

def afficher_barre(valeur, largeur=20):
    rempli = int((valeur / 100) * largeur)
    return f"[{'█' * rempli}{'░' * (largeur - rempli)}] {valeur:5.1f}%"

def monitor_loop():
    while monitoring_actif:
        cpu_cores = psutil.cpu_percent(interval=None, percpu=True)
        ram       = psutil.virtual_memory()
        cpu_moy   = sum(cpu_cores) / len(cpu_cores)

        os.system("clear")
        print("=" * 50)
        print("  📊 MONITORING EN TEMPS RÉEL")
        print("=" * 50)

        for i, usage in enumerate(cpu_cores):
            print(f"  Cœur {i+1} : {afficher_barre(usage)}")

        print(f"\n  Moyenne : {afficher_barre(cpu_moy)}")
        print(f"\n💾 RAM utilisée : {afficher_barre(ram.percent)}")
        print(f"   {ram.used // 1024**2} Mo / {ram.total // 1024**2} Mo")
        print("=" * 50)

        time.sleep(0.5)

# --- COMPRESSION ---
def compress_data(data: bytes) -> bytes:
    return zstd.ZstdCompressor().compress(data)

def decompress_data(data: bytes) -> bytes:
    return zstd.ZstdDecompressor().decompress(data)

# --- DATASET ---
def generate_data(n=10000):
    return [random.randint(0, 1000) for _ in range(n)]

def serialize(batch):
    return ",".join(map(str, batch)).encode()

def deserialize(data):
    return list(map(int, data.decode().split(",")))

# --- TRAITEMENT ---
def process_batch(compressed_batch):
    raw    = decompress_data(compressed_batch)
    batch  = deserialize(raw)
    result = [x ** 4 + x ** 3 - x ** 2 for x in batch]
    time.sleep(0.01)
    return sum(result)

# --- SCHEDULER ---
def get_optimal_workers():
    cpu = psutil.cpu_percent(interval=0.5)
    if cpu > CPU_LIMIT:
        return max(1, MAX_WORKERS // 2)
    return MAX_WORKERS

# --- PIPELINE ---
def create_batches(data):
    for i in range(0, len(data), BATCH_SIZE):
        yield data[i:i + BATCH_SIZE]

# --- MAIN ---
if __name__ == "__main__":
    
    # Démarre le monitoring en arrière-plan
    thread = threading.Thread(target=monitor_loop, daemon=True)
    thread.start()

    time.sleep(1)  # laisse le monitoring s'afficher

    # Pipeline
    data = generate_data(200000)
    compressed_batches = []
    for batch in create_batches(data):
        compressed_batches.append(compress_data(serialize(batch)))

    workers = get_optimal_workers()

    t1 = time.time()
    with mp.Pool(workers) as pool:
        results = pool.map(process_batch, compressed_batches)
    t2 = time.time()

    # Arrête le monitoring
    monitoring_actif = False
    time.sleep(0.6)

    os.system("clear")
    print("=" * 50)
    print("  ✅ PIPELINE TERMINÉ")
    print("=" * 50)
    print(f"  Workers utilisés : {workers}")
    print(f"  Temps            : {t2-t1:.2f}s")
    print(f"  Résultat final   : {sum(results)}")
    print("=" * 50)
