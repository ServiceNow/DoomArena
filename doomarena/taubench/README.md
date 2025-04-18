# TauBench experiments

This repository contains tools and scripts for defining and evaluating threat models in the [TauBench](https://github.com/sierra-research/tau-bench) framework. TauBench focuses on **LLM agents in tool-augmented environments**, providing a way to simulate realistic adversarial attacks in domains like **retail** and **airline** customer service.

## Overview

The framework provides a structured way to:
- Simulate tool-based adversarial scenarios against LLM agents
- Measure metrics like Attack Success Rate (ASR), Task Success Rate (TSR), and stealthiness of attacks
- Compare defenses or model variants across structured multi-turn tasks
- Evaluate robustness of tool-using agents in realistic settings

## Domains

TauBench currently supports:

- **Retail**: Multi-tool shopping agents that handle product searches, returns, and recommendations
- **Airline**: Agents for booking flights, managing itineraries, and accessing sensitive account information

## Installation

1. Install this package
```
# install main from this repo
pip install -e doomarena/taubench

# or install from pypi
pip install doomarena-taubench
```

2. Install taubench

```bash
git clone https://github.com/sierra-research/tau-bench scripts/tau-bench
pip install -e git+https://github.com/sierra-research/tau-bench.git#egg=tau_bench
```

3. You may also need to set your OpenRouter API key:

```bash
export OPENROUTER_API_KEY=<your-api-key>
export OPENAI_API_KEY=<your-api-key>
```

## Usage

Example (Retail malicious user attack):

```bash
cd doomarena/taubench/src/doomarena/taubench
python scripts/attack_script.py \
  --config scripts/malicious_user_retail_attack.yaml
```

### Experiment Configuration Options

- `combined_retail_attack.yaml`  
  Runs multiple retail attack types in a single config for comprehensive evaluation.

- `malicious_catalog_fixed_injection_retail_attack.yaml`  
  Inserts a malicious product entry into the retail catalog with a fixed injection strategy.

- `malicious_catalog_retail_attack.yaml`  
  Injects a dynamic malicious catalog item to mislead the retail agent.

- `malicious_user_airline_attack.yaml`  
  Simulates a malicious user attempting to manipulate the airline booking assistant.

- `malicious_user_fixed_injection_airline_attack.yaml`  
  Similar to the above but with fixed injection content for consistent attack setup.

- `malicious_user_retail_attack.yaml`  
  Tests how a retail agent handles adversarial inputs from a user aiming to bypass rules or gain unauthorized benefits.

Each config specifies:

- Attack type and injection method
- Success filters
- Prompt construction (system + few-shot examples)

## Results and Metrics

Experiment results are stored in the `results/taubench` directory, organized by the datetime when they were created. Each results folder includes:

- Metadata about the attack configuration, agent, and dataset used
- CSV files containing metrics such as:
  - Attack Success Rate (ASR)
  - Task Success Rate (TSR)
  - Attack Stealth Rate
  - Tool call counts and usage breakdowns
  - Input/output token counts
  - Step-by-step interaction logs with the agent

You can analyze per-task outcomes to understand failure modes, effectiveness of the attacks, and behavior of tool-augmented agents under adversarial pressure.

## Project Structure

```
├── README.md 
├── pyproject.toml 
├── src/doomarena/taubench/                  
    ├── attack_gateway.py            # Entry point for attack orchestration
    ├── data/                        # JSON datasets for different domains
    │   ├── airline_classification.json
    │   ├── retail_classification.json
    │   └── sample_airline.json
    ├── filters/                     # Filters for selecting relevant agent actions
    │   ├── is_get_product_details_action_filter.py
    │   └── is_respond_action_filter.py
    ├── success_filters/            # Criteria for judging if attack succeeded
    │   ├── airline_info_leak_success_filter.py
    │   ├── llm_judge.py
    │   ├── retail_refund_success_filter.py
    │   ├── retail_secrets_success_filter.py
    │   └── send_certificate_success_filters.py
    ├── system_prompt_config/       # Prompt configurations and few-shot data
    │   ├── system_prompt_initialization.py
    │   ├── utils.py
    │   ├── dan_mode/
    │   │   ├── dan_mode_airline.txt
    │   │   ├── dan_mode_retail.txt
    │   │   └── dan_mode_retaildb.txt
    │   ├── few_shot_examples/
    │   │   ├── airline_few_shot.json
    │   │   ├── retail_few_shot.json
    │   │   └── retaildb_few_shot.json
    │   └── tools/
    │       ├── airline_tools.json
    │       └── retail_tools.json
    ├── scripts/                    # YAML attack configs and the main runner
    │   ├── combined_retail_attack.yaml
    │   ├── malicious_catalog_fixed_injection_retail_attack.yaml
    │   ├── malicious_catalog_retail_attack.yaml
    │   ├── malicious_user_airline_attack.yaml
    │   ├── malicious_user_fixed_injection_airline_attack.yaml
    │   ├── malicious_user_retail_attack.yaml
    │   └── attack_script.py
├── tests/
    ├── test_data
        ├── taubench_config.yaml
    ├── __init__.py
    ├── test_run_tau_bench_attack.py
    ├── test_taubench_attack_config.py
    ├── test_taubench_attack_gateway.py
```

## Contributing

Contributions are welcome! You can extend this framework by:
1. Adding new attack vectors -- new prompt injections or misuse of tools in the airline or retail domains
2. Testing additional agent models -- evaluate how different LLMs or fine-tuned agents perform under attack
3. Implementing new evaluation metrics -- define novel task-specific or stealth-aware success criteria