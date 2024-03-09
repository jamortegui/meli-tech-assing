import asyncio

from .utils import call_endpoint
from .users import get_user_nicknames
from .categories import set_category_name
from .currencies import set_currency_description
from test_app import settings


def get_items_basic_info(lines, errors):
    # Makes a single call to items API with all the item ids form the chunk and retrieves the relevant atributes
    # Note that this is a sync function since its a single call fot the whole chunk and the data needs to be available before statirg the futher calls.
    product_ids = ",".join([line["site"] + str(line["id"]) for line in lines])
    attributes = ",".join(settings.ATTRIBUTES_TO_RETRIEVE)
    url = settings.ITEMS_API_URL.format(product_ids, attributes)
    status, response = asyncio.run(call_endpoint(url, requires_auth=True))
    valid_lines = []
    if status != 200:
        errors.append({"error": "There was an error calling items api", "row": lines, "code": status, "message": response.get('message')})
        return (valid_lines, errors)
    for response_obj in response:
        item_id = response_obj.get("body").get("id")
        for i, line in enumerate(lines):
            line_item_id = line["site"] + str(line["id"])
            if item_id == line_item_id:
                break
        line = lines.pop(i)
        if response_obj.get("code") == 200:
            for attribute in settings.ATTRIBUTES_TO_RETRIEVE:
                line[attribute] = response_obj.get("body").get(attribute)
            valid_lines.append(line)
        else:
            errors.append({"error": "There was an issue calling the items endpoint", "row": line, "code": response_obj.get('code'), "message": response_obj.get('body').get('message')})

    return (valid_lines, errors)


async def get_items_complement_info(lines):
    # Asyncronously retrieves the information from the other APIs once the items API data have been gathered
    tasks = []

    attributes_fncs = [set_category_name, set_currency_description]

    for i in range(len(lines)):
        for attribute_fn in attributes_fncs:
            task = attribute_fn(lines, i)
            tasks.append(task)

    tasks.append(get_user_nicknames(lines))

    # Execute all tasks concurrently and await their results
    await asyncio.gather(*tasks)
