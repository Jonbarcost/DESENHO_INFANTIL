# Entrega — A Sementinha Mágica

Data: 2026-11-10. Produção concluída localmente, sem publicação ou push.

- Arquivo: `build/episodio_01/episodio_01_final.mp4` (16.42 MiB).
- Vídeo: H.264, 1920×1080 nativo, 16:9, yuv420p, 12 fps, 831 quadros.
- Duração: 69.25 segundos. Áudio: AAC estéreo, 48 kHz, 192 kb/s.
- Doze falas reutilizadas integralmente, com agenda compartilhada para áudio e movimentos.
- Quatorze tomadas; plantio, rega, crescimento, abertura da flor e acenos finais.
- Legendas em português: SRT e faixa selecionável no MP4.
- Música instrumental e efeitos sintetizados pelo código, sem samples externos.

## Evidências executadas

- 7 testes de timeline, arquivos ausentes, retomada, integridade da cena e loudness aprovados.
- Todos os 831 PNGs verificados por resolução, integridade CRC e terminador IEND.
- Decodificação integral do MP4 pelo FFmpeg, sem erro.
- ffprobe confirmou codecs, tamanho, cadência, quantidade de quadros e duração.
- Exportação medida: **-16.69 LUFS**, **-1.51 dBTP**, LRA 6.90 LU.
- Movimento visual medido dentro de todas as 14 tomadas, sem contar os cortes de câmera.
- Cena baked verificada: controles de corpo, cabeça, braços e boca animados nos três personagens;
  semente desce à terra e flor cresce no intervalo previsto. Inspeção de poses e da folha de contato.
- Retomada executada nos quadros 1–12: imagens válidas reaproveitadas.
- **42 arquivos originais intactos**, comparados aos hashes da auditoria inicial.
- Revisão independente identificou validação de loudness incompleta; corrigida e coberta por teste.
- Revisões visuais corrigiram a trajetória da semente e a câmera da última fala de Maya.

SHA-256 do MP4:
`8b6a6dc7d4cd970e8873979bdbc39aa542cca1f79665fcd618d28da0e0cb8c5d`

Relatórios completos, WAVs separados, folha de contato, cena editável e sequência PNG ficam em
`build/episodio_01/`. Auditoria e scripts estão versionados; binários gerados ficam fora do Git.
Backups locais das duas revisões anteriores foram preservados em `build/`.

## Limites artísticos e material preservado

A canção foi realizada como instrumental com os versos na tela, pois não havia coro gravado.
A despedida coletiva é visual. A boca acompanha energia da voz, sem sincronização fonética.
O render usa iluminação de estúdio Workbench, sem ray tracing ou luz volumétrica. A trilha antiga,
as mixagens, as vozes, os modelos e as cenas anteriores estão preservados sem sobrescrita.
Não se presumiu licença da música existente: ela não foi incluída no filme final.

Para reproduzir ou aprimorar: veja `PRODUCAO.md` e `docs/AUDITORIA_EPISODIO_01.md`.
