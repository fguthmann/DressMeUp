import logging
import psycopg2
import random


def get_random_item(clothing_type, db_params):
    table_name = f"table_{clothing_type}"
    logging.info(f"Fetching random item for {clothing_type}")
    with psycopg2.connect(**db_params) as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT image_data FROM {table_name};")
            items = cur.fetchall()
            if items:
                logging.info(f"Found {len(items)} items for {clothing_type}, selecting random one")
                # Returns the image binary data
                return random.choice(items)[0]
            else:
                logging.warning(f"No items found for {clothing_type}")
                return None


def pick_outfit(temp_celsius, db_params):
    logging.info(f"Picking an outfit for {temp_celsius}°C")
    outfit = {}
    if temp_celsius > 22:
        outfit['dress'] = get_random_item('dress', db_params)
        outfit['shoe'] = get_random_item('shoe', db_params)
        outfit['bag'] = get_random_item('bag', db_params)
    elif temp_celsius < 12:
        outfit['shirt'] = get_random_item('shirt', db_params)
        outfit['jacket'] = get_random_item('jacket', db_params)
        outfit['pants'] = get_random_item('pants', db_params)
        outfit['shoe'] = get_random_item('shoe', db_params)
        outfit['bag'] = get_random_item('bag', db_params)
    else:
        outfit['shirt'] = get_random_item('shirt', db_params)
        outfit['pants'] = get_random_item('pants', db_params)
        outfit['shoe'] = get_random_item('shoe', db_params)
        outfit['bag'] = get_random_item('bag', db_params)
    return outfit
