# Weekly data pulls

The FluSight and RSV forecasts of each Wednesday read one operational data root. This page
records those pulls and the panel hashes; each challenge's submission log refers to them.
The 14 October 2026 pulls (reference date 17 October) are recorded in the 17 October
[FluSight](flusight-weekly.md#reference-date-17-october-2026) and
[RSV](rsv.md#reference-date-17-october-2026) entries. MetroCast and BDBV read their own Hub
target data, recorded in their entries.

## Operational inputs, issuance 28 October 2026 (reference date 31 October)

The flu and RSV forecasts for 31 October read one operational data root, `data/operational-20261028/`: a copy of the 21 October root with fresh pulls on 28 October 2026 between 20:28 and 20:39 UTC (16:28-16:39 EDT) of Delphi NHSN, Delphi NSSP, the FluSight, RSV and COVID Hub target histories, and PopHIVE Kinsa. Other sources are the 14 October snapshots. The Hubs had posted the week ending 24 October between 11:20 and 12:32 EDT that day; Delphi NHSN and NSSP both reached that week. Panels:

- Influenza: `data/operational-20261028/processed/panel.npz`, SHA256 `af38b52146df5d476ab2c2009267885e9d7c5b3b0dc3c320bf08128277073f71`.
- RSV: `panel-rsv.npz` in the same folder, NHSN RSV admissions before 2024-11-02 masked as in training, SHA256 `9506578ad5fdfadcb1dc312332d4949f763d882bade2be8f2f5e2b8ea3f32698`.

The FluSight Hub's target data has no ED share for Iowa, Georgia and Delaware for the week ending 24 October. Unlike 21 October, the panel was not checked cell by cell against the Hubs' latest target data.


## Operational inputs, issuance 21 October 2026 (reference date 24 October)

Both 24 October forecasts read one operational data root, `data/operational-20261021/`: a copy of the 14 October root with fresh pulls on 22 October 2026 between 00:13 and 00:29 UTC (20:13-20:29 EDT on 21 October) of Delphi NHSN, Delphi NSSP, the FluSight, RSV and COVID Hub target histories, and PopHIVE Kinsa. Other sources are the 14 October snapshots. Panels:

- Influenza: `data/operational-20261021/processed/panel.npz`, SHA256 `05f983687c7da5a2e5db6832f96a37614762eab4602bb3b3f6fa72f02dc2a547`.
- RSV: `panel-rsv.npz` in the same folder, the same panel with NHSN RSV admissions before 2024-11-02 masked as in training, SHA256 `a29b957449d8228291ed7c429d79f0e4e04056392daf7aae83c9e4ab05c67639`.

For every location and the 8 weeks through 17 October, the admissions and ED values seen at the 21 October issuance equal each Hub's latest target data. The only empty cells are empty on the Hub too: the FluSight Hub's 21 October "Remove suppressed data" commit (16:21 EDT) removed Iowa ED share again for the weeks ending 29 August to 10 October, and Delaware ED share for the week ending 17 October is missing. The same Iowa and Delaware gaps are in the RSV ED share.

