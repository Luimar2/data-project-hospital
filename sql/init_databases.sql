-- Cria o banco analítico (caso a variável de ambiente não o faça)
CREATE DATABASE IF NOT EXISTS hospital_dw CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Cria o banco de metadados do Metabase
CREATE DATABASE IF NOT EXISTS metabase_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Concede privilégios ao usuário da aplicação em ambos os bancos
GRANT ALL PRIVILEGES ON hospital_dw.* TO 'user'@'%';
GRANT ALL PRIVILEGES ON metabase_db.* TO 'user'@'%';
FLUSH PRIVILEGES;