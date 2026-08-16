# Cœur d'apprentissage (hyperparams + F1 + erreurs)

## Pipeline
1. Fragmentation → 2. Features → 3. Labels bootstrap → 4. Features labellisées
5. **RandomizedSearchCV** (F1-macro) sur DT/RF/ExtraTrees/GB
6. **Analyse F1** par classe + confusions + diagnostics
7. Re-tri modèle

## Logs
- `data/models/hyperparam_search.json`
- `data/models/f1_error_analysis.json`
- `data/models/metrics.json`

## Erreurs
`ml/errors.py` : InsufficientData, TrainingFailed, LowQualityModel, ModelNotFound, PredictionFailed

```bash
python start_train.py
python start_train.py --skip-hyper
```
