import csv


def download_file(response, ingredients):
    writer = csv.writer(response, delimiter=' ', quotechar='|')
    for ingredient in ingredients:
        writer.writerow([
            f'{ingredient.get("ingredient__name")} '
            f'({ingredient.get("ingredient__measurement_unit")}) - '
            f'{ingredient.get("amount")}'
        ])
    return writer
