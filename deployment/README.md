# Deployment

AWS deployments will be managed using AWS CDK. This directory has files with CDK Stack objects.

## Creating

To create a new stack, add a file and follow the same pattern as the others. The Stack won't be synthesized until it is added to [app.py](../app.py).

## Isolation

In general, the stack files encapsulate all resources related to those ingest processes. This allowas creation and deletion without any side effects in the other stacks.

## Current State

At the end of the hackathon, the following was completed:

- dhw and npp ingest Stacks were added and deployed. However, the Cloudwatch event is disabled as the API was not ready.

Action Items:

- Sort out how to manually trigger the initial ingest for the dynamic sources. The Batch job or lambda will already exist, so they can be triggered manually, or sort out some other event.
- None of the ingest processes have been tested.
