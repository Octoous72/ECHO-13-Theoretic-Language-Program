name: Deploy Python project to Azure Function App

on:
  push:
    branches: [ "main" ]

env:
  AZURE_FUNCTIONAPP_NAME: ${{ secrets.AZURE_FUNCTIONAPP_NAME }}
  AZURE_FUNCTIONAPP_PACKAGE_PATH: "."
  PYTHON_VERSION: "3.10"

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    environment: dev

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Resolve Project Dependencies Using Pip
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt --target=".python_packages/lib/site-packages"
          pushd .
          popd

      - name: Run Azure Functions Action
        id: fa
        uses: Azure/functions-action@v1
        with:
          app-name: ${{ env.AZURE_FUNCTIONAPP_NAME }}
          package: ${{ env.AZURE_FUNCTIONAPP_PACKAGE_PATH }}
          publish-profile: ${{ secrets.AZURE_FUNCTIONAPP_PUBLISH_PROFILE }}
          scm-do-build-during-deployment: true
          enable-oryx-build: true
