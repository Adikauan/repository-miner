## Introdução do problema
O problema partiu de uma necessidade real dentro do meu ambiente de trabalho. Normalmente utilizamos o método cascata para a gestão de nossos projetos. O cliente ao qual eu presto serviços paga um valor para a empresa contratante para ter acesso ao código fonte, com isso, podendo realizar desenvolvimento em cima do nosso produto.

Em alguns projetos, por decisão do cliente, a etapa de publicação em produção não ocorre após a finalização dos testes em ambiente de homologação. No projeto em questão, a data da publicação foi marcada para 8 meses após a finalização dos testes. Como medida de controle, estabelecemos testes exploratórios próximo a data de publicação para garantir funcionalidades básicas do sistema. Como o cliente pode reealizar desenvolvimento em cima do nosso sistema, identificamos, através de erros registrados em testes, que o cliente tinha sobrescrito funcionalidades do projeto no ambiente de qualidade. A não identificação disso poderia ocasionar perdas financeiras para o cliente e para a empresa ao qual eu trabalho.

Com isso, a necessidade de realizar um controle de branches se torna necessário para garantir a entrega do produto.

O projeto contempla um MVP do que seria um monitoramento de branches de repositórios em desenvolvimento, espera-se, através de configuração, conseguirmos prever falhas no fluxo de versionamento ocasionadas por multiplas equipes e projetos sendo executados paralelamente.

## Informação sobre uso de modelo de IA
O projeto foi utilizado utilizado a versão web do chatGPT, no nivel alto, para gerar a primeira ideia do MVP. com o codex cli, versão gpt-5.6-sol no nivel low foi escolhido para utilização do speckit. A partir da segunda spec, foi utilizado o modelo gpt-5.6-luna no nivel médio para utilização do speckit.


## 1. Iniciando com spec kit

Realizei uma conversa com o o ChatGPT sobre o spec kit, onde ele me apresentou as principais funcionalidades e como utilizar cada skill. Após a conversa sobre o spec kit, estabelecemos o que seria o realizado no projeto para atender a demanda necessária. A conversa iniciou com um cenário geral, mas depois foi reduzida a construção de um MVP. Com as principais funcionalidades estabelecidas, iniciamos os TRABALHOS.

## 2. Desenvolvimento assistido por CODEX

Por eu possuir um plano de ChatGPT, optei por utilizá-lo ao invés do copilot. 

#### 2.1. Criando o projeto a constitution

Com o auxilio do codex, foram estabelecidos 10 principios:

```
$speckit-constitution

O Repository Miner deverá seguir estes princípios:

1. Simplicidade arquitetural
A solução deverá utilizar a arquitetura mais simples capaz de atender aos requisitos atuais. Microserviços, filas, processamento distribuído ou infraestrutura adicional somente deverão ser introduzidos quando existir uma necessidade concreta.

2. Segurança de credenciais
Tokens do GitLab e chaves de API de provedores de inteligência artificial são informações sensíveis e nunca deverão aparecer em logs, relatórios ou código-fonte.

3. Rastreabilidade
Todo resultado da mineração deverá ser rastreável até sua origem, incluindo repository, branch, commit, autor e arquivos relacionados.

4. Mineração incremental
Execuções recorrentes deverão evitar reprocessar commits já analisados anteriormente.

5. Isolamento de integrações
A integração com GitLab e com provedores de inteligência artificial deverá permanecer desacoplada das regras de negócio.

6. Resultados de IA não determinísticos
Resultados de análise semântica deverão ser tratados como possíveis riscos e nunca como confirmação absoluta de bug ou vulnerabilidade.

7. Testabilidade
As regras de mineração e análise deverão poder ser testadas sem depender de conexões reais com GitLab ou provedores de IA.

8. Falhas isoladas
A falha no processamento de um repository ou commit não deverá necessariamente interromper os demais repositories da execução.

9. Privacidade do código
Somente as informações necessárias para análise deverão ser enviadas ao provedor de IA.

10. Observabilidade
As execuções deverão registrar início, fim, estado, repositories processados, commits analisados, falhas e achados.
```

