"""Welcome to the Blip quickstart! This project contains a series of helpful
functions, API endpoint interactions, sample data, and structured examples that
will help you take advantage of all the Blip has to offer.
"""
import json
import time
from os import getenv
from typing import AsyncGenerator

import httpx
from aiofiles import open as aopen
from fastapi import Depends, FastAPI

app = FastAPI()

api_key = getenv("BLIP_API_KEY", "")
base_url = getenv("BLIP_API_URL", "")


async def get_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """This is a method of returning an instance of an httpx AsyncClient that
    comes pre-baked with your API key and set to use the base URL you specify
    in your .env file.

    Returns:
        AsyncGenerator[httpx.AsyncClient, None]: An async generator

    Yields:
        Iterator[AsyncGenerator[httpx.AsyncClient, None]]: An async httpx
            client
    """
    async with httpx.AsyncClient(
        headers={
            "X-API-Key": api_key,
        },
        base_url=base_url,
    ) as client:
        yield client


async def get_sample_transactions() -> list[dict]:
    """Reads the sample transactions json file and returns its parsed contents.

    Returns:
        list[dict]: A list of transactions
    """
    async with aopen("data/sample_transactions.json", "r") as file:
        data = await file.read()
        return json.loads(data)


async def get_sample_endusers() -> list[dict]:
    """Reads the sample endusers json file and returns its parsed contents.

    Returns:
        list[dict]: A list of endusers
    """
    async with aopen("data/sample_endusers.json", "r") as file:
        data = await file.read()
        return json.loads(data)


async def get_endusers(client: httpx.AsyncClient) -> dict:
    """Uses the Blip API to get all current endusers associated with your
    institution, which are accessible because of your API key.

    Args:
        client (httpx.AsyncClient): Pass in the pre-baked httpx AsyncClient
            from calling get_client

    Returns:
        dict: A dictionary with its "items" property set to a paginated list
            of endusers associated with your institution. Note that because
            it's paginated, you may not see every result in practice.
    """
    resp = await client.request(
        method="GET",
        url="/endusers",
    )

    return resp.json()


async def create_endusers(
    client: httpx.AsyncClient,
    endusers: list[dict],
) -> dict:
    """Creates all endusers specified in the provided endusers argument.

    Args:
        client (httpx.AsyncClient): Pass in the pre-baked httpx AsyncClient
            from calling get_client
        endusers (list[dict]): A list of dictionaries, each with the oid
            property set to some globally unique identifier that comes from
            your own data sources, so that you can keep track of your endusers
            across platforms.

    Returns:
        dict: A dictionary containing the total number of endusers created.
    """
    resp = await client.request(method="POST", url="/endusers", json=endusers)

    return resp.json()


async def delete_endusers(
    client: httpx.AsyncClient,
    endusers: list[str],
) -> dict:
    """Deletes endusers from Blip by passing in a list of origin ID values
    that correspond to each enduser.

    Args:
        client (httpx.AsyncClient): Pass in the pre-baked httpx AsyncClient
            from calling get_client
        endusers (list[str]): A list of enduser oid (origin id) strings

    Returns:
        dict: A dictionary containing the total number of endusers deleted
    """
    resp = await client.request(
        method="DELETE",
        url="/endusers",
        json=endusers,
    )

    return resp.json()


async def create_transactions(
    client: httpx.AsyncClient,
    transactions: list[dict],
) -> dict:
    """Calls the Blip API to create the provided transactions.

    Args:
        client (httpx.AsyncClient): Pass in the pre-baked httpx AsyncClient
            from calling get_client
        transactions (list[dict]): A list of transactions

    Returns:
        dict: The total number of transactions created
    """
    resp = await client.request(
        method="POST",
        url="/transactions",
        json=transactions,
    )

    return resp.json()


