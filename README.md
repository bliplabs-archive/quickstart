# Blip Quickstart

This repository contains a fast and simple quickstart for writing software that works with Blip.

## Table of contents

- [Blip Quickstart](#blip-quickstart)
  - [Table of contents](#table-of-contents)
  - [Blazing fast quickstart](#blazing-fast-quickstart)
  - [Requirements](#requirements)
  - [1. Clone the repository](#1-clone-the-repository)
  - [2. Set up environment variables](#2-set-up-environment-variables)
  - [3. Run with Docker](#3-run-with-docker)
  - [4. Interact](#4-interact)
    - [(Automated) Automatic workflow](#automated-automatic-workflow)
      - [(Automated) Reset the data](#automated-reset-the-data)
    - [(Manual) Do it yourself, one step at a time](#manual-do-it-yourself-one-step-at-a-time)
      - [1. Get and create endusers](#1-get-and-create-endusers)
      - [2. Create some transactions - simulate endusers buying things](#2-create-some-transactions---simulate-endusers-buying-things)
      - [3. Check if Blip identified any bills from the transactions](#3-check-if-blip-identified-any-bills-from-the-transactions)
      - [4. Done! Reset and delete the data we just added](#4-done-reset-and-delete-the-data-we-just-added)
    - [Summary](#summary)
  - [Development](#development)
    - [Python development environment setup](#python-development-environment-setup)
      - [Python vscode setup](#python-vscode-setup)

## Blazing fast quickstart

If you just want to start making API calls to Blip using `curl`, all you have to do is [retrieve your API key from the dashboard](https://app.bliplabs.com/profile) and pass it as an `X-API-Key` header, for example:

```bash
curl -H 'X-API-Key: some-api-key' 'https://api.bliplabs.com/v2/endusers'
```

The rest of this guide will walk you through a typical Blip workflow using real code.

## Requirements

- Git
- Docker
- Docker compose
- Port `20001` (default, you can change)
- `curl` or a browser

## 1. Clone the repository

```bash
git clone https://github.com/bliplabs/quickstart.git

cd quickstart
```

## 2. Set up environment variables

Start by copying the `.env.example` to a new file called `.env`:

```bash
cp .env.example .env
```

Populate the contents of your new `.env` with API keys and any other values. Each of the required environment variables in this file should have a comment that will guide you through the process.

## 3. Run with Docker

In the below steps, `docker-compose` is used as the default - depending on how your system is configured, `docker compose` may be preferred.

```bash
docker-compose build
docker-compose up -d
docker-compose logs -f
```

## 4. Interact

The API is now up and running, and you can proceed to interact with the Blip API!

Using the `curl` command, the commands below accomplish the following sequence:

1. Create some endusers
1. Push transactions that those endusers have created
1. Wait for Blip to process those transactions and detect bills
1. Get the processed bills from Blip

### (Automated) Automatic workflow

The automatic workflow does the above steps all without any intervention. It is recommended to open the running container's logs in a separate window, as there will be live log output that will likely be more interesting than the data that gets returned by the `curl` command below.

```bash
# in one terminal, start by following the logs:
docker-compose logs -f

# in another terminal, execute the following curl command to begin the workflow
curl -v http://localhost:20001/workflow

# after watching the logs for what will likely take 5-10 seconds (hardcoded in
# this repository's code, you can change), you will get the processed bills in
# the form of a raw API response
```

#### (Automated) Reset the data

Similar to the above section, you may want to watch the logs when running this command, as it might show more interesting information that will not be returned over the REST API call.

```bash
# warning: be careful using this, as it will delete ALL of the endusers,
# transactions, and bills associated with your institution's API key.

# Seriously, don't run this unless without first checking what data you already
# have - run the following commands to *safely* review what data is
# associated with your current API key:
# curl -v http://localhost:20001/transactions/get
# curl -v http://localhost:20001/endusers/get
# curl -v http://localhost:20001/bills/get
#
# If all of that data looks OK to delete, then run the following command:
curl -v http://localhost:20001/reset # this is the dangerous command
```

That's it!

### (Manual) Do it yourself, one step at a time

While the automated workflow is nice, it can help to manually work with the Blip API. As part of the quickstart, our Python code runs in a Docker container that has some very basic REST API endpoints running on port `20001` on your local system. We've engineered it to be very straightforward - all you have to do is do a `curl` `GET` request and the code will perform the desired operations on Blip's actual API's.

The underlying API interactions with Blip are actually pretty simple, but we wanted to make this as easy as possible for you to test out and play with by preparing a bunch of easily trigger-able Blip API interactions, as seen in the following sections.

#### 1. Get and create endusers

Endusers are consumers that create transactions. Your data has unique ID's for each of its endusers, which we refer to as `enduser_oid`, where `oid` is the "origin ID". This simply means that it's the globally unique identifier in _your_ system, which allows you to keep your data consistent across platforms.

```bash
# start by getting the list of endusers - may be empty, or contain previous
# endusers that you've created
curl -v http://localhost:20001/endusers/get

# create some endusers based on the sample json data in this repo.
# Note that running this multiple times will not allow duplicate endusers with
# the same "origin id" values to be created
curl -v http://localhost:20001/endusers/create

# check the list of endusers again to see the difference
curl -v http://localhost:20001/endusers/get
```

Now that you've created some endusers, move on to the next step.

#### 2. Create some transactions - simulate endusers buying things

```bash
# start by getting the list of transactions
curl -v http://localhost:20001/transactions/get

# create some Netflix transactions that one particular enduser made
# Note: this will return a "batch_id", you may want to copy this value for
# later, as it can be used to check if a batch of transactions have finished
# processing
curl -v http://localhost:20001/transactions/create

# check that they were created.
# You can periodically refresh this to verify if any of the bills are processing
# or you can use the batch_id from above when interacting directly with the Blip
# API (not part of this manual demo)
curl -v http://localhost:20001/transactions/get
```

#### 3. Check if Blip identified any bills from the transactions

```bash
# start by getting the list of bills
curl -v http://localhost:20001/bills/get

# you can also just get a bill for one of the endusers by enduser_oid
curl -v http://localhost:20001/bills/get/35f83baa-77d3-4cae-80c1-45d1984a185d
```

#### 4. Done! Reset and delete the data we just added

```bash
curl -v http://localhost:20001/bills/delete
curl -v http://localhost:20001/transactions/delete
curl -v http://localhost:20001/endusers/delete
```

### Summary

In just a few steps, we've manually added endusers, transactions, and a bill to Blip.

This quickstart guide is an example of how you can successfully interact with the Blip API for your future projects. The `localhost:20001` API is just a wrapper to help you execute a few prepared commands with Blip, and should serve as a guide for the way Blip is meant to be used.

## Development

For developers that wish to go further with this quickstart, follow the below instructions according to each programming language or framework below.

### Python development environment setup

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate # may vary slightly on different platforms
pip3 install -r requirements.txt
pip3 install -r requirements-dev.txt
```

For linting and type checking, you can run the following tools from the `./python` directory:

```bash
black main.py # autoformats main.py
isort main.py # sorts imports in main.py
flake8 main.py # linting
pylint main.py # more linting

# mypy provides type checking and more in-depth code analysis, may ask to
# install packages that provide type annotations
MYPYPATH=.venv mypy --install-types --python-executable .venv/bin/python3 main.py
```

#### Python vscode setup

We aim to be platform-agnostic where possible, but a few of us at Blip do use Visual Studio Code, and felt it would only benefit the community to share a working IDE configuration for this quickstart.

After setting up the virtual environment according to the steps outlined in the previous section, populate `.vscode/settings.json` with the following - note that `${workspaceFolder}` _does not need to be changed_, it is a variable that is evaluated by vscode:

```json
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.cwd": "${workspaceFolder}/python",
    "editor.formatOnSave": true,
    "python.linting.flake8Args": [
        "--config",
        "${workspaceFolder}/python/.flake8"
    ],
    "python.defaultInterpreterPath": "${workspaceFolder}/python/.venv/bin/python3",
    "python.formatting.provider": "black"
}
```
