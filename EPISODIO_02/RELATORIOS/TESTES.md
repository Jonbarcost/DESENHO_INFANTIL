# Validação executada — Episódio 02

**Produção incompleta:** novas vozes bloqueadas por HTTP 403. Não existe MP4 final.

- Suíte completa: `python3 -m unittest discover -s tests -v`: **17 testes aprovados**.
- Sete testes anteriores, preservados; dez novos testes de roteiro, timeline, falta
  de voz, assinatura/cache, proteção do Episódio 01 e isolamento do áudio provisório.
- Revisão independente: duas falhas P2 reproduzidas por testes falhando e corrigidas.
  Música provisória usa subpasta própria; saída externa é rejeitada antes do trabalho.
- Layout: sete sequências, 51 tomadas, personagens e borboleta visíveis em amostras
  por cena; pés e asas com rotação mensurável. Tempos estimados, sem sincronização
  de fala validada. Inspeção visual feita na folha de contato.
- Teste visual: 48 quadros, quatro segundos, 1280×720, H.264, sem áudio, com marca
  explícita de planejamento. Decodificação integral passou; zero quadros pretos ou
  pares consecutivos congelados. Menor diferença RGB média: 0,472 em escala 0–255.
- Workbench: 0,72 s/quadro 1080p após warmup; estimativa de 31,7 minutos para 2.638
  quadros. Eevee: uma amostra pequena de 20,6 s incluindo inicialização; sem estimativa
  integral. Não houve render completo nem repetição do benchmark.
- Música e efeitos originais foram gerados por síntese local, separados da mixagem final.
- Hashes dos arquivos anteriores, incluindo MP4/cena/quadros do Episódio 01,
  conferidos contra preservacao-inicial.json. Quantidade e resultado em STATUS.json.
- Tentativa real de síntese e comando principal falharam com HTTP 403. Nenhuma fala
  válida foi gerada; o cliente deixou apenas um arquivo temporário vazio, que não
  é aceito pelo cache. Não há master final, cena final medida ou MP4 completo.

## Ainda não executado

Síntese das 44 falas, medição da duração real, mixagem com diálogos, sincronização
facial por energia, render integral, montagem e QA do MP4 final. Essas etapas estão
implementadas, mas permanecem pendentes. A duração final e a qualidade do filme com
vozes ainda não foram verificadas. O teste curto não satisfaz o critério de sucesso.

## Retomada

Liberar speech.platform.bing.com nas configurações de rede (HTTPS/WSS 443) e executar
`python3 -m producao.serie EPISODIO_02/ROTEIRO/roteiro.json` na raiz do repositório.
Nenhuma chave de API precisa ser fornecida em chat. O comando não publica vídeos.
