# MVP - ENGENHARIA DE DADOS
# https://github.com/literaturaandre-byte/mvp-literatura-sul-global-databricks
## DISCENTE: CARLOS ANDRÉ CORDEIRO DE OLIVEIRA

# Pipeline de dados no Databricks para análise exploratória da visibilidade de obras literárias brasileiras no Sul Global.
# Circulação editorial e linguística de obras literárias na Open Library
## Estudo de caso com arquitetura Bronze–Silver–Gold em Databricks

> **Nota de entrega:** este README foi escrito para conter todo o racional descritivo e compor a documentação do repositório e servir de base para um documento em PDF contendo as capturas de tela dos procedimentos e do dashboard gerado.

---

# 1. Contexto de Negócios e Perguntas (Etapas 2 e 4.1)

## 1.1 Problema do estudo

O estudo investiga como um corpus de obras literárias pode ser analisado a partir de metadados bibliográficos abertos, com atenção à circulação editorial, aos idiomas de edição, aos locais de publicação e às editoras associadas a cada obra. O problema não consiste em estimar vendas, alcance de leitores ou prestígio literário; tais variáveis não estão disponíveis na fonte utilizada. O foco é construir um MVP de engenharia e análise de dados capaz de transformar respostas de API em um conjunto auditável de tabelas analíticas e, a partir delas, responder perguntas exploratórias sobre padrões de catalogação editorial.

A fonte principal é a Open Library, uma base bibliográfica aberta e colaborativa. Para cada obra do corpus, o pipeline consultou o endpoint de edições da API, persistiu a resposta bruta e derivou tabelas estruturadas. O resultado é uma cadeia reproduzível que separa dados de origem, dados tratados, métricas analíticas e tabelas de apresentação.

O corpus analisado contém **82 obras**. Foram recuperadas **116 edições** no recorte de coleta. Para cada obra, foi usada a primeira página do endpoint de edições com o parâmetro `limit=100`; por isso, o estudo não deve ser lido como inventário exaustivo de todas as edições existentes no mundo.

## 1.2 Objetivo geral

Construir, em Databricks, um pipeline de dados em camadas Bronze–Silver–Gold para coletar, persistir, estruturar, qualificar e analisar metadados de edições literárias disponíveis na Open Library, produzindo indicadores sobre idiomas, temporalidade, editoras, locais de publicação e sinais bibliográficos de circulação internacional.

## 1.3 Objetivos específicos

- Coletar e persistir respostas brutas do endpoint de edições para as 82 obras do corpus.
- Transformar os JSONs retornados pela API em uma tabela no nível de edição.
- Normalizar atributos multivalorados — idiomas, locais e editoras — em tabelas relacionais próprias.
- Extrair um ano de publicação de datas heterogêneas, sem descartar as datas originais.
- Produzir tabelas Gold para análise por obra, idioma, ano, editora e local.
- Criar um indicador exploratório de sinais de circulação internacional.
- Construir tabelas específicas para dashboard e uma auditoria final de consistência.
- Documentar as limitações da fonte e distinguir ausência de metadado de ausência de circulação.

## 1.4 Perguntas de negócio

As perguntas foram formuladas de modo compatível com os dados disponíveis. Em vez de afirmar causalidade ou medir mercado editorial, elas investigam padrões observáveis nos metadados catalogados.

1. **Quais idiomas predominam nas edições do corpus recuperadas pela Open Library?**
2. **As obras apresentam mais registros de edição em português ou em inglês?**
3. **Quais editoras aparecem com maior frequência nas edições catalogadas?**
4. **Quais locais de publicação aparecem com maior frequência após normalização conservadora de grafias?**
5. **Qual é a distribuição temporal das edições com ano de publicação identificável?**
6. **Quantas obras apresentam sinais bibliográficos de circulação internacional, definidos pela presença de edição em inglês e/ou local editorial fora dos polos brasileiros estabelecidos na regra?**
7. **Qual é a cobertura e a qualidade dos campos bibliográficos necessários para sustentar essas análises?**

## 1.5 Escopo e não-escopo

O estudo cobre metadados bibliográficos disponíveis na Open Library para o corpus definido. A análise observa edição, idioma, editora, local, ano e relações exploratórias entre esses elementos.

O estudo **não** mede:

- vendas, tiragem ou receita editorial;
- leitura, recepção crítica ou alcance de leitores;
- total real de traduções publicadas;
- disponibilidade comercial atual;
- qualidade literária, relevância canônica ou prestígio das editoras;
- causalidade entre idioma, local e sucesso de circulação.

Essa delimitação é central para evitar interpretações indevidas de uma base bibliográfica colaborativa.

---

# 2. Contexto dos Dados Brutos e Licença

## 2.1 Origem dos dados

Os dados foram obtidos da **Open Library**, por meio do endpoint de edições associado a cada identificador de obra:

