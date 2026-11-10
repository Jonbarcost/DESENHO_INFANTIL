"""Create delivery records only after the movie and additional QA are validated."""
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    out=ROOT/'EPISODIO_02/ARTEFATOS';reports=ROOT/'EPISODIO_02/RELATORIOS';movie=out/'episodio_02_final.mp4'
    validation=json.loads((out/'validation.json').read_text())
    if not validation.get('completed') or hashlib.sha256(movie.read_bytes()).hexdigest()!=validation['sha256']:
        raise ValueError('Filme ausente, alterado ou não validado')
    lip=json.loads((out/'lip-sync-validation.json').read_text())
    motion=json.loads((out/'motion-report.json').read_text())
    tests=(out/'tests-continuacao.log').read_text();count=int(re.findall(r'Ran (\d+) tests',tests)[-1])
    if not lip['passed'] or 'OK' not in tests or count<22:raise ValueError('Verificações adicionais pendentes')
    timeline=json.loads((out/'timeline.json').read_text());levels=json.loads((out/'audio-report.json').read_text())
    import sys
    sys.path.insert(0,str(ROOT))
    from producao.serie.pipeline import preserve
    preserved=preserve(reports/'preservacao-inicial.json')
    status=json.loads((reports/'STATUS.json').read_text())
    status.update(completed=True,blocker=None,phase='validated',actual_duration=validation['duration'],
        actual_frames=validation['frames'],valid_new_voices=validation['speech_count'],full_render=True,
        final_mix=True,final_mp4=True,tests_passed=count,preserved_files=preserved,published=False,
        video_sha256=validation['sha256'],voice_backend='kokoro-local-pt-br',windows_native_test=False)
    (reports/'STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2))
    (out/'status.json').write_text(json.dumps(dict(completed=True,stage='validated',sha256=validation['sha256']),indent=2))
    for source,target in [('validation.json','validacao-final.json'),('scene-qa.json','cena-final-qa.json'),
                          ('lip-sync-validation.json','sincronismo-final.json'),('motion-report.json','movimento-final.json'),
                          ('estimate.json','estimativa-render-real.json')]:
        (reports/target).write_bytes((out/source).read_bytes())
    (out/'SHA256SUMS').write_text(f"{validation['sha256']}  episodio_02_final.mp4\n")
    seconds=validation['duration'];minimum=min(x['voice_background_db'] for x in levels['speech_background'])
    text=f'''# Episódio 02 — O Mistério da Borboleta Azul

**Produção concluída e validada. Nada publicado no YouTube.**

- [MP4 final](ARTEFATOS/episodio_02_final.mp4): {int(seconds//60)}min{seconds%60:05.2f}s,
  1920×1080 nativo, 16:9, 12 fps, {validation['frames']} quadros, H.264/AAC estéreo.
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

- {count} testes aprovados, incluindo montagem real por FFmpeg, cache de voz,
  integridade de modelos e trava de promoção de candidato validado.
- Todos os {validation['frames']} PNGs foram conferidos na montagem; MP4 inteiramente decodificado.
- {motion['shots']} tomadas com variação visual medida dentro de cada plano, sem contar cortes.
- {lip['dialogue_checks']} falas dos personagens com boca comparada à energia dos MP3 reais;
  correlação mínima {lip['minimum_correlation']:.3f}. Narração não exige boca em cena.
- Volume final: {validation['loudness']['input_i']} LUFS e pico {validation['loudness']['input_tp']} dBTP.
  Voz/fundo RMS mínimo por fala antes da masterização: {minimum:.2f} dB.
- Detecção de preto/congelamento passou. Fades intencionais de cena foram mantidos.
- {preserved} arquivos anteriores conferidos por SHA-256, incluindo entrega e renders do Episódio 01.
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
EPISODIO_02\\produzir_windows.cmd
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
'''
    (ROOT/'EPISODIO_02/README.md').write_text(text,encoding='utf-8')
    delivery=f'''# Entrega validada — Episódio 02

Arquivo: ARTEFATOS/episodio_02_final.mp4 ({movie.stat().st_size/1024/1024:.2f} MiB).
Duração {seconds:.6f} s; {validation['frames']} quadros; 1080p nativo; 12 fps; H.264/AAC.
44 falas com Kokoro pt-BR local, música/efeitos originais, SRT/MOV text em português.

SHA-256: `{validation['sha256']}`

{count} testes aprovados. Decodificação integral, formatos, duração, quantidade de
quadros, áudio e detecção de preto/congelamento passaram. {motion['shots']} tomadas
com movimento medido. Sincronismo de energia nas {lip['dialogue_checks']} falas dos
personagens, correlação mínima {lip['minimum_correlation']:.6f}.

Volume {validation['loudness']['input_i']} LUFS, pico verdadeiro {validation['loudness']['input_tp']} dBTP.
Verificados {preserved} hashes de recursos anteriores. Nenhuma publicação ou serviço pago.
Vozes alternativas autorizadas; identidade vocal Microsoft não foi reproduzida.
Comando Windows e pacote portátil preparados; execução nativa Windows não testada.

Os registros anteriores de bloqueio/plano/teste silencioso são históricos. A decisão
de conclusão se baseia em validacao-final.json, no SHA-256 do filme e nos arquivos reais.
'''
    (reports/'ENTREGA.md').write_text(delivery,encoding='utf-8')
    print('DELIVERY_RECORDED',seconds,validation['frames'],count,preserved,flush=True)


if __name__=='__main__':main()
