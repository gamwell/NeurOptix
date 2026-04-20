But du projet NeurOptix:
Optimiser les ressources CPU et RAM d'une machine Windows en combinant plusieurs techniques : compression intelligente (zstandard), traitement parallèle, monitoring en temps réel, et décisions automatiques via une IA locale (Phi3:mini via Ollama). C'est un agent autonome qui observe, décide et agit.
Organisation du projet:
OptiCPU-RAM/          ← dossier racine (nom local)
│
├── src/              ← tout le code métier
│   ├── pipeline.py           # compression zstd simple
│   ├── pipeline_parallel.py  # version multiprocessing
│   ├── pipeline_final.py     # version finale optimisée
│   ├── pipeline_monitored.py # version avec monitoring
│   ├── pipeline_torch_cpu.py # réseau de neurones CPU
│   ├── pipeline_torch_gpu.py # réseau de neurones GPU
│   ├── monitor.py            # surveillance CPU/RAM psutil
│   ├── optimizer.py          # grid search automatique
│   └── neuroptix_ai.py       # analyse IA via Ollama
│
├── tests/            ← tests unitaires
│   └── test_compression.py
│
├── dist/             ← exécutables compilés
│   ├── OptiCPU-RAM.exe       # terminal
│   └── OptiCPU-RAM-GUI.exe   # interface graphique
│
├── agent.py          ← agent autonome principal
├── gui.py            ← interface graphique tkinter
├── main.py           ← point d'entrée terminal
└── README.md
└── Claude.md		  

Règles du projet:
Il n'y avait pas de règles formellement définies dans le projet — on a codé en Python, commentaires en français quand on en a mis, mais rien d'écrit officiellement.
### Langue
- Tous les commentaires dans le code sont en français
- Les noms de variables et fonctions sont en anglais (convention Python universelle)
- Les messages affichés à l'utilisateur sont en français

### Code
- Langage : Python 3.12+
- Un fichier = une responsabilité (ex: monitor.py ne fait que surveiller)
- Toujours utiliser le virtual environment venv312_new

### Git
- Les messages de commit suivent le format : type: description (ex: feat:, fix:, docs:)
- On commit uniquement du code qui fonctionne

### Fichiers
- Le code métier va dans /src
- Les tests vont dans /tests
- Les exécutables compilés vont dans /dist
- On ne commit pas le dossier venv312_new/ ni __pycache__/
"@ | Set-Content -Path "$HOME\OptiCPU-RAM\CLAUDE.md" -Encoding UTF8
	
 

