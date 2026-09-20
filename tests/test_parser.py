import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from parser import normalizar_preco, normalizar_imagem

assert normalizar_preco(29.99) == 29.99
assert normalizar_preco("29.99") == 29.99
assert normalizar_preco("29,99") == 29.99
assert normalizar_preco("1.299,99") == 1299.99
assert normalizar_preco("1,299.99") == 1299.99
assert normalizar_preco("29,99 €") == 29.99
assert normalizar_preco(None) is None
assert normalizar_preco("abc") is None

assert normalizar_imagem("a.jpg") == "a.jpg"
assert normalizar_imagem(["a.jpg", "b.jpg"]) == "a.jpg"
assert normalizar_imagem({"url": "a.jpg"}) == "a.jpg"
assert normalizar_imagem([{"url": "a.jpg"}]) == "a.jpg"
assert normalizar_imagem([]) is None
assert normalizar_imagem(None) is None

print("Tudo OK")