```text
https://openlibrary.org/works/<WORK_ID>/editions.json?limit=100
```

A requisição retorna um objeto JSON cuja estrutura principal inclui um array chamado `entries`, com registros de edição. Cada resposta corresponde a uma obra, mas pode conter uma ou várias edições.

A coleta foi realizada com uma pausa de aproximadamente um segundo entre requisições, reduzindo a pressão sobre o serviço e tornando o processo mais responsável para uma API pública.

## 2.2 Estrutura dos dados brutos

A camada Bronze preserva a resposta completa da API sem transformação substantiva. A tabela bruta de edições é:

| Tabela | Granularidade | Principais colunas |
|---|---|---|
| `workspace.default.bronze_openlibrary_editions_raw` | Uma resposta JSON por obra | `work_id`, `source_url`, `extracted_at_utc`, `raw_json` |

- `work_id`: identificador da obra na Open Library.
- `source_url`: URL exata consultada para recuperar as edições.
- `extracted_at_utc`: horário UTC da extração.
- `raw_json`: resposta integral da API serializada como texto JSON.

No JSON bruto, os campos relevantes para a análise aparecem dentro de `entries`. Entre eles estão:

| Campo do JSON de edição | Uso no estudo |
|---|---|
| `key` | Identificador da edição (`edition_key`) |
| `title` | Título da edição |
| `publish_date` | Data de publicação em formato heterogêneo |
| `publish_places` | Lista de locais de publicação |
| `publishers` | Lista de editoras |
| `languages` | Lista de idiomas, com chaves como `/languages/por` |

A estrutura é semiestruturada: uma edição pode conter arrays de idiomas, locais e editoras. Por isso, uma modelagem relacional direta em uma única tabela levaria à repetição de valores ou à perda de relações multivaloradas.

## 2.3 Licença e uso responsável

A Open Library publica informações de licenciamento e reutilização em sua página de direitos autorais e termos de uso. Em geral, a base é aberta e disponibiliza APIs para acesso a metadados, mas o projeto deve ser tratado como uma fonte colaborativa, sujeita a correções, lacunas e mudanças no catálogo.

Para este estudo, os dados foram usados exclusivamente para fins acadêmicos e de portfólio analítico. Foram preservados:

- a URL de origem de cada resposta;
- a data/hora de extração;
- a resposta bruta na camada Bronze;
- a distinção entre dado informado e dado inferido pelo pipeline.

Recomenda-se incluir no PDF a referência oficial de licença/termos consultada no momento da entrega e registrar a data de acesso. Se o repositório publicar qualquer extrato de dados, deve manter atribuição à Open Library e evitar redistribuir conteúdo que não seja necessário para reprodução do estudo.

**[Screenshot recomendado 1 — Fonte e coleta]**

Inserir captura do notebook ou da tabela Bronze mostrando `work_id`, `source_url`, `extracted_at_utc` e `raw_json`, comprovando a rastreabilidade da coleta.

---

# 3. Carga dos Dados (Etapa de Coleta e Ingestão)

## 3.1 Estratégia de carga

A carga foi feita em duas etapas lógicas:

1. Recuperação dos identificadores das obras já existentes em `silver_works`.
2. Consulta do endpoint de edições da Open Library para cada `work_id`, seguida da persistência da resposta integral na camada Bronze.

O processo usou uma função Python baseada em `urllib.request`, com `User-Agent` explícito e timeout. A cada obra, o pipeline montou uma URL no padrão:

```python
f"https://openlibrary.org/works/{work_id}/editions.json?limit=100"
```

As respostas bem-sucedidas foram armazenadas em uma lista de registros contendo o identificador da obra, a URL, o instante de extração e o JSON bruto. Caso uma requisição falhasse, o processo registraria o erro e continuaria para a obra seguinte; no resultado final, foram obtidas **82 respostas para 82 obras**.

## 3.2 Persistência na plataforma

A persistência foi realizada como tabela Delta no Databricks:

```python
(
    df_openlibrary_editions_raw.write
    .format("delta")
    .mode("overwrite")
    .saveAsTable("workspace.default.bronze_openlibrary_editions_raw")
)
```

A tabela Bronze contém 82 linhas, uma para cada resposta de endpoint. Não há ainda uma linha por edição nessa etapa; essa normalização ocorre na camada Silver.

## 3.3 Scripts e repositório

A execução foi documentada em notebooks do repositório Git associado ao workspace Databricks. A referência esperada é:

| Artefato | Responsabilidade |
|---|---|
| `01_bronze_ingestao` | Ingestão inicial e persistência de dados brutos |
| `02_silver_transformacao` | Transformações Silver, Gold, auditorias e tabelas de visualização |
| `extract_openlibrary.py` (se presente no repositório) | Funções auxiliares ou alternativa scriptada para extração |
| `README.md` | Documentação técnica e analítica do estudo |