async def delete_transactions(
    client: httpx.AsyncClient, transactions: list[str]
) -> list[dict]:
    """Deletes transactions from Blip by passing in a list of transaction oid
    string values.

    Args:
        client (httpx.AsyncClient): Pass in the pre-baked httpx AsyncClient
            from calling get_client
        transactions (list[str]): A list of transaction oid strings to delete

    Returns:
        list[dict]: All of the deleted transactions
    """
    deleted_transactions = []
    for transaction_oid in transactions:
        resp = await client.request(
            method="DELETE",
            url=f"/transactions/{transaction_oid}",
        )

        deleted_transactions.append(resp.json())

        # to avoid flooding the API, add a small time buffer between each
        # delete request
        time.sleep(0.4)

    return deleted_transactions


async def get_transactions(client: httpx.AsyncClient) -> dict:
    """Returns all available transactions from Blip's API.

    Args:
        client (httpx.AsyncClient): Pass in the pre-baked httpx AsyncClient
            from calling get_client

    Returns:
        dict: A dictionary whose "items" key contains a paginated list of
            transactions.
    """
    resp = await client.request(
        method="GET",
        url="/transactions",
    )

    return resp.json()


async def get_transactions_for_batch_id(
    client: httpx.AsyncClient,
    batch_id: str,
) -> dict:
    """Returns all available transactions from Blips API for the provided
    "batch_id" value, which comes from some earlier API call to create one or
    more transactions. Useful for keeping track of a large group of
    transactions that span multiple merchants and/or endusers.

    Args:
        client (httpx.AsyncClient): Pass in the pre-baked httpx AsyncClient
            from calling get_client
        batch_id (str): The batch_id value whose associated transactions will
            be returned

    Returns:
        dict: A dictionary whose "items" key contains a paginated list of
            transactions associated with the provided batch ID.
    """
    resp = await client.request(
        method="GET",
        url=f"/transactions?batch_id={batch_id}",
    )

    return resp.json()


async def get_bills(client: httpx.AsyncClient) -> dict:
    """Returns the bills that have been identified by Blip. Scoped to only
    return identified bills that come from your institution's endusers'
    transactions. Calls the Blip API.

    Args:
        client (httpx.AsyncClient): Pass in the pre-baked httpx AsyncClient
            from calling get_client

    Returns:
        dict: A dictionary whose "items" key contains a paginated list of bills
    """
    resp = await client.request(
        method="GET",
        url="/bills",
    )

    return resp.json()


async def get_bills_for_enduser(
    client: httpx.AsyncClient,
    enduser_oid: str,
) -> dict:
    """Calls the Blip API to retrieve all identified bills associated with
    a particular enduser.

    Args:
        client (httpx.AsyncClient): Pass in the pre-baked httpx AsyncClient
            from calling get_client
        enduser_oid (str): Your globally unique identifier for an enduser
            associated with your institution whose bills will be returned.

    Returns:
        dict: A dictionary whose "items" key contains a paginated list of bills
    """
    resp = await client.request(
        method="GET",
        url=f"/bills?enduser_oid={enduser_oid}",
    )

    return resp.json()


async def delete_bills(
    client: httpx.AsyncClient,
    bills: list[str],
) -> list[dict]:
    """Calls the Blip API to delete all bills that match the provided ID's, one
    at a time.

    Args:
        client (httpx.AsyncClient): Pass in the pre-baked httpx AsyncClient
            from calling get_client
        bills (list[str]): A list of bill ID string values

    Returns:
        list[dict]: A list of deleted bills (not paginated like other API
            calls)
    """
    deleted_bills = []
    for bill_id in bills:
        resp = await client.request(
            method="DELETE",
            url=f"/bills/{bill_id}",
        )

        deleted_bills.append(resp.json())

        # to avoid flooding the API, add a small time buffer between each
        # delete request
        time.sleep(0.4)

    return deleted_bills


