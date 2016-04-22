SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL';

CREATE SCHEMA IF NOT EXISTS `activae` ;

-- -----------------------------------------------------
-- Table `activae`.`profiles`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `activae`.`profiles` ;

CREATE  TABLE IF NOT EXISTS `activae`.`profiles` (
  `id` INT NULL AUTO_INCREMENT ,
  `name` VARCHAR(45) NOT NULL ,
  `description` VARCHAR(256) NULL ,
  PRIMARY KEY (`id`) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `activae`.`users`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `activae`.`users` ;

CREATE  TABLE IF NOT EXISTS `activae`.`users` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `username` VARCHAR(45) NOT NULL ,
  `password` VARCHAR(45) NOT NULL ,
  `forename` VARCHAR(45) NULL ,
  `surname1` VARCHAR(45) NULL ,
  `surname2` VARCHAR(45) NULL ,
  `email` VARCHAR(128) NULL ,
  `creation_stamp` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ,
  `profile_id` INT NOT NULL ,
  PRIMARY KEY (`id`) ,
  UNIQUE INDEX `username_UNIQUE` (`username` ASC) ,
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) ,
  INDEX `fk_users_profiles` (`profile_id` ASC) ,
  CONSTRAINT `fk_users_profiles`
    FOREIGN KEY (`profile_id` )
    REFERENCES `activae`.`profiles` (`id` )
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB
COMMENT = 'User information';


-- -----------------------------------------------------
-- Table `activae`.`formats`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `activae`.`formats` ;

CREATE  TABLE IF NOT EXISTS `activae`.`formats` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `format` VARCHAR(45) NULL ,
  `lossy_flag` TINYINT NOT NULL DEFAULT 0 ,
  PRIMARY KEY (`id`) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `activae`.`asset_types`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `activae`.`asset_types` ;

CREATE  TABLE IF NOT EXISTS `activae`.`asset_types` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `type` VARCHAR(45) NULL ,
  PRIMARY KEY (`id`) ,
  UNIQUE INDEX `type_UNIQUE` (`type` ASC) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `activae`.`licenses`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `activae`.`licenses` ;

CREATE  TABLE IF NOT EXISTS `activae`.`licenses` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `name` VARCHAR(45) NULL ,
  `description` VARCHAR(45) NULL ,
  PRIMARY KEY (`id`) ,
  UNIQUE INDEX `name_UNIQUE` (`name` ASC) )
ENGINE = InnoDB
COMMENT = 'License information';


-- -----------------------------------------------------
-- Table `activae`.`collections`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `activae`.`collections` ;

CREATE  TABLE IF NOT EXISTS `activae`.`collections` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `name` VARCHAR(256) NULL ,
  `creator_id` INT NOT NULL DEFAULT 1 ,
  PRIMARY KEY (`id`) ,
  INDEX `fk_collections_users1` (`creator_id` ASC) ,
  CONSTRAINT `fk_collections_users1`
    FOREIGN KEY (`creator_id` )
    REFERENCES `activae`.`users` (`id` )
    ON DELETE RESTRICT
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `activae`.`assets`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `activae`.`assets` ;

