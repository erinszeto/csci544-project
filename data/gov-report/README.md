# Government Report Dataset

### File Description

Collected reports and their summaries are in `crs` and `gao` directories. Each report and its summary is organized in a json file with its ID as the filename. 

The IDs for train/validation/test splits are in `split_ids` directory. For example, the IDs of GAO training samples are in the file `split_ids/gao_train.ids`.

Each report json file includes the following keys:

```
-----      metadata      -----
id: the report ID
url: the report web page [for GAO reports]
title: the title of the report
released_date: the released date
published_date: the published date [for GAO reports]

----- summary and report -----
[CRS]
summary: the summary paragraphs
report: the nested, structured report

[GAO]
highlight: the structured summary
report: the nested, structured report

-----        extra       -----
[GAO]
fastfact: paragraphs of a shorter summary (not used in our paper)
```

**NOTE:** For experiments using GAO reports, we do not include the paragraphs in the Letter section (its subsections are included).
