# Episódio 02 — O Mistério da Borboleta Azul

**Produção concluída e validada. Nada publicado no YouTube.**

- [MP4 final](ARTEFATOS/episodio_02_final.mp4): 3min44.58s,
  1920×1080 nativo, 16:9, 12 fps, 2695 quadros, H.264/AAC estéreo.
- [Cena Blender editável](ARTEFATOS/episodio_02_final.blend).
- [Roteiro completo](ROTEIRO/roteiro.md) e [fonte JSON](ROTEIRO/roteiro.json), 44 falas.
- Áudios individuais: ARTEFATOS/VOZES/kokoro/ (MP3, WAV de origem e metadados assinados).
- Música, efeitos, diálogos separados e master: ARTEFATOS/*.wav.
- Legendas: [SRT](ARTEFATOS/legendas.srt), também incluídas como faixa no MP4.
- [Relatório final](RELATORIOS/ENTREGA.md), [status](RELATORIOS/STATUS.json)
  e [metadados para YouTube](youtube.json).

## Vozes e recursos preservados

O Edge TTS permaneceu bloqueado por HTTP 403. A alternativa gratuita autorizada foi
Kokoro ONNX, com fonetização pt-br e inferência local. As vozes masculinas/femininas,
velocidades relativas e alturas foram diferenciadas para Capi, Teco, Maya e narradora.
**A identidade vocal difere da Microsoft.** Os perfis Edge aprovados e todos os
materiais do Episódio 01 continuam preservados. Detalhes, licenças e checksums dos
modelos em [VOZES_LOCAIS.md](RELATORIOS/VOZES_LOCAIS.md).

O roteiro, cenário, modelos e planejamento anteriores foram aproveitados. A cena
final usa durações reais das falas. Uma correção pontual baixou o voo no jardim para
manter o rosto de Maya visível, sem reconstruir personagens ou descartar quadros equivalentes.

## Evidências da entrega

- 22 testes aprovados, incluindo montagem real por FFmpeg, cache de voz,
  integridade de modelos e trava de promoção de candidato validado.
- Todos os 2695 PNGs foram conferidos na montagem; MP4 inteiramente decodificado.
- 51 tomadas com variação visual medida dentro de cada plano, sem contar cortes.
- 37 falas dos personagens com boca comparada à energia dos MP3 reais;
  correlação mínima 0.955. Narração não exige boca em cena.
- Volume final: -16.60 LUFS e pico -1.43 dBTP.
  Voz/fundo RMS mínimo por fala antes da masterização: 23.58 dB.
- Detecção de preto/congelamento passou. Fades intencionais de cena foram mantidos.
- 940 arquivos anteriores conferidos por SHA-256, incluindo entrega e renders do Episódio 01.
- Arquivo candidato recebeu o nome final somente depois das verificações e preservação.

A boca é sincronizada aproximadamente pela energia da voz; não há análise fonética
de visemas. A imagem usa Workbench de estúdio em CPU, sem iluminação volumétrica.
O planejamento e o teste antigo sem vozes continuam disponíveis como histórico,
separados da entrega final.

## Reexecutar sem refazer trabalho concluído

Linux, na raiz do projeto:

```bash
python3 -m producao.serie EPISODIO_02/ROTEIRO/roteiro.json --tts kokoro
```

Com filme validado, hashes e configuração idênticos, o comando confirma a entrega
e encerra sem gerar vozes ou renderizar novamente. Em produção interrompida, o cache
e os PNGs íntegros são reaproveitados por lotes. Para mudar texto, provedor ou aparência,
use uma nova pasta, por exemplo `--output EPISODIO_02/ARTEFATOS_V2`.

Windows, com Python 3.12, Blender 4.3.x e FFmpeg instalados:

```bat
EPISODIO_02\produzir_windows.cmd
```

O lançador cria um venv próprio, instala dependências gratuitas e verifica os modelos
oficiais por SHA-256. Reconhece uma entrega validada já transferida e evita refazer as
etapas. Não enfraquece TLS/política de execução, não usa API paga e não publica vídeos.
Execução nativa Windows foi preparada, mas não testada neste ambiente Linux.

Pacote de transferência: build/Clareira_Episodio02_Windows.zip. Contém fontes do projeto,
filme, cena editável e áudios; omite venvs e os volumosos PNGs. Modelos podem ser obtidos
automaticamente pelo lançador quando forem necessários. O pacote só é gerado após validação.

## Produzir o Episódio 03

Copie ROTEIRO/roteiro.json para EPISODIO_03/ROTEIRO/roteiro.json e altere episode para
03, título, diálogos e IDs únicos. O orquestrador, vozes/cache, timeline, áudio, render
e QA são reutilizáveis. O builder atual usa os sete modos intro/discovery/chase/
investigate/garden/care/finale e os elementos de borboleta/jardim. Para outro tema,
adapte os elementos específicos em producao/serie/cena.py e os efeitos em audio.py.
Isso preserva modelos e pipeline; não promete encenar automaticamente qualquer enredo.

Revise um layout, depois execute:

```bash
python3 -m producao.serie EPISODIO_03/ROTEIRO/roteiro.json --tts kokoro
```

Para a voz Microsoft original, quando a rede permitir, use --tts edge numa nova pasta.
A publicação permanece fora do pipeline e depende de autorização específica.
