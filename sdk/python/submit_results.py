import argparse
import os
import requests
import sys

def submit_results(file_path, project, environment, base_url, api_key, source="xml"):
    """
    Submits an XML file to the test-results-api.
    """
    url = f"{base_url.rstrip('/')}/xml-execution/process-and-save"

    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        sys.exit(1)

    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f, 'application/xml')}
        params = {
            'project': project,
            'environment': environment,
            'source': source
        }
        headers = {
            'X-API-Key': api_key
        }

        try:
            print(f"Submitting {file_path} to {url}...")
            print(f"Project: {project}, Environment: {environment}")

            response = requests.post(url, files=files, params=params, headers=headers)

            if response.status_code in (200, 201):
                print("Success! Execution created.")
                print(f"Response: {response.json()}")
                return True
            else:
                print(f"Failed with status code: {response.status_code}")
                print(f"Response: {response.text}")
                sys.exit(1)

        except requests.exceptions.RequestException as e:
            print(f"Network error occurred: {e}")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Submit XML test results to the Test Results API.")

    parser.add_argument('--file', required=True, help="Path to the XML file")
    parser.add_argument('--project', required=True, help="Name of the project")
    parser.add_argument('--environment', required=True, help="Execution environment (e.g., dev, staging)")
    parser.add_argument('--url', required=True, help="Base URL of the API (e.g., http://localhost:8000/api/v1)")
    parser.add_argument('--key', help="API Key (can also be set via API_KEY env var)")
    parser.add_argument('--source', default="xml", help="Source of the test results (default: xml)")

    args = parser.parse_args()

    api_key = args.key or os.environ.get('API_KEY')
    if not api_key:
        print("Error: API Key must be provided via --key argument or API_KEY environment variable.")
        sys.exit(1)

    submit_results(args.file, args.project, args.environment, args.url, api_key, args.source)

if __name__ == "__main__":
    main()
