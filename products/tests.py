# Инициализация списка с одним пустым множеством
all_products_property = [set()]

# Представим, что у нас есть два продукта с производителями "Apple" и "Samsung"
products = [{"manufacturer": "Apple"}, {"manufacturer": "Samsung"}]

# Итерация по каждому продукту
for product in products:
    # Добавление производителя в множество
    all_products_property[0].add(product['manufacturer'])
    print("Текущее множество производителей:", all_products_property[0])