A execução feita para criação da constitution criou o documento todo em inglês.

#### 2.2. Criando o Specify

Utilizamos o Specify para gerar as primeiras informações do projeto. Na spec, incluímos as principais funcionalidades e onde seria utilizado, além das informações importantes a serem monitoradas. Dei uma de sabichão e inclui no texto criado pelo Codex, adicionando informações que eu achava pertinente. Acontece que não é esse o momento de inserir as Stacks trabalhadas. Com a ajuda do Codex, retrabalhamos a spec para que fique conforme o esperado.

#### 2.3. Utilizando o Clarify
Rodei o comando de Clarify sem nenhuma instrução. Com isso, o Codex identifica sozinho as maiores ambiguidades da minha spec.

Foram realizadas as seguintes perguntas:

Na primeira execução de uma configuração, quais commits da branch devem ser considerados novos?

A - Analisar todo o histórico disponível da branch na primeira execução.
B - Registrar o estado da branch na ativação e analisar somente commits posteriores.
C - Analisar commits dentro de um período inicial configurável, como os últimos 30 dias
D - Analisar os últimos N commits, com quantidade configurável.

A resposta recomendada foi a B. Segui o voto do relator.

O operador deve poder iniciar uma execução manualmente, além das execuções agendadas?

A - Permitir execução manual de qualquer configuração válida, mesmo desabilitada.
B - Permitir execução manual somente quando a configuração estiver habilitada.
C - Não permitir execução manual; somente o agendamento inicia execuções.

A resposta recomendada foi a A. Segui o voto do relator.

O que deve acontecer quando uma configuração já possui uma execução em andamento e outra execução é solicitada ou fica agendada?
  
A - Não iniciar outra execução; recusar a manual ou ignorar a ocorrência agendada com motivo registrado.
B - Colocar a nova execução em fila para começar quando a atual terminar.
C - Permitir execuções simultâneas para a mesma configuração.

A resposta recomendada foi a A. Segui o voto do relator.

Quando branch, repositories, usuários esperados ou provedor de IA forem alterados, a configuração deve eprocessar commits já concluídos?

A - Não reprocessar; mudanças valem para commits futuros e novas combinações começam no estado atual.
B - Reprocessar todos os commits anteriores sempre que qualquer configuração de análise mudar.
C - Permitir que o operador escolha entre preservar ou reiniciar os checkpoints a cada alteração.

A resposta recomendada foi a A. Segui o voto do relator.

Quando uma configuração nunca habilitada for executada manualmente pela primeira vez, qual deve ser o marco inicial?

A - O primeiro disparo manual registra o estado atual e não analisa o histórico anterior.
B - Considerar o momento em que a configuração foi salva e analisar commits posteriores a ele.
C - Exigir que a configuração seja habilitada uma vez antes de permitir execução manual.

A resposta recomendada foi a A. Segui o voto do relator.

As sugestões de respostas pareciam fazer sentido para mim. Para cada resposta que eu dava, ele alterava minha spec. MANEIRO DEMAAAIS.

Após a finalização do Clarify, recebi um relatório do que ocorreu!

 Decisões registradas:

  - Primeira ativação não analisa o histórico anterior.
  - Configurações válidas podem ser executadas manualmente.
  - Apenas uma execução por configuração pode permanecer ativa.
  - Alterações de configuração não reprocessam commits concluídos.
  - O primeiro disparo manual também estabelece o estado atual como marco inicial.

  Seções alteradas: Clarifications, User Story 2, Edge Cases, Functional Requirements e Assumptions.

Após isso, e com ajuda de uma seção dedicada do GPT, analizamos cada uma das minhas respostas e rodando mais um Clarify, agora com foco em análise semantica, processamento de diffs, erros relacionados a IA, descobertas, vulnerabilidades e relatório de execução.

As seguintes perguntas foram feitas:

