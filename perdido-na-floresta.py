import os
import random
import time # Importa a biblioteca time para pausas

# ==============================================================================
# ESTADO DO JOGO
# Controla o fluxo principal e as interações do jogador
# ==============================================================================
rodando = True        # Controla se o jogo está ativo (true) ou encerrado (false)
menu = True           # Controla se o jogador está no menu principal
jogando = False       # Controla se o jogador está em uma sessão de jogo ativa
regras = False        # Controla se a tela de regras está sendo exibida
tem_bussola = False   # Indica se o jogador possui a bússola (item chave)
lutando = False       # Controla se o jogador está em combate
parado = True         # Indica se o jogador está parado (afeta encontros aleatórios)
comprando = False     # Controla se o jogador está na loja
falando = False       # Controla se o jogador está conversando com um NPC (Velho Caçador)
chefao = False        # Indica se o jogador está na área do chefão e pronto para a batalha final

# ==============================================================================
# STATUS DO JOGADOR
# Atributos e inventário do personagem principal
# ==============================================================================
HP = 50               # Pontos de Vida atuais
HPMAX = 50            # Pontos de Vida máximos
ATK = 3               # Dano de Ataque
pocoes = 1            # Quantidade de poções de cura
elixires = 0          # Quantidade de elixires de cura
frutas = 0            # Moeda do jogo (coletadas de inimigos)
x = 0                 # Posição horizontal (coluna) do jogador no mapa
y = 0                 # Posição vertical (linha) do jogador no mapa
nome = ""             # Nome do jogador (definido no início ou carregado)

# ==============================================================================
# MAPA DO JOGO E BIOMAS
# Definição do ambiente de jogo
# ==============================================================================
mapa = [
    ["clareira", "trilha", "trilha", "trilha", "mata", "pedras", "desfiladeiro"],
    ["mata", "mata", "mata", "trilha", "mata", "colina", "pedras"],
    ["mata", "rio", "ponte", "clareira", "colina", "mata", "colina"],
    ["clareira", "cabana", "acampamento", "cacador", "clareira", "colina", "pedras"],
    ["clareira", "rio", "rio", "clareira", "colina", "pedras", "pedras"]
]

y_max = len(mapa) - 1   # Índice máximo da linha no mapa
x_max = len(mapa[0]) - 1 # Índice máximo da coluna no mapa

# Dicionário de biomas com nomes amigáveis e se permitem encontros (e - inimigo)
biomas = {
    "clareira": {"t": "CLAREIRA", "e": True},
    "trilha": {"t": "TRILHA", "e": True},
    "mata": {"t": "MATA FECHADA", "e": True},
    "ponte": {"t": "PONTE", "e": True},
    "acampamento": {"t": "ACAMPAMENTO ABANDONADO", "e": False}, # Locais seguros/interativos
    "cabana": {"t": "CABANA DE SOBREVIVENTE", "e": False},
    "cacador": {"t": "VELHO CAÇADOR", "e": False},
    "desfiladeiro": {"t": "DESFILADEIRO DA SAÍDA", "e": False},
    "pedras": {"t": "PEDREIRA", "e": True},
    "colina": {"t": "COLINA", "e": True},
    "rio": {"t": "MARGEM DO RIO", "e": True}
}

# ==============================================================================
# INIMIGOS
# Definição dos tipos de inimigos e seus atributos
# ==============================================================================
lista_inimigos = ["Lobo", "Javali", "Cobra"] # Inimigos regulares
inimigos = {
    "Lobo": {"hp": 15, "at": 3, "go": 8},   # HP, Ataque, Frutas (Gold)
    "Javali": {"hp": 35, "at": 5, "go": 18},
    "Cobra": {"hp": 30, "at": 2, "go": 12},
    "Urso Gigante": {"hp": 100, "at": 8, "go": 100} # Chefão final
}

# ==============================================================================
# FUNÇÕES AUXILIARES
# Funções para interações comuns do jogo
# ==============================================================================

def limpar():
    """Limpa o console para uma interface mais limpa."""
    os.system("cls" if os.name == "nt" else "clear")

def linha():
    """Imprime uma linha separadora para organização visual."""
    print("xX--------------------Xx")

def salvar():
    """Salva o estado atual do jogo em um arquivo."""
    dados = [
        nome,
        str(HP),
        str(ATK),
        str(pocoes),
        str(elixires),
        str(frutas),
        str(x),
        str(y),
        str(tem_bussola) # Salva como string "True" ou "False"
    ]
    try:
        with open("salvo.txt", "w") as arquivo:
            for item in dados:
                arquivo.write(item + "\n")
        print("Jogo salvo com sucesso!")
        time.sleep(1) # Pequena pausa para o jogador ver a mensagem
    except IOError:
        print("Erro ao salvar o jogo.")
        time.sleep(1)

