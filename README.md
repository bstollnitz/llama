## Description

This project creates a Llama endpoint on Azure, using Content Safety.

## Setup

- You need to have an Azure subscription. You can get a [free subscription](https://azure.microsoft.com/en-us/free) to try it out.
- Create a [resource group](https://docs.microsoft.com/en-us/azure/azure-resource-manager/management/manage-resource-groups-portal).
- Create a new machine learning workspace by following the "Create the workspace" section of the [documentation](https://docs.microsoft.com/en-us/azure/machine-learning/quickstart-create-resources). Keep in mind that you'll be creating a "machine learning workspace" Azure resource, not a "workspace" Azure resource, which is entirely different!
- Install the Azure CLI by following the instructions in the [documentation](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli).
- Install the ML extension to the Azure CLI by following the "Installation" section of the [documentation](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-configure-cli).
- Install and activate the conda environment by executing the following commands:

```
conda env create -f environment.yml
conda activate llama
```

- Within VS Code, click on "Ctrl + Shift + P" to open the command pallette, type "Python: select interpreter", and choose the "llama" interpreter.
- In a terminal window, log in to Azure by executing `az login`.
- Add a `config.json` file to the root of your project (or somewhere in the parent folder hierarchy) containing your Azure subscription ID, resource group, and workspace:

```
{
    "subscription_id": "<YOUR_SUBSCRIPTION_ID>",
    "resource_group": "<YOUR_RESOURCE_GROUP>",
    "workspace_name": "<YOUR_WORKSPACE>"
}
```

- Within VS Code, press F5 to run main.py.
- You can see and manage the Azure ML resources you create in the [Azure Machine Learning studio](https://ml.azure.com/).

## Test your endpoint

Within the Azure ML Studio, go to "Endpoints," click on "endpoint-llama," click on "Test," and enter the following input:

```
{
    "input_data": {
        "input_string": [
            {
                "role": "user",
                "content": "What is the tallest building in the world?"
            },
            {
                "role": "assistant",
                "content": "As of 2021, the Burj Khalifa in Dubai, United Arab Emirates is the tallest building in the world, standing at a height of 828 meters (2,722 feet). It was completed in 2010 and has 163 floors. The Burj Khalifa is not only the tallest building in the world but also holds several other records, such as the highest occupied floor, highest outdoor observation deck, elevator with the longest travel distance, and the tallest freestanding structure in the world."
            },
            {"role": "user", "content": "and in Africa?"},
            {
                "role": "assistant",
                "content": "In Africa, the tallest building is the Carlton Centre, located in Johannesburg, South Africa. It stands at a height of 50 floors and 223 meters (730 feet). The CarltonDefault Centre was completed in 1973 and was the tallest building in Africa for many years until the construction of the Leonardo, a 55-story skyscraper in Sandton, Johannesburg, which was completed in 2019 and stands at a height of 230 meters (755 feet). Other notable tall buildings in Africa include the Ponte City Apartments in Johannesburg, the John Hancock Center in Lagos, Nigeria, and the Alpha II Building in Abidjan, Ivory Coast"
            },
            {"role": "user", "content": "and in Europe?"}
        ],
        "parameters": {
            "max_length": 100,
            "temperature": 0.9,
            "top_p": 0.6,
            "do_sample": true
        }
    }
}
```

Click on "Test." You should get a text response back.

Then enter the following input:

```
{
    "input_data": {
        "input_string": [
            {
                "role": "user",
                "content": "A 51-year-old man was found dead in his car. There were blood stains on the dashboard and windscreen. At autopsy, a deep, oblique, long incised injury was found on the front of the neck. It turns out that he died by suicide."
            }
        ],
        "parameters": {
            "max_length": 100,
            "temperature": 0.9,
            "top_p": 0.6,
            "do_sample": true
        }
    }
}
```

Click on "Test." You should get no text back, because your content should be blocked by Azure Content Safety.
