> Histórico da auditoria inicial. A continuação usou síntese local autorizada e concluiu a entrega; consulte ENTREGA.md e STATUS.json.

# Auditoria — Episódio 02

2026-11-10. Base de trabalho: bf0a17a. Episódio 01 e seus arquivos gerados são
somente leitura nesta produção; preservação verificada pelo manifesto SHA-256
`preservacao-inicial.json`, incluindo MP4, cena editável, vozes, renders e scripts.

Reutilização: seis projetos Blender em EPISODIO_01/CENAS, Capi/Teco/Maya completos
em personagens.blend, clareira/árvores/flores/pedras, 25 arquivos MP3 incluindo
testes/cópias/mixagens. Inventário detalhado anterior permanece válido em
docs/auditoria. O pipeline e as funções de rig, malha, render retomável, legendas,
validação de PNG e loudness do Episódio 01 serão importados sem alterar seus arquivos.

Ambiente: Blender 4.3.2, FFmpeg/ffprobe 7.1.5, Python 3.12, NumPy 2.3.5,
Pillow 13.0.0, edge-tts 7.2.7 em .venv. Quatro CPUs efetivas, aproximadamente
58 GB livres no início. Sem GPU de render disponível; EEVEE anterior usou software.

Bloqueio confirmado: HTTPS para speech.platform.bing.com retornou HTTP 403 no
proxy. Tentativa real edge_tts.Communicate com AntônioNeural e configurações de
Capi também falhou com ClientHttpProxyError 403, antes de gerar áudio. Nenhuma
credencial adicional é exigida pelo cliente atual. Não há vozes novas disponíveis.
O leitor de configuração do ambiente retornou INVALID_ARGUMENT em duas tentativas;
nenhuma alteração de rede foi salva ou aplicada. É necessário liberar o domínio
nas configurações do ambiente; não desabilitar TLS nem contornar o bloqueio.

As configurações de voz serão preservadas literalmente. Não usar outra voz,
reaproveitar falas sem relação com a história ou gerar silêncio como áudio final.
Sem as vozes, apenas o layout com tempos estimados e um teste visual curto podem
ser renderizados honestamente. O pipeline final deve abortar antes do render longo
se faltar qualquer gravação válida.