> Ajustar os links abaixo ao endereço real do repositório antes de publicar.
>
> - Notebook de ingestão: `[01_bronze_ingestao](./notebooks/01_bronze_ingestao)`
> - Notebook de transformação: `[02_silver_transformacao](./notebooks/02_silver_transformacao)`
> - Script de extração: `[extract_openlibrary.py](./extract_openlibrary.py)`

## 3.4 Resultado da carga

- Obras consultadas: 82.
- Respostas de edição persistidas: 82.
- Limite por obra: até 100 edições retornadas pela primeira página da API.
- Edições estruturadas após transformação: 116.

**[Screenshot recomendado 2 — Carga Bronze]**

Inserir a captura que exibe:

```text
Tabela Bronze de edições criada: workspace.default.bronze_openlibrary_editions_raw
+---------------+
|total_responses|
+---------------+
|             82|
+---------------+
```

---

# 4. Modelagem e Catálogo de Dados (Etapa de Modelagem)

## 4.1 Decisão de arquitetura

A arquitetura adotada usa o padrão **Medallion** — Bronze, Silver e Gold — com uma camada adicional `viz_*` para apresentação. A escolha separa claramente:

- o conteúdo original da API;
- as transformações estruturais;
- as métricas consolidadas;
- as tabelas voltadas aos gráficos.

Essa separação torna a análise auditável. Caso uma regra de normalização seja alterada, por exemplo, a consolidação de grafias de locais, é possível refazer a camada Gold sem apagar ou alterar a resposta original na Bronze.

## 4.2 Visão do modelo relacional

A entidade central é a **obra**. Cada obra pode ter várias **edições**. Uma edição pode ter vários idiomas, editoras e locais. Portanto, foram criadas tabelas de relacionamento em vez de armazenar listas JSON dentro das tabelas analíticas.

```text
Obra (silver_works)
  ├── Obra–assunto (silver_work_subjects)
  └── Edição (silver_editions)
        ├── Edição–idioma (silver_edition_languages)
        ├── Edição–local (silver_edition_places)
        └── Edição–editora (silver_edition_publishers)
```

## 4.3 Catálogo de dados transcrito

### Camada Bronze

| Tabela | Objetivo | Granularidade | Linhas esperadas |
|---|---|---|---:|
| `bronze_openlibrary_editions_raw` | Preservar respostas brutas da API de edições | Uma resposta JSON por obra | 82 |

**Principais colunas:**

| Coluna | Tipo lógico | Descrição |
|---|---|---|
| `work_id` | texto | Identificador da obra consultada |
| `source_url` | texto | Endpoint de origem |
| `extracted_at_utc` | texto/timestamp serializado | Momento da extração |
| `raw_json` | texto JSON | Resposta integral sem transformação |

### Camada Silver

| Tabela | Objetivo | Granularidade | Linhas esperadas |
|---|---|---|---:|
| `silver_works` | Obras normalizadas do corpus | Uma linha por obra | 82 |
| `silver_work_subjects` | Relações entre obra e assunto | Uma linha por relação | 183 |
| `silver_editions` | Edições estruturadas | Uma linha por edição | 116 |
| `silver_editions_enriched` | Edições com ano extraído | Uma linha por edição com ano válido | 114 |
| `silver_edition_languages` | Relações edição–idioma | Uma linha por relação | 104 |
| `silver_edition_places` | Relações edição–local | Uma linha por relação | 73 |
| `silver_edition_publishers` | Relações edição–editora | Uma linha por relação | 120 |
| `silver_editions_data_quality` | Auditoria de cobertura de campos | Uma linha de métricas | 1 |

**Estrutura de `silver_editions`:**

| Coluna | Descrição |
|---|---|
| `work_id` | Obra à qual a edição pertence |
| `source_url` | URL de origem da resposta |
| `extracted_at_utc` | Momento da extração |
| `edition_key` | Identificador da edição na Open Library |
| `title` | Título informado para a edição |
| `publish_date` | Data original da publicação, ainda como texto |
| `publish_places` | Lista JSON de locais de publicação |
| `publishers` | Lista JSON de editoras |
| `languages` | Lista JSON de idiomas |

**Estrutura das tabelas relacionais:**

| Tabela | Colunas centrais | Regra |
|---|---|---|
| `silver_edition_languages` | `edition_key`, `work_id`, `language_key` | Uma linha por idioma de cada edição |
| `silver_edition_places` | `edition_key`, `work_id`, `publish_place` | Uma linha por local de cada edição |
| `silver_edition_publishers` | `edition_key`, `work_id`, `publisher` | Uma linha por editora de cada edição |

### Camada Gold