def curar(valor):
    """Cura o HP do jogador, limitado ao HP máximo."""
    global HP
    HP = min(HPMAX, HP + valor)
    print(f"{nome} recuperou vida! HP atual: {HP}/{HPMAX}")

def batalha():
    """
    Controla a lógica de combate entre o jogador e um inimigo.
    Gerencia turnos, uso de itens e resultados da batalha.
    """
    global lutando, jogando, rodando, HP, pocoes, elixires, frutas, chefao, nome

    inimigo_atual_nome = "Urso Gigante" if chefao else random.choice(lista_inimigos)
    inimigo_info = inimigos[inimigo_atual_nome]
    hp_inimigo = inimigo_info["hp"]
    hpmax_inimigo = hp_inimigo
    atk_inimigo = inimigo_info["at"]
    recompensa_frutas = inimigo_info["go"]

    while lutando:
        limpar()
        linha()
        print(f"⚔ Enfrente o {inimigo_atual_nome} selvagem!")
        linha()
        print(f"HP do {inimigo_atual_nome}: {hp_inimigo}/{hpmax_inimigo}")
        print(f"Seu HP: {HP}/{HPMAX}")
        print(f"Poções: {pocoes} | Elixires: {elixires}")
        linha()
        print("1 - Atacar")
        if pocoes > 0:
            print("2 - Usar Poção (+30HP)")
        if elixires > 0:
            print("3 - Usar Elixir (+50HP)")
        linha()

        escolha = input("# ")

        if escolha == "1":
            dano_causado = ATK
            hp_inimigo -= dano_causado
            print(f"Você causou {dano_causado} de dano ao {inimigo_atual_nome}.")
            time.sleep(1)
            if hp_inimigo > 0:
                dano_recebido = atk_inimigo
                HP -= dano_recebido
                print(f"O {inimigo_atual_nome} causou {dano_recebido} de dano a você.")
                time.sleep(1)
        elif escolha == "2" and pocoes > 0:
            pocoes -= 1
            curar(30)
            time.sleep(1)
            dano_recebido = atk_inimigo
            HP -= dano_recebido
            print(f"O {inimigo_atual_nome} causou {dano_recebido} de dano a você.")
            time.sleep(1)
        elif escolha == "3" and elixires > 0:
            elixires -= 1
            curar(50)
            time.sleep(1)
            dano_recebido = atk_inimigo
            HP -= dano_recebido
            print(f"O {inimigo_atual_nome} causou {dano_recebido} de dano a você.")
            time.sleep(1)
        else:
            print("Ação inválida ou item insuficiente.")
            time.sleep(1)

        # Verifica as condições de vitória/derrota
        if HP <= 0:
            print(f"Você foi derrotado pelo {inimigo_atual_nome}...")
            linha()
            lutando = False
            jogando = False
            rodando = False # Fim do jogo
            print("GAME OVER")
            input("\nPressione Enter para sair...")
        elif hp_inimigo <= 0:
            print(f"Você venceu o {inimigo_atual_nome}!")
            linha()
            frutas += recompensa_frutas
            print(f"Você encontrou {recompensa_frutas} frutas.")

            # Chance de encontrar poção após a batalha
            if random.randint(0, 100) < 30: # 30% de chance
                pocoes += 1
                print("Você encontrou uma poção!")

            if inimigo_atual_nome == "Urso Gigante":
                print("Parabéns! Você encontrou a trilha para sair da floresta!")
                chefao = False
                jogando = False
                rodando = False # Fim do jogo após derrotar o chefão
            lutando = False
            input("\nPressione Enter para continuar explorando...")
            limpar()

def loja():
    """
    Gerencia as compras do jogador na Cabana de Sobrevivente.
    Permite comprar poções, elixires e melhorar o ataque.
    """
    global comprando, frutas, pocoes, elixires, ATK
    while comprando:
        limpar()
        linha()
        print("Bem-vindo à cabana do sobrevivente!")
        linha()
        print(f"Frutas: {frutas} | Poções: {pocoes} | Elixires: {elixires} | ATK: {ATK}")
        linha()
        print("1 - Comprar Poção (+30HP) - 5 Frutas")
        print("2 - Comprar Elixir (+50HP) - 8 Frutas")
        print("3 - Melhorar arma (+2 ATK) - 10 Frutas")
        print("4 - Sair")
        linha()

        escolha = input("# ")
        if escolha == "1":
            if frutas >= 5:
                frutas -= 5
                pocoes += 1
                print("Você comprou uma poção.")
            else:
                print("Frutas insuficientes para comprar uma poção.")
        elif escolha == "2":
            if frutas >= 8:
                frutas -= 8
                elixires += 1
                print("Você comprou um elixir.")
            else:
                print("Frutas insuficientes para comprar um elixir.")
        elif escolha == "3":
            if frutas >= 10:
                frutas -= 10
                ATK += 2
                print("Você melhorou sua arma!")
            else:
                print("Frutas insuficientes para melhorar sua arma.")
        elif escolha == "4":
            comprando = False
            print("Saindo da loja.")
        else:
            print("Opção inválida.")
        time.sleep(1) # Pequena pausa após a ação na loja

