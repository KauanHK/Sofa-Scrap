import os
from sofa_scrap.utils import get_file_path


# Verificar se as categorias estão salvas
file_path = get_file_path("categories")
if not os.path.exists(file_path):

    from sofa_scrap.utils import Urls, get_data, save_json

    url = Urls.CATEGORIES
    data = get_data(Urls.CATEGORIES)
    data = data["categories"]
    data = {t["name"]: t["id"] for t in data}
    save_json(data, "categories", update=False)
    print("Categorias salvas com sucesso")


