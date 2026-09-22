# Quickstart: Visualização de Relatório de Execução

## Pré-requisitos

- Backend e frontend do Repository Miner configurados conforme o projeto atual.
- Uma execução sintética existente ou mocks de respostas do cliente de consulta.
- Nenhum token real ou credencial real nos dados de teste.

## Validação automatizada

Na pasta frontend:

    npm test -- --run
    npm run build

Os testes devem cobrir carregamento, erro, execução inexistente, os cinco estados, sete contadores, listas, e-mail nulo, paginação, erros seguros e navegação para acompanhamento.

## Cenário manual

1. Inicie backend e frontend conforme a documentação do projeto.
2. Abra o histórico de execuções.
3. Selecione uma execução existente e acione o relatório.
4. Confirme o resumo, os sete contadores canônicos e os estados disponíveis.
5. Confirme repositories, commits, alertas e falhas; use a paginação quando houver mais de uma página.
6. Abra uma execução running e confirme a ação para o acompanhamento existente.
7. Reabra uma execução terminal e confirme que os dados persistidos prevalecem.
8. Confirme que mensagens e dados apresentados não contêm tokens ou credenciais.

## Resultados esperados

- Execução inexistente apresenta erro seguro.
- Lista vazia de commits, alertas ou falhas é um resultado válido.
- author_email nulo aparece explicitamente como ausente.
- Repositories falhos são distinguíveis dos concluídos.
- Os contadores exibidos são exatamente os valores recebidos, sem recálculo no frontend.
