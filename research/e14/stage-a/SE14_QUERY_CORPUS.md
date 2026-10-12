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

25. find the current documented way in this pinned FFmpeg revision to inspect media metadata
26. which pinned pandas capability supports time-series operations
27. find the pinned MinIO capability for STS temporary credentials
28. which LibreOffice help capability in the frozen revision covers PDF export
29. find a media operation whose behavior is tied to the frozen FFmpeg source revision
30. find a tabular-data operation valid for the frozen pandas revision
31. find a storage operation whose source is the frozen MinIO revision
32. find a Writer/Calc/Impress operation backed by the frozen LibreOffice help revision

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

41. find a capability that should not claim it can preserve arbitrary media without re-encoding when filters are required
42. find a table operation that should not pretend missing-data handling and text processing are the same job
43. find a storage capability that should not be presented as object retention if it only enables versioning
44. find a LibreOffice action that should not use screenshots or coordinate clicks as its binding
45. avoid selecting an output muxer when the request is only to inspect media streams
46. avoid returning generic DataFrame reshaping when the request specifically needs a keyed merge
47. avoid returning site replication when the request is temporary credential issuance
48. avoid returning document saving when the request specifically requires PDF export

## Anti-cheating

- no expected provider/tool/item is encoded unless the user intent naturally names the software class;
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
