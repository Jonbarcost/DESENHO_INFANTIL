# Registro de execução

Plano: `superpowers/plans/2026-11-10-episodio-01.md`.

- Auditoria completa: 42 originais, 6 cenas Blender abertas, 25 MP3 medidos,
  dependências externas de imagem ausentes. Inventário e hashes preservados.
- Timeline implementada e testada: 12 falas sem sobreposição, 0,6 s entre falas,
  4 s de plantio e 8 s de cuidados; 69,25 s, 831 quadros.
- Direção definida pelo agente dentro da autonomia solicitada: derivar personagens.blend,
  sem substituir modelos. Canção instrumental com versos visuais e despedida com acenos,
  pois faltam gravações coletivas. Custo artístico: não há coro cantado nesta versão.
- Benchmark: Cycles 1080p/16 amostras 21,3 s/quadro, EEVEE software 34,2 s;
  decisão: Workbench de estúdio 1080p/AA8 para tornar possível o render completo em CPU.
  Custo artístico: luz de estúdio sem ray tracing/volumetria; magia feita com estrelas coloridas.
- Revisão visual de cinco poses identificou sombras artificiais e plantio oculto.
  Ajustes na nova cena: iluminação mais limpa, semente à frente do personagem,
  patch de terra e flor à frente, Teco se aproxima durante a rega.
- Música/SFX criados por síntese local determinística; nenhuma gravação externa adicionada.
  A música existente foi preservada, mas não usada por falta de documentação de licença.
- Revisão independente dos scripts concluída: lacuna na validação de loudness identificada.
  Corrigida com teste que rejeita pico acima de -1 dBTP, loudness fora de -18…-14 LUFS,
  medições ausentes e valores não finitos. Suíte: 7 testes aprovados.
- Proteção de retomada ampliada para detectar edições manuais na cena/timeline, além
  de assinaturas de configuração e CRC de cada PNG; teste de corrupção e truncamento aprovado.
- Validação da cena baked: os três personagens têm movimento de corpo/cabeça/braço/boca;
  a semente desce de aproximadamente 1,01 a -0,12 unidades, a flor cresce de escala
  0,001 a 1 no intervalo programado e há 14 tomadas de câmera.
- Inspeção do plantio em sequência revelou que a semente passava à frente do rosto
  durante a aproximação. Corrigida para acompanhar a mão. Comparação entre cenas
  verificou geometria orientada, materiais, configuração, câmera e matrizes mundiais:
  somente quadros 367–418 mudaram. Os demais podem ser reutilizados após validação;
  os 52 quadros afetados são renderizados novamente em uma revisão separada.
- A folha de contato das 14 tomadas revelou a flor encobrindo Maya em sua última
  fala. Câmera reposicionada para o lado esquerdo, mantendo boca e olhos visíveis.
  Comparação de geometria/poses e projeção da câmera por quadro identificou somente
  o intervalo 649–703 como afetado; esses 55 quadros foram selecionados para novo render.
- Render, montagem e validação final concluídos: 831 quadros, 69,25 s, MP4 1080p, decodificação integral, 14 tomadas com movimento, 7 testes e 42 hashes de originais aprovados. Resultados em ENTREGA_EPISODIO_01.md.

Não houve publicação, push ou envio de materiais a terceiros.