async def await_processed_transactions(
    client: httpx.AsyncClient,
    batch_id: str,
) -> dict:
    """Uses a simple loop to periodically check the Blip API to see if a batch
    of transactions (correlated by the provided "batch_id" argument) are done
    processing or not.

    Args:
        client (httpx.AsyncClient): Pass in the pre-baked httpx AsyncClient
            from calling get_client
        batch_id (str): When uploading transactions, a batch_id is returned.
            This is the value that should be used here

    Raises:
        Exception: In the event that the loop completes without ever seeing
            a "complete" state for the given batch

    Returns:
        dict: The final raw API response from Blip that indicates that the
            batch has completed processing.
    """
    wait_time_seconds = 5
    # try up to 10 times
    max_tries = 10
    for current_try in range(max_tries):
        print(
            f"({current_try}/{max_tries}) awaiting transactions processing...",
        )
        resp = await client.request(
            method="GET",
            url=f"/transactions/status?batch_id={batch_id}",
        )

        response = resp.json()

        status = response.get("status", None)
        if status != "complete":
            print(f"status: {status}, sleeping {wait_time_seconds} sec...")
            time.sleep(wait_time_seconds)
            continue

        return response

    raise Exception("transactions were not all processed before timeout")


async def create_endusers_command(client: httpx.AsyncClient) -> dict:
    """This is a prepared command that loads the sample endusers and attempts
    to create them via Blip's API.

    Args:
        client (httpx.AsyncClient): Pass in the pre-baked httpx AsyncClient
            from calling get_client

    Returns:
        dict: The output of create_endusers
    """
    endusers_to_create: list[dict] = await get_sample_endusers()
    return await create_endusers(client, endusers_to_create)


async def create_transactions_command(client: httpx.AsyncClient) -> dict:
    """This is a prepared command that loads the sample transactions and
    attempts to create them via Blip's API.

    Args:
        client (httpx.AsyncClient): Pass in the pre-baked httpx AsyncClient
            from calling get_client

    Returns:
        dict: The output of create_transactions
    """
    transactions_to_create = await get_sample_transactions()
    return await create_transactions(client, transactions_to_create)


async def delete_bills_command(client: httpx.AsyncClient) -> list[dict]:
    """This is a prepared command that loads the sample bills and attempts
    to delete them via Blip's API.

    Args:
        client (httpx.AsyncClient): Pass in the pre-baked httpx AsyncClient
            from calling get_client

    Returns:
        dict: The output of delete_bills
    """
    bills: dict = await get_bills(client)
    bill_ids_to_delete: list[str] = []

    for bill in bills["items"]:
        bill_ids_to_delete.append(bill["id"])

    return await delete_bills(client, bill_ids_to_delete)


async def delete_endusers_command(client: httpx.AsyncClient) -> dict:
    """This is a prepared command that loads the sample endusers and attempts
    to delete them via Blip's API.

    Args:
        client (httpx.AsyncClient): Pass in the pre-baked httpx AsyncClient
            from calling get_client

    Returns:
        dict: The output of delete_endusers
    """
    endusers_to_delete: list[dict] = await get_sample_endusers()

    enduser_oids_to_delete: list[str] = []

    for enduser in endusers_to_delete:
        enduser_oids_to_delete.append(enduser["oid"])

    return await delete_endusers(client, enduser_oids_to_delete)


async def delete_transactions_command(client: httpx.AsyncClient) -> list[dict]:
    """This is a prepared command that loads the sample transactions and
    attempts to delete them via Blip's API.

    Args:
        client (httpx.AsyncClient): Pass in the pre-baked httpx AsyncClient
            from calling get_client

    Returns:
        dict: The output of delete_transactions
    """
    existing_transactions = await get_transactions(client)

    transaction_ids_to_delete: list[str] = []
    for transaction in existing_transactions["items"]:
        transaction_ids_to_delete.append(transaction["oid"])

    return await delete_transactions(client, transaction_ids_to_delete)


