# Quickstart: Paginação de Planos de Verificação

## Pré-requisitos

- Python 3.13+ e dependências do backend instaladas.
- Node.js e dependências do frontend instaladas.
- Banco de teste local; nenhum GitLab real é necessário.

## Backend

```powershell
python -m pytest backend/tests/contract/test_configuration_list_contract.py backend/tests/integration/configuration -q
```

Os testes devem cobrir `offset`/`limit`, `total`/`total_pages`, primeira página mais recente, páginas posteriores, empate determinístico por ID, dataset sem duplicação/omissão, página vazia e ausência de tokens/ciphertext.

## Frontend

```powershell
cd frontend
npm test -- --run tests/plans/plan-list-pagination.test.tsx
npm run build
```

Os testes devem cobrir abertura em offset zero, navegação, nova consulta, loading, erro/retry, estado vazio, retorno à primeira página após criação, página inválida e ausência de paginação local.

## Verificação manual

Com mais de uma página de planos, abrir `/`, confirmar os planos mais recentes, navegar entre páginas e criar um novo plano. Após a atualização, o novo plano deve aparecer na primeira página com todos os campos e ações atuais preservados.
