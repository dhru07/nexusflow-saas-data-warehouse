# GitHub Actions CI Runbook

## Purpose

The NexusFlow CI workflow automatically checks Python syntax and parses the dbt project when relevant files are pushed to `main` or included in a pull request targeting `main`.

This first CI stage intentionally does **not** connect to BigQuery or run `dbt build`. It therefore requires no Google Cloud key, service-account JSON, or GitHub secret. BigQuery-backed deployment and test execution will be added separately after repository setup and secure GitHub-to-GCP authentication are configured.

## Files

Copy the workflow to:

```text
.github/workflows/dbt-ci.yml
```

Keep this runbook at:

```text
docs/github_actions_ci_runbook.md
```

## What the workflow checks

1. Checks out the repository.
2. Uses Python 3.11.
3. Installs the project's pinned dbt Core and BigQuery adapter versions.
4. Creates a CI-only dbt profile using the same project, dataset, and region as development. OAuth is declared for profile validation; the workflow does not invoke a BigQuery connection.
5. Runs `python -m compileall -q src scripts`.
6. Runs `dbt parse --no-partial-parse` from `dbt_warehouse/saas_warehouse`.

`DBT_ENGINE_MANAGE_STATE=0` disables dbt-state management in this CI parse job, matching the local workaround used in this project. The reserved-prefix deprecation warning may appear; it is not itself a failure.

## GitHub setup and first run

1. Ensure the repository has a `main` branch on GitHub.
2. Copy the two files above into the repository, preserving their paths.
3. Commit and push the changes:

```bash
git add .github/workflows/dbt-ci.yml docs/github_actions_ci_runbook.md
git commit -m "Add GitHub Actions dbt CI validation"
git push origin main
```

4. Open the repository on GitHub and select **Actions**.
5. Open **NexusFlow dbt CI** and inspect the latest run.
6. Confirm the `Validate Python and dbt project` job passes.

You can also trigger the workflow manually using **Actions → NexusFlow dbt CI → Run workflow**.

## Trigger behavior

The workflow runs on pushes and pull requests that change any of:

- `dbt_warehouse/**`
- `src/**`
- `scripts/**`
- `requirements.txt`
- `.github/workflows/dbt-ci.yml`

It can also be started manually.

## Current scope and next stage

This is a validation-only CI workflow. It does not claim to test warehouse data or deploy models. The next stage is to configure GitHub Actions authentication to Google Cloud using Workload Identity Federation (OIDC), then add authenticated dbt build/test jobs with appropriately scoped permissions. Avoid storing a long-lived service-account JSON key in the repository.
