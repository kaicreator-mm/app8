# V04 pandas ABI host smoke — candidate receipt

Source: [#150 host offline install and ABI smoke report](https://github.com/kaicreator-mm/app8/issues/150#issuecomment-6174378731). This **data-only** JSON transcribes the host's narrow import/ABI observations, without changing the historical exact target selection or the four-target candidate manifest.

Artifact: `research/mla/v04-mla-pandas-abi-host-candidate.json`. Known lane `python:3.12-bookworm@sha256:5560…fa98b`; known wheel SHA256 for pandas, numpy, python-dateutil, six. Host reported read-only wheel mounts, `--network none`, offline install=0, imports=0 and 10 small ABI operations passing (no formal evaluation). Image and published artifacts unchanged.

**Important limit:** `host_reported_observation_only=true` and `independent_approval=false`. This candidate does **not** convert `research/mla/v04-mla-four-target-reentry-candidate.json` fields to READY, establish target/claim suitability, approve LibreOffice `DIVERGED`, sign an oracle, or execute any P/R/X experiment. The submitted host log is reported evidence and not a signed external runtime receipt. Its existing evidence directory can expire without falsifying the narrow provenance record.

Independent reviewer can now accept the documented pandas *import capability* evidence for subsequent candidate target decisions without asking for another docker reinstall. **Real behavior eligibility remains blocked until approved exact-claim applicability, independent oracle and an approved private target manifest.** SE10/SE11 NOT_RUN; Release NO.