| Tabela | Objetivo | Granularidade | Linhas esperadas |
|---|---|---|---:|
| `gold_work_edition_profile` | Perfil de edições, idiomas e período por obra | Uma linha por obra | 82 |
| `gold_work_publication_profile` | Perfil editorial por obra | Uma linha por obra | 82 |
| `gold_language_distribution` | Distribuição de idiomas | Uma linha por idioma | 6 |
| `gold_publication_year_distribution` | Distribuição anual | Uma linha por ano | 33 |
| `gold_publisher_distribution` | Distribuição por editora | Uma linha por editora | 67 |
| `gold_publish_place_distribution` | Distribuição bruta por local | Uma linha por local bruto | 34 |
| `gold_publish_place_distribution_normalized_final` | Distribuição por local normalizado | Uma linha por local normalizado | variável derivada |
| `gold_work_international_circulation` | Sinal exploratório de circulação internacional | Uma linha por obra | 82 |
| `gold_work_international_circulation_examples` | Obras com os dois sinais | Uma linha por obra selecionada | 10 esperadas |
| `gold_mvp_kpis` | Indicadores executivos | Uma linha | 1 |
| `gold_pipeline_validation` | Auditoria de contagens | Uma linha por dataset validado | 20 |
| `gold_project_data_inventory` | Inventário do projeto | Uma linha por dataset documentado | 19 |

### Camada de visualização

| Tabela | Finalidade | Linhas |
|---|---|---:|
| `viz_kpi_cards` | Cartões para dashboard | 8 |
| `viz_language_distribution` | Idiomas para gráfico | 6 |
| `viz_publication_years` | Série temporal para gráfico | 33 |
| `viz_top_publishers` | Ranking das 15 editoras principais | 15 |
| `viz_top_places` | Ranking dos 15 locais normalizados | 15 |
| `viz_international_circulation` | Distribuição dos sinais internacionais | 4 |

## 4.4 Inventário final do sistema

O inventário persistido no Databricks contém 19 datasets principais. Ele documenta camada, finalidade, granularidade e número esperado de linhas. Essa tabela é especialmente útil para demonstrar governança básica do projeto:

```sql
SELECT *
FROM workspace.default.gold_project_data_inventory
ORDER BY display_order;
```

**[Screenshot recomendado 3 — Catálogo/Inventário]**

Inserir a captura do `gold_project_data_inventory`, mostrando as 19 linhas e as colunas `data_layer`, `table_name`, `purpose`, `grain` e `expected_rows`.

**[Screenshot recomendado 4 — Persistência no catálogo]**

Inserir captura do explorador de dados do Databricks ou do catálogo Unity Catalog mostrando as tabelas Bronze, Silver, Gold e `viz_*` persistidas em `workspace.default`.

---

# 5. Pipeline de Dados (ETL/ELT)

## 5.1 Organização do processo

O pipeline foi organizado em notebooks, e não em um único bloco monolítico. Essa decisão facilita depuração, reexecução e documentação didática.

- **Notebook `01_bronze_ingestao`:** responsável pela obtenção e pela persistência de respostas brutas.
- **Notebook `02_silver_transformacao`:** responsável por estruturar as edições, normalizar os campos multivalorados, criar a camada Gold, gerar tabelas de visualização, executar auditorias e construir o inventário do projeto.

Embora a extração das edições tenha sido disparada durante a evolução do notebook de transformação, a persistência das respostas retornadas foi tratada conceitualmente como Bronze, pois são dados ainda sem transformação analítica.

## 5.2 Fluxo de transformação

### Etapa 1 — Bronze: preservar a resposta original

As 82 respostas JSON foram armazenadas integralmente. Essa etapa assegura reprocessamento e rastreabilidade sem depender de nova chamada à API para cada ajuste de modelagem.

### Etapa 2 — Silver: explodir o array de edições

O campo `entries` do JSON foi interpretado e expandido com `explode`, produzindo uma linha por edição. Foram extraídos `edition_key`, `title`, `publish_date`, `publish_places`, `publishers` e `languages`.

O resultado foi `silver_editions`, com **116 linhas** e **116 `edition_key`s distintos**, distribuídos pelas 82 obras.

### Etapa 3 — Silver: criar relações multivaloradas

Os campos `languages`, `publish_places` e `publishers` são arrays serializados em JSON. Cada um foi convertido e expandido em uma tabela própria:

- 104 relações edição–idioma;
- 73 relações edição–local;
- 120 relações edição–editora.

Essa escolha evita que uma edição com duas editoras ou dois idiomas seja reduzida artificialmente a um único valor.

### Etapa 4 — Silver: enriquecer datas

O campo `publish_date` continha anos simples, datas completas e strings com mês. O pipeline extraiu o primeiro ano de quatro dígitos e aplicou `try_cast` para impedir que valores ausentes ou malformados interrompessem a execução.

Foram obtidas **114 edições com ano válido**, entre 1979 e 2025. As datas originais foram preservadas em `publish_date`.

### Etapa 5 — Gold: agregar e responder perguntas

