# Sample Documents

Place the following acceptance corpus files in this directory:

1. `EPPF Asset Manager Questionnaire Domestic Equity_2025.pdf`
2. `EPPF Asset Manager Questionnaire Domestic Equity_2025.docx`
3. `EPPF Asset Manager Questionnaire Domestic Equity_2025 Final.pdf`
4. `Investment Manager DD Questionnaire - 19052026.xlsx`
5. `ESG Questionnaire.xlsx`
6. `Completed_HIM_RI_Questionnaire.xlsx`

Run sample ingestion after placing files:

```bash
uv run python scripts/ingest_samples.py
```

Synthetic test fixtures are available in `tests/fixtures/` for automated testing.
