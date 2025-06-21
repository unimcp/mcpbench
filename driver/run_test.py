import argparse
import json
import subprocess
from pathlib import Path
from .docker_generator import generate_test_compose

def load_sdk_info():
    with open('compatibility-tests/driver/sdkinfo.json', 'r') as f:
        return json.load(f)

def are_versions_compatible(sdk_info, lang1, ver1, lang2, ver2):
    try:
        compatible_versions = sdk_info[lang1][ver1]['compatibility_matrix'][lang2]
        return ver2 in compatible_versions
    except KeyError:
        return False

def main():
    parser = argparse.ArgumentParser(description='Run compatibility tests between two SDK versions')
    parser.add_argument('lang1', help='First language (python/typescript/rust)')
    parser.add_argument('ver1', help='First version')
    parser.add_argument('lang2', help='Second language (python/typescript/rust)')
    parser.add_argument('ver2', help='Second version')
    args = parser.parse_args()

    # Load SDK info and check compatibility
    sdk_info = load_sdk_info()
    if not are_versions_compatible(sdk_info, args.lang1, args.ver1, args.lang2, args.ver2):
        print(f"Error: {args.lang1} {args.ver1} is not compatible with {args.lang2} {args.ver2}")
        return 1

    # Generate docker-compose file
    test_dir = generate_test_compose(args.lang1, args.ver1, args.lang2, args.ver2)
    
    # Run docker-compose
    try:
        subprocess.run(['docker-compose', '-f', str(test_dir / 'docker-compose.yml'), 'up', '--build'], check=True)
        return 0
    except subprocess.CalledProcessError as e:
        print(f"Error running docker-compose: {e}")
        return 1

if __name__ == '__main__':
    exit(main()) 