Foram criadas distribuições por idioma, ano, editora e local; perfis por obra; indicadores executivos; e um sinal de circulação internacional. A camada Gold consolida as análises sem apagar as relações detalhadas da Silver.

### Etapa 6 — Visualização

As tabelas `viz_*` apresentam rótulos legíveis, percentuais e rankings para uso direto no dashboard. Dessa forma, a camada de apresentação não precisa aplicar novas regras analíticas no momento da visualização.

## 5.3 Auditoria e persistência

A tabela `gold_pipeline_validation` reúne a validação de 20 datasets. A execução final retornou:

```text
+-----------------+--------+
|validation_status|datasets|
+-----------------+--------+
|PASS             |20      |
+-----------------+--------+
```

Esse resultado demonstra consistência entre as contagens definidas no pipeline e as tabelas efetivamente persistidas na plataforma.

---

# 6. Qualidade de Dados

## 6.1 Diagnóstico de cobertura

A tabela `silver_editions_data_quality` consolidou a cobertura dos principais campos:

| Indicador | Valor | Cobertura sobre 116 edições |
|---|---:|---:|
| Edições recuperadas | 116 | 100,0% |
| Edições com ano extraível | 114 | 98,3% |
| Edições com idioma catalogado | 101 | 87,1% |
| Edições com local catalogado | 70 | 60,3% |
| Edições com editora catalogada | 116 | 100,0% |

A principal limitação é o campo de local: 46 edições não possuem local de publicação no catálogo. Essa ausência não foi interpretada como ausência de circulação editorial; foi mantida como ausência de informação catalogada.

## 6.2 Problemas detectados e tratamento adotado

| Problema | Evidência | Tratamento no pipeline | Limite do tratamento |
|---|---|---|---|
| Datas em formatos heterogêneos | `2007`, `January 2005`, `Mar 14, 2018`, `03/12/2014` | Extração do primeiro ano de quatro dígitos com regex e `try_cast` | Não valida mês/dia nem determina a data original completa |
| Valores sem ano identificável | 2 de 116 edições | Mantidos em `silver_editions`; excluídos apenas da tabela enriquecida temporal | Não se infere data ausente |
| Idiomas multivalorados | 104 relações para 101 edições | Criação de `silver_edition_languages` | Categorias não são necessariamente exclusivas |
| Idiomas ausentes | 15 edições sem idioma | Não preenchidos artificialmente | Ausência não significa idioma desconhecido no mundo real |
| Locais multivalorados | 73 relações para 70 edições | Criação de `silver_edition_places` | Nem todos os locais têm país ou padrão uniforme |
| Locais ausentes | 46 edições | Preservação como ausência de metadado | Não se classifica como local nacional ou internacional |
| Variações de local | `Rio de Janeiro`/`Rio de Janeiro, RJ`; `São Paulo`/`São Paulo, SP`/`Sao Paulo` | Normalização conservadora em tabela Gold final | Não foi feita geocodificação ou padronização global |
| Valor suspeito no local | `272 p` | Classificado como `suspect_non_place` e removido da distribuição normalizada | O registro bruto foi preservado para auditoria |
| Duplicidade aparente de títulos | Duas entradas de *Orphans of Eldorado* com `work_id`s distintos | Contagem baseada em `work_id` | Não houve deduplicação editorial por título |
| Limite do endpoint | `limit=100` por obra | Limitação documentada | Obras com mais de 100 edições podem estar sub-representadas |

## 6.3 Aprendizados de qualidade

A qualidade não foi tratada como uma etapa de “limpeza para parecer perfeita”. O pipeline preserva os dados brutos e torna explícitas as regras aplicadas. Esse desenho é mais apropriado para uma fonte bibliográfica colaborativa, em que a heterogeneidade faz parte do objeto de estudo.

A normalização geográfica, por exemplo, foi limitada a variações evidentes. Rio de Janeiro foi consolidado em 18 edições, São Paulo em 14 edições e Belo Horizonte em 7 edições no KPI final. Porém, locais internacionais e locais residuais não foram forçados em categorias amplas sem regra documentada.

---

# 7. Análise de Dados e Respostas às Perguntas (Etapa 4.1)

## 7.1 Resultado executivo

A tabela `gold_mvp_kpis` consolidou os indicadores abaixo:

| Indicador | Resultado |
|---|---:|
| Obras analisadas | 82 |
| Edições recuperadas | 116 |
| Edições com ano extraível | 114 |
| Edições com idioma catalogado | 101 |
| Edições com local catalogado | 70 |
| Edições com editora catalogada | 116 |
| Edições em português | 64 |
| Edições em inglês | 32 |
| Edições em espanhol | 4 |
| Edições em francês | 2 |
| Edições em alemão | 1 |
| Edições com idioma indefinido | 1 |
| Obras com edição em inglês | 20 |
| Obras com local internacional | 24 |
| Obras com sinal internacional combinado | 10 |

