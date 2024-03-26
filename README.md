# Statsig Semantic Layer Synchronization Demo

Welcome to the demonstration repository for synchronizing a semantic layer with Statsig. This repository showcases how to integrate Statsig with your data metrics and sources through an automated process. Utilizing a [script executed by a GitHub Action](https://github.com/statsig-io/semantic_layer/blob/main/.github/scripts/statsig_sync.py), this setup automatically synchronizes changes to `.yml` files located in the `/metrics` or `/metric_sources` directories. This means that whenever you create or update these files, the script either updates existing metrics or metric sources in Statsig or creates new ones accordingly. Note: The current setup does not handle deletions.

To integrate this process into your workflow, follow these steps:

1. Fork this repository to get started.
2. In your forked repository, add your Statsig Console API Key to GitHub Secrets.
3. Tailor the metric definitions to align with your data needs.
4. Verify the automation by modifying relevant files and observing the triggered GitHub Action.

## Detailed Guide

### Forking the Repository

1. **Fork this repository** to create a copy in your GitHub account.

### Adding the Statsig Console

2. Navigate to `Settings > Secrets` in your repository settings. Create a new secret named `STATSIG_API_KEY` with your Statsig Console API key as its value. This key facilitates authentication with the Statsig Console API for the synchronization process.

### Customizing Metric Definitions

3. Metric definitions reside within the `./metrics` directory, and metric source definitions are found in the `./metric_sources/` directory. To customize:

   - Utilize the Statsig Console API to fetch an existing `metric_source` and its associated metrics using [GET requests](https://docs.statsig.com/console-api/metrics#post-/metrics/metric_source/-name-) for metric sources and [metrics](https://docs.statsig.com/console-api/metrics#get-/metrics/-metric_id-).
   - Remove the provided example metrics and replace them with your definitions in `./metric_sources/*.yml` and `./metrics/*.yml`.

*Note:* For enhanced readability, we modified `metric.warehouseNative[]` to `metric.metricDefinition[]` in our examples. You can see this change [here](https://github.com/statsig-io/semantic_layer/blob/1611a68703caf18d7fa32088ff06d568d8b3b03a/.github/scripts/statsig_sync.py#L38). Feel free to adjust the translations or revert to using `metric.warehouseNative[]` in your definitions.

### Verifying Automation

4. To test, edit a metric or metric source description in your repository. This action should trigger the GitHub Action, visible under the `Actions` tab. The process will then either create or update your metrics and metric sources in Statsig based on the repository's semantic definitions.

### Seeking Feedback

5. This example serves as a basic Minimum Viable Product (MVP). We encourage testing and further development to meet production standards. Please share any feedback or improvements you've made to this workflow. Thank you for your contributions!
