"""zhol radar: what is coming on Europe's freight roads, and how likely it is.

Pipeline (runs at every site build, twice a day):
  sources.py  - news searches, trade-press feeds, weather forecasts at the passes
  signals.py  - each article -> a Signal (kind, stage, where, when, who), by Claude or by heuristics
  model.py    - the chance formula: prior from the stage x evidence multipliers -> probability
  outlook.py  - official calendars + weather + clustered news signals -> site/data/outlook.json
"""
