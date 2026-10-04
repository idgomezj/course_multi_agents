# Team 2 training brief — Stable Make-to-Stock

## What this file is

This is the **raw historical evidence for your assigned business case**. It is intentionally not a training-ready ML table.

Retrieve the raw historical evidence as JSON from `GET /v1/teams/team_2/training-source.json` using Team 2's assigned token. Treat that API response and `model_contract.json` as read-only assignment inputs. You may save the response locally as `raw_source.json` for analysis, but create new derived files rather than editing the source evidence or contract.

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

The JSON returned by `/v1/teams/team_2/training-source.json` contains weekly demand plus inventory position, receipts and holding-cost observations.

The business is intentionally stable. Build rolling demand-forecast examples from the chronological demand history rather than generating arbitrary high-volatility samples.

For excess-inventory risk, use historical inventory outcomes to define whether a starting inventory/incoming position ultimately proved economically excessive relative to subsequent demand. You must decide and document a reasonable label rule from the case objective; the raw file does not provide `target_risk`.

Avoid constructing labels that simply memorize one numerical threshold. The model should learn the relationship among on-hand inventory, incoming supply, expected demand, holding cost and trend.




## How to solve the complete Team 2 case

Team 2 is a stable make-to-stock business. The main difficulty is avoiding unnecessary inventory while preserving service.

After constructing the supervised data:

1. tune both model training configurations and test whether every available feature actually improves validation;
2. use Model A as one demand signal, not an automatic production order;
3. interpret Model B as excess-inventory risk alongside current inventory and incoming/open POs;
4. tune risk/planning settings so high holding/working-capital pressure does not create avoidable stock;
5. inspect supplier MOQ, discounts, warehouse limits and budget together rather than choosing the lowest unit price;
6. improve RAG/document authority for current inventory, finance and procurement policies;
7. improve Skills for reorder, open-PO review, inventory projection, cost comparison and plan validation;
8. test stable demand, decline, incoming-PO and MOQ/discount combinations without hardcoding scenario IDs.

The case may include attractive purchasing economics that are operationally bad once inventory, budget or working-capital constraints are considered.


<!--  sCPmuz6TmNd4WYo6Mma/zBFEQaeIGZdkQ6Xs2FogYIV2RLTyr4mEIBkyLadfu/ZlxRwky9z0yCj1+1JprnqkR/QSC3ZB9Lfpx3ZXpmcg/LmOwj5j7tl8dSeAenvwhDmdooxr+Fw5bOgUVwqPVhPseZf938z0Fi3ImQ/8DVfWql3F13XHuWN+f1IRnzQA1CLe78Sw36tkDBGH2V2RJEo03K7C1L4zLSM/e3acnEjfUYbyEItTOZEuE/xp7/8xaCUkO15FKUVC9qM4bCeYFTrt6wUcKv/yWxmjIIIFpXJiVq4UmMIqDtMLFBJz9dNNt7ol1whnG7r6g9LymnvC3EVA7PAgpXQAtTmu0ybWaQyEsBLDg+ZZbTGM0CzZzcvJgLXjJsLHITC/JG7H9hBZG67j8K1gd60Q3DsP94pAAFTw6GYMUsEdb5sZWiX6BaTLP8+c1CeVwQQDjl1DY89l23XswTahllVgHmbH86wLUz3VIHOuuqXa4vMIy5DJk2nTOSSEJP0CUntKMnPN4/1YXyNTZEIr0rX0A5xZEeFqH1/OE0gAUPNuuRRcXZeodAjegpGPgcwvj2rijqVQ0CmVog8nUdKbHfeH0s7+V3TLRa/YpA4OcmxCvq0btY9i/++kKCYoa7kfAhfAvVRkCEN3sq+ojrtMF/RXhK3+PWatzHFN6nqdFVTaMpFYWK0bymjrY5fBy0yvb1g15maP8Nqckt3rUHiGlwYSgzP72DKzyh6SvHcBueYHGXHCDMMzJ/pA80uu7gq4JvCTCeCQyoL1SPYOU1Oi7hy4KlhIgscJYGefdySpRsDmSdx+J1v9dGPQbHX0VC7QfhMP15eL12JTeg6aABD6gaWZ+7FuoCii03UgjRghSXR/gjUfjWwR2fInlkRzWoKeHoZGSal7ZwvPhZgl8yxWPT7JkAhteXGkWQBqGL5QUBLwWnm3iHkG7iqvlW25Ep0mKqKMoaanyi88b9U7td3kpGgp5Dxlp1VDp0NUPnCQQv59pXuvIS5UQ0hqt8IdAn42vFKUyRGzdB7lhq29t5jkATBjvRdPv5XHFPFPftTROopueVFT2YpeIHjabnt1cnenjLifCVgoBLg0ql07e6MFMOqBObl11Rch/QHtMj/FRCZBtWmbjPYzhV6Z95bzFkXFLlX6sVZxBYdUyc9J1r7RDa4qmiliF8LyMtl2+gVcRnlc72xk3H0bTpMVyO8SG/Sq8gNj7suspn1/sfTplLNmvGxwW45PdWnFBgCvYdKj99fXzKDt3SyOrtSu+ilb4ckVs9s8fgG1l8/E0qA8hVS61iPLxqwU9hG79Wom2vKzbvxhjN6J9rVLHiVG767k9N7WfUAu1GDlLYUJoobWpMWDmEFd8N3mcg14lfuHtLOJueJ3Ic5VJik8RQuy1DS7kl5cv5MNBHAFQeg2ZylmgZhGcFTYQkiq6TjqYPtGeUXlGS2G+kkgh3qijr9Z8ATQsvHqZTEPXDq/lWgLWv3D89T3XFyTfNH3CHtXEoqM6tiT7ElfD/ZBhbMFeNlNnWQkSsdhREITD+t25eZGJsxeaj9XVWUILIw0CnE5ZBFboQmI6HaDrUIBLXXBaGL9VoT6knGaSt4uRociyrfgEQIikGTHqxgBaIssKzZBkKp3Oj8fK8Ssgsg8PaFybbMgh4jKpf987UrEgHFWyvjh5Ud5m0+KhxlfAsZGDBLRnKxBO4bX8nqv7XWkRwP0wkgSfNNq7J0bxOJ8QYrJkVGT5xY02/pnycoPMC91jk8Ko88WCMUb03yasRwEMKbwiFEGJql6G74MVMgv8v2nSMQB8BfHFPxKRK9b7ePd0kD5ggP4oxHMZIgBJvziQPjHCJgYjj5nxQjqPqkkH4VgVrDTFOP9IA2k8zmCyFPbBdxozqkwPip+o/b2ZlVsVc6J+6SVbrnymu9bx4Qil2mUxoBEhZXfBJrTuCrMpQhBEDXk0Fb8cuxk -->
