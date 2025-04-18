# DoomArena - Adaptive Security Testing against Evolving Risks

<img src="https://github.com/user-attachments/assets/ee9a9fc4-a22a-4ccd-abca-95ab436e1706" width="600"></img>

## Setup

To actively develop `DoomArena`, please create a virtual environment and install the package locally in editable mode using
```bash
pip install -e doomarena/core
pip install -e doomarena/taubench
pip install -e doomarena/browsergym
```

If you just want to use the library just run
```bash
pip install doomarena
pip install doomarena-taubench  # optional
pip install doomarena-browsergym  # optional
```

Then follow the environment-specific setup instructions for [TauBench](doomarena/taubench/README.md) and [BrowserGym](doomarena/browsergym/README.md)

Export relevant API keys into your environment or `.env` file.
```bash
OPENAI_API_KEY="<your api key>"
OPENROUTER_API_KEY="<your api key>"
```

Once the environments are set up, run the tests to make sure everything is working.
```bash
make ci-tests
make tests  # requires openai key
```



