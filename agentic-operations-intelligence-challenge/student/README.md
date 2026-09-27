# Student editable area

Students modify only their assigned team folder:

```text
student/team_X/
├── models/
│   ├── spec.json       # interface contract; do not change
│   ├── model_a.pt      # trained/exported by students
│   └── model_b.pt
├── rag/
│   └── config.yaml     # editable
└── skills/
    └── *.md            # editable
```

Starter training:

```bash
python student/train_pytorch.py --team team_X --model model_a
python student/train_pytorch.py --team team_X --model model_b
```

Students may improve architecture, training, regularization and hyperparameters. Final artifacts must be TorchScript-compatible with `spec.json`.
