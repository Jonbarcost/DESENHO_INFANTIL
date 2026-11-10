# Episódio 02 — O Mistério da Borboleta Azul

**Status: produção final bloqueada pela geração das vozes. Não existe MP4 final
deste episódio.** O teste visual disponível é curto, sem vozes e identificado como
planejamento; não deve ser confundido com a entrega solicitada.

O serviço Edge TTS em `speech.platform.bing.com` respondeu **HTTP 403 no proxy**,
tanto na consulta HTTPS quanto em uma tentativa real de síntese. As quatro vozes
solicitadas foram mantidas na configuração, sem substituição. O acesso ao domínio
precisa ser liberado nas configurações de rede deste ambiente, incluindo HTTPS/WSS
na porta 443. Não é necessário fornecer senha/token em chat. Não foi possível
salvar essa alteração: o leitor de configurações retornou INVALID_ARGUMENT duas
vezes. Nenhuma mudança de rede foi aplicada.

## Trabalho já executado

- Roteiro completo: [ROTEIRO/roteiro.md](ROTEIRO/roteiro.md), 44 falas em sete cenas.
- Fonte estruturada: [ROTEIRO/roteiro.json](ROTEIRO/roteiro.json).
- Layout editável: `ARTEFATOS/episodio_02_planejamento.blend`, 2.638 quadros,
  219,83 s estimados a 12 fps. A duração será recalculada a partir dos MP3 reais.
- Personagens e cenário originais reutilizados; marcha com pés/braços alternados,
  tropeço leve, asas articuladas, trajetória da borboleta, rega e jardim animados.
- 51 tomadas planejadas; os três personagens e a borboleta foram detectados nas
  sete sequências por checagem de projeção da câmera. Isso não substitui inspeção
  de oclusão de todos os quadros, ainda pendente com a timeline real.
- Música e efeitos originais por síntese local em `ARTEFATOS/MUSICA_PLANEJAMENTO/`.
- Teste de 48 quadros/4 s em `ARTEFATOS/TESTE/teste_visual_sem_vozes.mp4`, exportado
  em 1280×720 a partir de quadros 1080p. Decodificação completa e movimento medidos.
- Auditoria, hashes de preservação, benchmark e testes em `RELATORIOS/` e `ARTEFATOS/`.
- Título, descrição, palavras-chave e classificação infantil: [youtube.json](youtube.json).

Os WAVs atuais são trilhas de planejamento. Não há novas falas, master final,
timeline medida ou exportação final. A boca depende da energia das novas vozes;
no layout provisório ela não representa sincronização validada.

## Retomar a produção completa

Na raiz do repositório, depois de liberar o serviço de voz:

```bash
python3 -m producao.serie EPISODIO_02/ROTEIRO/roteiro.json
```

O pipeline utiliza o Python atual e, quando necessário, `.venv/bin/python` para o
worker Edge TTS já instalado. Em outro ambiente, instale as dependências num venv:

```bash
python3 -m pip install -r producao/serie/requirements.txt
```

Blender 4.3.2 e FFmpeg/ffprobe 7.1.5 devem estar no PATH. A fonte DejaVu Sans Bold
deve existir em `/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf`.

O comando gera/cacheia vozes, mede suas durações, recalcula a timeline, cria a cena,
mixagem/legendas, estima custo num primeiro lote reaproveitado, renderiza em lotes,
monta e valida o MP4. **Não publica.** A geração falha antes do render final se faltar
qualquer gravação, sem fabricar silêncio ou reutilizar falas alheias à história.

Etapas independentes:

```bash
python3 -m producao.serie EPISODIO_02/ROTEIRO/roteiro.json --stage voices
python3 -m producao.serie EPISODIO_02/ROTEIRO/roteiro.json --stage prepare
python3 -m producao.serie EPISODIO_02/ROTEIRO/roteiro.json --stage render --batch 120
python3 -m producao.serie EPISODIO_02/ROTEIRO/roteiro.json --stage assemble
python3 -m producao.serie EPISODIO_02/ROTEIRO/roteiro.json --stage verify
```

