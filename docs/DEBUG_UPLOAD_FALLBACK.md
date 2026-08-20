# Diagnóstico do fallback de upload

Durante a validação no navegador local em 20 de agosto de 2026, o upload do arquivo público `ISIC_0024306.jpg` foi aceito pelo input, mas a aplicação exibiu um erro React:

`ReferenceError: isDemoMode is not defined at UploadTab`

A causa imediata foi a remoção do import de `isDemoMode` junto com o bloqueio de inferência, enquanto ainda existe uma referência dessa variável na parte visual do `UploadTab.tsx`. A correção seguinte deve manter a interface, eliminar somente o fallback que rejeita automaticamente a imagem e substituir qualquer uso visual remanescente por um estado neutro de processamento real.
Após a correção, a tentativa de clicar no botão de recarga com um índice antigo falhou porque a página já havia sido atualizada; será necessário capturar um novo estado do navegador antes de interagir novamente.
Após remover a referência remanescente a `isDemoMode`, a interface foi recarregada e o upload de `ISIC_0024306.jpg` foi aceito. A prévia apareceu e o botão passou a exibir `Iniciar análise de câncer`, confirmando que o fallback de demonstração não é mais acionado durante a preparação.
A análise foi iniciada pela interface corrigida com o status `Processando no servidor...` e `Enviando imagem e executando triagem e classificação...` em 15%, sem a mensagem de demonstração. A inferência ainda estava em andamento no primeiro monitoramento.
O teste pela interface foi concluído com sucesso: triagem aceita (600 × 450; qualidade 0,527; OOD 0,619), resultado Benigna, confiança do ensemble 91,8%, três modelos executados e mapas de explicabilidade exibidos. A abstenção operacional foi recomendada pela incerteza agregada, o que é comportamento esperado e distinto de rejeição por configuração.
