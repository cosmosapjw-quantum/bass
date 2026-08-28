# GitHub connector import / push / PR / merge smoke test

```yaml
repository: cosmosapjw-quantum/bass
scope: isolated connector-smoke branches only
scientific_code_changed: false
raw_data_changed: false
production_branch_changed: false
history_rewrite: false
```

This marker verifies that the connected GitHub surface can import/read the repository, create branches, push a UTF-8 file commit, open a pull request, merge with an expected-head guard, and read the merged content back from the isolated base branch.
