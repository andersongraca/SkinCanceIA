CREATE TABLE `dermatological_images` (
	`id` int AUTO_INCREMENT NOT NULL,
	`user_id` int NOT NULL,
	`file_name` varchar(255) NOT NULL,
	`image_path` text NOT NULL,
	`thumbnail_path` text,
	`file_size` int NOT NULL,
	`mime_type` varchar(50) NOT NULL,
	`description` text,
	`uploaded_at` timestamp NOT NULL DEFAULT (now()),
	`updated_at` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `dermatological_images_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `diagnoses` (
	`id` int AUTO_INCREMENT NOT NULL,
	`image_id` int NOT NULL,
	`user_id` int NOT NULL,
	`classification` varchar(50) NOT NULL,
	`confidence` int NOT NULL,
	`cnn_result` varchar(50),
	`cnn_confidence` int,
	`vit_result` varchar(50),
	`vit_confidence` int,
	`hybrid_result` varchar(50),
	`hybrid_confidence` int,
	`heatmap_path` text,
	`model_version` varchar(50),
	`diagnosed_at` timestamp NOT NULL DEFAULT (now()),
	`updated_at` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `diagnoses_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `model_metrics` (
	`id` int AUTO_INCREMENT NOT NULL,
	`model_name` varchar(100) NOT NULL,
	`model_version` varchar(50) NOT NULL,
	`accuracy` int NOT NULL,
	`sensitivity` int NOT NULL,
	`specificity` int NOT NULL,
	`f1_score` int NOT NULL,
	`auc` int NOT NULL,
	`precision` int NOT NULL,
	`sample_count` int NOT NULL,
	`updated_at` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `model_metrics_id` PRIMARY KEY(`id`),
	CONSTRAINT `model_metrics_model_version_unique` UNIQUE(`model_name`,`model_version`)
);
--> statement-breakpoint
CREATE TABLE `users` (
	`id` int AUTO_INCREMENT NOT NULL,
	`openId` varchar(64) NOT NULL,
	`name` text,
	`email` varchar(320),
	`loginMethod` varchar(64),
	`role` enum('user','admin') NOT NULL DEFAULT 'user',
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	`lastSignedIn` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `users_id` PRIMARY KEY(`id`),
	CONSTRAINT `users_openId_unique` UNIQUE(`openId`)
);
--> statement-breakpoint
ALTER TABLE `dermatological_images` ADD CONSTRAINT `dermatological_images_user_id_users_id_fk` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE `diagnoses` ADD CONSTRAINT `diagnoses_image_id_dermatological_images_id_fk` FOREIGN KEY (`image_id`) REFERENCES `dermatological_images`(`id`) ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE `diagnoses` ADD CONSTRAINT `diagnoses_user_id_users_id_fk` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
CREATE INDEX `dermatological_images_user_idx` ON `dermatological_images` (`user_id`);--> statement-breakpoint
CREATE INDEX `diagnoses_user_idx` ON `diagnoses` (`user_id`);--> statement-breakpoint
CREATE INDEX `diagnoses_image_idx` ON `diagnoses` (`image_id`);--> statement-breakpoint
CREATE INDEX `diagnoses_diagnosed_at_idx` ON `diagnoses` (`diagnosed_at`);