async def delete_all_command(client: httpx.AsyncClient) -> dict:
    """Deletes all transaction clusters (bills), transactions, and
    endusers that were created earlier as part of this quickstart. This is
    a dangerous endpoint to hit, so be careful!

    Args:
        client (httpx.AsyncClient): Pass in the pre-baked httpx AsyncClient
            from calling get_client

    Returns:
        dict: A mostly useless dictionary that contains {"success": True}
    """
    print("deleting bills...")
    print(await delete_bills_route(client))
    print("deleting transactions...")
    print(await delete_transactions_route(client))
    print("deleting endusers...")
    print(await delete_endusers_command(client))
    print("done deleting everything.")
    return {"success": True}


async def workflow_command(client: httpx.AsyncClient) -> dict:
    """Executes the automated workflow described in the README.md file:
    1. Creates endusers based on the sample endusers json file
    2. Creates transactions (that the previously created endusers made)
    3. Waits for the transactions to be identified as bills
    4. Once the bills are identified, it retrieves them and returns them to you

    Args:
        client (httpx.AsyncClient): Pass in the pre-baked httpx AsyncClient
            from calling get_client

    Raises:
        Exception: When a "batch_id" is not returned upon creating transactions

    Returns:
        dict: The data from the Blip API bills endpoint, which should contain
            identified bill(s)
    """
    # create some endusers
    endusers_to_create: list[dict] = await get_sample_endusers()
    created_users = await create_endusers(client, endusers_to_create)

    print(f"created user(s): {created_users}")

    # create transactions
    transactions_to_create: list[dict] = await get_sample_transactions()
    created_transactions: dict = await create_transactions(
        client,
        transactions_to_create,
    )

    batch_id = created_transactions.get("batch_id", None)
    if batch_id is None:
        raise Exception(
            "no batch_id received from creating transactions",
        )

    print(f"batch_id: {batch_id}")

    # wait for Blip to process those transactions and detect bills
    await await_processed_transactions(client, batch_id)

    processed_transactions = await get_transactions_for_batch_id(
        client,
        batch_id,
    )

    print(f"processed transactions: {processed_transactions}")

    # get the processed bills from Blip for only the first enduser, since
    # they're the one with all the recurring transactions
    bills = await get_bills_for_enduser(client, endusers_to_create[0]["oid"])

    # present the processed bills to the user
    return bills


@app.get("/")
async def hello_world() -> dict:
    """Returns hello world!

    Returns:
        dict: Hello, world!
    """
    return {"Hello": "World"}


@app.get("/endusers/get")
async def get_endusers_route(
    client: httpx.AsyncClient = Depends(get_client),
) -> dict:
    """Returns all endusers, scoped to your institution/API key.

    Args:
        client (httpx.AsyncClient, optional): An instance of an
            httpx.AsyncClient that is injected via FastAPI's dependency
            injection mechanism. You don't need to worry about this

    Returns:
        dict: The output of get_endusers
    """
    return await get_endusers(client)


@app.get("/endusers/create")
async def create_endusers_route(
    client: httpx.AsyncClient = Depends(get_client),
) -> dict:
    """Creates the endusers contained within the sample endusers json file.

    Args:
        client (httpx.AsyncClient, optional): An instance of an
            httpx.AsyncClient that is injected via FastAPI's dependency
            injection mechanism. You don't need to worry about this

    Returns:
        dict: The output of create_endusers_command
    """
    return await create_endusers_command(client)


@app.get("/endusers/delete")
async def delete_endusers_route(
    client: httpx.AsyncClient = Depends(get_client),
) -> dict:
    """Deletes the endusers contained within the sample endusers json file.

    Args:
        client (httpx.AsyncClient, optional): An instance of an
            httpx.AsyncClient that is injected via FastAPI's dependency
            injection mechanism. You don't need to worry about this

    Returns:
        dict: The output of delete_endusers_command
    """
    return await delete_endusers_command(client)


