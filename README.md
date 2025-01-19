# ExSimula

ExSimula is an advanced platform for autonomous, multi-agent large language model (LLM) workflows.


## Prerequisites

Create a virtual environment using:

```
python -m pip install virtualenv
python -m virtualenv .venv
source .venv/bin/activate
```

## Requirements

Install all requirements using:

```
python -m pip install -r requirements.txt
```


## Usage

See help using:

```
python main.py --help
```

## Example

Run the example using:

```
python main.py \
	--program "example/program.json" \
	--memory "example/memory.json"
```