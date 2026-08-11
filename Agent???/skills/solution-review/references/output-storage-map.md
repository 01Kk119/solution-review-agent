# Output Storage Map

Use this map whenever the user asks where new project analysis or review results should be stored.

## Fixed Storage Policy

| Artifact | Save Location |
|---|---|
| Raw project files | `02_项目资料与运行数据/Agent运行数据/projects_input/<ProjectKey>/` |
| Working/staging output | `02_项目资料与运行数据/Agent运行数据/output/<ProjectKey>/` |
| Final result package folder | `<OriginalProjectDir>/评估结果/` |
| Deterministic extraction JSON | `<OriginalProjectDir>/评估结果/extracted/` |
| Extracted images and snapshots | `<OriginalProjectDir>/评估结果/assets/` |
| Structured source package | `<OriginalProjectDir>/评估结果/<ProjectFolderName>_project_requirement_package.md` |
| Rendered source package | `<OriginalProjectDir>/评估结果/<ProjectFolderName>_project_requirement_package.html` |
| Evidence index | `<OriginalProjectDir>/评估结果/<ProjectFolderName>_evidence_index.json` |
| Missing information checklist | `<OriginalProjectDir>/评估结果/<ProjectFolderName>_missing_info_checklist.md` |
| Latest review analysis | `<OriginalProjectDir>/评估结果/<ProjectFolderName>_review_analysis.md` |
| Rendered review analysis | `<OriginalProjectDir>/评估结果/<ProjectFolderName>_review_analysis.html` |
| Version recommendation | `<OriginalProjectDir>/评估结果/<ProjectFolderName>_version_recommendation.md` |
| Rendered version recommendation | `<OriginalProjectDir>/评估结果/<ProjectFolderName>_version_recommendation.html` |
| Custom development checklist | `<OriginalProjectDir>/评估结果/<ProjectFolderName>_custom_development_checklist.md` |
| Rendered custom development checklist | `<OriginalProjectDir>/评估结果/<ProjectFolderName>_custom_development_checklist.html` |
| Nonstandard development items | `<OriginalProjectDir>/评估结果/<ProjectFolderName>_nonstandard_development_items.md` |
| Rendered nonstandard determination | `<OriginalProjectDir>/评估结果/<ProjectFolderName>_nonstandard_development_items.html` |
| Effort recommendation | `<OriginalProjectDir>/评估结果/<ProjectFolderName>_effort_recommendation.md` |
| Rendered effort recommendation | `<OriginalProjectDir>/评估结果/<ProjectFolderName>_effort_recommendation.html` |
| Dated review snapshots | `<OriginalProjectDir>/评估结果/reviews/review_analysis_YYYYMMDD.md` |
| Multi-Agent trace | `<OriginalProjectDir>/评估结果/agent_trace/<trace_id>/` |
| Cross-project index | `02_项目资料与运行数据/Agent运行数据/项目汇总包/project_index.csv` |
| Per-project summary record | `02_项目资料与运行数据/Agent运行数据/项目汇总包/records/<ProjectKey>.md` |

## Registration Rule

The five prefixed Markdown files are audit sources and the five prefixed HTML files are user-facing project review deliverables in the final `评估结果/` folder. `项目汇总包/project_index.csv` is only the cross-project index. Do not paste long analysis into the CSV; put detailed documents under `<OriginalProjectDir>/评估结果/` and register that exported result folder with `Register-ProjectReview.ps1 -ProjectOutputDir`.

## Export Rule

After the working output passes validation, run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File ".\01_Agent程序与知识库\Agent工作区\scripts\Export-ReviewResult.ps1" `
  -ProjectOutputDir ".\02_项目资料与运行数据\Agent运行数据\output\<ProjectKey>" `
  -OriginalProjectDir "<OriginalProjectDir>" `
  -Clean
```

The central `output/<ProjectKey>/` folder remains the working cache and keeps standard file names for render and validation. User-facing saved results should be the exported `评估结果/` folder in the original project directory.

The exported `评估结果/` folder must contain only one project-folder-name-prefixed set of the main deliverable files, including all five Markdown/HTML pairs. Do not keep duplicate unprefixed copies in the final user-facing result folder.
