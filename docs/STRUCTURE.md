# Structure SentinelAI

```
detection/
├── start.py / start.sh / start_train.py / run_app.py
├── requirements.txt / .env.example
├── backend/          # FastAPI + IA + services
├── desktop/          # PyQt6 + QML
├── ml/               # Apprentissage
├── scripts/          # Outils (QA, train, RTSP, verify)
├── docs/             # Guides
├── data/             # Runtime (db, models, features)
├── données/vidéo/    # Vidéos source train
└── native/           # C++ ONNX optionnel
```

Voir `docs/GUIDE_LANCEMENT.md` pour le lancement.