CREATE  TABLE IF NOT EXISTS `activae`.`assets` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `title` VARCHAR(256) NOT NULL ,
  `subject` VARCHAR(45) NULL ,
  `publisher_id` INT NULL ,
  `published_flag` TINYINT(1)  NOT NULL DEFAULT 0 ,
  `language` VARCHAR(45) NULL ,
  `views` INT NOT NULL DEFAULT 0 ,
  `date_modified` TIMESTAMP NULL ,
  `date_created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ,
  `date_available` TIMESTAMP NULL ,
  `asset_types_id` INT NOT NULL DEFAULT 1 ,
  `edited_flag` TINYINT(1)  NOT NULL DEFAULT 0 ,
  `licenses_id` INT NOT NULL ,
  `collections_id` INT NULL ,
  `creator_id` INT NOT NULL ,
  `version` INT NULL DEFAULT 1 ,
  `description` VARCHAR(8192) NULL ,
  `editor_id` INT NULL ,
  PRIMARY KEY (`id`) ,
  INDEX `fk_assets_asset_types1` (`asset_types_id` ASC) ,
  INDEX `fk_assets_licenses1` (`licenses_id` ASC) ,
  INDEX `fk_assets_users1` (`creator_id` ASC) ,
  CONSTRAINT `fk_assets_asset_types1`
    FOREIGN KEY (`asset_types_id` )
    REFERENCES `activae`.`asset_types` (`id` )
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_assets_licenses1`
    FOREIGN KEY (`licenses_id` )
    REFERENCES `activae`.`licenses` (`id` )
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_assets_users1`
    FOREIGN KEY (`creator_id` )
    REFERENCES `activae`.`users` (`id` )
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB
COMMENT = 'Asset information';


-- -----------------------------------------------------
-- Table `activae`.`profiles_has_roles`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `activae`.`profiles_has_roles` ;

CREATE  TABLE IF NOT EXISTS `activae`.`profiles_has_roles` (
  `profiles_id` INT NOT NULL ,
  `roles_id` INT NOT NULL ,
  PRIMARY KEY (`profiles_id`, `roles_id`) ,
  INDEX `fk_profiles_has_roles_profiles1` (`profiles_id` ASC) ,
  CONSTRAINT `fk_profiles_has_roles_profiles1`
    FOREIGN KEY (`profiles_id` )
    REFERENCES `activae`.`profiles` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `activae`.`parts`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `activae`.`parts` ;

CREATE  TABLE IF NOT EXISTS `activae`.`parts` (
  `source_id` INT NOT NULL ,
  `derivative_id` INT NOT NULL ,
  PRIMARY KEY (`source_id`, `derivative_id`) ,
  INDEX `fk_source` (`source_id` ASC) ,
  INDEX `fk_derivative` (`derivative_id` ASC) ,
  CONSTRAINT `fk_source`
    FOREIGN KEY (`source_id` )
    REFERENCES `activae`.`assets` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_derivative`
    FOREIGN KEY (`derivative_id` )
    REFERENCES `activae`.`assets` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `activae`.`children`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `activae`.`children` ;

