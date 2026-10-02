import database

nome = "DevCntrol"
senha = "01102026"

if database.criar_conta_dev(nome, senha):
    print("Conta Dev criada com sucesso!")
    print("Nome:", nome)
else:
    print("Essa conta Dev já existe.")