## 7.2 Pergunta 1 — Quais idiomas predominam?

O português é o idioma mais frequente entre as relações edição–idioma: **64 edições**, associadas a **55 obras**. O inglês aparece em **32 edições**, associadas a **20 obras**. Espanhol, francês e alemão aparecem de maneira residual.

| Idioma | Edições | Obras |
|---|---:|---:|
| Português | 64 | 55 |
| Inglês | 32 | 20 |
| Espanhol | 4 | 4 |
| Francês | 2 | 2 |
| Alemão | 1 | 1 |
| Não definido | 1 | 1 |

A leitura correta é que o conjunto recuperado pela Open Library contém mais relações de edição em português do que em inglês. Isso não permite concluir que todas as obras circulam predominantemente em português em todos os mercados, pois a base pode ter cobertura desigual e uma edição pode possuir múltiplos idiomas.

**Resposta:** no recorte analisado, o português predomina; o inglês é o segundo idioma mais frequente.


## 7.3 Pergunta 2 — Quais editoras aparecem com maior frequência?

A distribuição de editoras registra **67 nomes distintos** e **120 relações edição–editora**. As editoras mais frequentes são:

| Editora | Edições | Obras |
|---|---:|---:|
| Companhia das Letras | 14 | 14 |
| Rocco | 8 | 7 |
| Publifolha | 5 | 2 |
| Alfaguara | 4 | 4 |
| Todavia | 4 | 4 |
| Editora Record | 3 | 3 |
| Relicário | 3 | 3 |
| Bloomsbury | 3 | 2 |
| Bloomsbury Publishing Plc | 3 | 2 |
| Texas Tech University Press | 3 | 2 |

A Companhia das Letras é a editora mais recorrente no corpus recuperado. A Rocco ocupa a segunda posição. O resultado descreve frequência de registros, não participação de mercado, volume de vendas, alcance nacional ou relevância literária.

Também é necessário reconhecer que nomes como `Bloomsbury` e `Bloomsbury Publishing Plc` podem representar variação cadastral. Como não foi usado um identificador editorial externo, a análise preserva a forma fornecida pela Open Library.


## 7.4 Pergunta 3 — Quais locais de publicação aparecem com maior frequência?

A distribuição bruta continha 34 valores distintos, com variações de grafia, abreviações e um valor inválido. Após uma normalização conservadora, os principais locais são:

| Local normalizado | Edições | Obras | Variantes brutas |
|---|---:|---:|---:|
| Rio de Janeiro | 18 | 16 | 2 |
| São Paulo | 14 | 12 | 5 |
| Belo Horizonte | 7 | 7 | 3 |
| London | 5 | 4 | 2 |
| New York | 3 | 3 | 1 |
| Brazil | 2 | 2 | 1 |
| Edinburgh | 2 | 2 | 1 |

Rio de Janeiro é o principal polo registrado, seguido por São Paulo e Belo Horizonte. A presença de London, New York e Edinburgh oferece evidência de registros editoriais fora dos polos brasileiros definidos no estudo.

A normalização não deve ser confundida com geocodificação. Ela apenas consolida grafias evidentes, como `Rio de Janeiro` e `Rio de Janeiro, RJ`; `São Paulo`, `São Paulo, SP`, `Sao Paulo` e variantes com país; e formas de Belo Horizonte com siglas ou país.

**Resposta:** os polos mais recorrentes são Rio de Janeiro, São Paulo e Belo Horizonte; entre os locais internacionais mais frequentes estão London, New York e Edinburgh.

## 7.5 Pergunta 4 — Como as edições se distribuem no tempo?

Das 116 edições, 114 possuem ano extraível. O intervalo temporal vai de **1979 a 2025**, com 33 anos distintos registrados.

A distribuição revela poucos registros antes de 2000 e maior concentração a partir dos anos 2000. Alguns pontos de destaque:

- 2004: 6 edições;
- 2007: 9 edições, maior pico individual;
- 2008: 6 edições;
- 2010: 7 edições;
- 2014: 6 edições;
- 2018: 8 edições;
- 2019: 8 edições.

O comportamento sugere presença catalogada relevante de edições nas décadas mais recentes, mas não permite atribuir a concentração a uma causa específica. Uma parte dos registros pode refletir reedições, novas traduções, atualizações do catálogo ou diferenças na cobertura da base.

**Resposta:** a série é concentrada sobretudo após 2000, com pico em 2007 e nova concentração em 2018–2019.


## 7.6 Pergunta 5 — Há sinais de circulação internacional?

Foi criado um indicador exploratório por obra. Ele usa dois sinais distintos:

1. existência de pelo menos uma edição marcada como inglês (`/languages/eng`);
2. existência de pelo menos uma edição com local editorial classificado como internacional, isto é, diferente de Rio de Janeiro, São Paulo, Belo Horizonte ou Brazil na regra adotada.