def cacador():
    """
    Interage com o Velho Caçador.
    Ele oferece a bússola se o jogador tiver ataque suficiente.
    """
    global falando, tem_bussola, nome
    while falando:
        limpar()
        linha()
        print("👴 Velho Caçador:")
        print(f"Ah, você chegou até aqui, {nome}...")
        if ATK < 10:
            print("Ainda não está pronto para enfrentar o Urso Gigante.")
            print("Treine mais para aumentar seu ataque!")
            tem_bussola = False # Garante que a bússola não seja obtida prematuramente
        else:
            print("Você demonstrou força! Pegue esta bússola e vá até o desfiladeiro!")
            tem_bussola = True
        linha()
        print("1 - Sair")
        escolha = input("# ")
        if escolha == "1":
            falando = False
            print("Você se despede do Velho Caçador.")
        else:
            print("Opção inválida.")
        time.sleep(1)

def desfiladeiro():
    """
    Gerencia a área do Desfiladeiro da Saída, onde o chefão reside.
    Permite iniciar a batalha final se o jogador tiver a bússola.
    """
    global chefao, tem_bussola, lutando
    while chefao:
        limpar()
        linha()
        print("⛰ Você está diante do desfiladeiro guardado pelo Urso Gigante.")
        linha()
        if tem_bussola:
            print("1 - Usar a bússola e avançar para enfrentar o Urso Gigante")
        print("2 - Voltar para a floresta")
        linha()
        escolha = input("# ")
        if escolha == "1" and tem_bussola:
            print("Você se prepara para a batalha final...")
            time.sleep(2)
            lutando = True
            batalha()
            # Se a batalha acabar aqui (derrota ou vitória), o loop chefao também vai parar.
            # O estado de chefao será alterado dentro de batalha() se o chefão for derrotado.
        elif escolha == "2":
            chefao = False
            print("Você decide recuar do desfiladeiro por enquanto.")
            time.sleep(1)
        else:
            print("Opção inválida ou você não possui a bússola para avançar.")
            time.sleep(1)

