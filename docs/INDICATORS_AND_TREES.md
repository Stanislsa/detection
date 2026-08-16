# Indicateurs, features et arbres

## Indicateurs (21)
- **motion**: motion_mean, motion_max, motion_std, motion_energy, optical_flow_mag
- **appearance**: luma_*, edge_density, hist_b0..b7
- **dynamics**: n_frames, motion_trend, stillness_ratio

## Stockage features
```
data/features/raw/<id>.json
data/features/processed/features_table.csv, X.npy, y.npy
data/features/by_class/{normal,urgent,critique}.csv
```

## Arbres
- DecisionTreeClassifier → trees_export/tree_decision_rules.txt
- RandomForestClassifier → data/models/severity_trees.joblib

```bash
python start_train.py
python start_train.py --list-indicators
python start_train.py --describe-trees
```
