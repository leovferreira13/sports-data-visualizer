# Football, Visualized — roadmap de entrega

**Status:** plano para a primeira publicação · **Atualizado:** 26/09/2026

## Regra de execução

Construir uma primeira interação funcionando o quanto antes; completar uma publicação curta e confiável depois. Os tempos abaixo são **estimativas de esforço focado**, não prazos prometidos. A investigação do modelo determina se a publicação cabe em um fim de semana ou exige outro ciclo.

| Marco | Esforço indicativo | Demonstração ao final | Critério de saída |
| --- | --- | --- | --- |
| **0. Preparar** | 1–2 h | Repositório, app executável e três documentos de referência. | Executa localmente; escopo e critérios registrados. |
| **1. Campo jogável** | 4–8 h | Campo responsivo com chutador, goleiro, dois defensores e presets; distância e ângulo reagem ao arrastar. | Mouse e toque funcionam; limites do campo são respeitados; nenhum número provisório é rotulado xG. |
| **2. Prova do cálculo** | 3–6 h para avaliar artefato existente; mais tempo se exigir treino | Pequeno teste que recebe o estado do campo e devolve uma estimativa reproduzível. | Licença e entrada do modelo verificadas; goleiro/defensores afetam o valor quando declarados; cenários plausíveis; limitações documentadas. |
| **3. Playground publicável** | 6–10 h após marco 2 | Valor em tempo real, explicações, cinco presets, adicionar/remover até três defensores, reset e interface `pt-BR`/`en`. | Critérios de aceitação da v0.1 atendidos em desktop e celular. |
| **4. Aprender e publicar** | 4–8 h | Tutorial opcional de 2–3 passos no mesmo campo, README, URL e rodada curta de feedback. | Fluxo completo nos dois idiomas; fonte/limites do modelo visíveis; link público testado. |
| **5. Refinar com uso real** | Conforme feedback | Correções de confusão, bugs e fricções relatados por fãs e comentaristas. | Prioridades derivadas de observação, não de uma lista de funcionalidades futuras. |

**Primeiro marco observável:** ao fim do marco 1, é possível arrastar as peças e alternar presets. Isso responde cedo à pergunta “quão rápido conseguimos montar uma primeira versão que funciona?”. **Marco de publicação:** só depois do marco 2 o número pode ser apresentado como estimativa de xG.

## Decisão do modelo no marco 2

Investigar primeiro um artefato existente cujo **código e pesos** possam ser reutilizados, cujas entradas correspondam aos controles do campo e cuja execução caiba em uma app pequena. Registrar origem, licença, features e teste mínimo. Repositório público sem licença clara não conta como permissão de reutilização.

Se não houver encaixe, treinar **uma regressão logística pequena**, fora da aplicação, com chutes e posições disponíveis em dados abertos. Exportar coeficientes e metadados para inferência no navegador. Isso é uma alternativa delimitada, não uma trilha de pesquisa. Separar ou excluir pênaltis se o conjunto/modelo não os representar corretamente; não “forçar” um valor fixo dentro do mesmo modelo sem informar ao usuário.

Se o modelo contextual não ficar pronto imediatamente, o campo pode ser testado como protótipo com **geometria e indicadores**, mas sem publicar um xG que finge reagir a goleiro/defensores. Se o fallback for um modelo apenas de localização, o produto deve dizer isso claramente e não atribuir a ele o efeito dos outros jogadores. Uma v0.1 completa exige uma estimativa que corresponda às interações prometidas.

## Escopo de v0.1

**Interface e interação**