# ==============================================================================
# LOOP PRINCIPAL DO JOGO
# Gerencia a transição entre menu e jogabilidade
# ==============================================================================
while rodando:
    while menu:
        limpar()
        linha()
        print("         JOGO: PERDIDO NA FLORESTA         ")
        linha()
        print("1 - NOVO JOGO")
        print("2 - CARREGAR JOGO")
        print("3 - REGRAS")
        print("4 - SAIR")
        linha()

        if regras:
            print("\n REGRAS:")
            print("- Explore a floresta e colete frutas derrotando animais selvagens.")
            print("- Use as frutas coletadas para comprar poções de cura e melhorar suas armas na cabana do sobrevivente.")
            print("- Fale com o Velho Caçador para pegar a bússola, um item essencial para encontrar a saída.")
            print("- Com a bússola em mãos, você poderá ir até o desfiladeiro e enfrentar o grande Urso Gigante para sair da floresta e vencer o jogo!")
            input("\nPressione Enter para voltar ao menu principal...")
            regras = False
        else:
            escolha = input("Sua escolha: ")
            if escolha == "1":
                limpar()
                nome = input("Qual o seu nome, garoto perdido? ")
                HP = 50
                ATK = 3
                pocoes = 1
                elixires = 0
                frutas = 0
                x = 0
                y = 0
                tem_bussola = False
                print(f"Bem-vindo(a), {nome}! Uma nova aventura começa...")
                time.sleep(2)
                menu = False
                jogando = True
            elif escolha == "2":
                try:
                    with open("salvo.txt", "r") as f:
                        dados = f.readlines()
                    if len(dados) == 9: # Verifica se todos os 9 dados esperados estão presentes
                        nome = dados[0].strip()
                        HP = int(dados[1])
                        ATK = int(dados[2])
                        pocoes = int(dados[3])
                        elixires = int(dados[4])
                        frutas = int(dados[5])
                        x = int(dados[6])
                        y = int(dados[7])
                        tem_bussola = dados[8].strip() == "True" # Converte a string de volta para booleano
                        print(f"Bem-vindo(a) de volta, {nome}!")
                        input("\nPressione Enter para continuar...")
                        menu = False
                        jogando = True
                    else:
                        print("Arquivo de salvamento corrompido ou incompleto.")
                        input("\nPressione Enter para continuar...")
                except FileNotFoundError:
                    print("Nenhum jogo salvo encontrado.")
                    input("\nPressione Enter para continuar...")
                except ValueError:
                    print("Erro: Dados de salvamento inválidos (não numéricos).")
                    input("\nPressione Enter para continuar...")
                except Exception as e:
                    print(f"Ocorreu um erro inesperado ao carregar: {e}")
                    input("\nPressione Enter para continuar...")
            elif escolha == "3":
                regras = True
            elif escolha == "4":
                print("Saindo do jogo. Até a próxima!")
                time.sleep(1)
                quit() # Sai do programa Python
            else:
                print("Opção inválida. Por favor, escolha novamente.")
                time.sleep(1)

    while jogando:
        salvar() # Salva o jogo a cada turno de exploração

        limpar()
        # Lógica de encontro aleatório
        # Ocorre apenas se o jogador não estiver parado e o bioma permitir encontros
        if not parado and biomas[mapa[y][x]]["e"]:
            if random.randint(0, 100) < 30: # 30% de chance de encontro
                print("Um inimigo apareceu!")
                time.sleep(1)
                lutando = True
                batalha()

        # Garante que o jogo continua rodando após a batalha ou se não houve encontro
        if jogando: # Verifica se o jogo ainda está ativo após um possível fim em batalha
            limpar()
            linha()
            print(f" LOCAL: {biomas[mapa[y][x]]['t']}")
            linha()
            print(f" NOME: {nome}")
            print(f" VIDA: {HP}/{HPMAX} | ATK: {ATK}")
            print(f" Poções: {pocoes} | Elixires: {elixires} | Frutas: {frutas}")
            print(f" Bússola: {'SIM' if tem_bussola else 'NÃO'}")
            print(f" Coordenadas: ({x}, {y})")
            linha()
            print("0 - SALVAR E SAIR PARA O MENU")
            if y > 0: print("1 - IR PARA O NORTE")
            if x < x_max: print("2 - IR PARA O LESTE")
            if y < y_max: print("3 - IR PARA O SUL")
            if x > 0: print("4 - IR PARA O OESTE")
            if pocoes > 0: print("5 - USAR POÇÃO (+30HP)")
            if elixires > 0: print("6 - USAR ELIXIR (+50HP)")
            # Opção para entrar em locais específicos (cabana, caçador, desfiladeiro)
            if mapa[y][x] in ["cabana", "cacador", "desfiladeiro"]:
                print("7 - ENTRAR")
            linha()

            acao = input("Ação: ")
            parado = False # Assume que o jogador irá se mover ou fazer algo que não seja "parar"

            if acao == "0":
                jogando = False
                menu = True
                salvar() # Salva antes de voltar ao menu
            elif acao == "1" and y > 0:
                y -= 1
            elif acao == "2" and x < x_max:
                x += 1
            elif acao == "3" and y < y_max:
                y += 1
            elif acao == "4" and x > 0:
                x -= 1
            elif acao == "5":
                if pocoes > 0:
                    pocoes -= 1
                    curar(30)
                    print("Você usou uma poção.")
                    parado = True # Usar item te deixa parado
                    time.sleep(1)
                else:
                    print("Você não tem poções.")
                    time.sleep(1)
                    parado = True # Ação inválida também te deixa parado
            elif acao == "6":
                if elixires > 0:
                    elixires -= 1
                    curar(50)
                    print("Você usou um elixir.")
                    parado = True # Usar item te deixa parado
                    time.sleep(1)
                else:
                    print("Você não tem elixires.")
                    time.sleep(1)
                    parado = True # Ação inválida também te deixa parado
            elif acao == "7":
                local_atual = mapa[y][x]
                if local_atual == "cabana":
                    comprando = True
                    loja()
                elif local_atual == "cacador":
                    falando = True
                    cacador()
                elif local_atual == "desfiladeiro":
                    chefao = True
                    desfiladeiro()
                parado = True # Entrar em um local é uma ação que te deixa parado
            else:
                print("Ação inválida. Tente novamente.")
                time.sleep(1)
                parado = True # Ação inválida te deixa parado