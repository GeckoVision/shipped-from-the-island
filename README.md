# Shipped from the Island

What IslandDAO v5 produced, as data: attendance read from IslandDAO's on-chain check-ins and proven against the chain, plus every project milestone from the event, dated and linked to its source.

Live page: https://geckovision.github.io/shipped-from-the-island/

Built by [Gecko](https://geckovision.tech) for IslandHack V5 (build area: Payments + Commerce).

## What is in this repository

| Path | What it is |
|---|---|
| `index.html` | The page. Static HTML; reads `data/site.json`. |
| `data/ledger.csv` | The milestones ledger: project, date, type, claim, public source, who said it, confidence. |
| `data/editions.json` | V4 and V5 totals and the V4 to V5 comeback, counts only. |
| `data/attendance-raw.json` | Snapshot of Gecko's daily attendance dataset (aggregates; small cells withheld). |
| `scripts/build_data.py` | Builds `data/site.json` from the three inputs. Standard library only. |

## How the numbers are made

1. **Check-in.** Builders check in every day with the IslandDAO app; each check-in is a Solana transaction the builder signs and the venue key co-signs.
2. **Index.** We run our own indexer for the check-in program. It started from [Envio's open IslandDAO demo](https://github.com/enviodev/envio-islanddao-demo), which decodes the program without a published IDL. Our deployment code is not in this repo; see Envio's repo for the decoder.
3. **Prove.** Our counts are identical to the reference indexer (V5 and V4 registrations and check-ins, 9 Nov 2026), and all 251 attendance accounts match a direct chain read (slot 466,981,886).
4. **Dataset.** Gecko keeps `islanddao-v5-attendance`: one row per day, with new and returning check-ins, refreshed at no cost, with a source and a read time on every value.
5. **Ledger.** Milestones come from public posts and sites: the project's own channels, the organizers, or third parties, each marked. Rows from personal accounts, rows outside the event window, and low-confidence rows were removed. Self-reported numbers are marked.
6. **Join.** For now the ledger is joined to the event by hand. A join step inside Gecko is in review and will replace it.

## Used by

- **Brot Markets** settled a devnet campaign on this data: ["Will we see 60 check-ins on the final day of IslandDAO V5?"](https://v5.brot.markets/c/5368792077394394715) closed NO on 12 Nov, with 19 check-ins on 11 Nov in `islanddao-v5-attendance` (version 14). Test SOL only.

To rebuild: `python3 scripts/build_data.py`. With `GECKO_READER_KEY` set (a read-only key limited to that one dataset), it refreshes the attendance snapshot first.

## Rules we hold ourselves to

- Aggregates only: no wallet addresses, no names of individuals, no group under 5.
- "Logged during v5", never "because of v5".
- Counts are check-in identifiers (one per account), not verified people.
- Days follow the program's own rule: local days in Florianópolis (UTC−3).

## Add or correct a milestone

Open an issue with the project, the date, what shipped and a public link.

## Credits and licence

Project logos in `assets/logos/` are each project's own site icon, shown to identify it; they belong to their owners and are not covered by the MIT licence.


Attendance data comes from IslandDAO's on-chain check-in system. The indexer approach comes from Envio's open demo. Code in this repository is MIT licensed. The ledger quotes public sources, each linked.
