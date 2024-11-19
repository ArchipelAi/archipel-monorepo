import json
import os
from typing import Annotated

from langchain.agents import tool


cur_dir = os.path.dirname(__file__)

file_path = os.path.join(cur_dir, '..', 'data/restaurants.json')


@tool
def order_pizza(
	city: Annotated[str, 'The city'],
	restaurant: Annotated[str, 'The restaurant in the city'],
	pizza: Annotated[str, 'The pizza which should be ordered'],
):
	"""Use this to order a pizza."""
	f = open(file_path)
	data = json.load(f)
	found_city = [el for el in data if el['city'] == city]
	if not found_city:
		return 'The city is not available.'
	found_restaurant = [
		el for el in found_city[0]['restaurants'] if el['name'] == restaurant
	]
	if not found_restaurant:
		return 'The restaurant is not available in this city.'
	if pizza not in found_restaurant[0]['pizzas']:
		return 'The pizza is not available in this restaurant.'
	return 'Order Successfull. Will be delivered soon.'
