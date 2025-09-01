weaver: Roadmap de Produto (Primeiros 3 Meses)
Visão do Produto: Ser a forma mais rápida e intuitiva para desenvolvedores Python criarem dados de teste realistas, contextuais e seguros, permitindo que eles construam software de maior qualidade, mais rápido.

Pilha Tecnológica Inicial:

Linguagem: Python 3.10+

Schema & Validação: Pydantic V2

LLM Provider: OpenAI (usando GPT-4-Turbo ou superior para o json_mode)

Distribuição: PyPI

Mês 1: MVP (Minimum Viable Product) - O Núcleo Mágico
Objetivo Principal: Provar que a funcionalidade central é viável e gera um "Uau!" nos primeiros usuários. O foco é 100% na funcionalidade, não no polimento.

Features a Implementar:
[x] Estrutura da Biblioteca: Criação do layout básico do projeto, setup.py, e dependências (pydantic, openai).

[x] Função Core weaver.generate(): A função principal que orquestra todo o processo.

[x] Conversor de Schema: Lógica para converter um modelo Pydantic em uma representação JSON Schema que será enviada para o LLM.

[x] Integração com LLM: Conexão com a API da OpenAI, enviando o prompt do sistema (com o schema) e o prompt do usuário.

[x] Validação de Resposta: Parse da resposta JSON do LLM e validação rigorosa contra o modelo Pydantic original. Se a validação falhar, levanta um erro claro.

[x] Suporte a Tipos Básicos e Aninhados: Garantir que a geração funcione para tipos primitivos (str, int, bool), datetime, e para modelos Pydantic aninhados (ex: um User que contém um objeto Address).

[x] Suporte a Listas de Objetos: Permitir que um modelo contenha uma lista de outros modelos (ex: um User com List[Order]).

Sintaxe Alvo no Final do Mês 1:
from pydantic import BaseModel
from typing import List
from weaver import Weaver

# O desenvolvedor define seus modelos
class Order(BaseModel):
    product_id: int
    quantity: int

class User(BaseModel):
    name: str
    email: str
    orders: List[Order]

# Instancia o Weaver (com a chave de API)
weaver = Weaver()

# Descreve o que quer em linguagem natural
prompt = "Um usuário chamado João que fez 2 pedidos de produtos diferentes."
generated_user = weaver.generate(model=User, prompt=prompt)

# O resultado é um objeto Pydantic validado e pronto para uso
print(generated_user.model_dump_json(indent=2))
# {
#   "name": "João da Silva",
#   "email": "joao.silva@example.com",
#   "orders": [
#     { "product_id": 101, "quantity": 2 },
#     { "product_id": 204, "quantity": 1 }
#   ]
# }

Métricas de Sucesso:
A biblioteca gera dados válidos para 5 modelos Pydantic de complexidade variada de forma consistente.

3 desenvolvedores "amigos" conseguem instalar e rodar o exemplo acima com sucesso.

Mês 2: Lançamento Open Source e Foco em DX (Developer Experience)
Objetivo Principal: Transformar o protótipo funcional em uma ferramenta open source polida que os desenvolvedores queiram usar e compartilhar.

Features a Implementar:
[ ] Empacotamento e Publicação no PyPI: Tornar a biblioteca publicamente instalável via pip install data-weaver.

[ ] Melhoria de Error Handling: Em caso de falha de validação, exibir um "diff" claro entre o que a IA retornou e o que o schema esperava.

[ ] Sistema de Cache: Implementar um cache local simples (baseado em arquivo ou em memória) para evitar chamadas repetidas à API do LLM para o mesmo prompt/schema, economizando tempo e dinheiro.

[ ] Suporte a Tipos Avançados: Adicionar suporte a Enum, Union, Literal do Pydantic.

[ ] Documentação e README: Criar um README.md no GitHub com exemplos claros, um GIF demonstrando o uso, e uma documentação básica.

