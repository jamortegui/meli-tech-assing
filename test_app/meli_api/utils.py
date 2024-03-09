import os
import asyncio
import requests

from test_app import settings


MELI_AUTH_KEY = os.environ.get("MELI_AUTH_KEY")


async def call_endpoint(url, requires_auth=False, num_retrys=0):
    # Performs an async API call to the given URL

    headers = {
        "Authorization": f"Bearer {MELI_AUTH_KEY}"
    }

    if requires_auth and MELI_AUTH_KEY is not None:
        response = await asyncio.to_thread(requests.get, url, headers=headers)
    else:
        response = await asyncio.to_thread(requests.get, url)

    if response.status_code >= 300 and response.status_code != 404 and num_retrys <= settings.MAX_RETRIES:
        await asyncio.sleep(settings.RETRY_WAIT_TIME)
        return await call_endpoint(url, requires_auth=False, num_retrys=num_retrys + 1)
    try:
        json_obj = response.json()
    except requests.exceptions.JSONDecodeError:
        json_obj = {"code": response.status_code, "message": "Empty api response"}

    return response.status_code, json_obj


async def get_attribute(lines, i, url_string, drop_key, target_key):
    # Gets a given attribute (target_key) from an API with the format https://base_url/$drop_key
    # And implicitly updates the corresponding line with the new value.

    value = lines[i].pop(drop_key)
    url = url_string.format(value)
    _, response = await call_endpoint(url)
    lines[i][target_key] = response.get(target_key)