Como a análise semântica deve tratar um diff textual maior do que o limite aceito pelo provedor de IA?

A - Dividir o diff em partes, analisar todas e consolidar os achados do commit.
B - Truncar o diff, analisar somente a parte permitida e marcar a análise como parcial.
C - Não analisar o diff; registrar uma falha por limite excedido.

A resposta recomendada foi a A.

Quando o provedor de IA falhar temporariamente, quantas tentativas devem ocorrer antes de registrar falha na análise do commit?

A - Realizar até três tentativas; depois registrar falha e continuar o processamento independente.
B - Realizar apenas uma tentativa e registrar falha imediatamente.
C - Continuar tentando até o provedor responder, mantendo a execução aberta.

A resposta recomendada foi a A. 

Depois que as três tentativas de IA falharem, o commit deve ser tentado novamente em uma execução futura?

A - Manter pendente e tentar novamente na próxima execução, sem avançar seu checkpoint de análise.
B - Considerar o commit concluído com falha e nunca tentar novamente automaticamente.
C - Tentar novamente somente quando o operador solicitar explicitamente.

A resposta recomendada foi a A.

Quais informações padronizadas cada achado semântico deve apresentar além da rastreabilidade básica?

A - Categoria, severidade estimada, explicação, arquivos e trechos afetados; vulnerabilidades incluem identificador reconhecido quando disponível.
B - Categoria, explicação e evidência, sem classificação de severidade.
C - Preservar apenas o texto livre retornado pelo provedor, sem campos padronizados.

A resposta recomendada foi a A.

Como o relatório deve contabilizar commits cuja análise de IA falhou após todas as tentativas?

A - Exibir em categoria separada; não contar como possível problema nem como análise sem achados.
B - Contar como commit com possível problema por precaução.
C - Exibir apenas na lista geral de falhas, sem identificar a cobertura semântica incompleta.

A resposta recomendada foi a A.

Com isso realizado, o relatório foi:

 Decisões registradas:

  - Diffs grandes serão divididos e analisados integralmente.
  - Falhas transitórias terão até três tentativas por execução.
  - Commits sem análise concluída permanecerão pendentes para execuções futuras.
  - Achados terão categoria, severidade estimada, explicação e evidência localizada.
  - Vulnerabilidades poderão registrar identificadores reconhecidos.
  - O relatório separará análises pendentes ou falhas de possíveis problemas.

  Seções alteradas: Clarifications, User Story 2, User Story 4, Edge Cases, Functional Requirements, Key Entities e
  Success Criteria.


#### 2.4. Criando o Plan

O plan sugerido pelo ChatGPT já considerava o backend utilizando .NET. Por achar que ele fez essa escolha por conta da minha stack, comecei uma análise em conjunto para identificar se essa realmente era a melhor escolha.

Após um embate ferrenho e visando a evolução desse projeto para o mestrado/outras operações, consideramos a utilização de python no backend.

.NET eu já sei usar, agora quero ter proficiência com outras linguagens.

Com isso, criamos nosso plan, com destaque:

- Utilização de React com typescript no frontend, utilizando componentes do Material UI.
- O backend será o famoso MONOLITO MODULAR.
- Será utilizado um banco de dados relacional para armazenar as informações.
- Nesse momento, não estamos considerando a utilização rabbitMQ, kafka, Celery, etc.

Após a execução do Analyze, algumas inconsistências foram classificadas como HIGH. A alteração da Spec e geração de um novo Plan trouxeram também novas ponderações. Por conta disso, optamos por fazer uma simplificaçã odo projeto.

#### 2.5. Simplificando o projeto

Como eu já estava utilizando ChatGPT para estudo de análise semântica e mineração, ele usou o contexto anterior para me ajudar com a criação desse projeto. Como eu estava olhando coisas mais elaboradas, acabou que o projeto ficou muito mais COMPLEXO que eu gostaria. A ideia era somente utilizar mineração e classificação de commits. A Análise semântica de diffs ficaria para um segundo momento. Por conta disso, simplifiquei o projeto, removendo a utilização de modelos para análise semântica e foquei somente na interface visual e classificação de commits. 

