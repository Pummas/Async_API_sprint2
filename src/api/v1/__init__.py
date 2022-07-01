# (query_params, def_file, response_code, pages)

# дефолтные параметры 
def_data = [({}, 'film_default.json', 200, 25)]

sort_parameters = [
    ({"sort":"imdb_rating"}, "film_def.json", 200, 25),
    ({"sort":"-imdb_rating"}, "film_def.json", 200, 25)
]

page_parameters = [
    ({"page_number":15}, "film_def.json", 200, 25)
]