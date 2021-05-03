# Discursos da Câmara em um Mongodb
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Este projeto automatiza, de forma reprodutível e segura, algo que acabei fazendo várias vezes nos últimos anos: extrair e armazenar discursos feitos por deputados e deputadas federais na Câmara. 

## O que isso faz?

Um [script](src/speech_data.py) extrai a lista de  todas as pessoas que ocuparam mandatos na Câmara em um dado período e, a partir daí, usa a [API Rest dos Dados Abertos](https://dadosabertos.camara.leg.br/) da casa para recuperar seus discursos em plenário. Ao longo do processo, além disso, lotes de discursos são salvos em uma coleção de [Mongodb](https://www.mongodb.com/) -- que é rápido e permite salvar o conteúdo inteiro retornado em `json` de cada requisição, preservando informações que podem ser úteis no futuro.

## Como usar?

Com [Docker](https://docs.docker.com/get-docker/) e [Docker-compose](https://docs.docker.com/compose/install/) instalados, basta clonar este repositório e, com o terminal aberto nele, rodar:

`docker-compose up -d`

Os dados são persistidos em um volume chamado `dbdata`, que pode então ser utilizado por outras imagens ou carregado numa instalação local do Mongodb.

### Parâmetros

É possível alterar alguns parâmetros de extração editando o [docker-compose.yml](docker-compose.yml) diretamente. Particularmente, `START_LEGIS`, sob o serviço `etl_python3.8`, indica a legislatura a partir da qual extrair discursos (o padrão é `52` porque, antes disso, a API da Câmara não retorna o conteúdo dos discursos, apenas seus metadados).

