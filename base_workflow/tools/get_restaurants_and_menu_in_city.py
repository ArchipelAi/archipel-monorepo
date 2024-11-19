import json
import os
from typing import Annotated

from langchain.agents import tool


cur_dir = os.path.dirname(__file__)

file_path = os.path.join(cur_dir, '..', 'data/restaurants.json')


@tool
def get_restaurants_and_menu_in_city(
	city: Annotated[str, 'The city for which the restaurants should get retrieved.'],
):
	"""Use this to get a list of restaurants for a given city."""
	f = open(file_path)
	data = json.load(f)
	restaurants: list[str] = []
	for el in data:
		if el['city'] == city:
			restaurants = el['restaurants']
	return restaurants
