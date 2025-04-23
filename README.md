# DoomArena: A Framework for Testing AI Agents Against Evolving Security Threats


[![pypi](https://badge.fury.io/py/doomarena.svg)](https://pypi.org/project/doomarena/)
[![PyPI - License](https://img.shields.io/pypi/l/doomarena?style=flat-square)]([https://opensource.org/licenses/MIT](http://www.apache.org/licenses/LICENSE-2.0))
[![PyPI - Downloads](https://img.shields.io/pypi/dm/doomarena?style=flat-square)](https://pypistats.org/packages/doomarena)
[![GitHub star chart](https://img.shields.io/github/stars/ServiceNow/DoomArena?style=flat-square)](https://star-history.com/#ServiceNow/DoomArena)

[DoomArena](https://servicenow.github.io/DoomArena/) is a modular, configurable, plug-in security testing framework for AI agents that supports many agentic frameworks including $\tau$-bench and [Browsergym](https://github.com/ServiceNow/browsergym). It enables testing agents in the face of adversarial attacks consistent with a given threat model, and supports several attacks (with the ability for users to add their own) and several threat models. 

<img src="https://raw.githubusercontent.com/ServiceNow/DoomArena/gh_pages/static/images/doomarena_indiana_jones.jpg" width="600"></img>





## Quick Start

The [DoomArena Intro Notebook](https://colab.research.google.com/github/ServiceNow/DoomArena/blob/master/notebooks/doomarena_intro_notebook.ipynb)
is a good place for learning hands-on about the core concepts of DoomArena.
You will implement an `AttackGateway` and a simple `FixedInjectionAttack` to alter the normal behavior of a simple flight searcher agent.

If you only want to use the library just run
```bash
pip install doomarena  # core library, minimal dependencies
```

If you want to run DoomArena integrated with [TauBench](https://github.com/sierra-research/tau-bench/), additionally run

```bash
pip install doomarena-taubench  # optional
```

If you want to run DoomArena integrated with [Browsergym](https://github.com/ServiceNow/BrowserGym), additionally run

```bash
pip install doomarena-browsergym  # optional
```



Export relevant API keys into your environment or `.env` file.
```bash
OPENAI_API_KEY="<your api key>"
OPENROUTER_API_KEY="<your api key>"
```

## Advanced Setup

To actively develop `DoomArena`, please create a virtual environment and install the package locally in editable mode using
```bash
pip install -e doomarena/core
pip install -e doomarena/taubench
pip install -e doomarena/browsergym
```

Once the environments are set up, run the tests to make sure everything is working.
```bash
make ci-tests
make tests  # requires openai key
```


## Running Experiments

Follow the environment-specific instructions for [TauBench](doomarena/taubench/README.md) and [BrowserGym](doomarena/browsergym/README.md)


## Paper

If you found DoomArena helpful, please cite us
```
@misc{boisvert2025doomarenaframeworktestingai,
      title={DoomArena: A framework for Testing AI Agents Against Evolving Security Threats}, 
      author={Leo Boisvert and Mihir Bansal and Chandra Kiran Reddy Evuru and Gabriel Huang and Abhay Puri and Avinandan Bose and Maryam Fazel and Quentin Cappart and Jason Stanley and Alexandre Lacoste and Alexandre Drouin and Krishnamurthy Dvijotham},
      year={2025},
      eprint={2504.14064},
      archivePrefix={arXiv},
      primaryClass={cs.CR},
      url={https://arxiv.org/abs/2504.14064}, 
}
```