@app.get("/transactions/get")
async def get_transactions_route(
    client: httpx.AsyncClient = Depends(get_client),
) -> dict:
    """Retrieves all transactions associated with any endusers, scoped to your
    institution/API key.

    Args:
        client (httpx.AsyncClient, optional): An instance of an
            httpx.AsyncClient that is injected via FastAPI's dependency
            injection mechanism. You don't need to worry about this

    Returns:
        dict: The output of get_transactions
    """
    return await get_transactions(client)


@app.get("/transactions/create")
async def create_transactions_route(
    client: httpx.AsyncClient = Depends(get_client),
) -> dict:
    """Creates one or more transactions defined in the sample transactions json
    file.

    Args:
        client (httpx.AsyncClient, optional): An instance of an
            httpx.AsyncClient that is injected via FastAPI's dependency
            injection mechanism. You don't need to worry about this

    Returns:
        dict: The output of create_transactions_command
    """
    return await create_transactions_command(client)


@app.get("/transactions/delete")
async def delete_transactions_route(
    client: httpx.AsyncClient = Depends(get_client),
) -> list[dict]:
    """Deletes all transactions that were created as part of this quickstart.

    Args:
        client (httpx.AsyncClient, optional): An instance of an
            httpx.AsyncClient that is injected via FastAPI's dependency
            injection mechanism. You don't need to worry about this

    Returns:
        list[dict]: The output of delete_transactions_command
    """
    return await delete_transactions_command(client)


@app.get("/bills/get")
async def get_bills_route(
    client: httpx.AsyncClient = Depends(get_client),
) -> dict:
    """Retrieves all bills scoped within your current institution/API key.

    Args:
        client (httpx.AsyncClient, optional): An instance of an
            httpx.AsyncClient that is injected via FastAPI's dependency
            injection mechanism. You don't need to worry about this

    Returns:
        dict: The output of get_bills
    """
    return await get_bills(client)


@app.get("/bills/get/{enduser_oid}")
async def get_bills_for_enduser_oid_route(
    enduser_oid: str,
    client: httpx.AsyncClient = Depends(get_client),
) -> dict:
    """Retrieves bills for a given enduser.

    Args:
        enduser_oid (str): Will retrieve bills for the specified enduser's
            origin ID.
        client (httpx.AsyncClient, optional): An instance of an
            httpx.AsyncClient that is injected via FastAPI's dependency
            injection mechanism. You don't need to worry about this

    Returns:
        dict: The output of get_bills_for_enduser
    """
    return await get_bills_for_enduser(client, enduser_oid)


@app.get("/bills/delete")
async def delete_bills_route(
    client: httpx.AsyncClient = Depends(get_client),
) -> list[dict]:
    """Deletes the bills that were created by this quickstart.
    Executes the delete_bills_command function.

    Args:
        client (httpx.AsyncClient, optional): An instance of an
            httpx.AsyncClient that is injected via FastAPI's dependency
            injection mechanism. You don't need to worry about this

    Returns:
        list[dict]: The output of delete_bills_command
    """
    return await delete_bills_command(client)


@app.get("/reset")
async def reset_route(client: httpx.AsyncClient = Depends(get_client)) -> dict:
    """Deletes all transaction clusters (bills), transactions, and
    endusers that were created earlier as part of this quickstart. This is
    a dangerous endpoint to hit, so be careful!

    Args:
        client (httpx.AsyncClient, optional): An instance of an
            httpx.AsyncClient that is injected via FastAPI's dependency
            injection mechanism. You don't need to worry about this

    Returns:
        dict: The output from delete_all_command
    """
    return await delete_all_command(client)


@app.get("/workflow")
async def do_flow_route(
    client: httpx.AsyncClient = Depends(get_client),
) -> dict:
    """Executes the automated workflow described in the README.md file. For
    more info, see the workflow_command function.

    Args:
        client (httpx.AsyncClient, optional): An instance of an
            httpx.AsyncClient that is injected via FastAPI's dependency
            injection mechanism. You don't need to worry about this

    Returns:
        dict: The output from workflow_command
    """
    return await workflow_command(client)
