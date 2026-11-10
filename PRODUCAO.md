# Produzir A Sementinha Mágica

Os arquivos anteriores continuam intactos. A nova produção está em `producao/` e
gera todos os resultados em `build/episodio_01/`, ignorado pelo Git. A cena derivada
é `episodio_01_final.blend`; a entrega é `episodio_01_final.mp4`.

## Ferramentas

Ambiente validado: Blender 4.3.2, FFmpeg/ffprobe 7.1.5, Python 3.12 com NumPy 2.3.5
e Pillow para inspeção visual. Os scripts antigos não precisam ser executados.
Nenhuma chave de API, acesso a serviço de voz ou download de mídia é necessário.
Blender deve usar sua própria versão de Python para `animacao.py` e `render.py`;
os demais comandos usam `python3` do ambiente, que já inclui NumPy.

Se instalar dependências em outro computador, crie um ambiente virtual e instale
`numpy==2.3.5` e `Pillow==13.0.0` (Pillow é usado apenas pelo relatório visual).
As versões estão em `producao/requirements.txt` para instalação com pip.
Instale Blender/FFmpeg pelos canais oficiais, preservando verificações TLS e de
integridade. A fonte usada nas cartelas é DejaVu Sans Bold, incluída na distribuição
Linux em `/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf`.

## Execução

Na raiz deste repositório:

```bash
python3 -m unittest discover -s tests -v
python3 -m producao.pipeline --stage all
```

Etapas separadas, úteis para diagnóstico e retomada:

```bash
python3 -m producao.pipeline --stage prepare
python3 -m producao.pipeline --stage render
python3 -m producao.pipeline --stage assemble
python3 -m producao.pipeline --stage verify
python3 -m producao.qa
blender -b build/episodio_01/episodio_01_final.blend --python-exit-code 1 --python producao/qa_blender.py -- "$(pwd)/build/episodio_01"
```

Render parcial: `--stage render --start 1 --end 120`. Rodar novamente renderiza
somente quadros ausentes ou com PNG/CRC incompleto. A assinatura inclui a cena fonte,
as vozes, os scripts que determinam quadros e a configuração. Se mudar esses
elementos, use uma nova pasta com `--output build/outra-versao` para não misturar
quadros antigos. A assinatura também confere a cena derivada e a timeline, para
detectar edições manuais antes de retomar. Cada quadro e o MP4 final são publicados por rename depois de
escritos; um processo interrompido não transforma um arquivo parcial em entrega.

Padrão: **1920×1080 nativo, 16:9, 12 fps**, Workbench, H.264 CRF18, AAC 192 kb/s,
48 kHz, yuv420p e faststart. Os 12 fps são quadros de animação distintos, sem
repetir um pequeno vídeo nem ampliar imagens de baixa resolução. Para uma prévia
mais barata, `--width 480 --output build/previa`. Para render alternativo com
traçado de raios, `--engine CYCLES --samples 16 --output build/cycles` (muito mais lento).

A máquina dispõe de quatro CPUs efetivas; o pipeline usa quatro threads. O render
final de estúdio mediu aproximadamente 0,7–0,8 s/quadro após inicialização, antes de
outras tarefas concorrentes. Reserve cerca de 15 minutos e 2 GB para quadros,
mixagens, cenas e exportação; o tempo real depende da carga do ambiente.

## Arquivos gerados

- `timeline.json`: falas, tempos, envelopes de energia e eventos narrativos.
- `shots.json`: cortes e câmeras de cada tomada.
- `episodio_01_final.blend`: animação baked, editável sem handlers/scripts externos.
- `frames/0001.png` … `0831.png`: sequência completa em resolução nativa.
- `dialogos.wav`, `musica_original.wav`, `efeitos_originais.wav`: stems de áudio.
- `master.wav`: mixagem normalizada, com música reduzida durante diálogos.
- `legendas.srt`: 12 falas em português; também incluídas como faixa selecionável no MP4.
- `episodio_01_final.mp4`: filme montado com cartelas, versos visuais e fades.
- `validation.json`, `loudness.log`, `decode.log`: resultados de validação da exportação.
- `animation-report.json`: amplitudes de movimento dos controles e checagem dos eventos.
- `motion-report.json`, `storyboard-final.jpg`: diferenças visuais dentro das 14 tomadas e folha de contato.

Os WAV separados facilitam remixagem sem perda. A validação confere codecs, tamanho,
duração, cadência, quantidade de quadros, decodificação integral e hashes dos 42
arquivos originais. A medição EBU R128 fica em loudness.log; objetivo -16 LUFS e
pico verdadeiro de até -1,5 dBTP antes da codificação AAC. A aprovação da exportação
exige volume entre -18 e -14 LUFS e pico verdadeiro máximo de -1 dBTP, incluindo
eventual overshoot da codificação AAC; valores não finitos também são reprovados.

## Direção e limites desta versão

A semente flutua perto de Capi, ele se aproxima para plantar, Teco rega e os três
acompanham o crescimento. Braços, passos, troncos, cabeças, olhos e bocas têm
animação independente, com gestos durante as falas, reações e acenos finais.
As câmeras alternam planos gerais, interlocutores e detalhes, com dolly suave.

A boca usa a energia da gravação, sem análise fonética; personagens simples mantêm
o desenho original. Não há novas vozes coletivas: versos são visuais durante a
música, e a despedida é feita com acenos. A trilha antiga e todas as mixagens
anteriores continuam disponíveis; consulte [a auditoria](docs/AUDITORIA_EPISODIO_01.md)
para proveniência e limitações. Nada é enviado ao YouTube pelo pipeline.
