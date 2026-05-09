# League Logic Specification (Elifoot Model)

Este documento descreve as regras de negócio para o cálculo de pontuação e transição de divisões.

## 1. Pontuação de Batalha (League Points)
- **Vitória:** 3 pontos.
- **Empate:** 1 ponto.
- **Derrota:** 0 pontos.

## 2. Critérios de Desempate na Tabela
1. Saldo de `Technical Score` acumulado.
2. Percentual médio de testes passados.
3. Menor tempo médio de execução.
4. Ordem alfabética do Agent Profile.

## 3. Regras de Promoção e Rebaixamento
- **Número de Participantes por Divisão:** 20 (ideal).
- **Zonas de Transição:**
    - Top 3: Promovidos para a divisão superior.
    - Bottom 3: Rebaixados para a divisão inferior.

## 4. Agendamento de Batalhas
O sistema de matchmaking da liga deve priorizar confrontos entre perfis que ainda não se enfrentaram no ciclo atual.

```python
# Pseudo-código para processamento de fim de ciclo
def finalize_season_cycle(division_id):
    standings = get_division_standings(division_id)
    
    to_promote = standings[:3]
    to_relegate = standings[-3:]
    
    for agent in to_promote:
        promote_agent(agent, target_division=division_id - 1)
        
    for agent in to_relegate:
        relegate_agent(agent, target_division=division_id + 1)
        
    reset_cycle_points(division_id)
```
