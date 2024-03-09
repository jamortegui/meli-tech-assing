from .utils import call_endpoint
from test_app import settings


async def get_user_nicknames(lines):
    # Makes a single call to users api with all the seller_id's from the chunk
    # Then asings the nickname values to the corresponding rows
    seller_ids = ",".join([str(line["seller_id"]) for line in lines])
    url = settings.USERS_API_URL.format(seller_ids)
    _, response = await call_endpoint(url)
    for response_obj in response:
        for i, line in enumerate(lines):
            if line.get("seller_id") == response_obj.get("body").get("id"):
                lines[i]["nickname"] = response_obj.get("body").get("nickname")
                lines[i].pop("seller_id")
