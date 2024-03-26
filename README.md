# Statsig Semantic Layer Sync Demo

This repository is a working example of a semantic layer sync into Statsig. This repository has a [GitHub Action](https://github.com/statsig-io/semantic_layer/blob/main/.github/scripts/statsig_sync.py) that [syncs on file creation or update](https://github.com/statsig-io/semantic_layer/blob/main/.github/workflows/statsig_sync.yml) to `*.yml` files in the `/metrics` or `/metric_sources` directories, and then either updates or creates a new metric or metric source in Statsig. The setup steps are as follows:

1. Clone this repository.
2. Add the Statsig Console API Key to GitHub Secrets.
3. Update metric defitions to match your data as necessary.
4. Test that the Python script is called by the GitHub Action when the relevant files are changed.

Below is a guide on how to implement this solution.

### Step 1: Clone this repository

### Step 2: Add the Statsig Console API Key to GitHub Secrets in your repository

In your GitHub repository, go to Settings > Secrets and add a new secret named `STATSIG_API_KEY` with your Statsig *Console API key* as the value. This key will be used by the GitHub Action to securely authenticate with Statsig's API.

### Step 3: Update metric defitions to match your data as necessary

Metrics are defined in the `./metrics` folder and metric sources are defined in the `./metric_sources/` folder.

A good way to get started here using your own configurations is to use the Statsig Console API to [GET an already created metric_source](https://docs.statsig.com/console-api/metrics#post-/metrics/metric_source/-name-) and some of it's associated [metrics](https://docs.statsig.com/console-api/metrics#get-/metrics/-metric_id-). Then, you can remove the example metrics and add your defitions into `./metric_sources/*.yml` and `./metrics/*.yml`.

*Important note:* In this example, in my metric defitions I have changed `metric.warehouseNative[]` to `metric.metricDefition[]` for human readability. [That change is made here](https://github.com/statsig-io/semantic_layer/blob/1611a68703caf18d7fa32088ff06d568d8b3b03a/.github/scripts/statsig_sync.py#L38) if you want to tinker around with translations or remove this example and use `metric.warehouseNative[]` in your semantic defitions.

### Step 4: Ensure that the Python script is called by the GitHub Action when relevant files are changed

Now, edit the description of one of your metrics or metric sources. This should kick off a call to the Github Action, which you can monitor in the `Actions` tab, which should create or update your metrics and metric sources in Statsig based on the semantic definitions in the repository.

### Step 5: Feedback?

This is a very basic working MVP example. Please test and harden for production use cases. Share feedback or improvements you've made to this workflow. Thanks!

