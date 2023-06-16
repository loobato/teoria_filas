#%%
import simpy
import random
import pandas as pd

pd.set_option('display.max_columns', None)

# -------------------------------------------------- Inputs ---------------------------------------------------------- #

NumFuncionario = 2
TempoAtend = 1.34
LambdChegada = 1.08
TMFila = 4.9
Tempo = 710

# ------------------------------------------------- Variaveis -------------------------------------------------------- #

c_atendidos = 0
c_fila = 0
auxfila = 0
cheg = list()
esp = list()
ate = list()
ate1 = list()
ate2 = list()
said = list()
cfila = list()
sistema = list()
rows = list()


# ------------------------------------------------ Primarias --------------------------------------------------------- #

class Supermercado:

    def __init__(self, env, nfuncionario, tempo):
        self.env = env
        self.staff = simpy.Resource(env, capacity=nfuncionario)
        self.support_time = tempo

    def support(self, cliente):
        global said, TempoAtend
        random_time = random.expovariate(1 / TempoAtend)
        yield self.env.timeout(random_time)
        print(f'Conclusão do atendimento do cliente {cliente} às {self.env.now:.2f}')
        tsaida = env.now
        said.append(tsaida)


def customer(env, nome, supermercado):
    global c_atendidos, cheg, c_fila, auxfila

    if len(ate) > 2:
        clientenafila = auxfila - c_atendidos - 2
    else:
        clientenafila = 0

    print(f'Cliente {nome} entra na fila às {env.now:.2f}')
    clientenafila += 1
    auxfila += 1
    cheg.append(env.now)
    if nome > 3:
        fila = random.expovariate(1 / TMFila)
        esp.append(fila)
        yield env.timeout(fila)
    else:
        pass
    with supermercado.staff.request() as request:
        yield request
        x = env.now
        espera(cheg[-1], x)
        print(f'Cliente {nome} entra em atendimento às {env.now:.2f}!')
        cfila.append(clientenafila)
        yield env.process(supermercado.support(nome))
        print(f'Cliente {nome} sai do atendimento às {env.now:.2f}')
        atendimento(x, env.now)
        if len(ate) % 2 != 0:
            caixa1(x, env.now)
            caixa2(sim=False)
        else:
            caixa1(sim=True)
            caixa2(x, env.now)
        c_atendidos += 1


# ---------------------------------------------- Secundarias --------------------------------------------------------- #

def espera(iespera, fespera):
    global esp
    tfil = fespera - iespera
    esp.append(tfil)


def atendimento(iatend, fatend):
    global ate
    tatend = fatend - iatend
    ate.append(tatend)


def caixa1(iatend=0, fatend=0, sim=True):
    global ate1
    if sim:
        tatend = fatend - iatend
        ate1.append(tatend)
    else:
        ate1.append(0)


def caixa2(iatend=0, fatend=0, sim=True):
    global ate2
    if sim:
        tatend = fatend - iatend
        ate2.append(tatend)
    else:
        ate2.append(0)


# -------------------------------------------------- Main() ---------------------------------------------------------- #

def setup(env, nfuncionario, temp, tmchegada):
    call_center = Supermercado(env, nfuncionario, temp)

    for i in range(1, 5):
        env.process(customer(env, i, call_center))

    while True:
        yield env.timeout(random.expovariate(1 / tmchegada))
        i += 1
        env.process(customer(env, i, call_center))


# ------------------------------------------------- Run -------------------------------------------------------------- #

print('Simulador de Filas', end='\n')
env = simpy.Environment()
env.process(setup(env, NumFuncionario, TempoAtend, LambdChegada))
env.run(until=Tempo)

# ------------------------------------------------ Dataframe --------------------------------------------------------- #

print(f'Clientes Atendidos:  {str(c_atendidos)}')

if len(cheg) != len(said):
    cheg.pop()

for c in range(0, len(said)):
    sistema += [said[c] - cheg[c]]
    dis = dict()
    dis['cliente'] = c + 1
    dis['tchegada'] = cheg[c]
    dis['tespera'] = esp[c]
    dis['tsaida'] = said[c]
    dis['tatendcaixa1'] = ate1[c]
    dis['tatendcaixa2'] = ate2[c]
    dis['tnosistema'] = sistema[c]
    dis['cfila'] = cfila[c]
    dis['medclientefila'] = (sum(cfila[:])) / len(cfila)
    dis['medespera'] = (sum(esp[:])) / len(esp)
    dis['mednosistema'] = sum(sistema[0:c]) / len(sistema)
    rows.append(dis)


df = pd.DataFrame(rows)
df.columns = ['Cliente', 
              'Chegada (s)', 
              'Espera (s)', 
              'Saída (s)',
              'No caixa 1 (s)',
              'No caixa 2 (s)', 
              'No sistema (s)', 
              'Clientes na fila', 
              'Média de clientes na fila', 
              'Média de espera (s)', 
              'Média de clientes no sistema']
df.to_excel('simulação_modelo.xlsx', index=False, sheet_name='autoatend')