- Playground na abertura; campo de meia quadra com orientação e escala consistentes; chutador, goleiro e até três defensores manipuláveis por mouse e toque.
- Presets: pênalti, cara a cara, ângulo fechado, chute de longe e área congestionada; reset para o preset escolhido.
- Número em formato `0,xx xG` / `0.xx xG` e `%` equivalente, junto de distância, ângulo e leitura simples da ocupação do cone de chute.
- Painel “O que pesa nesta chance?” com observações do estado atual; ao mover peça, comparação antes/depois apenas dos fatores realmente utilizados pelo modelo.
- Modo Aprender com 2–3 experimentos opcionais: distância e ângulo; tirar defensor da frente; mudar posição do goleiro. Um passo inaplicável ao modelo selecionado não aparece.
- Alternador Português / English; idioma inicial pelas preferências do navegador, opção manual persistida; traduções completas inclusive para aviso metodológico.

**Entrega**

- URL e repositório públicos, README conciso com execução local, origem do modelo/dados, limitações, créditos, captura ou GIF e decisões de produto.
- Tamanho de toque confortável, layout utilizável no celular, suporte básico a teclado para selecionar e ajustar peças ou controles alternativos equivalentes.
- Verificação manual em navegador desktop e mobile, teste de função para geometria, inferência e serialização se houver link compartilhável.

## Critérios de aceitação

1. Em uma visita nova, a pessoa cai no Playground e consegue mover o chutador sem ler instruções extensas.
2. Alterar a posição do chute modifica distância/ângulo de forma geométrica coerente; os desenhos e os valores numéricos coincidem.
3. Arrastar goleiro ou defensor provoca mudança no xG **quando a feature correspondente existe no modelo**; a UI nunca sugere um efeito inexistente.
4. O valor fica entre 0 e 1; pênalti e estados inválidos seguem regra explícita; o sistema evita saltos absurdos por erro de coordenadas.
5. Os cinco presets carregam em ambos os idiomas e podem ser editados. O tutorial pode ser iniciado e interrompido sem reabrir o site.
6. Trocar idioma preserva cenário e modo, muda todos os textos e respeita a escolha em visitas seguintes; o idioma inicial segue preferência do navegador quando não há escolha salva.
7. A explicação indica que o resultado é uma estimativa e lista os fatores incluídos e ausentes. Descrições de mudanças são calculadas a partir das mesmas features da previsão.
8. O fluxo funciona com mouse e toque em larguras desktop e móvel; interações críticas têm alternativa acessível se o arrasto falhar.
9. README, atribuições e URL pública estão prontos para enviar a um comentarista ou recrutador.

## Pendências decididas pelo protótipo

- **Modelo:** reutilização licenciada ou regressão própria; registrar a escolha antes de publicar o valor.
- **Link de cenário:** desejável para comentaristas; entrar na v0.1 se couber após cálculo e acessibilidade. Senão, prioridade máxima no primeiro ajuste posterior.
- **Pênalti:** incluir preset visual já no campo; exibir xG apenas com tratamento metodologicamente compatível com o modelo escolhido.
- **Representação no mobile:** testar campo horizontal com enquadramento e toque antes de investir em uma versão vertical diferente.

## Depois da v0.1

**v0.2, conforme feedback:** links compartilháveis se não couberam antes; 3–5 gols históricos reconstruídos com fonte verificável, distinção entre posição observada e inferida, tipo de finalização e ausência de contextos não cobertos pelo modelo. Exemplos candidatos para pesquisar, ainda **não confirmados**: James Rodríguez em 2014, Van Persie em 2014, Ronaldinho em 2002.

**Mais tarde:** outras métricas como experimentos separados. Nenhum trabalho de xA, xThreat, portal de scout ou contas de usuário é dependência da primeira publicação.

## Ordem prática das primeiras tarefas

1. Criar app e geometria única do campo; desenhar gol, cone e peças.
2. Implementar drag por pointer events, limites e presets.
3. Provar pipeline `estado → features → modelo → xG` e documentar proveniência.
4. Adicionar leitura de variação sem inventar causalidade; tratar pênalti.
5. Fechar tradução, responsividade, Aprender e acessibilidade essencial.
6. Publicar, mostrar a usuários reais e registrar três melhorias prioritárias.
