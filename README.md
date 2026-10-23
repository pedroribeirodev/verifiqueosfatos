# 🔍 Verifique os Fatos

Plataforma de verificação de declarações com Content Update automático. Construída para ser mínima (MÍNIMA MESMO). Esta plataforma é construída pensando em otimização máxima de recursos e custos, na medida do necessário para rodar em infra-estruturas gratuitas ou extremamente baratas.

Instância produtiva em: https://verifiqueosfatos.com/

## Arquitetura e Fluxo

Esta aplicação é uma `PWA (Progressive Web App)` estática feita em vanilla `HTML/CSS/JS` com `Auto Update` sem necessidade de backend dedidcado, os arquivos devem ser servidos preferencialmente de maneira serverless. Recomenda-se uma CDN. Não há "backend", você só precisa de um host. Nesta Doc Section você entenderá o que acontece assim que um usuário acessa esta app, seja em modo local ou produtivo.

🟦 A index.html será carregada

Assim que a index for carregada o front será interpretado e carregará todos os assets necessários. A página será processada.

🟦 PWA Installing

O browser identificará a manifest e carregará o Service Worker que instalará a página localmente. A partir daqui o server não sofre mais hit para carregar o front e a experiência fica disponível mesmo offline

🟦 Load posts.json

A página enviará uma request para a const `URI_POSTS_JSON` para obter o arquivo posts.json. Caso haja sucesso a conciliação será feita, do contrário, falhará silênciosamente e manterá o último estado válido.

🟦 Posts Conciliation

Caso post.json tenha sido obtido com sucesso a página comparará os itens atuais com os novos, fará o diff e renderizará a diferença necessária. Assim novos itens aparecem, ou itens removidos são excluídos do front.

🟦 Render

Após este processo a função de rendering é chamada e o front reage, nessa fase é onde a página é de fato percebida pelo user.

## PWA (Progresstive Web App)

Um PWA (Progressive Web App ou Aplicativo Web Progressivo) é uma aplicação criada com tecnologias web tradicionais (HTML, CSS e JavaScript) que oferece uma experiência de uso semelhante à de um aplicativo nativo de celular ou computador. 

Esta app é uma PWA, isso significa que quando você carregar este site, o seu navegador vai "baixar" o site inteiro no seu dispositivo. Não queremos com isso nos assemelhar a uma app nativa, a vantagem aqui é que após o primeiro carregamento, esta página não envia mais request para o server solicitando sources. Diferente de um cache (onde algum server sofre hit), na PWA a request não sai do browser. Isso nos dá uma economia massiva de recursos. Por motivos estratégicos, o arquivo `/posts.json` é uma excessão e nunca será "instalado".

### Atualizando a página

Uma vez que você carregar esta página, ela será portanto "instalada" para você. Para que você possa atualizar a experiência caso algo mude, você deve ignorar o service worker em modo local, ou acessar a rota `/update` para que o service worker atual seja automaticamente descartado, forçando o browser a atualizar os sources baixados.

## Serverless & Static

Esta aplicação inteira é "estática" e servelers. Isso quer dizer que não é necessário um server dedicado, não existe SSE (server sent events), não há socket, backend requests, REST, nada... apenas: arquivos.

Esta decisão é estratégica: Statics são mais baratos e simples de servir. A Web roda sob arquitetura distribuída por natureza. Todo site pode ser servido de multiplos hosts, e todo device é um client distrído. Se inserirmos uma camada backend para suportar a carga massiva que essa apliação suporta, temos que inserir também camadas de segurança, caching, queue e por aí vai.

Ao fazer com que a aplicação possa ser servida de forma estática e mantê-la mínima, fazemos com que qualquer servless host gratuito ou CDN tenha a capacidade de distritbuí-la. Isso simplifica toda a estrutura de Deploy e corta custos de maneira massiva. Por isso essa aplicação não tem camada de backend, nem SSE, nem Socket, nem Filas, nem nada disso. Claro que perdemos parte do controle fino (que não precisamos aqui), mas ganhamos em agilidade e praticidade: o que teríamos que gerenciar num backend, qualquer CDN free entrega -> distribuição rápida, queues, alta disponibilidade, escalabilidade elástica, etc...

## Design Mínimo

O Design deve ser mínimo. Quando digo mínimo é MÍNIMO MESMO. Não há libraries de terceiros, trackings, layouts rebuscados. A prioridade é servir o conteúdo de forma organizada e O MAIS RAPIDO POSSÍVEL. Como a aplicação é feito para rodar em escala massiva da maneira mais barata que pudermos, todo byte conta com custo na escala. Fique à vontade para contribuir deixando a app mais bonita, mas tenha isso que acabo de dizer como premissa: nada além do mínimo necessário.

## O arquivo "posts.json"

O arquivo `posts.json` é o coração dessa aplicação. Ele "emlula" uma REST API e age como nosso backend.

Sempre que carregada a app buscará pelo `posts.json` enviando um GET para o endereço determinado na const `URI_POSTS_JSON`. Por padrão na rota '/posts.json' dela mesma.

Este arquivo deve ser uma SST (Single Source of Truth). Ou seja, toda instância que buscar por ele deve baixar sempre o mesmo dado. Se esse dado é modificado, a próxima request deve receber ele modificado, sem cache, sem camada intermediária.

