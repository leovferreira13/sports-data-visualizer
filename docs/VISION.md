# Football, Visualized — visão do produto

**Status:** direção inicial · **Módulo inicial:** Expected Goals (xG) · **Atualizado:** 26/09/2026

## Ideia em uma frase

Um campo de futebol interativo em que qualquer pessoa move o chutador, o goleiro e os defensores para explorar como a situação de um chute altera sua probabilidade estimada de virar gol.

## Problema e público

O xG aparece em transmissões e análises como um número pronto. Para quem acompanha futebol, é difícil enxergar quais características da chance influenciaram a estimativa e por que duas chances aparentemente parecidas recebem valores diferentes. Comentadores e criadores de conteúdo também precisam montar um lance e explicá-lo rapidamente ao público.

O primeiro público é o fã curioso de futebol; o segundo é o analista, jornalista ou comentarista que quer **demonstrar** uma situação de jogo. A experiência deve funcionar sem conhecimento estatístico, cadastro ou leitura prévia.

## Proposta

**Playground é a tela inicial.** A pessoa encontra um lance já montado, o valor de xG em destaque e uma instrução curta: “Arraste os jogadores para testar outra situação”. Pode trocar de cenário, mover os elementos e entender quais fatores observáveis mudaram. Um controle discreto abre **Aprender**, que conduz uma explicação interativa usando o mesmo campo, sem sair para uma página teórica.

Nome de trabalho: **Football, Visualized**. Mensagem de produto: **Move os jogadores. Entenda o que muda uma chance de gol.** O nome não pressupõe a construção de um portal na primeira versão.

## Experiência principal

1. Abrir o site no idioma sugerido pelo navegador: português do Brasil ou inglês. O seletor no topo permite trocar a qualquer momento.
2. Ver uma jogada inicial com chutador, goleiro, dois defensores, gol, valor estimado e uma frase de contexto.
3. Arrastar um jogador; o campo, os indicadores e a estimativa respondem durante ou logo após o movimento.
4. Escolher um preset — **Pênalti, Cara a cara, Ângulo fechado, Chute de longe, Área congestionada** — e modificar sua configuração.
5. Alternar para **Aprender** para seguir pequenos desafios, como afastar um defensor da linha do chute e observar o que mudou.
6. Copiar o link da situação para mostrar a outra pessoa, se essa capacidade passar no orçamento da primeira entrega; no mínimo, os presets devem ser reproduzíveis.

O painel mostra **distância**, **ângulo de finalização** e **posição dos adversários/goleiro**. Sua explicação deve distinguir observações geométricas (“um defensor está no cone do chute”) de efeitos calculados pelo modelo (“nesta estimativa, retirá-lo elevou o valor em 0,04”). Nunca apresentar o movimento como causa garantida de um gol.

## Dois modos, uma única simulação

| Modo | Objetivo | Comportamento |
| --- | --- | --- |
| **Playground — padrão** | Montar e demonstrar lances livremente | Campo editável, presets, estimativa, indicadores e explicações curtas. |
| **Aprender** | Entender xG na prática | Passos opcionais e curtos que propõem uma mudança no campo, mostram o antes/depois e devolvem o controle livre. |

O modo Aprender usa as mesmas regras, o mesmo cálculo e os mesmos controles do Playground; a pessoa pode abandoná-lo sem perder a situação que montou.

## Princípios de produto

- **Mostrar antes de explicar:** o campo utilizável aparece sem onboarding obrigatório.
- **Número com contexto:** indicar qual modelo gera o xG, o que ele usa e o que deixa de fora. “0,20 xG” significa aproximadamente 20 gols em 100 chutes comparáveis segundo aquele modelo, não a probabilidade de um jogador específico marcar.
- **Explicação honesta:** variações da previsão são comparações dentro do modelo, não afirmações causais sobre o futebol real. Um fator visível não deve ser descrito como parte do cálculo se não o for.
- **Experiência de demonstração:** leitura rápida, área de campo generosa, movimento fluido e boa apresentação em celular e desktop.
- **Pequeno e concluído:** primeira publicação é um módulo de xG, não um portal de scout.
- **Bilinguismo desde o início:** interface, textos explicativos e indicação das limitações em `pt-BR` e `en`.

## O que define sucesso

**Meta de produto:** alguém que nunca estudou xG consegue montar uma chance e dizer, em palavras próprias, por que o modelo a avaliou daquela maneira. **Meta de entrega:** uma URL pública e um repositório público utilizáveis como peça de portfólio.

Na primeira rodada, testar com 5–8 pessoas, incluindo pelo menos um criador ou comentarista. Observar: conseguem interagir sem instrução oral? Entendem que o número é uma estimativa de modelo? Conseguem reconstruir um lance e explicar a mudança? Registraremos feedback qualitativo e falhas mais frequentes; analytics de produto são opcionais. Um resultado inicial bom é a maioria completar a primeira interação e explicar ao menos uma mudança com precisão, sem depender de uma meta estatística artificial para uma amostra pequena.

## Limites da primeira versão

Um chutador, um goleiro, até três defensores, cinco presets, dois modos e dois idiomas. Sem contas, banco, backend obrigatório, times, partidas em tempo real, editor tático, outros tipos de estatística ou IA generativa. Gols famosos vêm **depois da validação**: recriar um lance histórico exigirá fonte confiável para posições e contexto do chute; qualquer aproximação será identificada como reconstrução ilustrativa.

## Evolução possível

Se o módulo funcionar bem, manter a marca como guarda-chuva para experimentos independentes: gols famosos, xA, xThreat ou outras visualizações. A adição de um módulo dependerá de uso e aprendizado do primeiro, não de uma arquitetura preparada antecipadamente para vários produtos.
