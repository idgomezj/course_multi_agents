# Student editable area

The runtime application and evaluator are provided. Your team is responsible for teaching the system how to operate your assigned case through **PyTorch models, RAG, and Skills**.

## Your team workspace

```text
student/team_X/
├── training/
│   ├── CASE_TRAINING.md
│   ├── raw_case_history.csv
│   ├── model_contract.json
│   ├── model_a_training.csv      # YOU create this
│   └── model_b_training.csv      # YOU create this
├── models/
│   ├── model_a.pt2               # YOU train/export this
│   └── model_b.pt2               # YOU train/export this
├── rag/
│   └── config.yaml
└── skills/
    └── *.md
```

## Training is intentionally not provided by the Data API

The Data API is used by the running challenge to provide the current business/scenario state and authorized knowledge. It does **not** provide ready-made training rows and it does not provide the student model contract.

Your case package already contains readable historical evidence:

```text
student/team_X/training/raw_case_history.csv
```

and the fixed runtime interface:

```text
student/team_X/training/model_contract.json
```

Treat `raw_case_history.csv` and `model_contract.json` as read-only assignment inputs. Read `CASE_TRAINING.md` and the assigned case description, then build new supervised dataset files yourself.

That work includes, depending on the case:

- constructing time windows;
- deriving rolling statistics;
- converting raw order/inventory/line history into model inputs;
- defining labels from later realized outcomes;
- avoiding target leakage;
- deciding how to handle noise and class imbalance;
- choosing a defensible train/validation strategy;
- documenting assumptions.

The raw file intentionally does **not** contain columns such as `target_delay`, `target_risk`, `target_downtime`, or four-week forecast targets ready for training.

## Fixed model contract

The exported model must respect `model_contract.json`: feature names/order, output shape, task type and artifact name are part of the platform interface.

You may improve the neural-network architecture, preprocessing inside the model, optimizer, loss, regularization, sampling, hyperparameters and training procedure. Do not change the runtime contract unless the assignment explicitly says otherwise.

## Starter trainer

After you create:

```text
student/team_X/training/model_a_training.csv
student/team_X/training/model_b_training.csv
```

you can use or modify the starter trainer:

```bash
python student/train_pytorch.py --team team_X --model model_a
python student/train_pytorch.py --team team_X --model model_b
```

The starter trainer validates that your CSV contains the required feature/target columns, trains a baseline PyTorch network and exports `.pt2` artifacts. It does **not** build the dataset for you.
