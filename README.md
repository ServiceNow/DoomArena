# Research on Agent Attacks

<img src="https://github.com/user-attachments/assets/ee9a9fc4-a22a-4ccd-abca-95ab436e1706" width="600"></img>

## Contributing

Contributions are welcome! You can extend this framework by:
1. Contributing new attacks, including automated red-teaming agents
2. Supporting new environements by implementing new attack gateways
3. Supporting new threat models / attack vectors by extending existing attack gateways
4. Implementing new evaluation metrics.
5. Testing additional agent models and LLMs.

## Setup

Create a virtual environment and install the package locally in editable mode using
```bash
pip install -e doomarena/core
```

Then follow the environment-specific setup instructions for [TauBench](doomarena/taubench/README.md) and [BrowserGym](doomarena/browsergym/README.md)

Export relevant API keys into your environment or `.env` file.
```bash
OPENAI_API_KEY="<your api key>"
OPENROUTER_API_KEY="<your api key>"
```

Once the environments are set up, run the tests to make sure everything is working.
```bash
pytest
```



