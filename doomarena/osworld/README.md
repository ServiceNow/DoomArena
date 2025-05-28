# OsWorld Attack Gateway

## Acknowledgements

Some of the files in this package have been directly copied from the original OSWorld repository, 
due to the difficulty of importing them, as they are not part of the `desktop_env` package.
In particular, the `mm_agents`, `run.py` and `doomarena/osworld/src/doomarena/osworld/lib_run_single.py` have been copied with minimal changes.

## Setup

Install the OSWOrld Gateway package. Note that this will install OSWorld as a dependency.
```bash
pip install -e doomarena/osworld
```

Additionally, please clone [OSWorld](https://github.com/xlang-ai/OSWorld) to a sibling directory to DoomArena to provide access to the evaluation examples.

Finally, complete the OSWorld setup by following their original setup instructions.
- You need to setup a virtual machine - we used VMWare Fusion on Mac.
- Please download the cache/ and place it in the root folder. This is important otherwise, we found several tasks depending on cache may fail.


## Run the experiment

Export your API keys to the environemnt. Note that we use openrouter for anthropic models.
```
export OPENROUTER_API_KEY="..."  # for anthropic models
export OPENAI_API_KEY="..."  # for openai models
```

Run experiments with Claude on a 
```bash
python doomarena/osworld/src/doomarena/osworld/scripts/run.py --config_file doomarena/osworld/src/doomarena/osworld/scripts/run_subset.yaml
```