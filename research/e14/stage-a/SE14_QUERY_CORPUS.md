# SE14 Stage A — Frozen Query Corpus

Status: CANDIDATE_FOR_FRESH_REVIEW
Owning issue: #49
Protocol blob: 177c70ffa6c7e89da45d438738a809523e44c0d3

These 48 natural-language queries are frozen before relevance judgments and before either search arm is executed. They contain no expected item IDs or labels.

## Plain intent (12)

01. convert a video file to another format
02. inspect the streams inside a media file
03. filter rows in a table
04. combine two tabular datasets
05. configure object retention in storage
06. enable object version history
07. insert a chart into a document
08. save a document
09. calculate grouped statistics from a table
10. apply an audio filter to media
11. configure storage event notifications
12. export a document as PDF

## Constraint-sensitive (12)

13. copy existing media streams without re-encoding them
14. select only particular media streams for output
15. join tables while controlling how keys match
16. work with missing values without silently treating them as normal values
17. keep stored objects from being deleted before a retention period ends
18. create temporary storage credentials instead of long-lived credentials
19. print only selected text rather than the whole Writer document
20. import a CSV into Calc while preserving the intended parsing behavior
21. process a time series with time-based resampling
22. choose a specific output container rather than relying on filename inference
23. replicate storage data to another deployment with explicit replication configuration
24. apply a slide transition without using pixel-coordinate automation

## Platform/version/currentness (8)

25. for the installed FFmpeg version, how do I inspect the video and audio streams in a file
26. in this installed pandas version, what operation resamples timestamp-indexed measurements
27. on this MinIO server version, how can I obtain temporary access credentials
28. in this installed LibreOffice release, how can I export a document as PDF
29. does this FFmpeg version allow changing containers without re-encoding the streams
30. on this pandas version, can I join two DataFrames using matching key columns
31. on my installed MinIO server, can I configure object retention to prevent early deletion
32. for this LibreOffice version, how do I rearrange slides in an existing presentation

## Variant-selection (8)

33. choose between re-encoding and stream-copying media
34. choose a table combination method appropriate for joining datasets
35. choose between ordinary storage credentials and temporary STS credentials
36. choose a Calc operation for importing CSV rather than general document saving
37. choose a media input/demuxing behavior rather than an output muxer
38. choose between table pivoting and grouping/aggregation
39. choose a storage replication capability rather than simple versioning
40. choose a presentation table insertion action rather than Writer table insertion

## Negative-boundary/readiness (8)

41. add a visual filter to a video while guaranteeing that the existing compressed streams remain byte-for-byte unchanged
42. is there one pandas operation that both fills missing values and transforms the text in every column
43. can I guarantee retention against deletion by turning on bucket versioning alone
44. automate a LibreOffice document action without relying on screen coordinates or screenshots
45. inspect which streams are inside a video file, without creating an output media container
46. merge two data tables based on a shared customer ID, not by reshaping columns
47. issue short-lived storage credentials for a client without configuring cross-site replication
48. produce a PDF copy of a Writer file rather than simply saving the editable document

## Anti-cheating

- no expected provider/tool/item is encoded unless the user intent naturally names the software class;
- user-language queries avoid experiment-only tokens such as pinned source SHA, frozen corpus, Capability-arm identity, or internal reference IDs;
- no query rewrite may use later relevance labels;
- no query replacement after ranked outputs are viewed;
- independent adjudicators must create graded relevance labels before search results are exposed;
- at least 24 queries are deliberately constraint/variant/version/negative cases where a superficial name/description match can be semantically wrong.

```text
QUERY_COUNT=48
PLAIN=12
CONSTRAINT=12
VERSION_CURRENTNESS=8
VARIANT=8
NEGATIVE_BOUNDARY=8
RELEVANCE_LABELS=NOT_CREATED
SEARCH_RESULTS=NOT_RUN
```
