# Metodologia e Fontes de Dados

## 1. Contexto do MVP

Este projeto implementa um pipeline de dados de ponta a ponta no Databricks Free Edition para analisar indicadores bibliográficos e editoriais associados à visibilidade de obras literárias de autores brasileiros no século XXI.

O problema norteador preservado é:

> Quero entender quais fatores mais influenciam as pessoas na escolha de livros de literatura no Sul Global no século XXI.

Como os dados públicos selecionados não medem diretamente decisões individuais de leitura, o MVP utiliza indicadores indiretos e agregados de visibilidade bibliográfica e circulação editorial.

## 2. Delimitação do estudo

O estudo utiliza uma amostra intencional de dez autores brasileiros:

1. Adriana Lisboa
2. Ana Maria Gonçalves
3. Bernardo Carvalho
4. Carola Saavedra
5. Conceição Evaristo
6. Geovani Martins
7. Itamar Vieira Junior
8. Jeferson Tenório
9. Julián Fuks
10. Milton Hatoum

O recorte não representa a totalidade da literatura brasileira, das literaturas do Sul Global ou das práticas de leitura. Trata-se de um estudo de caso exploratório, desenvolvido para demonstrar um pipeline de dados reproduzível.

## 3. Perguntas de negócio

1. Quais obras de autores brasileiros, publicadas ou reeditadas no século XXI, apresentam maior visibilidade no recorte selecionado?
2. A disponibilidade de uma obra em múltiplos idiomas está associada a maior visibilidade no catálogo?
3. Quais idiomas, além do português, aparecem com maior frequência entre as edições de obras do recorte?
4. Como se distribuem, ao longo do século XXI, as publicações e edições das obras no recorte?
5. Quais temas ou assuntos literários aparecem com mais frequência entre as obras mais visíveis?
6. Em que medida os dados disponíveis permitem explicar a escolha de leitores, em vez de apenas descrever visibilidade bibliográfica e recepção agregada?

## 4. Fontes de dados

### 4.1 Wikidata

Papel no pipeline:

- constituir e documentar a dimensão de autores;
- registrar identificadores estáveis;
- recuperar nome, data de nascimento, cidadania, ocupação e identificadores externos;
- garantir rastreabilidade do recorte autoral.

Método de acesso:

- consulta SPARQL no Wikidata Query Service;
- exportação do resultado em CSV;
- ingestão do arquivo exportado na camada Bronze.

Licença:

- os dados estruturados do Wikidata são disponibilizados sob Creative Commons Zero 1.0 Universal (CC0).

Referências:

- https://www.wikidata.org/wiki/Wikidata:Licensing
- https://query.wikidata.org/

### 4.2 Open Library

Papel no pipeline:

- obter metadados de autores, obras e edições;
- coletar títulos, identificadores, datas de publicação, idiomas, editoras e assuntos;
- obter métricas agregadas de avaliações quando disponíveis;
- permitir análise de circulação bibliográfica e diversidade linguística.

Método de acesso:

- API pública em JSON;
- extração controlada e de baixo volume;
- consulta restrita a 14 identificadores de autor para representar os 10 autores canônicos do recorte.

Licença e uso:

- a Open Library é um catálogo bibliográfico aberto;
- o MVP utilizará apenas metadados e métricas agregadas disponíveis;
- não serão coletados textos integrais de obras, perfis de usuários, comentários individuais, e-mails ou outros dados pessoais;
- a origem, os endpoints, os identificadores e a data de extração serão registrados nos arquivos Bronze.

Referências:

- https://openlibrary.org/developers
- https://openlibrary.org/developers/api
- https://openlibrary.org/developers/licensing

## 5. Estratégia de correspondência entre fontes

A correspondência entre Wikidata e Open Library não foi feita apenas pela igualdade textual dos nomes. Cada identificação foi validada por evidências contextuais, como títulos reconhecidos, página autoral coerente, ocupação, cidadania e compatibilidade com o item do Wikidata.

A coleta utilizará 14 IDs de autor da Open Library para representar os 10 autores canônicos. Conceição Evaristo e Jeferson Tenório possuem mais de um perfil na Open Library, em razão de fragmentação catalográfica e variações de grafia.

## 6. Limitações metodológicas

- Os indicadores de avaliações e edições representam visibilidade e circulação bibliográfica no catálogo, não preferência universal ou escolha individual de leitores.
- A ausência de registros ou avaliações na Open Library pode decorrer de cobertura catalográfica incompleta.
- Datas, idiomas, assuntos e editoras podem estar ausentes ou ser registrados de maneira inconsistente.
- A associação observada entre variáveis não permite inferir causalidade.
- O recorte de autores é intencional e não é estatisticamente representativo da literatura brasileira ou do Sul Global.