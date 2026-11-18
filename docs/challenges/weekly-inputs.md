# Weekly data pulls

The FluSight, RSV and COVID forecasts of each Wednesday read one operational data root. This page
records those pulls and the panel hashes; each challenge's submission log refers to them.
The 14 October 2026 pulls (reference date 17 October) are recorded in the 17 October
[FluSight](flusight-weekly.md#reference-date-17-october-2026) and
[RSV](rsv.md#reference-date-17-october-2026) entries. MetroCast and BDBV read their own Hub
target data, recorded in their entries.

## Operational inputs, issuance 18 November 2026 (reference date 21 November)

Root `data/operational-20261118/`: a new root sharing the raw snapshot store with the 11 November catalog, and fresh pulls on 18 November 2026 between 20:58 and 21:06 UTC (15:58-16:06 EST) of Delphi NHSN, Delphi NSSP, the FluSight, RSV and COVID Hub target histories, and PopHIVE Kinsa (pulled from the COVID/RSV session). The Hubs' target data had reached the week ending 14 November. Panels (built 16:09 EST):

- Influenza (also read by COVID): `data/operational-20261118/processed/panel.npz`, SHA256 `d4cccc684df500c0a8c00657b1cd3c7816a2fb63d3e795b6044934547f40ed2a`.
- RSV: `panel-rsv.npz` in the same folder, NHSN RSV admissions before 2024-11-02 masked, SHA256 `5cbf192f2880e133a395aa77d05e2c2f1806c38df42547ec28af5618a043c86b`.

The panel was not checked cell by cell against the Hubs' target data.

## Operational inputs, issuance 11 November 2026 (reference date 14 November)

Root `data/operational-20261111/`, pulled from the flu session on Thursday 12 November 2026 between 16:51 and 17:02 EST (same sources as 4 November). The Hubs released the week ending 7 November on Thursday 12 November, a day late after Veterans Day, and took forecasts that day, although their configured submission window had closed on Wednesday 11 November at 23:59 EST. Panels:

- Influenza (also read by COVID): `processed/panel.npz`, SHA256 `f478b2da51e97e1403ac557b4dbbb2dd46a9bf4cf38c9151a198c56b39cdb90d`.
- RSV: `processed/panel-rsv.npz`, NHSN RSV admissions before 2024-11-02 masked, SHA256 `39e8c421c4160372ddddb9afdccacb7013606e2707cfc640f0ab3a659b458b77`.

**Hospitals reporting after the holiday** (NHSN, the same hospitals for all three pathogens, sum over states and DC, as a share of the hospitals reporting 3-5 weeks earlier in the same release): 0.871 for the week ending 7 November and 0.960 for the week before, against 0.882-0.887 and 0.966-0.979 in the four previous Wednesday releases (0.844-0.887 for the newest week over this season and November 2025). Inputs were not adjusted. COVID admissions for that week were revised from 4,412 to 4,659 (+5.6%) by 18 November, an ordinary revision.

## Operational inputs, issuance 4 November 2026 (reference date 7 November)

The flu and RSV forecasts for 7 November read one operational data root, `data/operational-20261104/`: a new root sharing the raw snapshot store (`raw`, `metadata` and `mirrors` link to `data/`) with the 28 October catalog, and fresh pulls on 4 November 2026 between 21:00 and 21:07 UTC (16:00-16:07 EST) of Delphi NHSN, Delphi NSSP, the FluSight, RSV and COVID Hub target histories, and PopHIVE Kinsa. Other sources are the 14 October snapshots. The Delphi pulls need the project key (`DELPHI_EPIDATA_KEY`, from the repository's `DELPHI_API_KEY` file). The Hubs had posted the week ending 31 October between 11:47 and 13:01 EST that day; Delphi NHSN and NSSP both reached that week. Panels:

- Influenza: `data/operational-20261104/processed/panel.npz`, SHA256 `6486441cdc6ef06dbc6a5a9724a8841b196ca6b4ba0bf55cf5f64fcf2b162d7c`.
- RSV: `panel-rsv.npz` in the same folder, NHSN RSV admissions before 2024-11-02 masked as in training, SHA256 `df76a3a84b2d496cde79b216c4ef1ddd4c658d321f3c68e1bf586f5c276ea19c`.

For the week ending 31 October, admissions are present for every location; ED share is missing for Delaware, Georgia and Iowa (all three pathogens). The panel was not checked cell by cell against the Hubs' latest target data.

**Revisions seen on 4 November** (sum over states and DC for admissions, US value for ED share; each week's value on 4 November against its first report): flu admissions for the week ending 24 October +5.5% after one week (the week ending 17 October had been revised +5.4% after one week), 17 October +7.1% after two weeks, 10 October +7.8% after three. Flu ED share for 24 October +7.0% after one week, against +1-3% for the earlier weeks. RSV admissions for 24 October +0.7% (earlier weeks +4-7%). COVID admissions for 24 October +4.9%, 17 October +7.4%, 10 October +9.3%. In MetroCast, the week ending 24 October changed in 61 of 89 locations (median +2.2%, 90th percentile +12.7%).

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