Com isso, criamos um novo Specify:

```
Criar uma aplicação web para configuração, execução e acompanhamento de mineração de repositories hospedados no GitLab.

O usuário deverá poder criar uma configuração de mineração informando uma URL de uma instância GitLab e uma credencial de acesso.

Após estabelecer a conexão, o sistema deverá consultar o GitLab e apresentar os repositories disponíveis em uma estrutura hierárquica de grupos, subgrupos e repositories.

O usuário deverá poder selecionar um grupo inteiro, um subgrupo ou repositories individuais para fazer parte da configuração de mineração.

Uma configuração deverá possuir uma branch alvo. Inicialmente o cenário principal será a branch QA.

O sistema deverá permitir cadastrar uma lista de usuários esperados para trabalhar na branch configurada. Cada usuário deverá possuir informações suficientes para permitir sua identificação como autor de um commit.

O sistema deverá permitir configurar um provedor de inteligência artificial, incluindo a chave necessária para acesso à API.

A chave da API e a credencial do GitLab deverão ser tratadas como informações sensíveis.

O usuário deverá configurar a periodicidade da execução da mineração, podendo escolher entre:

- diária;
- semanal;
- mensal.

Uma configuração deverá poder ser habilitada ou desabilitada.

Quando chegar o momento programado para uma configuração habilitada, o sistema deverá iniciar uma nova execução de mineração.

A execução deverá consultar os repositories configurados e identificar os commits novos existentes na branch alvo desde a última execução válida.

Para cada commit encontrado, deverão ser obtidas informações como:

- hash;
- autor;
- e-mail do autor;
- data;
- mensagem;
- arquivos modificados;
- diff das alterações.

O sistema deverá comparar o autor do commit com os usuários cadastrados para aquela configuração.

Caso seja identificado um commit realizado por um usuário que não esteja configurado para trabalhar naquela branch, deverá ser criado um achado para esse commit.

O diff e as informações relevantes do commit deverão ser submetidos a uma análise semântica por meio do provedor de inteligência artificial configurado.

A análise deverá procurar indícios de alterações que possam introduzir bugs, vulnerabilidades ou comportamentos inesperados.

O resultado da inteligência artificial deve ser tratado como uma indicação de possível risco e não como confirmação de que existe um defeito.

Quando a análise identificar um possível problema, deverá ser criado um achado relacionado ao commit.

Cada achado deverá ser rastreável até o repository, branch, commit, autor e arquivos envolvidos.

O sistema deverá armazenar histórico das execuções realizadas.

Durante uma execução, o usuário deverá conseguir acompanhar seu estado e progresso através da interface web.

Ao final da execução, deverá existir um relatório contendo pelo menos:

- repositories processados;
- commits analisados;
- commits com possíveis problemas;
- autores não esperados;
- possíveis bugs identificados;
- possíveis vulnerabilidades identificadas;
- falhas ocorridas durante a execução.

O relatório deverá permitir consultar os detalhes de cada achado e identificar o commit e o código relacionado.

O processamento deverá ser incremental, evitando analisar novamente commits já processados em uma execução anterior válida.

Falhas na mineração ou análise de um repository não deverão obrigatoriamente interromper o processamento dos demais repositories.

O primeiro MVP não deverá realizar correções automáticas de código, alterações em repositories ou criação automática de merge requests.
```


#### 2.6. Rodando a nova spec

Com a nova spec definida, executamos um novo Clarify

O operador poderá cancelar manualmente uma execução em andamento no MVP? (FR-025)

A - Não permitir cancelamento no MVP e remover cancelled dos estados canônicos.
B - Permitir cancelamento solicitado pelo operador, preservando todo trabalho concluído e checkpointsduráveis.
C - Manter cancelled apenas para interrupção administrativa do sistema, sem ação disponível na interface.

