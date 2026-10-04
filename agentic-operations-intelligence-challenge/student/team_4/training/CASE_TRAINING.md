# Team 4 training brief — Unreliable Supply Network

## What this file is

This is the **raw historical evidence for your assigned business case**. It is intentionally not a training-ready ML table.

Retrieve the raw historical evidence as JSON from `GET /v1/teams/team_4/training-source.json` using Team 4's assigned token. Treat that API response and `model_contract.json` as read-only assignment inputs. You may save the response locally as `raw_source.json` for analysis, but create new derived files rather than editing the source evidence or contract.

You must build the supervised learning dataset yourself. That means deciding how historical rows become examples, deriving the required model inputs from the raw observations, constructing defensible targets from later outcomes, handling missing/noisy observations, choosing train/validation splits, and documenting your assumptions.

The runtime model interface is fixed by `model_contract.json`. You may change the neural-network architecture, preprocessing inside the model, optimizer, loss, sampling, regularization, validation strategy, and training procedure, but the exported model must accept the feature columns and produce the target shape declared in the contract.

Do not hardcode public scenario IDs or benchmark answers into the training data. Your construction should generalize to unseen scenarios.

Your workflow should produce:

```text
student/team_X/training/model_a_training.csv
student/team_X/training/model_b_training.csv
student/team_X/models/model_a.pt2
student/team_X/models/model_b.pt2
```

The starter trainer refuses to create the supervised rows for you; it only trains after you create the model-specific CSV.


## Raw file

The JSON returned by `/v1/teams/team_4/training-source.json` contains supplier-order history including delivery timing and quality-inspection outcomes.

For the delay model, derive the same operational features available at order time and construct the classification target from the realized delivery outcome.

For supplier-quality risk, derive the target from the inspection/rejection outcome. Inputs such as quality score, recent reject rate, criticality and process change are known before receipt; rejected quantity is an outcome and must not leak into inputs.

The case emphasizes long lead times, delay and quality disruption, so class balance and recall on costly failure events should be considered rather than relying only on accuracy.




<!--  sCPmuz6TmNd4WYo6Mma/zBFEQaeIGZdkQ6Xs2FogYIV2RLTyr4mEIBkyLadfu/ZlxRwky9z0yCj1+1JprnqkR/QSC3ZB9Lfpx3ZXpmcg/LmOwj5j7tl8dSeAenvwhDmdooxr+Fw5bOgUVwqPVhPseZf938z0Fi3ImQ/8DVfWql3F13XHuWN+f1IRnzQA1CLe78Sw36tkDBGH2V2RJEo03K7C1L4zLSM/e3acnEjfUYbyEItTOZEuE/xp7/8xaCUkO15FKUVC9qM4bCeYFTrt6wUcKv/yWxmjIIIFpXJiVq4UmMIqDtMLFBJz9dNNt7ol1whnG7r6g9LymnvC3EVA7PAgpXQAtTmu0ybWaQyEsBLDg+ZZbTGM0CzZzcvJgLXjJsLHITC/JG7H9hBZG67j8K1gd60Q3DsP94pAAFTw6GYMUsEdb5sZWiX6BaTLP8+c1CeVwQQDjl1DY89l23XswTahllVgHmbH86wLUz3VIHOuuqXa4vMIy5DJk2nTOSSEJP0CUntKMnPN4/1YXyNTZEIr0rX0A5xZEeFqH1/OE0gAUPNuuRRcXZeodAjegpGPgcwvj2rijqVQ0CmVog8nUdKbHfeH0s7+V3TLRa/YpA4OcmxCvq0btY9i/++kKCYoa7kfAhfAvVRkCEN3sq+ojrtMF/RXhK3+PWatzHFN6nqdFVTaMpFYWK0bymjrY5fBy0yvb1g15maP8Nqckt3rUHiGlwYSgzP72DKzyh6SvHcBueYHGXHCDMMzJ/pA80uu7gq4JvCTCeCQyoL1SPYOU1Oi7hy4KlhIgscJYGefdySpRsDmSdx+J1v9dGPQbHX0VC7QfhMP15eL12JTeg6aABD6gaWZ+7FuoCii03UgjRghSXR/gjUfjWwR2fInlkRzWoKeHoZGSal7ZwvPhZgl8yxWPT7JkAhteXGkWQBqGL5QUBLwWnm3iHkG7iqvlW25Ep0mKqKMoaanyi88b9U7td3kpGgp5Dxlp1VDp0NUPnCQQv59pXuvIS5UQ0hqt8IdAn42vFKUyRGzdB7lhq29t5jkATBjvRdPv5XHFPFPftTROopueVFT2YpeIHjabnt1cnenjLifCVgoBLg0ql07e6MFMOqBObl11Rch/QHtMj/FRCZBtWmbjPYzhV6Z95bzFkXFLlX6sVZxBYdUyc9J1r7RDa4qmiliF8LyMtl2+gVcRnlc72xk3H0bTpMVyO8SG/Sq8gNj7suspn1/sfTplLNmvGxwW45PdWnFBgCvYdKj99fXzKDt3SyOrtSu+ilb4ckVs9s8fgG1l8/E0qA8hVS61iPLxqwU9hG79Wom2vKzbvxhjN6J9rVLHiVG767k9N7WfUAu1GDlLYUJoobWpMWDmEFd8N3mcg14lfuHtLOJueJ3Ic5VJik8RQuy1DS7kl5cv5MNBHAFQeg2ZylmgZhGcFTYQkiq6TjqYPtGeUXlGS2G+kkgh3qijr9Z8ATQsvHqZTEPXDq/lWgLWv3D89T3XFyTfNH3CHtXEoqM6tiT7ElfD/ZBhbMFeNlNnWQkSsdhREITD+t25eZGJsxeaj9XVWUILIw0CnE5ZBFboQmI6HaDrUIBLXXBaGL9VoT6knGaSt4uRociyrfgEQIikGTHqxgBaIssKzZBkKp3Oj8fK8Ssgsg8PaFybbMgh4jKpf987UrEgHFWyvjh5Ud5m0+KhxlfAsZGDBLRnKxBO4bX8nqv7XWkRwP0wkgSfNNq7J0bxOJ8QYrJkVGT5xY02/pnycoPMC91jk8Ko88WCMUb03yasRwEMKbwiFEGJql6G74MVMgv8v2nSMQB8BfHFPxKRK9b7ePd0kD5ggP4oxHMZIgBJvziQPjHCJgYjj5nxQjqPqkkH4VgVrDTFOP9IA2k8zmCyFPbBdxozqkwPip+o/b2ZlVsVc6J+6SVbrnymu9bx4Qil2mUxoBEhZXfBJrTuCrMpQhBEDXk0Fb8cuxk -->