O resultado foi:

| Sinal de circulação catalogada | Obras | Edições em inglês | Edições com local internacional |
|---|---:|---:|---:|
| Inglês e local internacional | 10 | 14 | 14 |
| Inglês somente | 10 | 18 | 0 |
| Local internacional somente | 14 | 0 | 15 |
| Sem sinal internacional catalogado | 48 | 0 | 0 |

Assim, **34 das 82 obras** apresentam pelo menos um sinal catalogado de circulação internacional. Dessas, 20 têm edição em inglês, 24 têm local internacional e 10 combinam os dois sinais.

Entre os exemplos com sinal combinado aparecem *Sinfonia em branco*, *Ashes of the Amazon*, *Dois Irmãos*, *Torto Arado*, *Orphans of Eldorado*, *Os filhos deste solo*, *Poncia vicencio* e *Rakushisha*. O uso de `work_id` é importante: duas entradas com o título *Orphans of Eldorado* têm identificadores distintos na Open Library e foram preservadas como registros distintos.

**Resposta:** há sinais bibliográficos de internacionalização em 34 obras; 10 combinam edição em inglês e local editorial internacional. O resultado é exploratório e não equivale a prova de tradução integral, distribuição comercial ou leitura internacional.

## 7.7 Síntese analítica

A análise indica um corpus cujo registro bibliográfico recuperado permanece fortemente associado ao português e a polos editoriais brasileiros, sobretudo Rio de Janeiro, São Paulo e Belo Horizonte. Ao mesmo tempo, a presença de 32 edições em inglês, 24 obras com locais internacionais e 10 obras com sinal combinado aponta para uma parcela do corpus que apresenta evidências catalogadas de circulação além desses polos.

O resultado mais relevante não é uma afirmação de que as obras “circulam internacionalmente” de maneira uniforme, mas a demonstração de que a infraestrutura de dados construída permite separar três situações: ausência de sinal no recorte, idioma inglês sem local internacional informado, local internacional sem edição inglesa informada, e ocorrência conjunta dos dois sinais. Essa distinção é mais informativa do que reduzir o problema a uma única classificação binária.

---

# 8. Dashboard e Evidências Visuais

## 8.1 Integração do dashboard

O dashboard Databricks deve utilizar exclusivamente as tabelas da camada `viz_*`, evitando cálculos adicionais nos widgets. Essa decisão garante que os gráficos reproduzam as regras documentadas no pipeline.

| Componente | Fonte |
|---|---|
| Cartões KPI | `workspace.default.viz_kpi_cards` |
| Idiomas | `workspace.default.viz_language_distribution` |
| Série temporal | `workspace.default.viz_publication_years` |
| Editoras | `workspace.default.viz_top_publishers` |
| Locais | `workspace.default.viz_top_places` |
| Circulação internacional | `workspace.default.viz_international_circulation` |

---

# 9. Autoavaliação

## 9.1 Atingimento dos objetivos

O objetivo central foi atingido: o estudo construiu um pipeline funcional e auditável, capaz de transformar respostas semiestruturadas da Open Library em dados relacionais, métricas analíticas e tabelas de visualização.

Os objetivos específicos também foram atingidos:

- as 82 respostas de edições foram coletadas e persistidas;
- foram estruturadas 116 edições;
- idiomas, locais e editoras foram normalizados em relações próprias;
- 114 anos foram extraídos sem interromper o processamento diante de dados heterogêneos;
- foram criadas tabelas Gold de perfil, distribuição e indicadores;
- foi criado um indicador exploratório de circulação internacional;
- foram produzidas seis tabelas de visualização e uma tabela de KPIs;
- a auditoria final retornou 20 datasets com status `PASS`.

Além de responder às perguntas de negócio, o projeto deixou explícitas as limitações que impedem interpretações excessivas. Esse aspecto é tão importante quanto a criação dos gráficos: um pipeline de dados confiável não esconde ausências ou inconsistências, mas as torna observáveis.

## 9.2 Dificuldades encontradas

A principal dificuldade foi a heterogeneidade dos metadados bibliográficos. O campo `publish_date`, por exemplo, continha formatos como ano isolado, data textual e data numérica. A primeira tentativa de extração falhou porque o padrão regular foi escrito com escape inadequado, levando a resultados vazios. A solução foi corrigir a expressão para `r"(\d{4})"` e usar `try_cast`, evitando que strings vazias causassem falhas de conversão.

Outra dificuldade foi a modelagem de campos multivalorados. Idiomas, editoras e locais não podiam ser tratados como uma única string se o objetivo era realizar contagens corretas. A expansão para tabelas de relacionamento resolveu o problema estrutural, mas exigiu cuidado interpretativo: 104 relações de idioma não equivalem a 104 edições, pois algumas edições possuem mais de uma etiqueta.

