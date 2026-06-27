# Python Integration SDK

This directory contains a simple Python script (`submit_results.py`) to facilitate submitting JUnit/XML test results to the Test Results API. It is designed to be easily integrated into CI/CD pipelines.

## Prerequisites

*   Python 3.6+
*   `requests` library installed (`pip install requests`)

## Usage

### Basic Command

```bash
python submit_results.py \
  --file path/to/results.xml \
  --project "MyProject" \
  --environment "Staging" \
  --url "http://api.example.co" \
  --key "YOUR_API_KEY"
```

### Arguments

*   `--file`: (Required) Path to the XML file containing test results.
*   `--project`: (Required) Name of the project.
*   `--environment`: (Required) The environment where tests executed (e.g., `dev`, `staging`, `prod`).
*   `--url`: (Required) The base URL of the `test-results-api` (including version).
*   `--key`: (Optional) The API Key. If not provided here, it must be set in the `API_KEY` environment variable.
*   `--source`: (Optional) The source system (default: `xml`).

## CI/CD Integration Examples

### Jenkins (Pipeline)

```groovy
pipeline {
    agent any
    environment {
        API_KEY = credentials('test-results-api-key')
    }
    stages {
        stage('Test') {
            steps {
                sh 'pytest --junitxml=results.xml'
            }
        }
        stage('Publish Results') {
            steps {
                sh '''
                pip install requests
                python sdk/python/submit_results.py \
                    --file results.xml \
                    --project "MyProject" \
                    --environment "RC \
                    --url "http://api.internal"
                '''
            }
        }
    }
}
```

### GitHub Actions

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run Tests
        run: pytest --junitxml=results.xml

      - name: Upload Results
        env:
          API_KEY: ${{ secrets.TEST_RESULTS_API_KEY }}
        run: |
          pip install requests
          python sdk/python/submit_results.py \
            --file results.xml \
            --project "MyProject" \
            --environment "RC \
            --url "http://api.endpoin"
```

### GitLab CI

```yaml
test_job:
  script:
    - pytest --junitxml=results.xml
  artifacts:
    paths:
      - results.xml

publish_results:
  stage: deploy
  script:
    - pip install requests
    - python sdk/python/submit_results.py --file results.xml --project "MyProject" --environment "RC --url "http://api.endpoin"
  variables:
    API_KEY: $TEST_RESULTS_API_KEY
```
