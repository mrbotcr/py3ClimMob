-- phpMyAdmin SQL Dump
-- version 4.2.12deb2+deb8u1build0.15.04.1
-- http://www.phpmyadmin.net
--
-- Servidor: localhost
-- Tiempo de generación: 02-02-2017 a las 09:39:27
-- Versión del servidor: 5.6.28-0ubuntu0.15.04.1
-- Versión de PHP: 5.6.4-4ubuntu6.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Base de datos: `climmobv3`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `activitylog`
--

CREATE TABLE IF NOT EXISTS `activitylog` (
`log_id` int(9) NOT NULL,
  `log_user` varchar(80) NOT NULL,
  `log_datetime` datetime DEFAULT NULL,
  `log_type` varchar(3) DEFAULT NULL,
  `log_message` text
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `apilog`
--

CREATE TABLE IF NOT EXISTS `apilog` (
`log_id` int(9) NOT NULL,
  `log_datetime` datetime DEFAULT NULL,
  `log_ip` varchar(45) DEFAULT NULL,
  `log_user` varchar(80) NOT NULL,
  `log_uuid` varchar(80) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `assessment`
--

CREATE TABLE IF NOT EXISTS `assessment` (
  `user_name` varchar(80) NOT NULL,
  `project_cod` varchar(80) NOT NULL,
  `question_id` int(11) NOT NULL,
  `section_user` varchar(80) NOT NULL,
  `section_project` varchar(80) NOT NULL,
  `section_id` int(11) NOT NULL,
  `question_order` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `asssection`
--

CREATE TABLE IF NOT EXISTS `asssection` (
  `user_name` varchar(80) NOT NULL,
  `project_cod` varchar(80) NOT NULL,
  `section_id` int(11) NOT NULL,
  `section_name` varchar(120) DEFAULT NULL,
  `section_content` text,
  `section_order` int(11) DEFAULT NULL,
  `section_color` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `country`
--

CREATE TABLE IF NOT EXISTS `country` (
  `cnty_cod` varchar(3) NOT NULL,
  `cnty_name` varchar(120) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `enumerator`
--

CREATE TABLE IF NOT EXISTS `enumerator` (
  `user_name` varchar(80) NOT NULL,
  `project_cod` varchar(80) NOT NULL,
  `enum_id` varchar(80) NOT NULL,
  `enum_name` varchar(120) DEFAULT NULL,
  `enum_password` varchar(80) DEFAULT NULL,
  `enum_active` tinyint(4) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `i18n`
--

CREATE TABLE IF NOT EXISTS `i18n` (
  `lang_code` varchar(5) NOT NULL,
  `lang_name` varchar(120) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `i18n_asssection`
--

CREATE TABLE IF NOT EXISTS `i18n_asssection` (
  `user_name` varchar(80) NOT NULL,
  `project_cod` varchar(80) NOT NULL,
  `section_id` int(11) NOT NULL,
  `lang_code` varchar(5) NOT NULL,
  `section_name` varchar(120) DEFAULT NULL,
  `section_content` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `i18n_prjalias`
--

CREATE TABLE IF NOT EXISTS `i18n_prjalias` (
  `user_name` varchar(80) NOT NULL,
  `project_cod` varchar(80) NOT NULL,
  `tech_id` int(11) NOT NULL,
  `alias_id` int(11) NOT NULL,
  `lang_code` varchar(5) NOT NULL,
  `alias_name` varchar(120) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `i18n_project`
--

CREATE TABLE IF NOT EXISTS `i18n_project` (
  `user_name` varchar(80) NOT NULL,
  `project_cod` varchar(80) NOT NULL,
  `lang_code` varchar(5) NOT NULL,
  `project_name` varchar(120) DEFAULT NULL,
  `project_abstract` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `i18n_qstoption`
--

CREATE TABLE IF NOT EXISTS `i18n_qstoption` (
  `question_id` int(11) NOT NULL,
  `value_code` int(11) NOT NULL,
  `lang_code` varchar(5) NOT NULL,
  `value_desc` varchar(120) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `i18n_question`
--

CREATE TABLE IF NOT EXISTS `i18n_question` (
  `question_id` int(11) NOT NULL,
  `lang_code` varchar(5) NOT NULL,
  `question_desc` varchar(120) DEFAULT NULL,
  `question_notes` text,
  `question_unit` varchar(120) DEFAULT NULL,
  `question_posstm` varchar(120) DEFAULT NULL,
  `question_negstm` varchar(120) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `i18n_regsection`
--

CREATE TABLE IF NOT EXISTS `i18n_regsection` (
  `user_name` varchar(80) NOT NULL,
  `project_cod` varchar(80) NOT NULL,
  `section_id` int(11) NOT NULL,
  `lang_code` varchar(5) NOT NULL,
  `section_name` varchar(120) DEFAULT NULL,
  `section_content` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `i18n_techalias`
--

CREATE TABLE IF NOT EXISTS `i18n_techalias` (
  `tech_id` int(11) NOT NULL,
  `alias_id` int(11) NOT NULL,
  `lang_code` varchar(5) NOT NULL,
  `alias_name` varchar(120) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `i18n_technology`
--

CREATE TABLE IF NOT EXISTS `i18n_technology` (
  `tech_id` int(11) NOT NULL,
  `lang_code` varchar(5) NOT NULL,
  `tech_name` varchar(45) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `package`
--

CREATE TABLE IF NOT EXISTS `package` (
  `user_name` varchar(80) NOT NULL,
  `project_cod` varchar(80) NOT NULL,
  `package_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pkgcomb`
--

CREATE TABLE IF NOT EXISTS `pkgcomb` (
  `user_name` varchar(80) NOT NULL,
  `project_cod` varchar(80) NOT NULL,
  `package_id` int(11) NOT NULL,
  `comb_user` varchar(80) NOT NULL,
  `comb_project` varchar(80) NOT NULL,
  `comb_code` int(11) NOT NULL,
  `pkgcomb_code` varchar(45) DEFAULT NULL,
  `pkgcomb_image` blob
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `prjalias`
--

CREATE TABLE IF NOT EXISTS `prjalias` (
  `user_name` varchar(80) NOT NULL,
  `project_cod` varchar(80) NOT NULL,
  `tech_id` int(11) NOT NULL,
  `alias_id` int(11) NOT NULL,
  `alias_name` varchar(120) DEFAULT NULL,
  `tech_used` int(11) DEFAULT NULL,
  `alias_used` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `prjcnty`
--

CREATE TABLE IF NOT EXISTS `prjcnty` (
  `user_name` varchar(80) NOT NULL,
  `project_cod` varchar(80) NOT NULL,
  `cnty_cod` varchar(3) NOT NULL,
  `cnty_contact` varchar(120) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `prjcombdet`
--

CREATE TABLE IF NOT EXISTS `prjcombdet` (
  `prjcomb_user` varchar(80) NOT NULL,
  `prjcomb_project` varchar(80) NOT NULL,
  `comb_code` int(11) NOT NULL,
  `user_name` varchar(80) NOT NULL,
  `project_cod` varchar(80) NOT NULL,
  `tech_id` int(11) NOT NULL,
  `alias_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `prjcombination`
--

CREATE TABLE IF NOT EXISTS `prjcombination` (
  `user_name` varchar(80) NOT NULL,
  `project_cod` varchar(80) NOT NULL,
  `comb_code` int(11) NOT NULL,
  `comb_usable` tinyint(4) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `prjlang`
--

CREATE TABLE IF NOT EXISTS `prjlang` (
  `user_name` varchar(80) NOT NULL,
  `project_cod` varchar(80) NOT NULL,
  `lang_code` varchar(5) NOT NULL,
  `lang_default` tinyint(4) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `prjtech`
--

CREATE TABLE IF NOT EXISTS `prjtech` (
  `user_name` varchar(80) NOT NULL,
  `project_cod` varchar(80) NOT NULL,
  `tech_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `project`
--

CREATE TABLE IF NOT EXISTS `project` (
  `user_name` varchar(80) NOT NULL,
  `project_cod` varchar(80) NOT NULL,
  `project_name` varchar(120) DEFAULT NULL,
  `project_abstract` text,
  `project_tags` text,
  `project_pi` varchar(120) DEFAULT NULL,
  `project_piemail` varchar(120) DEFAULT NULL,
  `project_active` tinyint(4) DEFAULT '1',
  `project_public` tinyint(4) DEFAULT '0',
  `project_numobs` int(11) NOT NULL DEFAULT '0',
  `project_numcom` int(11) NOT NULL,
  `project_lat` decimal(8,6) NOT NULL,
  `project_lon` decimal(8,6) NOT NULL,
  `project_creationdate` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `qstoption`
--

CREATE TABLE IF NOT EXISTS `qstoption` (
  `question_id` int(11) NOT NULL,
  `value_code` int(11) NOT NULL,
  `value_desc` varchar(120) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `qstprjopt`
--

CREATE TABLE IF NOT EXISTS `qstprjopt` (
  `project_user` varchar(80) NOT NULL,
  `project_cod` varchar(80) NOT NULL,
  `question_id` int(11) NOT NULL,
  `value_code` int(11) NOT NULL,
  `value_desc` varchar(120) DEFAULT NULL,
  `parent_user` varchar(80) DEFAULT NULL,
  `parent_project` varchar(80) DEFAULT NULL,
  `parent_question` int(11) DEFAULT NULL,
  `parent_value` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `question`
--

CREATE TABLE IF NOT EXISTS `question` (
`question_id` int(11) NOT NULL,
  `question_desc` varchar(120) DEFAULT NULL,
  `question_notes` text,
  `question_unit` varchar(120) DEFAULT NULL,
  `question_dtype` int(11) DEFAULT NULL COMMENT 'Can also be Producer input, producer select, package select, enumerator select',
  `question_oth` int(11) DEFAULT NULL,
  `question_cmp` varchar(120) DEFAULT NULL,
  `question_reqinreg` tinyint(4) DEFAULT '0',
  `question_reqinasses` tinyint(4) DEFAULT '0',
  `question_optperprj` tinyint(4) DEFAULT '0',
  `parent_question` int(11) DEFAULT NULL,
  `user_name` varchar(80) DEFAULT NULL,
  `question_posstm` varchar(120) DEFAULT NULL COMMENT 'Positive statement (if triad question)',
  `question_negstm` varchar(120) DEFAULT NULL COMMENT 'Negative statement (if triad question)',
  `question_twoitems` varchar(120) DEFAULT NULL,
  `question_moreitems` varchar(120) DEFAULT NULL,
  `question_requiredvalue` int(4) DEFAULT NULL
) ENGINE=InnoDB AUTO_INCREMENT=154 DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `registry`
--

CREATE TABLE IF NOT EXISTS `registry` (
  `user_name` varchar(80) NOT NULL,
  `project_cod` varchar(80) NOT NULL,
  `question_id` int(11) NOT NULL,
  `section_user` varchar(80) DEFAULT NULL,
  `section_project` varchar(80) DEFAULT NULL,
  `section_id` int(11) DEFAULT NULL,
  `question_order` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `regsection`
--

CREATE TABLE IF NOT EXISTS `regsection` (
  `user_name` varchar(80) NOT NULL,
  `project_cod` varchar(80) NOT NULL,
  `section_id` int(11) NOT NULL,
  `section_name` varchar(45) DEFAULT NULL,
  `section_content` text,
  `section_order` int(11) DEFAULT NULL,
  `section_color` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Registry section / Seccion en registro';

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `sector`
--

CREATE TABLE IF NOT EXISTS `sector` (
`sector_cod` int(11) NOT NULL,
  `sector_name` varchar(120) DEFAULT NULL
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `techalias`
--

CREATE TABLE IF NOT EXISTS `techalias` (
  `tech_id` int(11) NOT NULL,
  `alias_id` int(11) NOT NULL,
  `alias_name` varchar(120) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `technology`
--

CREATE TABLE IF NOT EXISTS `technology` (
`tech_id` int(11) NOT NULL,
  `tech_name` varchar(45) DEFAULT NULL,
  `user_name` varchar(80) DEFAULT NULL
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `user`
--

CREATE TABLE IF NOT EXISTS `user` (
  `user_name` varchar(80) NOT NULL,
  `user_fullname` varchar(120) DEFAULT NULL,
  `user_password` varchar(80) DEFAULT NULL,
  `user_organization` varchar(120) DEFAULT NULL,
  `user_email` varchar(120) DEFAULT NULL,
  `user_apikey` varchar(45) DEFAULT NULL,
  `user_about` text,
  `user_cnty` varchar(3) NOT NULL,
  `user_sector` int(11) NOT NULL,
  `user_active` tinyint(4) DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='User table: Store the users';

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `activitylog`
--
ALTER TABLE `activitylog`
 ADD PRIMARY KEY (`log_id`), ADD KEY `fk_activitylog_user1_idx` (`log_user`);

--
-- Indices de la tabla `apilog`
--
ALTER TABLE `apilog`
 ADD PRIMARY KEY (`log_id`), ADD KEY `fk_apilog_user1_idx` (`log_user`);

--
-- Indices de la tabla `assessment`
--
ALTER TABLE `assessment`
 ADD PRIMARY KEY (`user_name`,`project_cod`,`question_id`), ADD KEY `fk_assessment_question1_idx` (`question_id`), ADD KEY `fk_assessment_asssection1_idx` (`section_user`,`section_project`,`section_id`);

--
-- Indices de la tabla `asssection`
--
ALTER TABLE `asssection`
 ADD PRIMARY KEY (`user_name`,`project_cod`,`section_id`);

--
-- Indices de la tabla `country`
--
ALTER TABLE `country`
 ADD PRIMARY KEY (`cnty_cod`);

--
-- Indices de la tabla `enumerator`
--
ALTER TABLE `enumerator`
 ADD PRIMARY KEY (`user_name`,`project_cod`,`enum_id`);

--
-- Indices de la tabla `i18n`
--
ALTER TABLE `i18n`
 ADD PRIMARY KEY (`lang_code`);

--
-- Indices de la tabla `i18n_asssection`
--
ALTER TABLE `i18n_asssection`
 ADD PRIMARY KEY (`user_name`,`project_cod`,`section_id`,`lang_code`), ADD KEY `fk_i18n_asssection_i18n1_idx` (`lang_code`);

--
-- Indices de la tabla `i18n_prjalias`
--
ALTER TABLE `i18n_prjalias`
 ADD PRIMARY KEY (`user_name`,`project_cod`,`tech_id`,`alias_id`,`lang_code`), ADD KEY `fk_i18n_prjalias_i18n1_idx` (`lang_code`);

--
-- Indices de la tabla `i18n_project`
--
ALTER TABLE `i18n_project`
 ADD PRIMARY KEY (`user_name`,`project_cod`,`lang_code`), ADD KEY `fk_i18n_project_i18n1_idx` (`lang_code`);

--
-- Indices de la tabla `i18n_qstoption`
--
ALTER TABLE `i18n_qstoption`
 ADD PRIMARY KEY (`question_id`,`value_code`,`lang_code`), ADD KEY `fk_i18n_qstoption_i18n1_idx` (`lang_code`);

--
-- Indices de la tabla `i18n_question`
--
ALTER TABLE `i18n_question`
 ADD PRIMARY KEY (`question_id`,`lang_code`), ADD KEY `fk_i18n_question_i18n1_idx` (`lang_code`);

--
-- Indices de la tabla `i18n_regsection`
--
ALTER TABLE `i18n_regsection`
 ADD PRIMARY KEY (`user_name`,`project_cod`,`section_id`,`lang_code`), ADD KEY `fk_i18n_regsection_i18n1_idx` (`lang_code`);

--
-- Indices de la tabla `i18n_techalias`
--
ALTER TABLE `i18n_techalias`
 ADD PRIMARY KEY (`tech_id`,`alias_id`,`lang_code`), ADD KEY `fk_i18n_techalias_i18n1_idx` (`lang_code`);

--
-- Indices de la tabla `i18n_technology`
--
ALTER TABLE `i18n_technology`
 ADD PRIMARY KEY (`tech_id`,`lang_code`), ADD KEY `fk_i18n_technology_i18n1_idx` (`lang_code`);

--
-- Indices de la tabla `package`
--
ALTER TABLE `package`
 ADD PRIMARY KEY (`user_name`,`project_cod`,`package_id`);

--
-- Indices de la tabla `pkgcomb`
--
ALTER TABLE `pkgcomb`
 ADD PRIMARY KEY (`user_name`,`project_cod`,`package_id`,`comb_user`,`comb_project`,`comb_code`), ADD KEY `fk_pkgcomb_prjcombination1_idx` (`comb_user`,`comb_project`,`comb_code`);

--
-- Indices de la tabla `prjalias`
--
ALTER TABLE `prjalias`
 ADD PRIMARY KEY (`user_name`,`project_cod`,`tech_id`,`alias_id`), ADD KEY `fk_prjalias_prjtech1_idx` (`user_name`,`project_cod`,`tech_id`), ADD KEY `fk_prjalias_techalias1_idx` (`tech_used`,`alias_used`);

--
-- Indices de la tabla `prjcnty`
--
ALTER TABLE `prjcnty`
 ADD PRIMARY KEY (`user_name`,`project_cod`,`cnty_cod`), ADD KEY `fk_prjcnty_country1_idx` (`cnty_cod`);

--
-- Indices de la tabla `prjcombdet`
--
ALTER TABLE `prjcombdet`
 ADD PRIMARY KEY (`prjcomb_user`,`prjcomb_project`,`comb_code`,`user_name`,`project_cod`,`tech_id`,`alias_id`), ADD KEY `fk_prjcombdet_prjalias1_idx` (`user_name`,`project_cod`,`tech_id`,`alias_id`);

--
-- Indices de la tabla `prjcombination`
--
ALTER TABLE `prjcombination`
 ADD PRIMARY KEY (`user_name`,`project_cod`,`comb_code`);

--
-- Indices de la tabla `prjlang`
--
ALTER TABLE `prjlang`
 ADD PRIMARY KEY (`user_name`,`project_cod`,`lang_code`), ADD KEY `fk_prjlang_i18n1_idx` (`lang_code`);

--
-- Indices de la tabla `prjtech`
--
ALTER TABLE `prjtech`
 ADD PRIMARY KEY (`user_name`,`project_cod`,`tech_id`), ADD KEY `fk_prjtech_technology1_idx` (`tech_id`);

--
-- Indices de la tabla `project`
--
ALTER TABLE `project`
 ADD PRIMARY KEY (`user_name`,`project_cod`), ADD KEY `fk_project_user1_idx` (`user_name`);

--
-- Indices de la tabla `qstoption`
--
ALTER TABLE `qstoption`
 ADD PRIMARY KEY (`question_id`,`value_code`);

--
-- Indices de la tabla `qstprjopt`
--
ALTER TABLE `qstprjopt`
 ADD PRIMARY KEY (`project_user`,`project_cod`,`question_id`,`value_code`), ADD KEY `fk_qstprjopt_question1_idx` (`question_id`), ADD KEY `fk_qstprjopt_qstprjopt1_idx` (`parent_user`,`parent_project`,`parent_question`,`parent_value`);

--
-- Indices de la tabla `question`
--
ALTER TABLE `question`
 ADD PRIMARY KEY (`question_id`), ADD KEY `fk_question_user1_idx` (`user_name`), ADD KEY `fk_question_question1_idx` (`parent_question`);

--
-- Indices de la tabla `registry`
--
ALTER TABLE `registry`
 ADD PRIMARY KEY (`user_name`,`project_cod`,`question_id`), ADD KEY `fk_registry_question1_idx` (`question_id`), ADD KEY `fk_registry_regsection1_idx` (`section_user`,`section_project`,`section_id`);

--
-- Indices de la tabla `regsection`
--
ALTER TABLE `regsection`
 ADD PRIMARY KEY (`user_name`,`project_cod`,`section_id`);

--
-- Indices de la tabla `sector`
--
ALTER TABLE `sector`
 ADD PRIMARY KEY (`sector_cod`);

--
-- Indices de la tabla `techalias`
--
ALTER TABLE `techalias`
 ADD PRIMARY KEY (`tech_id`,`alias_id`), ADD KEY `fk_techalias_technology1_idx` (`tech_id`);

--
-- Indices de la tabla `technology`
--
ALTER TABLE `technology`
 ADD PRIMARY KEY (`tech_id`), ADD KEY `fk_crop_user1_idx` (`user_name`);

--
-- Indices de la tabla `user`
--
ALTER TABLE `user`
 ADD PRIMARY KEY (`user_name`), ADD KEY `fk_user_lkpcountry_idx` (`user_cnty`), ADD KEY `fk_user_lkpsector1_idx` (`user_sector`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `activitylog`
--
ALTER TABLE `activitylog`
MODIFY `log_id` int(9) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=4;
--
-- AUTO_INCREMENT de la tabla `apilog`
--
ALTER TABLE `apilog`
MODIFY `log_id` int(9) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT de la tabla `question`
--
ALTER TABLE `question`
MODIFY `question_id` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=154;
--
-- AUTO_INCREMENT de la tabla `sector`
--
ALTER TABLE `sector`
MODIFY `sector_cod` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=2;
--
-- AUTO_INCREMENT de la tabla `technology`
--
ALTER TABLE `technology`
MODIFY `tech_id` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=15;
--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `activitylog`
--
ALTER TABLE `activitylog`
ADD CONSTRAINT `fk_activitylog_user1` FOREIGN KEY (`log_user`) REFERENCES `user` (`user_name`) ON UPDATE NO ACTION;

--
-- Filtros para la tabla `apilog`
--
ALTER TABLE `apilog`
ADD CONSTRAINT `fk_apilog_user1` FOREIGN KEY (`log_user`) REFERENCES `user` (`user_name`) ON UPDATE NO ACTION;

--
-- Filtros para la tabla `assessment`
--
ALTER TABLE `assessment`
ADD CONSTRAINT `fk_assessment_asssection1` FOREIGN KEY (`section_user`, `section_project`, `section_id`) REFERENCES `asssection` (`user_name`, `project_cod`, `section_id`) ON DELETE CASCADE ON UPDATE NO ACTION,
ADD CONSTRAINT `fk_assessment_project1` FOREIGN KEY (`user_name`, `project_cod`) REFERENCES `project` (`user_name`, `project_cod`) ON DELETE CASCADE ON UPDATE NO ACTION,
ADD CONSTRAINT `fk_assessment_question1` FOREIGN KEY (`question_id`) REFERENCES `question` (`question_id`) ON DELETE CASCADE ON UPDATE NO ACTION;

--
-- Filtros para la tabla `asssection`
--
ALTER TABLE `asssection`
ADD CONSTRAINT `fk_asssection_project1` FOREIGN KEY (`user_name`, `project_cod`) REFERENCES `project` (`user_name`, `project_cod`) ON DELETE CASCADE ON UPDATE NO ACTION;

--
-- Filtros para la tabla `enumerator`
--
ALTER TABLE `enumerator`
ADD CONSTRAINT `fk_enumerator_project1` FOREIGN KEY (`user_name`, `project_cod`) REFERENCES `project` (`user_name`, `project_cod`) ON DELETE CASCADE ON UPDATE NO ACTION;

--
-- Filtros para la tabla `i18n_asssection`
--
ALTER TABLE `i18n_asssection`
ADD CONSTRAINT `fk_i18n_asssection_asssection1` FOREIGN KEY (`user_name`, `project_cod`, `section_id`) REFERENCES `asssection` (`user_name`, `project_cod`, `section_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
ADD CONSTRAINT `fk_i18n_asssection_i18n1` FOREIGN KEY (`lang_code`) REFERENCES `i18n` (`lang_code`) ON DELETE NO ACTION ON UPDATE NO ACTION;

--
-- Filtros para la tabla `i18n_prjalias`
--
ALTER TABLE `i18n_prjalias`
ADD CONSTRAINT `fk_i18n_prjalias_i18n1` FOREIGN KEY (`lang_code`) REFERENCES `i18n` (`lang_code`) ON DELETE NO ACTION ON UPDATE NO ACTION,
ADD CONSTRAINT `fk_i18n_prjalias_prjalias1` FOREIGN KEY (`user_name`, `project_cod`, `tech_id`, `alias_id`) REFERENCES `prjalias` (`user_name`, `project_cod`, `tech_id`, `alias_id`) ON DELETE NO ACTION ON UPDATE NO ACTION;

--
-- Filtros para la tabla `i18n_project`
--
ALTER TABLE `i18n_project`
ADD CONSTRAINT `fk_i18n_project_i18n1` FOREIGN KEY (`lang_code`) REFERENCES `i18n` (`lang_code`) ON DELETE NO ACTION ON UPDATE NO ACTION,
ADD CONSTRAINT `fk_i18n_project_project1` FOREIGN KEY (`user_name`, `project_cod`) REFERENCES `project` (`user_name`, `project_cod`) ON DELETE NO ACTION ON UPDATE NO ACTION;

--
-- Filtros para la tabla `i18n_qstoption`
--
ALTER TABLE `i18n_qstoption`
ADD CONSTRAINT `fk_i18n_qstoption_i18n1` FOREIGN KEY (`lang_code`) REFERENCES `i18n` (`lang_code`) ON DELETE NO ACTION ON UPDATE NO ACTION,
ADD CONSTRAINT `fk_i18n_qstoption_qstoption1` FOREIGN KEY (`question_id`, `value_code`) REFERENCES `qstoption` (`question_id`, `value_code`) ON DELETE NO ACTION ON UPDATE NO ACTION;

--
-- Filtros para la tabla `i18n_question`
--
ALTER TABLE `i18n_question`
ADD CONSTRAINT `fk_i18n_question_i18n1` FOREIGN KEY (`lang_code`) REFERENCES `i18n` (`lang_code`) ON DELETE NO ACTION ON UPDATE NO ACTION,
ADD CONSTRAINT `fk_i18n_question_question1` FOREIGN KEY (`question_id`) REFERENCES `question` (`question_id`) ON DELETE NO ACTION ON UPDATE NO ACTION;

--
-- Filtros para la tabla `i18n_regsection`
--
ALTER TABLE `i18n_regsection`
ADD CONSTRAINT `fk_i18n_regsection_i18n1` FOREIGN KEY (`lang_code`) REFERENCES `i18n` (`lang_code`) ON DELETE NO ACTION ON UPDATE NO ACTION,
ADD CONSTRAINT `fk_i18n_regsection_regsection1` FOREIGN KEY (`user_name`, `project_cod`, `section_id`) REFERENCES `regsection` (`user_name`, `project_cod`, `section_id`) ON DELETE NO ACTION ON UPDATE NO ACTION;

--
-- Filtros para la tabla `i18n_techalias`
--
ALTER TABLE `i18n_techalias`
ADD CONSTRAINT `fk_i18n_techalias_i18n1` FOREIGN KEY (`lang_code`) REFERENCES `i18n` (`lang_code`) ON DELETE NO ACTION ON UPDATE NO ACTION,
ADD CONSTRAINT `fk_i18n_techalias_techalias1` FOREIGN KEY (`tech_id`, `alias_id`) REFERENCES `techalias` (`tech_id`, `alias_id`) ON DELETE NO ACTION ON UPDATE NO ACTION;

--
-- Filtros para la tabla `i18n_technology`
--
ALTER TABLE `i18n_technology`
ADD CONSTRAINT `fk_i18n_technology_i18n1` FOREIGN KEY (`lang_code`) REFERENCES `i18n` (`lang_code`) ON DELETE NO ACTION ON UPDATE NO ACTION,
ADD CONSTRAINT `fk_i18n_technology_technology1` FOREIGN KEY (`tech_id`) REFERENCES `technology` (`tech_id`) ON DELETE NO ACTION ON UPDATE NO ACTION;

--
-- Filtros para la tabla `package`
--
ALTER TABLE `package`
ADD CONSTRAINT `fk_package_project1` FOREIGN KEY (`user_name`, `project_cod`) REFERENCES `project` (`user_name`, `project_cod`) ON DELETE CASCADE ON UPDATE NO ACTION;

--
-- Filtros para la tabla `pkgcomb`
--
ALTER TABLE `pkgcomb`
ADD CONSTRAINT `fk_pkgcomb_package1` FOREIGN KEY (`user_name`, `project_cod`, `package_id`) REFERENCES `package` (`user_name`, `project_cod`, `package_id`) ON DELETE CASCADE ON UPDATE NO ACTION,
ADD CONSTRAINT `fk_pkgcomb_prjcombination1` FOREIGN KEY (`comb_user`, `comb_project`, `comb_code`) REFERENCES `prjcombination` (`user_name`, `project_cod`, `comb_code`) ON DELETE CASCADE ON UPDATE NO ACTION;

--
-- Filtros para la tabla `prjalias`
--
ALTER TABLE `prjalias`
ADD CONSTRAINT `fk_prjalias_prjtech1` FOREIGN KEY (`user_name`, `project_cod`, `tech_id`) REFERENCES `prjtech` (`user_name`, `project_cod`, `tech_id`) ON DELETE CASCADE ON UPDATE NO ACTION,
ADD CONSTRAINT `fk_prjalias_techalias1` FOREIGN KEY (`tech_used`, `alias_used`) REFERENCES `techalias` (`tech_id`, `alias_id`) ON DELETE CASCADE ON UPDATE NO ACTION;

--
-- Filtros para la tabla `prjcnty`
--
ALTER TABLE `prjcnty`
ADD CONSTRAINT `fk_prjcnty_country1` FOREIGN KEY (`cnty_cod`) REFERENCES `country` (`cnty_cod`) ON DELETE CASCADE ON UPDATE NO ACTION,
ADD CONSTRAINT `fk_prjcnty_project1` FOREIGN KEY (`user_name`, `project_cod`) REFERENCES `project` (`user_name`, `project_cod`) ON DELETE CASCADE ON UPDATE NO ACTION;

--
-- Filtros para la tabla `prjcombdet`
--
ALTER TABLE `prjcombdet`
ADD CONSTRAINT `fk_prjcombdet_prjalias1` FOREIGN KEY (`user_name`, `project_cod`, `tech_id`, `alias_id`) REFERENCES `prjalias` (`user_name`, `project_cod`, `tech_id`, `alias_id`) ON DELETE CASCADE ON UPDATE NO ACTION,
ADD CONSTRAINT `fk_prjcombdet_prjcombination1` FOREIGN KEY (`prjcomb_user`, `prjcomb_project`, `comb_code`) REFERENCES `prjcombination` (`user_name`, `project_cod`, `comb_code`) ON DELETE CASCADE ON UPDATE NO ACTION;

--
-- Filtros para la tabla `prjcombination`
--
ALTER TABLE `prjcombination`
ADD CONSTRAINT `fk_prjcombination_project1` FOREIGN KEY (`user_name`, `project_cod`) REFERENCES `project` (`user_name`, `project_cod`) ON DELETE CASCADE ON UPDATE NO ACTION;

--
-- Filtros para la tabla `prjlang`
--
ALTER TABLE `prjlang`
ADD CONSTRAINT `fk_prjlang_i18n1` FOREIGN KEY (`lang_code`) REFERENCES `i18n` (`lang_code`) ON DELETE CASCADE ON UPDATE NO ACTION,
ADD CONSTRAINT `fk_prjlang_project1` FOREIGN KEY (`user_name`, `project_cod`) REFERENCES `project` (`user_name`, `project_cod`) ON DELETE CASCADE ON UPDATE NO ACTION;

--
-- Filtros para la tabla `prjtech`
--
ALTER TABLE `prjtech`
ADD CONSTRAINT `fk_prjtech_project1` FOREIGN KEY (`user_name`, `project_cod`) REFERENCES `project` (`user_name`, `project_cod`) ON DELETE CASCADE ON UPDATE NO ACTION,
ADD CONSTRAINT `fk_prjtech_technology1` FOREIGN KEY (`tech_id`) REFERENCES `technology` (`tech_id`) ON DELETE CASCADE ON UPDATE NO ACTION;

--
-- Filtros para la tabla `project`
--
ALTER TABLE `project`
ADD CONSTRAINT `fk_project_user1` FOREIGN KEY (`user_name`) REFERENCES `user` (`user_name`) ON UPDATE NO ACTION;

--
-- Filtros para la tabla `qstoption`
--
ALTER TABLE `qstoption`
ADD CONSTRAINT `fk_qstoption_question1` FOREIGN KEY (`question_id`) REFERENCES `question` (`question_id`) ON DELETE CASCADE ON UPDATE NO ACTION;

--
-- Filtros para la tabla `qstprjopt`
--
ALTER TABLE `qstprjopt`
ADD CONSTRAINT `fk_qstprjopt_project1` FOREIGN KEY (`project_user`, `project_cod`) REFERENCES `project` (`user_name`, `project_cod`) ON DELETE CASCADE ON UPDATE NO ACTION,
ADD CONSTRAINT `fk_qstprjopt_qstprjopt1` FOREIGN KEY (`parent_user`, `parent_project`, `parent_question`, `parent_value`) REFERENCES `qstprjopt` (`project_user`, `project_cod`, `question_id`, `value_code`) ON DELETE CASCADE ON UPDATE NO ACTION,
ADD CONSTRAINT `fk_qstprjopt_question1` FOREIGN KEY (`question_id`) REFERENCES `question` (`question_id`) ON DELETE CASCADE ON UPDATE NO ACTION;

--
-- Filtros para la tabla `question`
--
ALTER TABLE `question`
ADD CONSTRAINT `fk_question_question1` FOREIGN KEY (`parent_question`) REFERENCES `question` (`question_id`) ON DELETE CASCADE ON UPDATE NO ACTION,
ADD CONSTRAINT `fk_question_user1` FOREIGN KEY (`user_name`) REFERENCES `user` (`user_name`) ON UPDATE NO ACTION;

--
-- Filtros para la tabla `registry`
--
ALTER TABLE `registry`
ADD CONSTRAINT `fk_registry_project1` FOREIGN KEY (`user_name`, `project_cod`) REFERENCES `project` (`user_name`, `project_cod`) ON DELETE CASCADE ON UPDATE NO ACTION,
ADD CONSTRAINT `fk_registry_question1` FOREIGN KEY (`question_id`) REFERENCES `question` (`question_id`) ON DELETE CASCADE ON UPDATE NO ACTION,
ADD CONSTRAINT `fk_registry_regsection1` FOREIGN KEY (`section_user`, `section_project`, `section_id`) REFERENCES `regsection` (`user_name`, `project_cod`, `section_id`) ON DELETE CASCADE ON UPDATE NO ACTION;

--
-- Filtros para la tabla `regsection`
--
ALTER TABLE `regsection`
ADD CONSTRAINT `fk_regsection_project1` FOREIGN KEY (`user_name`, `project_cod`) REFERENCES `project` (`user_name`, `project_cod`) ON DELETE CASCADE ON UPDATE NO ACTION;

--
-- Filtros para la tabla `techalias`
--
ALTER TABLE `techalias`
ADD CONSTRAINT `fk_techalias_technology1` FOREIGN KEY (`tech_id`) REFERENCES `technology` (`tech_id`) ON DELETE CASCADE ON UPDATE NO ACTION;

--
-- Filtros para la tabla `technology`
--
ALTER TABLE `technology`
ADD CONSTRAINT `fk_crop_user1` FOREIGN KEY (`user_name`) REFERENCES `user` (`user_name`) ON DELETE CASCADE ON UPDATE NO ACTION;

--
-- Filtros para la tabla `user`
--
ALTER TABLE `user`
ADD CONSTRAINT `fk_user_lkpcountry` FOREIGN KEY (`user_cnty`) REFERENCES `country` (`cnty_cod`) ON UPDATE NO ACTION,
ADD CONSTRAINT `fk_user_lkpsector1` FOREIGN KEY (`user_sector`) REFERENCES `sector` (`sector_cod`) ON UPDATE NO ACTION;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
