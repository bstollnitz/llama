"Create an Azure endpoint and deployment for the llama model."

import logging

from azure.ai.ml import MLClient
from azure.ai.ml.entities import (CodeConfiguration, ManagedOnlineDeployment,
                                  ManagedOnlineEndpoint)
from azure.identity import DefaultAzureCredential
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient
from azure.mgmt.cognitiveservices.models import Account, AccountProperties, Sku

# Content Safety settings
# -----------------------
# Content Safety resources are currently available in two locations: "east us"
# and "west europe". Ideally, your endpoint should be in the same location as
# your Content Safety resource.
content_safety_name = "content-safety-llama"
content_safety_location = "east us"
content_safety_kind = "ContentSafety"
content_safety_sku_name = "S0"
content_safety_threshold = "2"

# Model settings
# --------------
# text generation: "Llama-2-7b", "Llama-2-13b", "Llama-2-70b"
# chat completion: "Llama-2-7b-chat", "Llama-2-13b-chat", "Llama-2-70b-chat"
model_name = "Llama-2-7b-chat"
model_version = "6"
registry_name = "azureml-meta"

# Endpoint and deployment settings
# --------------------------------
endpoint_name = "endpoint-llama"
deployment_name = "blue"
compute_instance_type = "Standard_NC24s_v3"


def find_content_safety_resource(csm_client, resource_group):
    """
    Find an existing Content Safety resource in the resource group, and return
    it.
    Return None if resource is not found.
    """
    resources = csm_client.accounts.list_by_resource_group(resource_group)
    content_safety_resources = [
        x for x in resources if x.kind == content_safety_kind and x.location ==
        content_safety_location and x.sku.name == content_safety_sku_name
    ]
    if len(content_safety_resources) > 0:
        aacs = content_safety_resources[0]
        logging.info("Found existing Content Safety resource %s.", aacs.name)
        return aacs
    return None


def create_content_safety_resource(csm_client, resource_group):
    """
    Create a new Content Safety resource in the resource group.
    """
    account = Account(
        sku=Sku(name=content_safety_sku_name),
        kind=content_safety_kind,
        location=content_safety_location,
        properties=AccountProperties(custom_sub_domain_name=content_safety_name,
                                     public_network_access="Enabled"),
    )
    content_safety = csm_client.accounts.begin_create(resource_group,
                                                      content_safety_name,
                                                      account).result()
    logging.info("Created Content Safety resource.")
    return content_safety


def find_or_create_content_safety_resource(credential, ml_client):
    """
    Create an Azure AI content safety resource, if one doesn't yet exist
    in the resource group.
    Return the endpoint and access key for the resource.
    """
    subscription_id = ml_client.subscription_id
    resource_group = ml_client.resource_group_name

    csm_client = CognitiveServicesManagementClient(credential, subscription_id)

    content_safety = find_content_safety_resource(csm_client, resource_group)
    if content_safety is None:
        content_safety = create_content_safety_resource(csm_client,
                                                        resource_group)

    content_safety_endpoint = content_safety.properties.endpoint

    content_safety_access_key = csm_client.accounts.list_keys(
        resource_group_name=resource_group,
        account_name=content_safety.name).key1

    logging.info("Content Safety endpoint is %s and access key is %s",
                 content_safety_endpoint, content_safety_access_key)
    return (content_safety_endpoint, content_safety_access_key)


def get_llama_model(credential, ml_client):
    """
    Get the llama model from the registry.
    """
    registry_client = MLClient(
        credential=credential,
        subscription_id=ml_client.subscription_id,
        resource_group_name=ml_client.resource_group_name,
        registry_name=registry_name,
    )
    llama_model = registry_client.models.get(model_name, version=model_version)
    return llama_model


def create_endpoint_deployment(ml_client, aacs_endpoint, aacs_access_key,
                               llama_model):
    """
    Create an endpoint and deployment for the llama model.
    """
    endpoint = ManagedOnlineEndpoint(name=endpoint_name)
    registered_endpoint = ml_client.begin_create_or_update(endpoint).result()

    deployment = ManagedOnlineDeployment(
        name=deployment_name,
        endpoint_name=endpoint_name,
        model=llama_model.id,
        instance_type=compute_instance_type,
        instance_count=1,
        code_configuration=CodeConfiguration(code="./llama/src/",
                                             scoring_script="score.py"),
        environment_variables={
            "CONTENT_SAFETY_ENDPOINT": aacs_endpoint,
            "CONTENT_SAFETY_KEY": aacs_access_key,
            "CONTENT_SAFETY_THRESHOLD": content_safety_threshold,
        })

    ml_client.begin_create_or_update(deployment).wait()

    # Set deployment traffic to 100%.
    registered_endpoint.traffic = {deployment_name: 100}
    ml_client.begin_create_or_update(registered_endpoint).wait()

    logging.info("Created endpoint %s and deployment %s.", endpoint_name,
                 deployment_name)


def main():
    logging.basicConfig(level=logging.INFO)

    # Authenticate to Azure.
    credential = DefaultAzureCredential()
    ml_client = MLClient.from_config(credential=credential)

    # Create a Content Safety resource on Azure.
    (aacs_endpoint, aacs_access_key) = find_or_create_content_safety_resource(
        credential, ml_client)

    # Get the llama model from the registry.
    llama_model = get_llama_model(credential, ml_client)

    # Create the endpoint and deployment.
    create_endpoint_deployment(ml_client, aacs_endpoint, aacs_access_key,
                               llama_model)


if __name__ == "__main__":
    main()