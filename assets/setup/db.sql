/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

CREATE DATABASE IF NOT EXISTS `cvewatch` /*!40100 DEFAULT CHARACTER SET utf8mb4 */;
USE `cvewatch`;

CREATE TABLE IF NOT EXISTS `auth_tokens` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `user_email` varchar(255) NOT NULL,
  `auth_type` varchar(255) NOT NULL,
  `selector` text NOT NULL,
  `token` longtext NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `expires_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `debian_cve` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cve_id` varchar(100) NOT NULL,
  `summary` longtext DEFAULT NULL,
  `scorev2` varchar(10) DEFAULT NULL,
  `scorev3` varchar(10) DEFAULT NULL,
  `link` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `cve_id_UNIQUE` (`cve_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `debian_package` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `debian_package_name` varchar(100) NOT NULL,
  `version` varchar(100) NOT NULL,
  `distribution` varchar(100) NOT NULL,
  `project_id` int(11) unsigned DEFAULT NULL,
  `is_vulnerable` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_debian_package_project1` (`project_id`),
  CONSTRAINT `fk_debian_package_project1` FOREIGN KEY (`project_id`) REFERENCES `project` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `debian_package_cve` (
  `debian_package_id` int(11) NOT NULL,
  `cve_id` int(11) NOT NULL,
  PRIMARY KEY (`debian_package_id`,`cve_id`),
  KEY `fk_debian_package_cve_cve1` (`cve_id`),
  CONSTRAINT `fk_debian_package_cve_cve1` FOREIGN KEY (`cve_id`) REFERENCES `debian_cve` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION,
  CONSTRAINT `fk_debian_package_cve_debian_package1` FOREIGN KEY (`debian_package_id`) REFERENCES `debian_package` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `project` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `project_name` varchar(100) NOT NULL,
  `operating_system` varchar(100) NOT NULL,
  `users_id` int(11) unsigned NOT NULL,
  `uploaded_file` longtext NOT NULL,
  `status_cve_check` varchar(50) DEFAULT NULL,
  `check_active` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_project_users` (`users_id`),
  CONSTRAINT `fk_project_users` FOREIGN KEY (`users_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `users` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `username` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `first_name` varchar(255) DEFAULT NULL,
  `last_name` varchar(255) DEFAULT NULL,
  `profile_image` varchar(255) NOT NULL DEFAULT '_defaultUser.png',
  `company` varchar(255) NOT NULL,
  `is_admin` varchar(255) DEFAULT NULL,
  `verified_at` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `deleted_at` timestamp NULL DEFAULT NULL,
  `last_login_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `users` (`id`, `username`, `email`, `password`, `first_name`, `last_name`, `profile_image`, `company`, `is_admin`, `verified_at`, `created_at`, `updated_at`, `deleted_at`, `last_login_at`) VALUES
	(1, 'admin', 'admin@example.com', '$2y$10$XqYWicW7glqMTOgyHTlniuGlh3ry2B1jZteYpIR7spAbcmqvn6Bga', 'Admin', 'Admin', '_defaultUser.png', 'Admin', 'true', '2021-08-30 14:50:03', '2021-08-30 13:19:30', '2021-09-21 14:45:16', NULL, '2021-09-20 13:59:43');

CREATE TABLE IF NOT EXISTS `yocto_cve` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cve_id` varchar(100) NOT NULL,
  `summary` longtext DEFAULT NULL,
  `scorev2` varchar(10) DEFAULT NULL,
  `scorev3` varchar(10) DEFAULT NULL,
  `link` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `cve_id_UNIQUE` (`cve_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `yocto_package` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `yocto_package_name` varchar(100) NOT NULL,
  `version` varchar(100) NOT NULL,
  `project_id` int(11) unsigned DEFAULT NULL,
  `is_vulnerable` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_yocto_package_project1` (`project_id`),
  CONSTRAINT `fk_yocto_package_project1` FOREIGN KEY (`project_id`) REFERENCES `project` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `yocto_package_cve` (
  `yocto_package_id` int(11) NOT NULL,
  `yocto_cve_id` int(11) NOT NULL,
  PRIMARY KEY (`yocto_package_id`,`yocto_cve_id`),
  KEY `fk_yocto_package_cve_cve1` (`yocto_cve_id`),
  CONSTRAINT `fk_yocto_package_cve_cve1` FOREIGN KEY (`yocto_cve_id`) REFERENCES `yocto_cve` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION,
  CONSTRAINT `fk_yocto_package_cve_yocto_package1` FOREIGN KEY (`yocto_package_id`) REFERENCES `yocto_package` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
