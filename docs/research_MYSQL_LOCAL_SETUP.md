# Fontes técnicas da configuração MySQL/MariaDB local

A configuração inicial tentou usar MySQL Community Server 8.4.9 no Windows. A documentação oficial do MySQL 8.4 recomenda que `--defaults-file` seja o primeiro argumento ao iniciar `mysqld` e informa que os dois Undo Tablespaces padrão são criados durante a inicialização da instância. Ela também define que `innodb_undo_directory`, quando configurado, precisa apontar para o local dos arquivos `undo_001` e `undo_002` durante a inicialização e em todas as partidas posteriores [1] [2].

Durante a inicialização manual no computador Windows, o MySQL 8.4.9 apresentou repetidamente `Can't create UNDO tablespace ... since '.\\undo_001' already exists`, mesmo após diretório de dados limpo e `--defaults-file` explícito. Para não bloquear o projeto, foi usada a alternativa compatível MariaDB Server 12.3.2, instalada pelo winget, com datadir já inicializado pelo pacote e servidor limitado a `127.0.0.1:3306`. A camada do projeto utiliza `drizzle-orm/mysql2` e SQL compatível, portanto o schema Drizzle foi aplicado sem mudanças.

A instância MariaDB foi validada com quatro tabelas do projeto (`users`, `dermatological_images`, `diagnoses`, `model_metrics`), usuário de aplicação separado (`skincancer_app`) e schema aplicado via `corepack pnpm db:push`. As credenciais ficam exclusivamente no `.env`, que não deve ser versionado. Backups de `.env`, logs do MariaDB e diretórios de dados locais foram adicionados ao `.gitignore`.

## Referências

[1]: https://dev.mysql.com/doc/refman/8.4/en/innodb-init-startup-configuration.html "MySQL 8.4 Reference Manual — InnoDB Startup Configuration"

[2]: https://dev.mysql.com/doc/refman/8.4/en/innodb-undo-tablespaces.html "MySQL 8.4 Reference Manual — Undo Tablespaces"

[3]: https://learn.microsoft.com/en-us/windows/package-manager/winget/ "Microsoft Learn — Windows Package Manager winget"
