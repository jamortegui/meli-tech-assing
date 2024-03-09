from functools import partial

from .utils import get_attribute
from test_app import settings


set_category_name = partial(get_attribute, url_string=settings.CATEGORIES_API_URL, drop_key="category_id", target_key="name")
