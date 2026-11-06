# Hand-encoded official calendars

Some official calendars are only published as PDF (Land Tirol "Dosierkalender", ASFINAG
"Luegbrücke Fahrkalender", the Italian MIT decree). A person encodes them here once per
quarter/year; every JSON file in `zhol/data/calendars/` (not in `examples/`) is loaded as
**approved** events with its source link.

Copy `tirol_dosing_TEMPLATE.json` to `../tirol_dosing_2026H2.json`, replace the example
dates with the dates in the official PDF, and keep the `source.url`.
Do not ship example dates as real ones.
