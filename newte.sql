-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Tempo de geração: 18/09/2025 às 16:38
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
(1, 'Leonardo', 'leonardo.vilelasilva08@gmail.com', '11999999999', '12345678901', 'MG1234567', 'Recursos Humanos', 'Analista de RH', 'alice.jpg', 'ATV', '2023-01-10', 'Profissional dedicada e organizada.', '1234', 'Rua das Flores, 123', 'admin', '5 anos em RH'),
(2, 'Matheus', 'matheus@example.com', '11988888888', '23456789012', 'SP2345678', 'TI', 'Desenvolvedor Back-End', 'bruno.jpg', 'ATV', '2022-07-25', 'Entusiasta de tecnologia e automação.', '1234', 'Av. Paulista, 456', 'user', '3 anos em desenvolvimento web');

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
  MODIFY `id_user` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

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