[ ] Testes Automatizados (CI): Configurar GitHub Actions para rodar uma suíte de testes (com pytest) a cada commit.

Sintaxe Alvo no Final do Mês 2:
from enum import Enum
from weaver import Weaver

class UserStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"

class User(BaseModel):
    name: str
    status: UserStatus

weaver = Weaver()

# O prompt agora pode referenciar Enums
prompt = "Um usuário ativo e um usuário com status pendente."

# O parâmetro `count` é introduzido
# A feature de cache torna a segunda chamada instantânea e gratuita
users_list = weaver.generate(model=User, prompt=prompt, count=2, use_cache=True)

for user in users_list:
    print(f"Nome: {user.name}, Status: {user.status.value}")
# Nome: Carlos Mendes, Status: active
# Nome: Ana Pereira, Status: pending

Métricas de Sucesso:
Biblioteca publicada no PyPI com mais de 1.000 downloads no primeiro mês.

Repositório no GitHub atinge 100+ estrelas.

Recebimento de pelo menos 5 "Issues" com feedback ou sugestões de features, indicando engajamento da comunidade.

Mês 3: Fundação "Pro" e Features de Time
Objetivo Principal: Construir as funcionalidades que resolvem dores de times e empresas, servindo de base para a futura versão comercial (SaaS).

Features a Implementar:
[ ] Introspecção de Schema de Banco de Dados (Killer Feature):

Criar um novo método weaver.from_db() que se conecta a uma URL de banco de dados (ex: postgresql://...).

Lê o schema de uma tabela específica.

Converte dinamicamente o schema da tabela em um modelo Pydantic "virtual" para usar na geração de dados.

[ ] Sistema de Templates:

Permitir que os usuários salvem prompts complexos em um arquivo local (weaver_templates.yml) e os reutilizem por nome. weaver.generate(model=User, template="new_ecommerce_customer").

[ ] Formatos de Saída (Export):

Adicionar um parâmetro output_format à função generate.

Suporte inicial para output_format="sql" (gera INSERT statements) e output_format="csv".

[ ] Landing Page e Waitlist:

Criar uma página web simples descrevendo a visão do "Weaver Pro" (GUI, colaboração, etc.) e um formulário para capturar emails de interessados.

Sintaxe Alvo no Final do Mês 3:
from weaver import Weaver

# 1. Geração a partir de um banco de dados existente (sem definir modelos!)
weaver_db = Weaver(db_url="postgresql://user:pass@host/db")
prompt_db = "Dois clientes de São Paulo (SP) e um do Rio de Janeiro (RJ)."
sql_inserts = weaver_db.generate(
    table_name="customers",
    prompt=prompt_db,
    count=3,
    output_format="sql"
)
print(sql_inserts)
# INSERT INTO customers (name, email, city, state) VALUES ('...', '...', 'São Paulo', 'SP');
# INSERT INTO customers (name, email, city, state) VALUES ('...', '...', 'São Paulo', 'SP');
# INSERT INTO customers (name, email, city, state) VALUES ('...', '...', 'Rio de Janeiro', 'RJ');

# 2. Usando um template salvo
prompt_template = "Um usuário admin com email terminando em @mycompany.com"
admin = weaver.generate(model=User, template="admin_user")

Métricas de Sucesso:
A introspecção de schema funciona para tabelas simples em PostgreSQL.

Conseguir 50+ emails na lista de espera para a versão Pro.

Ter 3 times que usam a versão open source concordando em testar as features "Pro" em um beta fechado.

Próximos Passos (Além dos 3 Meses)
Interface Gráfica (GUI): Uma aplicação web onde usuários não-técnicos (QAs, PMs) podem gerar dados.

Colaboração em Time: Workspace compartilhado para templates e schemas.

Compliance (LGPD/GDPR): Features de anonimização e detecção de dados sensíveis (PII).

Conectores Adicionais: Suporte para mais bancos de dados (MySQL, SQLite) e APIs (GraphQL).