Aqui está o maior desafio desta aplicação: posts.json deve ser servido para escalas massivas o mais rápido possível. Quanto mais rápido e com maior disponibilidade, mais confiável e performática será esta aplicação.

### Estrutura

Este arquivo deve servir um Array de objetos com a seguinte estrutura:

```json
[
  {
    "n": 1,
    "c": 1,
    "t": "Aqui estará a declaração feita pelo candidato descrita o mais fielmente possível",
    "v": "Aqui estará a verificação feita, com fontes e referências.",
    "s": ["https://www.ibge.gov.br/", "https://www.bcb.gov.br/"]
  }
]
```

Onde:

```
- `"n"` é o Nome do candidato. 1 para Lula, 2 para Flávio.
- `"c"` é o check status, 1 para Verdadeiro, 2 para Falso e 3 para Parcial
- `"t"` é o `text`, basicamente a declaração feita pelo candidato
- `"v"` é a verificação, ou seja: o texto de demonstrando o que foi verificado
- `"s"` (opcional) são as fontes: um array de URLs http(s), exibidas no card como links com o domínio de cada uma, sempre abertos em nova aba
```

Cada objeto no array seguindo essa estrutura será renderizado como um card contendo foto e as informações checadas. Caso posts.json falhe ou seja inválido a página falhará silenciosamente e manterá o estado atual válido. Este objeto é configurado assim pra que possa ser distribuído com custo mínimo. Você pode mudar imagens e os labels editando a index.html. 

### Atualizando os dados

Para atualizar a página para todos os clients, você só tem que atualizar a posts.json, lembrando que ela deve ser uma single source of truth. Se você adiciona um objeto novo, nas próximas requests todos os clientes passam a receber a atualziação e a tela reagirá automáticamente.

## Então como adicionamos ou removemos declarações?

Sua aplicação deve apontar pra um único /posts.json servido através de qualquer serviço. Você apenas edita esse /posts.json e atualiza ele. No próximo round todos os clientes conectados receberão o update. Exemplo:

Seu arquivo posts.json está no ar assim:

```
[]
```

Isso significa que todos os clientes estarão vendo NENHUMA declaração. Digamos que o Lula disse algo e você verificará. Você edita seu posts.json da maneira abaixo e atualiza o server que o está distribuindo, exemplo:

```
[
  {
    "n": 1,
    "c": 1,
    "t": "Aqui estará a declaração feita pelo candidato descrita o mais fielmente possível",
    "v": "Aqui estará a verificação feita, com fontes e referências."
  },
]
```

Suba isso no serviço que está distribuindo sua posts.json e pronto, no proximo round de update todos os clientes vão começar a mostrar a declaração verificada adicionada. Esse arquivo é incremental, portanto, digamos que na sequencia o Flávio disse algo. Novamente: vc adiciona ao Array de declarações, sobe novamente no seu server e aguarda o update, ele ficaria agora assim:

```
[
  {
    "n": 1,
    "c": 1,
    "t": "Aqui estará a declaração feita pelo candidato descrita o mais fielmente possível",
    "v": "Aqui estará a verificação feita, com fontes e referências."
  },  
  {
    "n": 2,
    "c": 2,
    "t": "Aqui estará a declaração feita pelo candidato descrita o mais fielmente possível",
    "v": "Aqui estará a verificação feita, com fontes e referências."
  }  
]
```

E assim adiante. Para entender esta estrutura, leia a sessão que explica sobre a posts.json nesta README. Mas em poucas palavras: a app é uma snapshot e front do que está declarado na posts.json. Para mostrar uma nova declaração apenas incremente a posts.json (que deve ser distribuída via ponto único de verdade, ou seja: mesmo endpoint e mesmo arquivo sem cache pra todo client). Quando sua posts.json muda, toda pessoa conectada recebe a mudança.

## Arquitetura e Códigos Enxutos (De Verdade!)

Como já dito: esta app visa otimização máxima. Assim todo o código e funcionamento é feito para rodar com o mínimo em infra estruturas mínimas aptas a servir milhões de requests. Tenha isso em mente ao propor mudanças.

### Por que esta app é construída assim?

Esta é uma aplicação feita pela comunidade para a comunidade, queremos gastar pouco e servir o máximo possível.

## Executando local

Na raiz do projeto suba qualquer local server, minha sugestão é via npx

```
npx serve
```

Ou php

```
php -S localhost:8000
```

Ou Python

```
python -m http.server
```

Ou o que você quiser. Após isso abra seu endereço local e você verá a app. Atualize sua posts.json e pronto, a app responderá.

## /update

Lembre-se: isso é uma PWA, uma vez carregada ela não muda mais. Para atualizar o estado da aplicação, desative o sw.js ou acesse a rota /update.

## Deployment

Apenas jogue esses arquivos em qualquer host ou CDN ligada a um domínio com SSL. Lembre-se que todos os clients devem apontar a request de posts.json para um single source of truth, ou seja: para um mesmo arquivo/host.

## Contribuindo

Contribuições são bem vindas. PRs inúteis serão fechadas sem explicação prévia.
