-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Tempo de geração: 16/10/2025 às 17:14
-- Versão do servidor: 10.4.32-MariaDB
-- Versão do PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Banco de dados: `newte`
--

-- --------------------------------------------------------

--
-- Estrutura para tabela `calendario_eventos`
--

CREATE TABLE `calendario_eventos` (
  `id_calendario` int(11) NOT NULL,
  `id_usuario` int(11) DEFAULT NULL,
  `titulo` varchar(100) DEFAULT NULL,
  `descricao` text DEFAULT NULL,
  `data_evento` date DEFAULT NULL,
  `hora_evento` time DEFAULT NULL,
  `data_criacao` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estrutura para tabela `licoes`
--

CREATE TABLE `licoes` (
  `id_licao` int(11) NOT NULL,
  `titulo` varchar(100) DEFAULT NULL,
  `conteudo` text DEFAULT NULL,
  `data_criacao` date DEFAULT NULL,
  `validade` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estrutura para tabela `mensagens_chat`
--

CREATE TABLE `mensagens_chat` (
  `id_mensagem` int(11) NOT NULL,
  `remetente_id` int(11) DEFAULT NULL,
  `destinatario_id` int(11) DEFAULT NULL,
  `mensagem` text DEFAULT NULL,
  `data_envio` date DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estrutura para tabela `recuperacao_senha`
--

CREATE TABLE `recuperacao_senha` (
  `id_recuperacao` int(11) NOT NULL,
  `email_usuario` varchar(120) NOT NULL,
  `codigo` varchar(6) NOT NULL,
  `data_criacao` timestamp NULL DEFAULT current_timestamp(),
  `valido_ate` timestamp NULL DEFAULT (current_timestamp() + interval 10 minute),
  `utilizado` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estrutura para tabela `usuario`
--

CREATE TABLE `usuario` (
  `id_user` int(11) NOT NULL,
  `nome` varchar(50) DEFAULT NULL,
  `email` varchar(120) DEFAULT NULL,
  `telefone` varchar(50) DEFAULT NULL,
  `cpf` varchar(11) DEFAULT NULL,
  `rg` varchar(9) DEFAULT NULL,
  `departamento` varchar(50) DEFAULT NULL,
  `cargo` varchar(50) DEFAULT NULL,
  `foto_perfil` varchar(255) DEFAULT NULL,
  `status` varchar(8) DEFAULT NULL,
  `data_entrada` date DEFAULT NULL,
  `sobre_mim` text DEFAULT NULL,
  `senha` varchar(255) DEFAULT NULL,
  `endereco` varchar(255) DEFAULT NULL,
  `tipo_usuario` varchar(20) DEFAULT NULL,
  `experiencias` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Despejando dados para a tabela `usuario`
--

INSERT INTO `usuario` (`id_user`, `nome`, `email`, `telefone`, `cpf`, `rg`, `departamento`, `cargo`, `foto_perfil`, `status`, `data_entrada`, `sobre_mim`, `senha`, `endereco`, `tipo_usuario`, `experiencias`) VALUES
(1, 'Leonardo', 'leonardo.vilelasilva08@gmail.com', '11999999999', '12345678901', 'MG1234567', 'Recursos Humanos', 'Analista de RH', 'alice.jpg', 'ATV', '2023-01-10', 'Profissional dedicada e organizada.', 'ec6a6536ca304edf844d1d248a4f08dc', 'Rua das Flores, 123', 'admin', '5 anos em RH'),
(2, 'Matheus', 'matheus@example.com', '11988888888', '23456789012', 'SP2345678', 'TI', 'Desenvolvedor Back-End', 'bruno.jpg', 'ATV', '2022-07-25', 'Entusiasta de tecnologia e automação.', 'ec6a6536ca304edf844d1d248a4f08dc', 'Av. Paulista, 456', 'user', '3 anos em desenvolvimento web'),
(4, 'Ana Ribeiro', 'ana@email.com', '11955555555', '56789012345', '321654987', 'TI', 'Desenvolvedora', NULL, 'ativo', '2025-02-10', 'Fã de tecnologia e inovação', '5390489da3971cbbcd22c159d54d24da', 'Rua E, 202', 'usuario', 'Desenvolvimento de sistemas'),
(5, 'Bruno Santos', 'bruno@email.com', '11944444444', '67890123456', '654987321', 'Financeiro', 'Analista', NULL, 'ativo', '2024-09-15', 'Planejamento financeiro', 'b304f234940a679b3ab3c699f80db849', 'Rua F, 303', 'usuario', 'Controle de contas e relatórios'),
(6, 'Camila Ferreira', 'camila@email.com', '11933333333', '78901234567', '987321654', 'RH', 'Coordenadora', NULL, 'ativo', '2023-12-20', 'Gestão de pessoas e treinamento', 'bd1982fef67ba9de321b9dcbbc88bb1a', 'Rua G, 404', 'usuario', 'Recrutamento e treinamento'),
(7, 'Daniel Oliveira', 'daniel@email.com', '11999999999', '89012345678', '321789654', 'Marketing', 'Desenvolvedor Sênior', NULL, 'ativo', '2022-06-05', 'Estratégias de mídia e criatividade', '975d7bdf549f6f9f6811c03c3c657901', 'Rua H, 505', 'usuario', 'Campanhas publicitárias');

--
-- Acionadores `usuario`
--
DELIMITER $$
CREATE TRIGGER `usuario_after_delete` AFTER DELETE ON `usuario` FOR EACH ROW BEGIN
  INSERT INTO usuario_logs (
    id_user,
    acao,
    data_hora,
    dados_anteriores,
    actor_id,
    actor_email,
    actor_db_user
  )
  VALUES (
    OLD.id_user,
    'DELETE',
    NOW(),
    JSON_OBJECT(
      'id_user', OLD.id_user,
      'nome', OLD.nome,
      'email', OLD.email,
      'telefone', OLD.telefone,
      'cpf', OLD.cpf,
      'rg', OLD.rg,
      'departamento', OLD.departamento,
      'cargo', OLD.cargo,
      'foto_perfil', OLD.foto_perfil,
      'status', OLD.status,
      'data_entrada', OLD.data_entrada,
      'sobre_mim', OLD.sobre_mim,
      'endereco', OLD.endereco,
      'tipo_usuario', OLD.tipo_usuario,
      'experiencias', OLD.experiencias
    ),
    @actor_id,
    @actor_email,
    CURRENT_USER()
  );
END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `usuario_after_insert` AFTER INSERT ON `usuario` FOR EACH ROW BEGIN
  INSERT INTO usuario_logs (
    id_user,
    acao,
    data_hora,
    dados_novos,
    actor_id,
    actor_email,
    actor_db_user
  )
  VALUES (
    NEW.id_user,
    'INSERT',
    NOW(),
    JSON_OBJECT(
      'id_user', NEW.id_user,
      'nome', NEW.nome,
      'email', NEW.email,
      'telefone', NEW.telefone,
      'cpf', NEW.cpf,
      'rg', NEW.rg,
      'departamento', NEW.departamento,
      'cargo', NEW.cargo,
      'foto_perfil', NEW.foto_perfil,
      'status', NEW.status,
      'data_entrada', NEW.data_entrada,
      'sobre_mim', NEW.sobre_mim,
      'endereco', NEW.endereco,
      'tipo_usuario', NEW.tipo_usuario,
      'experiencias', NEW.experiencias
    ),
    -- actor info read from session variables (set by app). Use NULL if not set.
    @actor_id,
    @actor_email,
    CURRENT_USER()
  );
END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `usuario_after_update` AFTER UPDATE ON `usuario` FOR EACH ROW BEGIN
  INSERT INTO usuario_logs (
    id_user,
    acao,
    data_hora,
    dados_anteriores,
    dados_novos,
    actor_id,
    actor_email,
    actor_db_user
  )
  VALUES (
    NEW.id_user,
    'UPDATE',
    NOW(),
    JSON_OBJECT(
      'id_user', OLD.id_user,
      'nome', OLD.nome,
      'email', OLD.email,
      'telefone', OLD.telefone,
      'cpf', OLD.cpf,
      'rg', OLD.rg,
      'departamento', OLD.departamento,
      'cargo', OLD.cargo,
      'foto_perfil', OLD.foto_perfil,
      'status', OLD.status,
      'data_entrada', OLD.data_entrada,
      'sobre_mim', OLD.sobre_mim,
      'endereco', OLD.endereco,
      'tipo_usuario', OLD.tipo_usuario,
      'experiencias', OLD.experiencias
    ),
    JSON_OBJECT(
      'id_user', NEW.id_user,
      'nome', NEW.nome,
      'email', NEW.email,
      'telefone', NEW.telefone,
      'cpf', NEW.cpf,
      'rg', NEW.rg,
      'departamento', NEW.departamento,
      'cargo', NEW.cargo,
      'foto_perfil', NEW.foto_perfil,
      'status', NEW.status,
      'data_entrada', NEW.data_entrada,
      'sobre_mim', NEW.sobre_mim,
      'endereco', NEW.endereco,
      'tipo_usuario', NEW.tipo_usuario,
      'experiencias', NEW.experiencias
    ),
    @actor_id,
    @actor_email,
    CURRENT_USER()
  );
END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `usuario_before_insert` BEFORE INSERT ON `usuario` FOR EACH ROW BEGIN
    SET NEW.senha = MD5(NEW.senha);
END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `usuario_before_update` BEFORE UPDATE ON `usuario` FOR EACH ROW BEGIN
    -- Só criptografa se a senha foi alterada
    IF NEW.senha <> OLD.senha THEN
        SET NEW.senha = MD5(NEW.senha);
    END IF;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Estrutura para tabela `usuario_evento_calendario`
--

CREATE TABLE `usuario_evento_calendario` (
  `id_usuario` int(11) NOT NULL,
  `id_evento` int(11) NOT NULL,
  `data_registro` timestamp NOT NULL DEFAULT current_timestamp(),
  `status` varchar(20) DEFAULT 'ativo'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estrutura para tabela `usuario_licao_realizada`
--

CREATE TABLE `usuario_licao_realizada` (
  `id_usuario` int(11) NOT NULL,
  `id_licao` int(11) NOT NULL,
  `data_registro` timestamp NOT NULL DEFAULT current_timestamp(),
  `status` varchar(20) DEFAULT 'concluida'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estrutura para tabela `usuario_logs`
--

CREATE TABLE `usuario_logs` (
  `id_log` int(11) NOT NULL,
  `id_user` int(11) NOT NULL,
  `acao` varchar(10) NOT NULL,
  `data_hora` datetime NOT NULL DEFAULT current_timestamp(),
  `dados_anteriores` text DEFAULT NULL,
  `dados_novos` text DEFAULT NULL,
  `actor_id` int(11) DEFAULT NULL,
  `actor_email` varchar(120) DEFAULT NULL,
  `actor_db_user` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Despejando dados para a tabela `usuario_logs`
--

INSERT INTO `usuario_logs` (`id_log`, `id_user`, `acao`, `data_hora`, `dados_anteriores`, `dados_novos`, `actor_id`, `actor_email`, `actor_db_user`) VALUES
(1, 7, 'UPDATE', '2025-10-16 12:01:52', '{\"id_user\": 7, \"nome\": \"Daniel Oliveira\", \"email\": \"daniel@email.com\", \"telefone\": \"11922222222\", \"cpf\": \"89012345678\", \"rg\": \"321789654\", \"departamento\": \"Marketing\", \"cargo\": \"Analista\", \"foto_perfil\": null, \"status\": \"ativo\", \"data_entrada\": \"2022-06-05\", \"sobre_mim\": \"Estratégias de mídia e criatividade\", \"endereco\": \"Rua H, 505\", \"tipo_usuario\": \"usuario\", \"experiencias\": \"Campanhas publicitárias\"}', '{\"id_user\": 7, \"nome\": \"Daniel Oliveira\", \"email\": \"daniel@email.com\", \"telefone\": \"11999999999\", \"cpf\": \"89012345678\", \"rg\": \"321789654\", \"departamento\": \"Marketing\", \"cargo\": \"Desenvolvedor Sênior\", \"foto_perfil\": null, \"status\": \"ativo\", \"data_entrada\": \"2022-06-05\", \"sobre_mim\": \"Estratégias de mídia e criatividade\", \"endereco\": \"Rua H, 505\", \"tipo_usuario\": \"usuario\", \"experiencias\": \"Campanhas publicitárias\"}', 1, 'leonardo.vilelasilva08@gmail.com', 'root@localhost'),
(2, 9, 'INSERT', '2025-10-16 12:06:26', NULL, '{\"id_user\": 9, \"nome\": \"Usuario Teste\", \"email\": \"usuario_teste@email.com\", \"telefone\": \"11955555555\", \"cpf\": \"98765432100\", \"rg\": \"12345678\", \"departamento\": \"TI\", \"cargo\": \"Tester\", \"foto_perfil\": null, \"status\": \"ativo\", \"data_entrada\": \"2025-10-16\", \"sobre_mim\": \"Usuário criado para teste de log\", \"endereco\": \"Rua Teste, 100\", \"tipo_usuario\": \"usuario\", \"experiencias\": \"Experiência teste\"}', 1, 'leonardo.vilelasilva08@gmail.com', 'root@localhost'),
(3, 9, 'DELETE', '2025-10-16 12:06:26', '{\"id_user\": 9, \"nome\": \"Usuario Teste\", \"email\": \"usuario_teste@email.com\", \"telefone\": \"11955555555\", \"cpf\": \"98765432100\", \"rg\": \"12345678\", \"departamento\": \"TI\", \"cargo\": \"Tester\", \"foto_perfil\": null, \"status\": \"ativo\", \"data_entrada\": \"2025-10-16\", \"sobre_mim\": \"Usuário criado para teste de log\", \"endereco\": \"Rua Teste, 100\", \"tipo_usuario\": \"usuario\", \"experiencias\": \"Experiência teste\"}', NULL, 1, 'leonardo.vilelasilva08@gmail.com', 'root@localhost');

-- --------------------------------------------------------

--
-- Estrutura para tabela `usuario_mensagem_enviada`
--

CREATE TABLE `usuario_mensagem_enviada` (
  `id_usuario` int(11) NOT NULL,
  `id_mensagem` int(11) NOT NULL,
  `data_registro` timestamp NOT NULL DEFAULT current_timestamp(),
  `status` varchar(20) DEFAULT 'enviado'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Índices para tabelas despejadas
--

--
-- Índices de tabela `calendario_eventos`
--
ALTER TABLE `calendario_eventos`
  ADD PRIMARY KEY (`id_calendario`),
  ADD KEY `id_usuario` (`id_usuario`);

--
-- Índices de tabela `licoes`
--
ALTER TABLE `licoes`
  ADD PRIMARY KEY (`id_licao`);

--
-- Índices de tabela `mensagens_chat`
--
ALTER TABLE `mensagens_chat`
  ADD PRIMARY KEY (`id_mensagem`),
  ADD KEY `remetente_id` (`remetente_id`),
  ADD KEY `destinatario_id` (`destinatario_id`);

--
-- Índices de tabela `recuperacao_senha`
--
ALTER TABLE `recuperacao_senha`
  ADD PRIMARY KEY (`id_recuperacao`);

--
-- Índices de tabela `usuario`
--
ALTER TABLE `usuario`
  ADD PRIMARY KEY (`id_user`),
  ADD UNIQUE KEY `email` (`email`),
  ADD UNIQUE KEY `cpf` (`cpf`);

--
-- Índices de tabela `usuario_evento_calendario`
--
ALTER TABLE `usuario_evento_calendario`
  ADD PRIMARY KEY (`id_usuario`,`id_evento`),
  ADD KEY `id_evento` (`id_evento`);

--
-- Índices de tabela `usuario_licao_realizada`
--
ALTER TABLE `usuario_licao_realizada`
  ADD PRIMARY KEY (`id_usuario`,`id_licao`),
  ADD KEY `id_licao` (`id_licao`);

--
-- Índices de tabela `usuario_logs`
--
ALTER TABLE `usuario_logs`
  ADD PRIMARY KEY (`id_log`);

--
-- Índices de tabela `usuario_mensagem_enviada`
--
ALTER TABLE `usuario_mensagem_enviada`
  ADD PRIMARY KEY (`id_usuario`,`id_mensagem`),
  ADD KEY `id_mensagem` (`id_mensagem`);

--
-- AUTO_INCREMENT para tabelas despejadas
--

--
-- AUTO_INCREMENT de tabela `recuperacao_senha`
--
ALTER TABLE `recuperacao_senha`
  MODIFY `id_recuperacao` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de tabela `usuario`
--
ALTER TABLE `usuario`
  MODIFY `id_user` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT de tabela `usuario_logs`
--
ALTER TABLE `usuario_logs`
  MODIFY `id_log` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- Restrições para tabelas despejadas
--

--
-- Restrições para tabelas `calendario_eventos`
--
ALTER TABLE `calendario_eventos`
  ADD CONSTRAINT `calendario_eventos_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_user`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Restrições para tabelas `mensagens_chat`
--
ALTER TABLE `mensagens_chat`
  ADD CONSTRAINT `mensagens_chat_ibfk_1` FOREIGN KEY (`remetente_id`) REFERENCES `usuario` (`id_user`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `mensagens_chat_ibfk_2` FOREIGN KEY (`destinatario_id`) REFERENCES `usuario` (`id_user`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Restrições para tabelas `usuario_evento_calendario`
--
ALTER TABLE `usuario_evento_calendario`
  ADD CONSTRAINT `usuario_evento_calendario_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_user`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `usuario_evento_calendario_ibfk_2` FOREIGN KEY (`id_evento`) REFERENCES `calendario_eventos` (`id_calendario`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Restrições para tabelas `usuario_licao_realizada`
--
ALTER TABLE `usuario_licao_realizada`
  ADD CONSTRAINT `usuario_licao_realizada_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_user`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `usuario_licao_realizada_ibfk_2` FOREIGN KEY (`id_licao`) REFERENCES `licoes` (`id_licao`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Restrições para tabelas `usuario_mensagem_enviada`
--
ALTER TABLE `usuario_mensagem_enviada`
  ADD CONSTRAINT `usuario_mensagem_enviada_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_user`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `usuario_mensagem_enviada_ibfk_2` FOREIGN KEY (`id_mensagem`) REFERENCES `mensagens_chat` (`id_mensagem`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
