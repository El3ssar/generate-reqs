#!/usr/bin/python3

import yaml
import click
import logging
import subprocess
import sys
import os

def parse_environment_yml(contents):
    """
    Parse the environment YAML contents and return the names of explicitly installed packages.
    """
    env = yaml.safe_load(contents)
    
    conda_packages = []
    for dep in env['dependencies']:
        if isinstance(dep, str):
            if 'pip' not in dep and 'python=' not in dep:
                conda_packages.append(dep.split('=')[0])  # Strip versions to match with conda list
        elif isinstance(dep, dict) and 'pip' in dep:
            # Handle pip packages listed in the YAML file
            conda_packages.extend([pkg.split('=')[0] for pkg in dep['pip']])

    return conda_packages

def get_conda_list_versions():
    """
    Get the list of installed packages with their versions using conda list.
    Strips off the build hash (if present).
    """
    try:
        result = subprocess.run(
            ['conda', 'list', '--export'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )
        conda_list = []
        for line in result.stdout.splitlines():
            if '=' in line:
                # Only keep the package=version part, discarding the build hash
                package_version = '='.join(line.split('=')[:2])
                conda_list.append(package_version)
        return conda_list
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to run conda list: {e.stderr}")
        sys.exit(1)

def filter_conda_list_with_history(history_packages, conda_list):
    """
    Filter the conda list output to match only the packages from conda env --from-history.
    """
    conda_dict = {pkg.split('=')[0]: pkg for pkg in conda_list if '=' in pkg}
    filtered_packages = [conda_dict[pkg] for pkg in history_packages if pkg in conda_dict]
    return filtered_packages

def write_requirements_txt(conda_packages, output_file):
    """
    Write the requirements.txt file from the list of conda packages.
    """
    with open(output_file, 'w') as file:
        for package in conda_packages:
            file.write(package + '\n')
    logging.info(f"requirements.txt generated with {len(conda_packages)} packages at {output_file}.")

def get_active_conda_env():
    """
    Get the name of the currently active conda environment.
    """
    conda_env = os.getenv('CONDA_DEFAULT_ENV')
    if conda_env == 'base':
        logging.error("You are using the 'base' conda environment. Please activate another environment.")
        sys.exit(1)
    return conda_env

def export_conda_env():
    """
    Export the current conda environment using `conda env export --from-history`.
    """
    try:
        result = subprocess.run(
            ['conda', 'env', 'export', '--from-history'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to export conda environment: {e.stderr}")
        sys.exit(1)

@click.command()
@click.argument('yml_file', required=False, type=click.Path(exists=True))
@click.option('-o', '--output', default='requirements.txt', help='Output file for the generated requirements.txt (default is "requirements.txt").')
@click.pass_context
def main(ctx, yml_file, output):
    """
    A utility to generate a requirements.txt from a conda environment.

    This script generates a `requirements.txt` file for Python projects
    based on the currently active conda environment, ensuring only explicitly installed 
    packages are included with their respective versions.

    Usage:
    
    - If no environment.yml is provided, the script will export the current active conda environment using `conda env export --from-history` and generate the `requirements.txt`.
    
    - If an environment.yml file is provided, the script will parse it, retrieve package names, 
      cross-reference with `conda list` to get the version information, and output the final `requirements.txt`.

    Examples:

    - Generate from the current conda environment:
        $ generate-reqs

    - Generate from a specific environment.yml file:
        $ generate-reqs environment.yml -o custom_requirements.txt
    """

    logging.basicConfig(level=logging.INFO)
    
    if not yml_file:
        # Check if a non-base conda environment is active
        conda_env = get_active_conda_env()
        logging.info(f"Retrieving conda environment: {conda_env}")
        
        # Export the active conda environment using `conda env export --from-history`
        yml_contents = export_conda_env()
    else:
        # Read the given environment.yml file
        with open(yml_file, 'r') as file:
            yml_contents = file.read()

    # Parse the environment YAML contents to get the list of explicitly installed packages
    history_packages = parse_environment_yml(yml_contents)

    # Get the installed packages with versions using conda list
    conda_list = get_conda_list_versions()

    # Filter the conda list output to only include packages from the history
    conda_packages = filter_conda_list_with_history(history_packages, conda_list)

    # Write the filtered packages to requirements.txt
    write_requirements_txt(conda_packages, output)

if __name__ == "__main__":
    main()

