# Student editable area

All immutable business data is delivered by the instructor Data API.

Students modify only their assigned team folder:

```text
student/team_X/
├── models/
│   ├── model_a.pt
│   └── model_b.pt
├── rag/
│   └── config.yaml
└── skills/
    └── *.md
```

The model interface/specification is also fetched from the Data API. Do not create a different input/output contract.

Starter training:

```bash
python student/train_pytorch.py --team team_X --model model_a
python student/train_pytorch.py --team team_X --model model_b
```

The training script downloads only the dataset authorized for the team token in `.env`.