Render parcial: `--stage render --start 1 --end 240`. PNGs válidos são reutilizados;
arquivos parciais/corrompidos são refeitos. Texto ou perfil alterados invalidam cache
de voz. Código, roteiro, MP3, cena, master, legendas ou metadados de mixagem alterados
invalidam a assinatura final: use nova pasta `--output EPISODIO_02/ARTEFATOS_V2`.
Saídas fora do repositório ou dentro do Episódio 01 são rejeitadas antes de iniciar.
Se apenas interromper, execute novamente o comando principal; ele retoma a configuração
válida, sem reconstruir a cena nem refazer quadros concluídos.

Etapas provisórias, separadas do fluxo final:

```bash
python3 -m producao.serie EPISODIO_02/ROTEIRO/roteiro.json --stage layout
python3 -m producao.serie EPISODIO_02/ROTEIRO/roteiro.json --stage music
python3 -m producao.serie EPISODIO_02/ROTEIRO/roteiro.json --stage benchmark
python3 -m producao.serie EPISODIO_02/ROTEIRO/roteiro.json --stage preview
```

O benchmark já foi executado; não há motivo para repeti-lo nesta máquina sem mudança
de hardware/configuração. Workbench: 0,72 s/quadro em duas amostras 1080p após warmup;
estimativa de **31,7 minutos** para a timeline provisória, mais montagem e validação.
Eevee: 20,6 s numa única amostra 480×270 incluindo inicialização/compilação em software;
essa amostra não permite uma estimativa confiável de custo integral. Workbench foi
selecionado para o ambiente atual. Não houve render completo: a estimativa não é
evidência de execução. Reserve aproximadamente 6 GB para o render final em PNG.

Padrão final: quadros **1920×1080 nativos**, H.264/yuv420p, 12 fps, AAC estéreo,
48 kHz, legendas selecionáveis em português e faststart. `--width 1280` usa render
intermediário 720p com ampliação Lanczos para 1080p; informe a mesma largura ao
retomar etapas. Mudança de largura requer nova pasta de saída.

## O que a validação final exige

180–300 s, todos os MP3 assinados e presentes, duração de cada fala preservada,
ausência de sobreposição, todos os quadros íntegros, codecs/tamanho/cadência corretos,
decodificação integral e verificação de preto/congelamento. Música/efeitos são
atenuados para manter a voz pelo menos 12 dB acima do fundo em RMS por fala. A
saída deve estar entre -18 e -14 LUFS, com pico verdadeiro máximo de -1 dBTP.
Essas verificações finais estão implementadas, mas **a execução integral está
pendente** por falta das vozes. A revisão artística com áudio também permanece pendente.

## Preparar o Episódio 03

1. Crie `EPISODIO_03/ROTEIRO/roteiro.json` copiando o schema do episódio 02.
2. Altere `episode` para `03`, título, diálogos, IDs únicos e metadados de YouTube.
   As vozes ficam em `voices`; duração-alvo e resolução ficam no mesmo JSON.
3. O preset atual de animação é específico à borboleta/jardim e usa os sete modos
   `intro`, `discovery`, `chase`, `investigate`, `garden`, `care`, `finale`.
   Para uma história semelhante, mantenha esses modos e mude o roteiro. Para o
   gancho do riacho ou novos objetos, adapte o builder `producao/serie/cena.py` e os
   efeitos em `audio.py`; o orquestrador, TTS, cache, timeline e render são reutilizáveis.
   O evento de tropeço é uma marca `"event": "stumble"` opcional numa fala, sem
   depender da palavra exata do texto. Não há geração automática de qualquer enredo 3D.
4. Execute `python3 -m producao.serie EPISODIO_03/ROTEIRO/roteiro.json --stage layout`
   e revise poses/enquadramentos. Depois execute o mesmo comando sem `--stage`.
5. Rode a suíte `python3 -m unittest discover -s tests -v`. Não reaproveite MP3 ou
   PNGs de roteiro/perfil/configuração diferentes. Publicação continua sendo uma
   decisão externa ao pipeline.

O Episódio 01 não foi modificado. Os novos scripts estão em `producao/serie/`;
binários gerados ficam fora do Git em ARTEFATOS, mas permanecem no workspace.
