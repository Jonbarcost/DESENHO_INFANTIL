# O Mistério da Borboleta Azul

Missão do usuário: episódio animado de 3–5 minutos, 1080p 16:9 MP4, para 3–7 anos,
com os modelos e vozes existentes, sem alterar o Episódio 01 ou publicar.
Autonomia criativa/técnica concedida; execução sem aprovações intermediárias.

Direção escolhida: sete sequências, aproximadamente 3min35s. Descoberta, perseguição
com tropeço leve, observação sem tocar nas asas, jardim com poucas flores, néctar e
polinização explicados por Maya, plantio de mudas/rega, passagem de dias, flores e
celebração. Gancho sonoro para um riacho. Nenhuma lição sugere pegar borboletas,
dar açúcar a insetos ou fazer flores crescerem instantaneamente pela água.

Reutilizar o rig por partes e os helpers do Episódio 01; novo pacote producao.serie
para roteiro JSON, vozes, timeline, layout, áudio, render em lotes e QA. Personagens
com marcha por deslocamento, pés alternados e braços opostos, reações individuais,
expressões e boca por energia das gravações. Borboleta de asas articuladas segue
trajetória suave; flores/folhas balançam discretamente. Vários enquadramentos e
fades breves nos intervalos de cena. Não reconstruir personagens/cenário.

Render: uma amostra curta em EEVEE e Workbench, com limite de custo. Preferir EEVEE
somente se compatibilidade/desempenho permitirem. Registrar a estimativa antes do
render integral; usar 1080p nativo ou 720p ampliado explicitamente conforme medição.
Não gastar o render integral enquanto as vozes estiverem bloqueadas.

Vozes exatas fornecidas no pedido; sem fallback silencioso. Endpoint Edge bloqueado
por rede neste ambiente. Pipeline deve distinguir layout provisório de timeline
medida e MP4 final. Layout editável/teste visual/música podem ser produzidos
independentemente. Aceitação final exige as vozes e medição real de todos os arquivos.

Música/efeitos por síntese matemática local, sem samples externos. Volume ducked
durante falas, loudness final verificado. Preservação por hashes inclui outputs do
Episódio 01. Metadados YouTube preparados, publicação desabilitada.
