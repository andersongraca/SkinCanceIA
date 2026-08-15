ALTER TABLE `dermatological_images`
  ADD CONSTRAINT `dermatological_images_user_id_users_id_fk`
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE cascade ON UPDATE no action;
--> statement-breakpoint
ALTER TABLE `diagnoses`
  ADD CONSTRAINT `diagnoses_image_id_dermatological_images_id_fk`
  FOREIGN KEY (`image_id`) REFERENCES `dermatological_images`(`id`) ON DELETE cascade ON UPDATE no action;
--> statement-breakpoint
ALTER TABLE `diagnoses`
  ADD CONSTRAINT `diagnoses_user_id_users_id_fk`
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE cascade ON UPDATE no action;
--> statement-breakpoint
CREATE INDEX `dermatological_images_user_idx` ON `dermatological_images` (`user_id`);
--> statement-breakpoint
CREATE INDEX `diagnoses_user_idx` ON `diagnoses` (`user_id`);
--> statement-breakpoint
CREATE INDEX `diagnoses_image_idx` ON `diagnoses` (`image_id`);
--> statement-breakpoint
CREATE INDEX `diagnoses_diagnosed_at_idx` ON `diagnoses` (`diagnosed_at`);
--> statement-breakpoint
CREATE UNIQUE INDEX `model_metrics_model_version_unique` ON `model_metrics` (`model_name`, `model_version`);
