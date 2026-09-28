# Dados

Os dados brutos utilizados no MVP não são versionados neste repositório.

A ingestão será realizada no Databricks Free Edition, onde os arquivos serão preservados na camada Bronze em um Volume do Unity Catalog ou em localização equivalente disponibilizada pela plataforma.

## Fontes

- Wikidata: dados estruturados de autores e identificadores.
- Open Library: metadados de autores, obras e edições, além de métricas agregadas disponíveis.

## Motivo

Os dados serão coletados e armazenados no ambiente de nuvem para que o pipeline possa ser executado no Databricks. O GitHub conterá apenas:

- códigos;
- notebooks;
- configurações não sensíveis;
- documentação;
- consultas;
- esquemas e descrições;
- resultados agregados necessários para demonstrar o MVP.

Não serão versionados neste diretório:

- tokens;
- senhas;
- chaves de API;
- dados pessoais;
- arquivos brutos completos;
- credenciais;
- arquivos temporários de execução.

## Rastreabilidade

A origem, a data de coleta, os endpoints utilizados, os identificadores consultados e as transformações realizadas serão registrados na documentação do projeto.