CREATE  TABLE IF NOT EXISTS `activae`.`children` (
  `parent_id` INT NOT NULL ,
  `child_id` INT NOT NULL ,
  INDEX `fk_assets_has_assets_assets3` (`parent_id` ASC) ,
  INDEX `fk_assets_has_assets_assets4` (`child_id` ASC) ,
  PRIMARY KEY (`parent_id`, `child_id`) ,
  UNIQUE INDEX `child_id_UNIQUE` (`child_id` ASC) ,
  CONSTRAINT `fk_assets_has_assets_assets3`
    FOREIGN KEY (`parent_id` )
    REFERENCES `activae`.`assets` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_assets_has_assets_assets4`
    FOREIGN KEY (`child_id` )
    REFERENCES `activae`.`assets` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `activae`.`asset_formats`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `activae`.`asset_formats` ;

CREATE  TABLE IF NOT EXISTS `activae`.`asset_formats` (
  `source_id` INT NOT NULL ,
  `target_id` INT NOT NULL ,
  INDEX `fk_asset_formats_assets2` (`source_id` ASC) ,
  INDEX `fk_asset_formats_assets3` (`target_id` ASC) ,
  PRIMARY KEY (`source_id`, `target_id`) ,
  CONSTRAINT `fk_asset_formats_assets2`
    FOREIGN KEY (`source_id` )
    REFERENCES `activae`.`assets` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_asset_formats_assets3`
    FOREIGN KEY (`target_id` )
    REFERENCES `activae`.`assets` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `activae`.`asset_versions`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `activae`.`asset_versions` ;

CREATE  TABLE IF NOT EXISTS `activae`.`asset_versions` (
  `source_id` INT NOT NULL ,
  `derivative_id` INT NOT NULL ,
  INDEX `fk_asset_versions_assets1` (`source_id` ASC) ,
  INDEX `fk_asset_versions_assets2` (`derivative_id` ASC) ,
  PRIMARY KEY (`source_id`, `derivative_id`) ,
  CONSTRAINT `fk_asset_versions_assets1`
    FOREIGN KEY (`source_id` )
    REFERENCES `activae`.`assets` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_asset_versions_assets2`
    FOREIGN KEY (`derivative_id` )
    REFERENCES `activae`.`assets` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `activae`.`replacements`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `activae`.`replacements` ;

CREATE  TABLE IF NOT EXISTS `activae`.`replacements` (
  `replacer_id` INT NOT NULL ,
  `replacee_id` INT NOT NULL ,
  PRIMARY KEY (`replacer_id`, `replacee_id`) ,
  INDEX `fk_replacements_assets1` (`replacer_id` ASC) ,
  INDEX `fk_replacements_assets2` (`replacee_id` ASC) ,
  CONSTRAINT `fk_replacements_assets1`
    FOREIGN KEY (`replacer_id` )
    REFERENCES `activae`.`assets` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_replacements_assets2`
    FOREIGN KEY (`replacee_id` )
    REFERENCES `activae`.`assets` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `activae`.`sessions`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `activae`.`sessions` ;

CREATE  TABLE IF NOT EXISTS `activae`.`sessions` (
  `user` VARCHAR(32) NOT NULL ,
  `validation` VARCHAR(128) NULL ,
  `expiration` DATETIME NULL ,
  PRIMARY KEY (`user`) )
ENGINE = MEMORY
COMMENT = 'Web Sessions';


-- -----------------------------------------------------
-- Table `activae`.`transcode_targets`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `activae`.`transcode_targets` ;

CREATE  TABLE IF NOT EXISTS `activae`.`transcode_targets` (
  `source_id` INT NOT NULL ,
  `target_id` INT NOT NULL ,
  PRIMARY KEY (`source_id`, `target_id`) ,
  INDEX `fk_transcode_targets_formats1` (`source_id` ASC) ,
  INDEX `fk_transcode_targets_formats2` (`target_id` ASC) ,
  CONSTRAINT `fk_transcode_targets_formats1`
    FOREIGN KEY (`source_id` )
    REFERENCES `activae`.`formats` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_transcode_targets_formats2`
    FOREIGN KEY (`target_id` )
    REFERENCES `activae`.`formats` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `activae`.`fullsearch`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `activae`.`fullsearch` ;

CREATE  TABLE IF NOT EXISTS `activae`.`fullsearch` (
  `assets_id` INT NOT NULL ,
  `creator_name` VARCHAR(45) NULL ,
  `publisher_name` VARCHAR(45) NULL ,
  `collection_name` VARCHAR(256) NULL ,
  `title` VARCHAR(256) NULL ,
  `subject` VARCHAR(45) NULL ,
  `description` VARCHAR(8192) NULL ,
  PRIMARY KEY (`assets_id`) ,
  INDEX `fk_fullsearch_assets1` (`assets_id` ASC) ,
  FULLTEXT INDEX `idx_fullsearch` (`creator_name` ASC, `publisher_name` ASC, `collection_name` ASC, `title` ASC, `subject` ASC, `description` ASC) ,
  CONSTRAINT `fk_fullsearch_assets1`
    FOREIGN KEY (`assets_id` )
    REFERENCES `activae`.`assets` (`id` )
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = MyISAM
COMMENT = 'MyISAM table to use when performing FULLSEARCH';


-- -----------------------------------------------------
-- Table `activae`.`bookmarks`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `activae`.`bookmarks` ;

CREATE  TABLE IF NOT EXISTS `activae`.`bookmarks` (
  `assets_id` INT NOT NULL ,
  `users_id` INT NOT NULL ,
  PRIMARY KEY (`assets_id`, `users_id`) ,
  INDEX `fk_bookmarks_assets1` (`assets_id` ASC) ,
  INDEX `fk_bookmarks_users1` (`users_id` ASC) ,
  CONSTRAINT `fk_bookmarks_assets1`
    FOREIGN KEY (`assets_id` )
    REFERENCES `activae`.`assets` (`id` )
    ON DELETE CASCADE
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_bookmarks_users1`
    FOREIGN KEY (`users_id` )
    REFERENCES `activae`.`users` (`id` )
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `activae`.`files`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `activae`.`files` ;

CREATE  TABLE IF NOT EXISTS `activae`.`files` (
  `id` INT NOT NULL ,
  `filename` VARCHAR(256) NOT NULL ,
  `size` INT NULL DEFAULT 0 ,
  `extent` TIME NULL ,
  `bitrate` INT NULL ,
  `width` SMALLINT NULL ,
  `height` SMALLINT NULL ,
  `queue_flag` BIGINT NULL DEFAULT 0 ,
  `formats_id` INT NULL ,
  PRIMARY KEY (`id`) ,
  INDEX `fk_files_assets1` (`id` ASC) ,
  INDEX `fk_files_formats1` (`formats_id` ASC) ,
  CONSTRAINT `fk_files_assets1`
    FOREIGN KEY (`id` )
    REFERENCES `activae`.`assets` (`id` )
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_files_formats1`
    FOREIGN KEY (`formats_id` )
    REFERENCES `activae`.`formats` (`id` )
    ON DELETE RESTRICT
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `activae`.`acl_assets`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `activae`.`acl_assets` ;

CREATE  TABLE IF NOT EXISTS `activae`.`acl_assets` (
  `id_acl` INT NOT NULL AUTO_INCREMENT ,
  `id` INT NOT NULL ,
  `user_id` INT NULL ,
  `role` INT NULL ,
  `ad` TINYINT(1)  NULL DEFAULT 0 ,
  `ed` TINYINT(1)  NULL DEFAULT 0 ,
  `rm` TINYINT(1)  NULL DEFAULT 0 ,
  `co` TINYINT(1)  NULL DEFAULT 0 ,
  PRIMARY KEY (`id_acl`, `id`) ,
  INDEX `fk_acl_asset_assets1` (`id` ASC) ,
  CONSTRAINT `fk_acl_asset_assets1`
    FOREIGN KEY (`id` )
    REFERENCES `activae`.`assets` (`id` )
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `activae`.`acl_collections`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `activae`.`acl_collections` ;

CREATE  TABLE IF NOT EXISTS `activae`.`acl_collections` (
  `id_acl` INT NOT NULL AUTO_INCREMENT ,
  `id` INT NOT NULL ,
  `user_id` INT NULL ,
  `role` INT NULL ,
  `ad` TINYINT(1)  NULL DEFAULT 0 ,
  `ed` TINYINT(1)  NULL DEFAULT 0 ,
  `rm` TINYINT(1)  NULL DEFAULT 0 ,
  `co` TINYINT(1)  NULL DEFAULT 0 ,
  PRIMARY KEY (`id_acl`, `id`) ,
  INDEX `fk_acl_asset_collections1` (`id` ASC) ,
  CONSTRAINT `fk_acl_asset_collections1`
    FOREIGN KEY (`id` )
    REFERENCES `activae`.`collections` (`id` )
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Placeholder table for view `activae`.`view_asset_versions`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `activae`.`view_asset_versions` (`source_id` INT, `derivative_id` INT, `version` INT);

-- -----------------------------------------------------
-- Placeholder table for view `activae`.`view_asset_formats`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `activae`.`view_asset_formats` (`id` INT, `source_id` INT, `formats_id` INT, `format` INT);

-- -----------------------------------------------------
-- Placeholder table for view `activae`.`view_asset_lookup`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `activae`.`view_asset_lookup` (`id` INT, `title` INT, `subject` INT, `published_flag` INT, `edited_flag` INT, `publisher_id` INT, `publisher_name` INT, `creator_id` INT, `creator_name` INT, `version` INT, `language` INT, `views` INT, `collections_id` INT, `collection_name` INT, `date_modified` INT, `date_created` INT, `date_available` INT, `asset_types_id` INT, `type` INT, `licenses_id` INT, `description` INT, `extent` INT, `filename` INT, `queue_flag` INT, `size` INT, `bitrate` INT, `width` INT, `height` INT, `formats_id` INT, `format` INT);

-- -----------------------------------------------------
-- View `activae`.`view_asset_versions`
-- -----------------------------------------------------
DROP VIEW IF EXISTS `activae`.`view_asset_versions` ;
DROP TABLE IF EXISTS `activae`.`view_asset_versions`;
-- This view shows versions of a given source Asset
CREATE  OR REPLACE VIEW `activae`.`view_asset_versions` AS
SELECT source_id, derivative_id, version FROM assets JOIN asset_versions ON assets.id=asset_versions.derivative_id;

;

-- -----------------------------------------------------
-- View `activae`.`view_asset_formats`
-- -----------------------------------------------------
DROP VIEW IF EXISTS `activae`.`view_asset_formats` ;
DROP TABLE IF EXISTS `activae`.`view_asset_formats`;
-- This view shows  the format_id, format name and source-asset of the assets
CREATE  OR REPLACE VIEW `activae`.`view_asset_formats` AS
SELECT assets.id, source_id, formats_id, format 
FROM assets 
LEFT JOIN files ON assets.id = files.id
LEFT JOIN asset_formats ON assets.id=asset_formats.target_id
JOIN formats ON formats.id = files.formats_id;
;

-- -----------------------------------------------------
-- View `activae`.`view_asset_lookup`
-- -----------------------------------------------------
DROP VIEW IF EXISTS `activae`.`view_asset_lookup` ;
DROP TABLE IF EXISTS `activae`.`view_asset_lookup`;
-- This view is used to perform lookups by field
CREATE  OR REPLACE VIEW `activae`.`view_asset_lookup` AS
SELECT assets.id, title, subject,  published_flag, edited_flag,
publisher_id, users.username AS publisher_name,
assets.creator_id, users2.username AS creator_name,
version, language, views, 
collections_id, collections.name AS collection_name,
date_modified, date_created, date_available,  
asset_types_id, type, licenses_id, description,
-- files
extent, filename, queue_flag, size, bitrate, width, height, formats_id,
-- formats
format
FROM assets  
JOIN asset_types ON asset_types_id = asset_types.id
LEFT JOIN collections ON collections_id = collections.id
LEFT JOIN users ON users.id = assets.publisher_id
LEFT JOIN users AS users2 ON users2.id = assets.creator_id
LEFT JOIN files ON assets.id = files.id
LEFT JOIN formats on formats_id = formats.id;

DELIMITER $$

USE `activae`$$
DROP TRIGGER IF EXISTS `activae`.`fs_upd` $$
USE `activae`$$


CREATE TRIGGER fs_upd AFTER UPDATE ON assets FOR EACH ROW
    BEGIN
	DELETE FROM fullsearch WHERE assets_id=NEW.id;
	INSERT INTO fullsearch
		SELECT id, creator_name, publisher_name, collection_name, title, subject,description 
		FROM view_asset_lookup 
		WHERE id=NEW.id;
    END$$


USE `activae`$$
DROP TRIGGER IF EXISTS `activae`.`fs_del` $$
USE `activae`$$


CREATE TRIGGER fs_del BEFORE DELETE ON assets FOR EACH ROW
    BEGIN
	DELETE FROM fullsearch WHERE assets_id=OLD.id;
    END$$


USE `activae`$$
DROP TRIGGER IF EXISTS `activae`.`fs_ins` $$
USE `activae`$$
CREATE TRIGGER fs_ins AFTER INSERT ON assets FOR EACH ROW
    BEGIN
	INSERT INTO fullsearch
		SELECT id, creator_name, publisher_name, collection_name, title, subject,description 
		FROM view_asset_lookup 
		WHERE id=NEW.id;
    END$$


DELIMITER ;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

-- -----------------------------------------------------
-- Data for table `activae`.`profiles`
-- -----------------------------------------------------
SET AUTOCOMMIT=0;
INSERT INTO `activae`.`profiles` (`id`, `name`, `description`) VALUES (1, 'admin', 'Responsable DAM');
INSERT INTO `activae`.`profiles` (`id`, `name`, `description`) VALUES (2, 'director', 'Director de programa');
INSERT INTO `activae`.`profiles` (`id`, `name`, `description`) VALUES (3, 'productor', 'Productor');
INSERT INTO `activae`.`profiles` (`id`, `name`, `description`) VALUES (4, 'realizador', 'Realizador');
INSERT INTO `activae`.`profiles` (`id`, `name`, `description`) VALUES (5, 'editor', 'Editor');
INSERT INTO `activae`.`profiles` (`id`, `name`, `description`) VALUES (6, 'regidor', 'Regidor');
INSERT INTO `activae`.`profiles` (`id`, `name`, `description`) VALUES (7, 'guionista', 'Guionista');
INSERT INTO `activae`.`profiles` (`id`, `name`, `description`) VALUES (8, 'redactor', 'Redactor');
INSERT INTO `activae`.`profiles` (`id`, `name`, `description`) VALUES (9, 'documentalista', 'Documentalista');
INSERT INTO `activae`.`profiles` (`id`, `name`, `description`) VALUES (10, 'script', 'Script');
INSERT INTO `activae`.`profiles` (`id`, `name`, `description`) VALUES (11, 'disenador', 'Disenador grafico');
INSERT INTO `activae`.`profiles` (`id`, `name`, `description`) VALUES (12, 'reportero', 'Reportero grafico');
INSERT INTO `activae`.`profiles` (`id`, `name`, `description`) VALUES (13, 'efectos', 'Tecnico de efectos de sala');
INSERT INTO `activae`.`profiles` (`id`, `name`, `description`) VALUES (14, 'montador', 'Tecnico en equipos audiovisuales');
INSERT INTO `activae`.`profiles` (`id`, `name`, `description`) VALUES (15, 'actor', 'Actor');
INSERT INTO `activae`.`profiles` (`id`, `name`, `description`) VALUES (16, 'presentador', 'Presentador');

COMMIT;

-- -----------------------------------------------------
-- Data for table `activae`.`users`
-- -----------------------------------------------------
SET AUTOCOMMIT=0;
INSERT INTO `activae`.`users` (`id`, `username`, `password`, `forename`, `surname1`, `surname2`, `email`, `creation_stamp`, `profile_id`) VALUES (1, 'admin', '21232f297a57a5a743894a0e4a801fc3', 'Admin', 'de', 'Activae', 'root@localhost', NULL, 1);

COMMIT;

-- -----------------------------------------------------
-- Data for table `activae`.`formats`
-- -----------------------------------------------------
SET AUTOCOMMIT=0;
INSERT INTO `activae`.`formats` (`id`, `format`, `lossy_flag`) VALUES (1, 'mp4', '1');
INSERT INTO `activae`.`formats` (`id`, `format`, `lossy_flag`) VALUES (2, 'mov', '1');
INSERT INTO `activae`.`formats` (`id`, `format`, `lossy_flag`) VALUES (3, 'ogv', '1');
INSERT INTO `activae`.`formats` (`id`, `format`, `lossy_flag`) VALUES (4, 'png', '0');
INSERT INTO `activae`.`formats` (`id`, `format`, `lossy_flag`) VALUES (5, 'jpg', '1');
INSERT INTO `activae`.`formats` (`id`, `format`, `lossy_flag`) VALUES (6, 'avi', '1');
INSERT INTO `activae`.`formats` (`id`, `format`, `lossy_flag`) VALUES (7, 'ogg', '1');
INSERT INTO `activae`.`formats` (`id`, `format`, `lossy_flag`) VALUES (8, 'mp3', '1');
INSERT INTO `activae`.`formats` (`id`, `format`, `lossy_flag`) VALUES (9, 'gif', '1');
INSERT INTO `activae`.`formats` (`id`, `format`, `lossy_flag`) VALUES (10, 'mpg', '1');
INSERT INTO `activae`.`formats` (`id`, `format`, `lossy_flag`) VALUES (11, 'jpeg', '1');

COMMIT;

-- -----------------------------------------------------
-- Data for table `activae`.`asset_types`
-- -----------------------------------------------------
SET AUTOCOMMIT=0;
INSERT INTO `activae`.`asset_types` (`id`, `type`) VALUES (1, 'Misc');
INSERT INTO `activae`.`asset_types` (`id`, `type`) VALUES (2, 'Video');
INSERT INTO `activae`.`asset_types` (`id`, `type`) VALUES (3, 'Audio');
INSERT INTO `activae`.`asset_types` (`id`, `type`) VALUES (4, 'Imagen');
INSERT INTO `activae`.`asset_types` (`id`, `type`) VALUES (5, 'Documento');

COMMIT;

-- -----------------------------------------------------
-- Data for table `activae`.`licenses`
-- -----------------------------------------------------
SET AUTOCOMMIT=0;
INSERT INTO `activae`.`licenses` (`id`, `name`, `description`) VALUES (1, 'Rights Reserved', 'All Rights Reserved');
INSERT INTO `activae`.`licenses` (`id`, `name`, `description`) VALUES (2, 'CC-BY', 'Creative Commons Attribution');
INSERT INTO `activae`.`licenses` (`id`, `name`, `description`) VALUES (3, 'CC-BY-ND', 'Creative Commons Attribution No Derivatives');
INSERT INTO `activae`.`licenses` (`id`, `name`, `description`) VALUES (4, 'CC-BY-SA', 'Creative Commons Attribution Share Alike');
INSERT INTO `activae`.`licenses` (`id`, `name`, `description`) VALUES (5, 'CC-BY-NC', 'Creative Commons Attribution Non-Commercial');
INSERT INTO `activae`.`licenses` (`id`, `name`, `description`) VALUES (6, 'CC-BY-NC-SA', 'Creative Commons Attribution Non-Commercial Share Alike');
INSERT INTO `activae`.`licenses` (`id`, `name`, `description`) VALUES (7, 'CC-BY-NC-ND', 'Creative Commons Attribution Non-Commercial No Derivatives');
INSERT INTO `activae`.`licenses` (`id`, `name`, `description`) VALUES (8, 'PD', 'Public Domain');
INSERT INTO `activae`.`licenses` (`id`, `name`, `description`) VALUES (9, 'GNU-FDL', 'GNU Free Documentation Licencse');

COMMIT;

-- -----------------------------------------------------
-- Data for table `activae`.`profiles_has_roles`
-- -----------------------------------------------------
SET AUTOCOMMIT=0;
INSERT INTO `activae`.`profiles_has_roles` (`profiles_id`, `roles_id`) VALUES (1, 1);
INSERT INTO `activae`.`profiles_has_roles` (`profiles_id`, `roles_id`) VALUES (1, 2);
INSERT INTO `activae`.`profiles_has_roles` (`profiles_id`, `roles_id`) VALUES (1, 3);
INSERT INTO `activae`.`profiles_has_roles` (`profiles_id`, `roles_id`) VALUES (1, 4);
INSERT INTO `activae`.`profiles_has_roles` (`profiles_id`, `roles_id`) VALUES (1, 5);
INSERT INTO `activae`.`profiles_has_roles` (`profiles_id`, `roles_id`) VALUES (2, 2);
INSERT INTO `activae`.`profiles_has_roles` (`profiles_id`, `roles_id`) VALUES (2, 3);
INSERT INTO `activae`.`profiles_has_roles` (`profiles_id`, `roles_id`) VALUES (2, 4);
INSERT INTO `activae`.`profiles_has_roles` (`profiles_id`, `roles_id`) VALUES (2, 5);
INSERT INTO `activae`.`profiles_has_roles` (`profiles_id`, `roles_id`) VALUES (3, 5);
INSERT INTO `activae`.`profiles_has_roles` (`profiles_id`, `roles_id`) VALUES (4, 4);
INSERT INTO `activae`.`profiles_has_roles` (`profiles_id`, `roles_id`) VALUES (4, 5);
INSERT INTO `activae`.`profiles_has_roles` (`profiles_id`, `roles_id`) VALUES (5, 2);
INSERT INTO `activae`.`profiles_has_roles` (`profiles_id`, `roles_id`) VALUES (5, 3);
INSERT INTO `activae`.`profiles_has_roles` (`profiles_id`, `roles_id`) VALUES (5, 5);
INSERT INTO `activae`.`profiles_has_roles` (`profiles_id`, `roles_id`) VALUES (6, 5);
INSERT INTO `activae`.`profiles_has_roles` (`profiles_id`, `roles_id`) VALUES (7, 2);
INSERT INTO `activae`.`profiles_has_roles` (`profiles_id`, `roles_id`) VALUES (7, 3);
INSERT INTO `activae`.`profiles_has_roles` (`profiles_id`, `roles_id`) VALUES (7, 4);
INSERT INTO `activae`.`profiles_has_roles` (`profiles_id`, `roles_id`) VALUES (7, 5);
INSERT INTO `activae`.`profiles_has_roles` (`profiles_id`, `roles_id`) VALUES (8, 2);
INSERT INTO `activae`.`profiles_has_roles` (`profiles_id`, `roles_id`) VALUES (8, 3);
INSERT INTO `activae`.`profiles_has_roles` (`profiles_id`, `roles_id`) VALUES (8, 5);
INSERT INTO `activae`.`profiles_has_roles` (`profiles_id`, `roles_id`) VALUES (9, 2);
INSERT INTO `activae`.`profiles_has_roles` (`profiles_id`, `roles_id`) VALUES (9, 3);
INSERT INTO `activae`.`profiles_has_roles` (`profiles_id`, `roles_id`) VALUES (9, 5);
INSERT INTO `activae`.`profiles_has_roles` (`profiles_id`, `roles_id`) VALUES (10, 2);
INSERT INTO `activae`.`profiles_has_roles` (`profiles_id`, `roles_id`) VALUES (10, 3);
INSERT INTO `activae`.`profiles_has_roles` (`profiles_id`, `roles_id`) VALUES (10, 5);
INSERT INTO `activae`.`profiles_has_roles` (`profiles_id`, `roles_id`) VALUES (11, 2);
INSERT INTO `activae`.`profiles_has_roles` (`profiles_id`, `roles_id`) VALUES (11, 3);
INSERT INTO `activae`.`profiles_has_roles` (`profiles_id`, `roles_id`) VALUES (11, 5);
INSERT INTO `activae`.`profiles_has_roles` (`profiles_id`, `roles_id`) VALUES (12, 2);
INSERT INTO `activae`.`profiles_has_roles` (`profiles_id`, `roles_id`) VALUES (12, 3);
INSERT INTO `activae`.`profiles_has_roles` (`profiles_id`, `roles_id`) VALUES (12, 5);
INSERT INTO `activae`.`profiles_has_roles` (`profiles_id`, `roles_id`) VALUES (13, 2);
INSERT INTO `activae`.`profiles_has_roles` (`profiles_id`, `roles_id`) VALUES (13, 3);
INSERT INTO `activae`.`profiles_has_roles` (`profiles_id`, `roles_id`) VALUES (13, 5);
INSERT INTO `activae`.`profiles_has_roles` (`profiles_id`, `roles_id`) VALUES (14, 2);
INSERT INTO `activae`.`profiles_has_roles` (`profiles_id`, `roles_id`) VALUES (14, 3);
INSERT INTO `activae`.`profiles_has_roles` (`profiles_id`, `roles_id`) VALUES (14, 5);
INSERT INTO `activae`.`profiles_has_roles` (`profiles_id`, `roles_id`) VALUES (15, 5);
INSERT INTO `activae`.`profiles_has_roles` (`profiles_id`, `roles_id`) VALUES (16, 5);
INSERT INTO `activae`.`profiles_has_roles` (`profiles_id`, `roles_id`) VALUES (3, 3);
INSERT INTO `activae`.`profiles_has_roles` (`profiles_id`, `roles_id`) VALUES (3, 4);

COMMIT;
