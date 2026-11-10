# Episódio 04 — A Viagem da Gotinha

Desenho infantil educativo em português brasileiro, com Capi, Teco e Maya, explicando evaporação, condensação e chuva. A história tem perguntas com pausas reais, brincadeira da chuva e dança com refrão falado sobre música original alegre a 112 BPM.

## Produzir e retomar

Na raiz do projeto, com Blender 4.3.2, FFmpeg e Python 3.12:

```sh
python -m producao.gotinha EPISODIO_04/ROTEIRO/roteiro.json --tts kokoro
```

Reutiliza o ambiente gratuito `build/tts-local` e os modelos verificados de `build/tts-models`. Perfis de voz do Episódio 03, com referências Microsoft preservadas no roteiro; Kokoro usa timbres alternativos, não clones. Licenças e hashes dos modelos em EPISODIO_02/RELATORIOS/VOZES_LOCAIS.md.

Windows: `EPISODIO_04\produzir_windows.cmd`. O lançador prepara dependências e modelos gratuitos com verificação HTTPS/SHA; requer Blender 4.3.x e FFmpeg instalados. Sem teste nativo no Windows. A partir do pacote editável, use `EPISODIO_04\produzir_windows.cmd --output EPISODIO_04/RENDER_WINDOWS` para gerar novamente masters e PNGs.

Etapas: `--stage voices|prepare|render|assemble|verify`. Retoma quadros válidos. Não altere fontes/cena/áudios de um render em curso; use nova saída para uma versão nova. Pastas dos três episódios anteriores são protegidas. Não há upload para o YouTube.

## Reutilização e edição

Malhas originais de personagens/clareira/árvores e bibliotecas compactas extraídas das flores do Ep02 e riacho do Ep03. Origem e hashes em ASSETS/origem.json. Esses arquivos pequenos permitem reproduzir a cena sem depender dos renders antigos.

A cena Blender contém animação em curvas editáveis. Vozes individuais, música e efeitos ficam em arquivos externos; montagem e mixagem são feitas pelo FFmpeg. O ZIP inclui esses recursos e exclui duplicatas de master e PNGs, que o comando regenera.

## Conteúdo educativo

Vapor de água é invisível. Setas e gotinha com rosto são representações imaginárias, rotuladas no vídeo. Nuvens são formadas por gotículas e/ou cristais de gelo. Evaporação não exige fervura. Chuva aparece após crescimento das gotas. O ciclo é apresentado em sequência simplificada; os caminhos da água variam na natureza.

As brincadeiras podem ser feitas no lugar, com espaço e cuidado. Personagens observam a chuva abrigados, como informa a narração, antes de voltar à clareira. A chuva no solo só aparece depois desse retorno narrado. Não há tempestade nem aproximação do riacho.

O gancho do próximo episódio é o canto dos pássaros: observar sons e cuidar dos animais sem capturá-los.
