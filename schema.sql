-- Execute este script no MySQL Workbench conectado ao seu MySQL Server.
-- MySQL 8.0.16+ (versão que aplica as restrições CHECK).
CREATE DATABASE IF NOT EXISTS crud_games
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE crud_games;

CREATE TABLE IF NOT EXISTS jogos (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(150) NOT NULL,
    plataforma VARCHAR(80) NOT NULL,
    status VARCHAR(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
    observacoes TEXT NOT NULL,
    criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_titulo CHECK (CHAR_LENGTH(TRIM(titulo)) > 0),
    CONSTRAINT chk_plataforma CHECK (CHAR_LENGTH(TRIM(plataforma)) > 0),
    CONSTRAINT chk_status CHECK (status IN ('Zerados', 'Platinados', 'Jogando', 'Um dia eu jogo'))
) ENGINE=InnoDB;

-- Exemplo opcional: execute separadamente após escolher uma senha própria.
-- CREATE USER 'crud_games'@'localhost' IDENTIFIED BY 'SUBSTITUA_PELA_SUA_SENHA';
-- GRANT SELECT, INSERT, UPDATE, DELETE ON crud_games.* TO 'crud_games'@'localhost';
