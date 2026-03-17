# Data Profile Report

Generated: 2026-03-10T10:37:40.304025+00:00

- Sample fraction: 0.01
- Rows after merge: 5905
- Fraud rate: 0.030483
- DeviceInfo missing ratio: 0.803218
- P_emaildomain missing ratio: 0.158171

## Engineered Features
- hour
- day
- card1_txn_count_past
- card1_amt_mean_past
- card1_device_degree
- card1_email_degree

## Leakage Notes
- Behavioral features use only historical rows after sorting by TransactionDT.
- Graph features are label-agnostic and rely only on transactional context.
