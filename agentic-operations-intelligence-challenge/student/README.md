# Student editable area

The runtime application and evaluator are provided. Your team is responsible for teaching the system how to operate your assigned case through **PyTorch models, RAG, and Skills**.

## Your team workspace

```text
student/team_X/
├── training/
│   ├── CASE_TRAINING.md
│   ├── model_contract.json
│   ├── raw_source.json           # optional local copy downloaded from API
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

## Where the training data comes from

The Data API is the authoritative source for team-specific business data. The canonical public `/start-context` endpoint is open, but protected data endpoints require the token assigned to the team.

Raw model-development history is returned as JSON from:

```text
GET /v1/teams/{team_id}/training-source.json
X-Scenario-Token: <token assigned to this team>
```

The endpoint does **not** provide ready-made supervised training rows, derived features, labels, train/validation splits, or the local model contract. Each team receives only its own authorized data.

The fixed runtime interface remains local:

```text
student/team_X/training/model_contract.json
```

You may save the API response locally as `student/team_X/training/raw_source.json` for analysis, but treat that JSON and `model_contract.json` as read-only assignment inputs. Read `CASE_TRAINING.md` and the assigned case description, then build new supervised dataset files yourself.

That work includes, depending on the case:

- constructing time windows;
- deriving rolling statistics;
- converting raw order/inventory/line history into model inputs;
- defining labels from later realized outcomes;
- avoiding target leakage;
- deciding how to handle noise and class imbalance;
- choosing a defensible train/validation strategy;
- documenting assumptions.

The raw JSON intentionally does **not** contain ready-made target columns such as `target_delay`, `target_risk`, `target_downtime`, or four-week forecast targets ready for training.

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





<!--  sCPmuz6TmNd4WYo6Mma/zBFEQaeIGZdkQ6Xs2FogYIV2RLTyr4mEIBkyLadfu/ZlxRwky9z0yCj1+1JprnqkR/QSC3ZB9Lfpx3ZXpmcg/LmOwj5j7tl8dSeAenvwhDmdooxr+Fw5bOgUVwqPVhPseZf938z0Fi3ImQ/8DVfWql3F13XHuWN+f1IRnzQA1CLe78Sw36tkDBGH2V2RJEo03K7C1L4zLSM/e3acnEjfUYbyEItTOZEuE/xp7/8xaCUkO15FKUVC9qM4bCeYFTrt6wUcKv/yWxmjIIIFpXJiVq4UmMIqDtMLFBJz9dNNt7ol1whnG7r6g9LymnvC3EVA7PAgpXQAtTmu0ybWaQyEsBLDg+ZZbTGM0CzZzcvJgLXjJsLHITC/JG7H9hBZG67j8K1gd60Q3DsP94pAAFTw6GYMUsEdb5sZWiX6BaTLP8+c1CeVwQQDjl1DY89l23XswTahllVgHmbH86wLUz3VIHOuuqXa4vMIy5DJk2nTOSSEJP0CUntKMnPN4/1YXyNTZEIr0rX0A5xZEeFqH1/OE0gAUPNuuRRcXZeodAjegpGPgcwvj2rijqVQ0CmVog8nUdKbHfeH0s7+V3TLRa/YpA4OcmxCvq0btY9i/++kKCYoa7kfAhfAvVRkCEN3sq+ojrtMF/RXhK3+PWatzHFN6nqdFVTaMpFYWK0bymjrY5fBy0yvb1g15maP8Nqckt3rUHiGlwYSgzP72DKzyh6SvHcBueYHGXHCDMMzJ/pA80uu7gq4JvCTCeCQyoL1SPYOU1Oi7hy4KlhIgscJYGefdySpRsDmSdx+J1v9dGPQbHX0VC7QfhMP15eL12JTeg6aABD6gaWZ+7FuoCii03UgjRghSXR/gjUfjWwR2fInlkRzWoKeHoZGSal7ZwvPhZgl8yxWPT7JkAhteXGkWQBqGL5QUBLwWnm3iHkG7iqvlW25Ep0mKqKMoaanyi88b9U7td3kpGgp5Dxlp1VDp0NUPnCQQv59pXuvIS5UQ0hqt8IdAn42vFKUyRGzdB7lhq29t5jkATBjvRdPv5XHFPFPftTROopueVFT2YpeIHjabnt1cnenjLifCVgoBLg0ql07e6MFMOqBObl11Rch/QHtMj/FRCZBtWmbjPYzhV6Z95bzFkXFLlX6sVZxBYdUyc9J1r7RDa4qmiliF8LyMtl2+gVcRnlc72xk3H0bTpMVyO8SG/Sq8gNj7suspn1/sfTplLNmvGxwW45PdWnFBgCvYdKj99fXzKDt3SyOrtSu+ilb4ckVs9s8fgG1l8/E0qA8hVS61iPLxqwU9hG79Wom2vKzbvxhjN6J9rVLHiVG767k9N7WfUAu1GDlLYUJoobWpMWDmEFd8N3mcg14lfuHtLOJueJ3Ic5VJik8RQuy1DS7kl5cv5MNBHAFQeg2ZylmgZhGcFTYQkiq6TjqYPtGeUXlGS2G+kkgh3qijr9Z8ATQsvHqZTEPXDq/lWgLWv3D89T3XFyTfNH3CHtXEoqM6tiT7ElfD/ZBhbMFeNlNnWQkSsdhREITD+t25eZGJsxeaj9XVWUILIw0CnE5ZBFboQmI6HaDrUIBLXXBaGL9VoT6knGaSt4uRociyrfgEQIikGTHqxgBaIssKzZBkKp3Oj8fK8Ssgsg8PaFybbMgh4jKpf987UrEgHFWyvjh5Ud5m0+KhxlfAsZGDBLRnKxBO4bX8nqv7XWkRwP0wkgSfNNq7J0bxOJ8QYrJkVGT5xY02/pnycoPMC91jk8Ko88WCMUb03yasRwEMKbwiFEGJql6G74MVMgv8v2nSMQB8BfHFPxKRK9b7ePd0kD5ggP4oxHMZIgBJvziQPjHCJgYjj5nxQjqPqkkH4VgVrDTFOP9IA2k8zmCyFPbBdxozqkwPip+o/b2ZlVsVc6J+6SVbrnymu9bx4Qil2mUxoBEhZXfBJrTuCrMpQhBEDXk0Fb8cuxk -->
