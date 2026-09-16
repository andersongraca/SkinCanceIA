CREATE TABLE `analysis_runs` (
	`id` int AUTO_INCREMENT NOT NULL,
	`image_id` int NOT NULL,
	`user_id` int NOT NULL,
	`run_id` varchar(64) NOT NULL,
	`status` varchar(32) NOT NULL,
	`rejection_reasons` text,
	`ood_score` double,
	`ood_threshold` double,
	`quality_score` double,
	`final_classification` varchar(50),
	`final_confidence` double,
	`abstained` int NOT NULL DEFAULT 0,
	`predictive_entropy` double,
	`tta_variance` double,
	`model_version` varchar(100),
	`thresholds` text,
	`model_results` text,
	`heatmap_paths` text,
	`started_at` timestamp NOT NULL DEFAULT (now()),
	`completed_at` timestamp,
	CONSTRAINT `analysis_runs_id` PRIMARY KEY(`id`),
	CONSTRAINT `analysis_runs_run_id_unique` UNIQUE(`run_id`)
);
--> statement-breakpoint
ALTER TABLE `analysis_runs` ADD CONSTRAINT `analysis_runs_image_id_dermatological_images_id_fk` FOREIGN KEY (`image_id`) REFERENCES `dermatological_images`(`id`) ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE `analysis_runs` ADD CONSTRAINT `analysis_runs_user_id_users_id_fk` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
CREATE INDEX `analysis_runs_image_idx` ON `analysis_runs` (`image_id`);--> statement-breakpoint
CREATE INDEX `analysis_runs_user_idx` ON `analysis_runs` (`user_id`);--> statement-breakpoint
CREATE INDEX `analysis_runs_started_at_idx` ON `analysis_runs` (`started_at`);