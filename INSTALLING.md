# Install AI Virtual Agent

This guide will help you to install the AI Virtual Agent on an OpenShift AI platform.

## Requirements

### Minimum hardware requirements

- 1 GPU with 24GB of VRAM for the LLM, refer to the chart below
- 1 GPU with 24GB of VRAM for the safety/shield model (optional)

### Required software

- OpenShift Cluster 4.16+ with OpenShift AI 2.19+
- OpenShift Client CLI - [oc](https://docs.redhat.com/en/documentation/openshift_container_platform/4.18/html/cli_tools/openshift-cli-oc#installing-openshift-cli)
- Helm CLI - helm
- [huggingface-cli](https://huggingface.co/docs/huggingface_hub/guides/cli) (optional)
- [Hugging Face Token](https://huggingface.co/settings/tokens)
- Access to [Meta Llama](https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct/) model.
- Access to [Meta Llama Guard](https://huggingface.co/meta-llama/Llama-Guard-3-8B/) model.

### Supported Models

| Function    | Model Name                             | GPU         | AWS
|-------------|----------------------------------------|-------------|-------------
| Embedding   | `all-MiniLM-L6-v2`                     | CPU or GPU  |
| Generation  | `meta-llama/Llama-3.2-3B-Instruct`     | L4          | g6.2xlarge
| Generation  | `meta-llama/Llama-3.1-8B-Instruct`     | L4          | g6.2xlarge
| Generation  | `meta-llama/Meta-Llama-3-70B-Instruct` | A100 x2     | p4d.24xlarge
| Safety      | `meta-llama/Llama-Guard-3-8B`          | L4          | g6.2xlarge

Note: the 70B model is NOT required for initial testing of this example.  The safety/shield model `Llama-Guard-3-8B` is also optional.

## Install

1. Clone the repo so you have a working copy

```bash
git clone https://github.com/rh-ai-kickstart/ai-virtual-agent
```

2. Login to your OpenShift Cluster

```bash
oc login --server="<cluster-api-endpoint>" --token="sha256~XYZ"
```

3. If the GPU nodes are tainted, find the taint key. You will have to pass in the
   make command to ensure that the llm pods are deployed on the tainted nodes with GPU.
   In the example below the key for the taint is `nvidia.com/gpu`

```bash
oc get nodes -l nvidia.com/gpu.present=true -o yaml | grep -A 3 taint 
```

The output of the command may be something like below

```
  taints:
    - effect: NoSchedule
      key: nvidia.com/gpu
      value: "true"
--
    taints:
    - effect: NoSchedule
      key: nvidia.com/gpu
      value: "true"
```

You can work with your OpenShift cluster admin team to determine what labels and taints identify GPU-enabled worker nodes.  It is also possible that all your worker nodes have GPUs therefore have no distinguishing taint.

4. Navigate to Helm deploy directory

```bash
cd deploy/helm
```

5. List available models

```bash
make list-models
```

The above command will list the models to use in the next command

```bash
(Output)
model: llama-3-1-8b-instruct (meta-llama/Llama-3.1-8B-Instruct)
model: llama-3-2-1b-instruct (meta-llama/Llama-3.2-1B-Instruct)
model: llama-3-2-1b-instruct-quantized (RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8)
model: llama-3-2-3b-instruct (meta-llama/Llama-3.2-3B-Instruct)
model: llama-3-3-70b-instruct (meta-llama/Llama-3.3-70B-Instruct)
model: llama-guard-3-1b (meta-llama/Llama-Guard-3-1B)
model: llama-guard-3-8b (meta-llama/Llama-Guard-3-8B)
```

The "guard" models can be used to test shields for profanity, hate speech, violence, etc.

6. Install via make

Use the taint key from above as the `LLM_TOLERATION` and `SAFETY_TOLERATION`

The namespace will be auto-created

To install only the AI Virtual Agent without shields, use the following command:

```bash
make install NAMESPACE=ai-virtual-agent LLM=llama-3-1-8b-instruct LLM_TOLERATION="nvidia.com/gpu"
```

To install AI Virtual Agent with the guard model to allow for shields, use the following command:

```bash
make install NAMESPACE=ai-virtual-agent LLM=llama-3-1-8b-instruct LLM_TOLERATION="nvidia.com/gpu" SAFETY=llama-guard-3-8b SAFETY_TOLERATION="nvidia.com/gpu"
```

If you have no tainted nodes, perhaps every worker node has a GPU, then you can use a simplified version of the make command

```bash
make install NAMESPACE=ai-virtual-agent LLM=llama-3-1-8b-instruct SAFETY=llama-guard-3-8b
```

When prompted, enter your **[Hugging Face Token]((https://huggingface.co/settings/tokens))**.

Note: This process may take 10 to 30 minutes depending on the number and size of models to be downloaded.

7. Watch/Monitor

```bash
oc get pods -n ai-virtual-agent
```

```
(Output)
NAME                                                                READY   STATUS      RESTARTS   AGE
add-default-ingestion-pipeline-brfbb                                0/1     Completed   0          10m
ai-virtual-agent-854f8588dc-86kmb                               2/2     Running     0          10m
ai-virtual-agent-fnc6j                                          0/1     Completed   3          10m
ai-virtual-agent-ingestion-pipeline-6dcb65b4fc-mxmp9            1/1     Running     0          10m
ai-virtual-agent-mcp-weather-646654864d-j8wbh                   1/1     Running     0          10m
ds-pipeline-dspa-855d64dcdc-gqtqw                                   2/2     Running     0          10m
ds-pipeline-metadata-envoy-dspa-7759f8589d-vhcvx                    2/2     Running     0          10m
ds-pipeline-metadata-grpc-dspa-6df7dbc65d-r4svx                     1/1     Running     0          10m
ds-pipeline-persistenceagent-dspa-c84c998bb-x2jnc                   1/1     Running     0          10m
ds-pipeline-scheduledworkflow-dspa-7f4cbfbb6f-vd6fz                 1/1     Running     0          10m
ds-pipeline-workflow-controller-dspa-dd69bddd6-5tj9b                1/1     Running     0          10m
fetch-and-store-pipeline-m6kbg-system-container-driver-3649736823   0/2     Completed   0          10m
fetch-and-store-pipeline-m6kbg-system-container-driver-662109129    0/2     Completed   0          10m
fetch-and-store-pipeline-m6kbg-system-container-impl-1096845703     0/2     Completed   0          10m
fetch-and-store-pipeline-m6kbg-system-container-impl-3659398265     0/2     Completed   0          10m
fetch-and-store-pipeline-m6kbg-system-dag-driver-1735541709         0/2     Completed   0          10m
ingestion-pipeline-monitor-85585696d4-d67zx                         2/2     Running     0          10m
llama-3-2-3b-instruct-predictor-00001-deployment-6bbf96f8674677     3/3     Running     0          10m
llamastack-6dc8bdd5c4-vpft7                                         1/1     Running     0          10m
mariadb-dspa-9bc764fdf-pq8wd                                        1/1     Running     0          10m
minio-0                                                             1/1     Running     0          10m
minio-dspa-68bf8b6947-dsxpv                                         1/1     Running     0          10m
pgvector-0                                                          1/1     Running     0          10m
rag-pipeline-notebook-0                                             2/2     Running     0          10m
upload-sample-docs-job-zlc74                                        0/1     Completed   0          10m

```

8. Verify:

Verify if all the pods are running, and the jobs have completed successfully.

```bash
oc get pods -n ai-virtual-agent
```

The key pods to watch include **predictor** in their name, those are the kserve model servers running vLLM

```bash
oc get pods -l component=predictor
```

Look for **2/2** under the Ready column

The **inferenceservice** CR describes the limits, requests, model name, serving-runtime, chat-template, etc.

```bash
oc get inferenceservice llama-3-1-8b-instruct \
  -n ai-virtual-agent \
  -o jsonpath='{.spec.predictor.model}' | jq
```

Watch the **llamastack** pod as that one becomes available after all the model servers are up.

```bash
 oc get pods -l app.kubernetes.io/name=llamastack
```

### Using the AI Virtual Agent UI

1. Get the route url for the application and open in your browser

```bash
URL=http://$(oc get routes --field-selector metadata.name=ai-virtual-assistant  -o jsonpath="{range .items[*]}{.status.ingress[0].host}{end}")
echo $URL
open $URL
```

## Uninstalling the AI Virtual Agent application

Uninstall the application and its dependencies

```bash
make uninstall NAMESPACE=ai-virtual-agent
```

Delete the project

```bash
oc delete project ai-virtual-agent
```
