# Auditoria — Clareira dos Curiosos

Data: 2026-11-10. Base: commit `ba4eeeedbe0555e1c3d9acb2a42bef080ef3aaf4`.
Inventário antes das alterações: **42 arquivos**, com SHA-256 em
[auditoria/ativos-originais.json](auditoria/ativos-originais.json).
Nenhum arquivo de produção original foi sobrescrito.

## Recursos encontrados

| Recurso | Conteúdo e condição |
|---|---|
| `clareira_3d.blend` | 14 objetos; 48 quadros a 12 fps; clareira, árvores, semente, iluminação e câmera |
| `clareira_3d_backup.blend` | Cópia idêntica de clareira_3d, preservada |
| `clareira_melhorada.blend` | 64 objetos; flores, arbustos, pedras e materiais adicionais |
| `personagens.blend` | 97 objetos; cenário e Capi, Teco, Maya; ponto de partida da produção derivada |
| `animacao_teste.blend` | 97 objetos; 36 quadros a 12 fps; teste de balanço de 3 segundos |
| `episodio_01_animado.blend` | 104 objetos; 612 quadros a 12 fps; primeira tentativa de plantio e flor |
| `ROTEIRO/episodio_01.txt` | Seis cenas, descoberta, cuidados, canção, magia e despedida |
| `ROTEIRO/tempos_falas.csv` | Tempos das 12 falas na primeira montagem, com vírgula decimal |
| `VOZES/cena_*.mp3` | 12 falas individuais, mono, durações medidas por ffprobe; usadas sem cortar conteúdo |
| Gravações de teste | Capi, Teco, Maya, narradora_v2 e narradora_teste; quatro também duplicadas em VOZES |
| `MUSICAS/tema_clareira.mp3` | 55,301 s; preservada; autoria e licença não documentadas no repositório |
| `EXPORTACAO/*.mp3` | episodio_01_audio, previa_ambientada, previa_vozes; 50,364 s cada; preservadas |
| Scripts Python originais | criar_cena, melhorar_cena, personagens, animar, animar_episodio, montar_episodio e gerar_vozes |

Total de áudio: **25 MP3**, incluindo cópias e mixagens. As seis cenas foram abertas
no Blender 4.3.2; foram salvas originalmente com versão 4.2.67. Não foram encontradas
texturas externas não empacotadas. Detalhes de objetos, transformações e animações:
[auditoria/cenas-originais.json](auditoria/cenas-originais.json).

## Lacunas da produção anterior

- Scripts fixam caminhos `C:\ESTUDIO_INFANTIL` e executável `ffmpeg.exe`.
- A montagem antiga repete um vídeo de 3 segundos; não existe esse MP4 no checkout.
- Os três personagens recebem movimentos de corpo muito semelhantes, sem gestos
  individuais, controle de cabeça, expressões faciais ou cortes de câmera.
- O crescimento começa perto de 34 s no projeto antigo, sem agenda compartilhada
  com o áudio, enquanto a narração da magia começa em 29,28 s na montagem anterior.
- Não há gravações para a canção da cena 4 nem para a despedida coletiva. O gerador
  de vozes ignora TODOS e linhas sem personagem, portanto não produz esses trechos.
- Não havia suíte de testes, pipeline multiplataforma ou instruções de execução.
- O Blender disponível não inclui OpenImageDenoise. Cycles 1080p/16 amostras levou
  21,3 s para um quadro; EEVEE em software levou 34,2 s para um quadro de teste.

## Decisões da nova produção

Reutilizar `personagens.blend` e as doze falas individuais, criando nova cena em
`build/episodio_01/`. A timeline tem **69,25 s, 831 quadros a 12 fps** e 14 tomadas.
Inclui 4 s de plantio e 8 s de cuidados instrumentais antes da magia. Abertura de
boca acompanha energia real da voz; não é sincronização fonética/visemas.

Workbench com iluminação de estúdio permite 1080p nativo com cores limpas,
antialiasing de 8 amostras e sem artefatos de sombras em software. Não há ray tracing
ou iluminação volumétrica: a magia é representada por estrelas coloridas e flor
animadas. Os originais permanecem disponíveis para uma renderização mais sofisticada.

Todos os sons adicionados são sintetizados por código determinístico: sinos,
arpejos, acordes, pássaros, água, plantio e resolução da magia. A trilha antiga foi
preservada, mas excluída da mixagem final por falta de documentação de licença.
Os versos da canção aparecem como texto durante o instrumental; não são cantados.
A despedida coletiva é visual, com acenos e cartela. Não se fingiu criar vozes ausentes.

As vozes e os modelos foram fornecidos pelo usuário no repositório. Esta auditoria
não estabelece direitos de distribuição desses ativos; não foi obtido material de
terceiros adicional nem houve publicação.