A normalização de locais foi outro ponto desafiador. Variantes como `Rio de Janeiro` e `Rio de Janeiro, RJ`, ou `São Paulo`, `São Paulo, SP` e `Sao Paulo`, fragmentavam os rankings. A solução foi criar uma tabela Gold adicional com regras explícitas e conservadoras, preservando sempre a tabela bruta. Essa escolha é preferível à substituição irreversível dos valores de origem.

Por fim, a presença de valores como `272 p` no campo de local mostrou que dados bibliográficos podem conter deslocamentos de campo ou ruído de catalogação. O valor não foi apagado da camada bruta; foi sinalizado e excluído somente da agregação geográfica normalizada.

## 9.3 Limites da solução

A solução é adequada como MVP, mas possui limites técnicos e analíticos:

- o endpoint foi chamado com `limit=100`, sem paginação adicional;
- não houve enriquecimento com identificadores externos de editoras, países ou autores;
- a normalização de locais não implementa geocodificação;
- a análise de autores permanece limitada porque `work_authors_raw` contém JSON bruto;
- a Open Library pode ter registros duplicados, incompletos ou com representação desigual entre mercados;
- o dashboard apresenta metadados catalogados, não fenômenos completos de circulação cultural.

## 9.4 Estudos futuros

O projeto pode ser aprofundado em quatro frentes.

### 1. Cobertura de coleta

Implementar paginação completa do endpoint de edições para obras com mais de 100 registros. A carga poderia registrar número total informado pela API, páginas consultadas e uma flag de completude por obra.

### 2. Enriquecimento de entidades

Criar dimensões normalizadas de autores, editoras e locais. Para editoras, isso exigiria regras documentadas ou fontes externas confiáveis para resolver variantes. Para locais, uma tabela de referência poderia associar cidade, estado e país, sem alterar o valor bruto original.

### 3. Análise temporal mais robusta

Distinguir ano de publicação original da obra, ano de edição, ano de tradução e ano de reedição quando essas informações puderem ser obtidas com fontes adicionais. Isso permitiria estudar defasagens temporais e ciclos editoriais com mais precisão.

### 4. Integração de fontes

Combinar a Open Library com catálogos nacionais, ISBN, páginas de editoras, WorldCat ou outras fontes bibliográficas. A triangulação reduziria o risco de interpretar lacunas de uma única base como ausência de circulação.

## 9.5 Conclusão da autoavaliação

O estudo demonstra domínio de uma sequência completa de engenharia de dados aplicada a um problema bibliográfico: ingestão por API, persistência em Delta, transformação de JSON, normalização relacional, auditoria de qualidade, criação de métricas e preparação para dashboard.

O principal resultado de portfólio não é apenas a tabela final de indicadores. É a capacidade de explicar como os resultados foram produzidos, quais decisões de modelagem sustentam cada gráfico, quais dados ficaram de fora e por que uma conclusão responsável precisa distinguir entre metadado ausente, catálogo incompleto e ausência real de fenômeno editorial.

---

# 10. Reprodutibilidade e Checklist de Entrega

## 10.1 Consultas de verificação

```sql
SELECT *
FROM workspace.default.gold_mvp_kpis;

SELECT *
FROM workspace.default.silver_editions_data_quality;

SELECT *
FROM workspace.default.gold_pipeline_validation
ORDER BY dataset;

SELECT *
FROM workspace.default.gold_project_data_inventory
ORDER BY display_order;
```

A validação final esperada é:

```text
+-----------------+--------+
|validation_status|datasets|
+-----------------+--------+
|PASS             |20      |
+-----------------+--------+
```

## 10.2 Checklist final

- [x] Dados brutos persistidos na camada Bronze.
- [x] Edições estruturadas na camada Silver.
- [x] Idiomas, locais e editoras normalizados.
- [x] Qualidade de dados documentada.
- [x] Tabelas Gold criadas.
- [x] Tabelas `viz_*` criadas para o dashboard.
- [x] Inventário do projeto criado com 19 datasets principais.
- [x] Auditoria final criada com 20 datasets.
- [x] Auditoria final executada com 20 `PASS`.
- [X] Dashboard final revisado e publicado no Databricks.
- [X] Screenshots inseridos no PDF.
- [X] Links reais do repositório Git substituídos neste README.
- [X] Documento final exportado para PDF.

---

# 11. Referências e atribuição

- Open Library. API de obras e edições. Consultada em setembro de 2026.
- Databricks. Plataforma utilizada para persistência Delta, transformação Spark SQL/PySpark, catálogo de tabelas e dashboard.
- Repositório do projeto:(https://github.com/literaturaandre-byte/mvp-literatura-sul-global-databricks)

> **Atribuição:** os metadados bibliográficos utilizados neste estudo foram recuperados da Open Library. As análises, modelagem, regras de transformação, normalização e interpretações descritas neste documento são específicas deste projeto.

