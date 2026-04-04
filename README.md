# OptiCPU-RAM

Pipeline IA optimisé avec compression RAM, parallélisme CPU et PyTorch.

## Stack
- Python 3.12
- PyTorch 2.11
- zstandard
- psutil
- MSYS2 UCRT64

## Configuration matérielle
- CPU : Intel i5-9500 (6 cœurs)
- RAM : 32 Go

## Scripts
| Script | Description |
|--------|-------------|
| src/pipeline.py | Pipeline séquentiel de base |
| src/pipeline_parallel.py | Pipeline multiprocessing |
| src/pipeline_final.py | Pipeline + scheduler thermique |
| src/monitor.py | Monitoring CPU/RAM temps réel |
| src/pipeline_monitored.py | Pipeline + monitoring |
| src/pipeline_torch_cpu.py | Pipeline PyTorch CPU |
| src/pipeline_torch_gpu.py | Pipeline PyTorch GPU/CPU |

## Installation
```bash
python -m venv venv312_new
source venv312_new/Scripts/activate
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install numpy zstandard psutil
```

## Usage
```bash
source venv312_new/Scripts/activate
python src/pipeline_torch_cpu.py
```
