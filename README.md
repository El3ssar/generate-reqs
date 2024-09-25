# generate-reqs

A utility to generate `requirements.txt` from a conda environment. This tool can help convert a conda environment to a pip-compatible `requirements.txt`.

## Usage

```bash
# Generate from the active conda environment:
$ generate-reqs

# Generate from a specific environment.yml file:
$ generate-reqs environment.yml -o custom_requirements.txt