A opção escolhida foi a A.

Como o estado final deve ser determinado quando repositories falham durante uma execução?

A - completed se todos terminarem; partially_completed se houver sucessos e falhas; failed se nenhumrepository puder ser processado com sucesso.
B - Qualquer falha de repository resulta em partially_completed, mesmo quando todos falharem.
C - Qualquer falha de repository resulta em failed, mesmo quando outros terminarem com sucesso.

A opção escolhida foi a A.

Em uma periodicidade mensal configurada para um dia inexistente no mês, quando a execução deverá ocorrer?

A - Executar no último dia do mês quando o dia configurado não existir.
B - Não executar naquele mês e aguardar o próximo mês que contenha o dia configurado.
C - Permitir somente dias de 1 a 28 nas configurações mensais.

A opção escolhida foi a A.

Se a credencial GitLab for marcada como comprometida durante uma execução ativa, o processamento ainda poderá fazer novas consultas ao GitLab?

A - Bloquear imediatamente novas consultas; preservar trabalho concluído e finalizar como partially_completed ou failed.
B - Permitir que a execução ativa termine, bloqueando somente execuções e testes de conexão posteriores.
C - Interromper toda a execução e descartar também os resultados produzidos antes da marcação.

A opção escolhida foi a A.

Executei uma serie de alterações de spec, plan e tasks para corrigir todas as inconsistências apontadas.

#### 2.7. Implementação e resultado inicial

Para uma implementação mais ágil, foi necessário adicionar ao comando $speckit-implement um texto orientando a não realizar pausas a cada task executada. Com isso, foi possível realizar a implementação em fases mais longas, minimizando minha interação.

## 3. Primeira versão

A primeira versão do projeto, apesar de atender brevemente as necessidades solicitadas, carecia de diversas funcionalidades que não foram solicitadas, como:

- Execução manual de agendamentos;
- Visualização de relatório de execução;
- Desconexão entre o planejamento e as execuções;
- Paginação de execuções;

Com isso identificado, optei por separar e executar novas specs para o projeto. A separação de specs foi fundamental para aplicação rápida das nova funcionalidades;

## 4. Conclusão e pontos de evolução

A MVP atendeu, mas com ressalvas, as necessidades estabelecidas inicialmente. Apesar disso, foi necessário entender alguns pontos importantes sobre a utilização do speckit:

1. $speckit-clarify Foi essencial na primeira spec, para estabeler as diretrizes iniciais da constitution e o primeiro plano. Com o avanço das specs, não foram realizadas mais perguntas sobre o sistema, mostrando que as principais inconsistências causadas inicialmente foram resolvidas.
2. $speckit-analyze Foi importante para entender inconsistências com alto impacto no sistema. Apesar disso, foi necessário entender o momento de parar de utilizar, pois acabava encontrando coisas cada vez melhores. Ao que parece, um projeto com sem inconsistências de níveis criticos ou altos podem ser suficiente para atender as necessidades do usuário. Cabe, entretanto, avaliar pontualmente para evitar problemas futuros.
3. $speckit-implement A implementação do código, apesar de ocorrer de forma fluida, NECESSITA de mais informações além do comando. Adicionar trechos como : "Execute todas as tarefas pendentes desta feature que estiverem desbloqueadas. Não pare ao final de uma fase ou user story se ainda houver tarefas executáveis. Continue implementando, testando e corrigindo até concluir todas as tarefas ou encontrar um bloqueio real." facilitava o desenvolvimento, visto que ele era capaz de executar multiplas tarefas sem necessidade de validação humana.

![Tela de login](Evidências/1-criando_teste.png)

![Tela de login](Evidências/2-criando_teste.png)

![Tela de login](Evidências/3-criando_teste.png)

![Tela de login](Evidências/4-teste_criado.png)

![Tela de login](Evidências/5-primeira_execucao.png)

![Tela de login](Evidências/6-primeira_execucao_relatorio.png)

![Tela de login](Evidências/7-execucao_manual.png)


