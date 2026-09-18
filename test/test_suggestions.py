from suggestions import sugerir_compra

itens_teste = [
    {'id': 1, 'name': 'A', 'price': 60, 'priority': 5},
    {'id': 2, 'name': 'B', 'price': 50, 'priority': 4},
    {'id': 3, 'name': 'C', 'price': 30, 'priority': 3},
]

prioridade_total, escolhidos = sugerir_compra(itens_teste, saldo=100)

print("Prioridade total:", prioridade_total)
print("Itens escolhidos:", [item['name'] for item in escolhidos])