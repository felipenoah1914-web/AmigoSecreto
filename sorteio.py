import random
import database


def gerar_sorteio():

    if database.sorteio_ja_realizado():
        print("O sorteio já foi realizado!")
        return False

    usuarios = database.listar_usuarios()

    participantes = []

    for usuario in usuarios:
        usuario_id = usuario[0]
        nome = usuario[1]
        participa = usuario[2]

        if participa == 1:
            participantes.append({
                "id": usuario_id,
                "nome": nome
            })

    if len(participantes) < 2:
        print("É necessário ter pelo menos 2 participantes.")
        return False

    quem_tira = [pessoa["id"] for pessoa in participantes]
    quem_e_tirado = quem_tira.copy()

    # Embaralha até ninguém tirar a si mesmo
    while True:
        random.shuffle(quem_e_tirado)

        valido = True

        for i in range(len(quem_tira)):
            if quem_tira[i] == quem_e_tirado[i]:
                valido = False
                break

        if valido:
            break

    # Salva os resultados
    for i in range(len(quem_tira)):
        usuario_id = quem_tira[i]
        amigo_id = quem_e_tirado[i]

        database.salvar_sorteio(
            usuario_id,
            amigo_id
        )

    database.marcar_sorteio_realizado()

    print()
    print("================================")
    print("       SORTEIO REALIZADO!")
    print("================================")
    print()
    print("Os resultados foram salvos no banco.")
    print("Os pares não são exibidos por segurança.")
    print()

    return True


if __name__ == "__main__":
    gerar_sorteio()