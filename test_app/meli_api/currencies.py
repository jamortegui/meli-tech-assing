from functools import partial

from .utils import get_attribute
from test_app import settings


set_currency_description = partial(get_attribute, url_string=settings.CURRENCIES_API_URL, drop_key="currency_id", target_key="description")
