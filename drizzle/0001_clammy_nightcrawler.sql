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
	CONSTRAINT `model_metrics_id` PRIMARY KEY(`id`)
);
