from database import Categories



cs = Categories()
c = cs.get_category(13)
t = c.get_tournament(325)

print(t.name)
print(t.id)