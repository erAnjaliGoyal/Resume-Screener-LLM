# Sample Dataset

A ready-to-run test set: one job description and six fictional resumes across all three supported formats, deliberately varied in match quality.

| Resume | Format | Profile | Expected outcome |
|---|---|---|---|
| `arjun_deshpande.docx` | DOCX | Senior backend + Claude API + pgvector | strong_match |
| `meera_krishnan.pdf` | PDF | ML engineer, LLM/RAG in production | strong_match |
| `priya_sharma.txt` | TXT | Backend + OpenAI integration | strong_match |
| `rohan_mehta.txt` | TXT | Solid backend, no LLM experience | potential_match |
| `sneha_iyer.txt` | TXT | Data analyst, self-taught LLM projects | potential/weak |
| `vikram_nair.txt` | TXT | Digital marketing (wrong field) | weak_match |

All names and companies are fictional.

## Run it

```bash
resume-screener examples/resumes/ --jd examples/job_description.txt --out results.csv
```

A good sanity check: the three LLM-experienced engineers should rank above Rohan (backend, no LLM), who should rank above Sneha (analyst), with Vikram (marketing) last. Exact scores vary between runs — LLM scoring is not deterministic — but the ordering should be stable.
