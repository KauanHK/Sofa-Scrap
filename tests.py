from sofa_scrap.db.category import Category


c = Category(13)
t = c.get_tournament(325)
print(t)