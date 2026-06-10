# Portal da Transparência — Consulta por CPF

Aplicação desktop para consulta consolidada de pessoas físicas na [API de Dados do Portal da Transparência](https://portaldatransparencia.gov.br/api-de-dados/usuario/cadastro) do Governo Federal.

Informe um CPF e o sistema busca automaticamente em todos os serviços da API que aceitam esse parâmetro, exibindo apenas os módulos com registros encontrados.

## Funcionalidades

- Consulta paralela em 21 serviços da API federal
- Interface moderna com sidebar, métricas e cards por serviço
- Modal com detalhes ao clicar em cada resultado
- Histórico de consultas salvo localmente
- Configuração da chave da API pela interface
- Tema claro/escuro
- Aplicação desktop via FlaskWebGUI

## Tecnologias

- Python 3.11+
- Flask
- FlaskWebGUI
- SQLite
- HTML / CSS / JavaScript

## Pré-requisitos

- Python 3.11 ou superior
- Chave de acesso à API do Portal da Transparência

Cadastre-se em: https://portaldatransparencia.gov.br/api-de-dados/usuario/cadastro

Documentação da API: https://api.portaldatransparencia.gov.br/swagger-ui/index.html

## Instalação

```bash
git clone <url-do-repositorio>
cd TransparenciaChart

python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
```

## Configuração da API

Na primeira execução, acesse **Configurações** no menu lateral e informe a chave da API. Ela é salva localmente em SQLite (`data/transparencia.db`).

Opcionalmente, é possível definir a chave no arquivo `.env` antes da primeira execução — ela será migrada automaticamente para o banco:

```env
GOV_KEY=chave-api-dados
GOV_VALUE=sua-chave-aqui
```

## Execução

```bash
python app.py
```

A aplicação abre em uma janela desktop. Para depuração no navegador, substitua `FlaskUI(...).run()` por `app.run(debug=True)` em `app.py`.

## Estrutura do projeto

```
TransparenciaChart/
├── app.py                  # Aplicação Flask e rotas da API
├── services/
│   ├── api.py              # Integração com a API federal
│   └── database.py         # SQLite (configurações e histórico)
├── templates/
│   └── index.html          # Interface principal
├── static/
│   ├── css/style.css
│   └── js/app.js
├── data/
│   └── transparencia.db    # Banco local (gerado automaticamente)
├── requirements.txt
└── .gitignore
```

## Serviços consultados

| Categoria | Serviços |
|-----------|----------|
| Cadastro | Pessoa Física |
| Servidores | Servidores, Remuneração, PEPs |
| Viagens | Viagens a Serviço |
| Contratos | Contratos |
| Patrimônio | Imóveis Funcionais |
| Despesas | Cartões, Recursos Recebidos, Empenhos, Liquidações, Pagamentos |
| Sanções | CEIS, CNEP, CEAF |
| Benefícios | Bolsa Família, Auxílio Emergencial, BPC, Seguro Defeso, Garantia-Safra, PETI |

## Endpoints internos

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/api/buscar` | Consulta CPF em todos os serviços |
| `GET` | `/api/historico` | Lista consultas anteriores |
| `GET` | `/api/historico/<id>` | Detalhe de uma consulta salva |
| `GET` | `/api/configuracoes` | Status da chave da API |
| `POST` | `/api/configuracoes` | Salva a chave da API |

## Observações

- A chave da API e o histórico ficam apenas no computador local.
- Alguns endpoints exigem parâmetros adicionais (período, ano etc.) — o sistema usa valores padrão razoáveis.
- `flaskwebgui==1.1.7` é fixado para compatibilidade com Python 3.11.

## Desenvolvedor

**Cristiano Ribeiro Ritta**

- Site: https://www.cristianoritta.com.br
- E-mail: cristiano-ritta@pc.rs.gov.br
- Telefone: (53) 99927-0103

## Licença

Uso dos dados sujeito às regras do [Portal da Transparência](https://portaldatransparencia.gov.br/) e ao [Decreto nº 8.777/2016](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2016/decreto/d8777.htm).
