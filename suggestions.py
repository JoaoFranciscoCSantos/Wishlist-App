def sugerir_compra(itens, saldo):
    saldo_centimos = round(saldo * 100)
    precos_centimos = [round(item['price'] * 100) for item in itens]
    prioridades = [item['priority'] for item in itens]
    n = len(itens)

    dp = [[0] * (saldo_centimos + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        preco = precos_centimos[i - 1]
        prioridade = prioridades[i - 1]

        for s in range(saldo_centimos + 1):
            dp[i][s] = dp[i - 1][s]
            if preco <= s:
                valor_com_item = prioridade + dp[i - 1][s - preco]
                if valor_com_item > dp[i][s]:
                    dp[i][s] = valor_com_item

    escolhidos = []
    s = saldo_centimos
    for i in range(n, 0, -1):
        if dp[i][s] != dp[i - 1][s]:
            escolhidos.append(itens[i - 1])
            s -= precos_centimos[i - 1]

    escolhidos.reverse()
    return dp[n][saldo_centimos], escolhidos