-- TechnoPark / MySQL 8.4. Schema dan data master publik, tanpa akun atau booking.

-- Untuk instalasi aplikasi gunakan Alembic + seed; jangan impor file ini lalu menjalankan migrasi awal.

SET NAMES utf8mb4;

CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `email` varchar(254) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` enum('user','admin') NOT NULL DEFAULT 'user',
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `rooms` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `capacity` int NOT NULL,
  `description` text NOT NULL,
  `thumbnail` varchar(255) NOT NULL,
  `visual_variant` int NOT NULL DEFAULT '0',
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `time_slots` (
  `id` int NOT NULL AUTO_INCREMENT,
  `start_time` time NOT NULL,
  `end_time` time NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `facilities` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(80) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `holidays` (
  `holiday_date` date NOT NULL,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`holiday_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `room_facilities` (
  `room_id` int NOT NULL,
  `facility_id` int NOT NULL,
  PRIMARY KEY (`room_id`,`facility_id`),
  KEY `facility_id` (`facility_id`),
  CONSTRAINT `room_facilities_ibfk_1` FOREIGN KEY (`room_id`) REFERENCES `rooms` (`id`) ON DELETE CASCADE,
  CONSTRAINT `room_facilities_ibfk_2` FOREIGN KEY (`facility_id`) REFERENCES `facilities` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `bookings` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `room_id` int NOT NULL,
  `time_slot_id` int NOT NULL,
  `usage_date` date NOT NULL,
  `status` enum('upcoming','completed','cancelled') NOT NULL DEFAULT 'upcoming',
  `active_date_key` date GENERATED ALWAYS AS ((case when (`status` = _utf8mb4'cancelled') then NULL else `usage_date` end)) STORED,
  `active_slot_key` int GENERATED ALWAYS AS ((case when (`status` = _utf8mb4'cancelled') then NULL else `time_slot_id` end)) STORED,
  `created_at` datetime NOT NULL,
  `cancelled_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_booking_user_active_date` (`user_id`,`active_date_key`),
  UNIQUE KEY `uq_booking_room_date_slot` (`room_id`,`usage_date`,`active_slot_key`),
  KEY `time_slot_id` (`time_slot_id`),
  CONSTRAINT `bookings_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `bookings_ibfk_2` FOREIGN KEY (`room_id`) REFERENCES `rooms` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `bookings_ibfk_3` FOREIGN KEY (`time_slot_id`) REFERENCES `time_slots` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `rooms` (id, name, capacity, description, thumbnail, visual_variant, is_active) VALUES (1, 'Ruang Adi Soemarmo', 4, 'Ruang ringkas untuk belajar bersama dan diskusi kelompok kecil dengan monitor pendukung.', '/images/rooms/adi-soemarmo.webp', 0, 1);

INSERT INTO `rooms` (id, name, capacity, description, thumbnail, visual_variant, is_active) VALUES (2, 'Ruang Balapan', 4, 'Tempat berdiskusi dalam kelompok kecil, dilengkapi whiteboard untuk merangkai ide.', '/images/rooms/balapan.webp', 1, 1);

INSERT INTO `rooms` (id, name, capacity, description, thumbnail, visual_variant, is_active) VALUES (3, 'Ruang Jebres', 4, 'Workspace untuk kerja kelompok dan sesi fokus bersama hingga empat peserta.', '/images/rooms/jebres.webp', 2, 1);

INSERT INTO `rooms` (id, name, capacity, description, thumbnail, visual_variant, is_active) VALUES (4, 'Ruang Tirtonadi', 6, 'Ruang meeting untuk meninjau pekerjaan, menyusun rencana, dan presentasi kelompok.', '/images/rooms/tirtonadi.webp', 3, 1);

INSERT INTO `rooms` (id, name, capacity, description, thumbnail, visual_variant, is_active) VALUES (5, 'Ruang Purwosari', 6, 'Ruang diskusi enam peserta dengan monitor dan whiteboard untuk kerja kolaboratif.', '/images/rooms/purwosari.webp', 4, 1);

INSERT INTO `rooms` (id, name, capacity, description, thumbnail, visual_variant, is_active) VALUES (6, 'Ruang Solo Kota', 6, 'Workspace untuk rapat komunitas, kelompok belajar, dan pertemuan tim kecil.', '/images/rooms/solo-kota.webp', 5, 1);

INSERT INTO `rooms` (id, name, capacity, description, thumbnail, visual_variant, is_active) VALUES (7, 'Ruang Batik Solo Trans', 8, 'Ruang kolaborasi delapan peserta dengan proyektor untuk presentasi dan berbagi gagasan.', '/images/rooms/batik-solo-trans.webp', 6, 1);

INSERT INTO `rooms` (id, name, capacity, description, thumbnail, visual_variant, is_active) VALUES (8, 'Ruang Kerten', 8, 'Ruang kerja kelompok yang mendukung diskusi, presentasi, dan perencanaan tim.', '/images/rooms/kerten.webp', 7, 1);

INSERT INTO `rooms` (id, name, capacity, description, thumbnail, visual_variant, is_active) VALUES (9, 'Ruang Kleco', 8, 'Workspace delapan peserta untuk lokakarya kecil dan sesi kolaborasi bersama.', '/images/rooms/kleco.webp', 8, 1);

INSERT INTO `facilities` (id, name) VALUES (4, 'AC');

INSERT INTO `facilities` (id, name) VALUES (2, 'Monitor');

INSERT INTO `facilities` (id, name) VALUES (5, 'Proyektor');

INSERT INTO `facilities` (id, name) VALUES (6, 'Stopkontak');

INSERT INTO `facilities` (id, name) VALUES (3, 'Whiteboard');

INSERT INTO `facilities` (id, name) VALUES (1, 'Wi-Fi');

INSERT INTO `time_slots` (id, start_time, end_time) VALUES (1, '09:00:00', '11:00:00');

INSERT INTO `time_slots` (id, start_time, end_time) VALUES (2, '11:00:00', '13:00:00');

INSERT INTO `time_slots` (id, start_time, end_time) VALUES (3, '13:00:00', '15:00:00');

INSERT INTO `time_slots` (id, start_time, end_time) VALUES (4, '15:00:00', '17:00:00');

INSERT INTO `time_slots` (id, start_time, end_time) VALUES (5, '17:00:00', '19:00:00');

INSERT INTO `holidays` (holiday_date, name) VALUES ('2026-01-01', 'Tahun Baru Masehi');

INSERT INTO `holidays` (holiday_date, name) VALUES ('2026-01-16', 'Isra Mikraj');

INSERT INTO `holidays` (holiday_date, name) VALUES ('2026-02-17', 'Tahun Baru Imlek');

INSERT INTO `holidays` (holiday_date, name) VALUES ('2026-03-19', 'Nyepi');

INSERT INTO `holidays` (holiday_date, name) VALUES ('2026-03-21', 'Idul Fitri');

INSERT INTO `holidays` (holiday_date, name) VALUES ('2026-03-22', 'Idul Fitri');

INSERT INTO `holidays` (holiday_date, name) VALUES ('2026-04-03', 'Wafat Yesus Kristus');

INSERT INTO `holidays` (holiday_date, name) VALUES ('2026-04-05', 'Paskah');

INSERT INTO `holidays` (holiday_date, name) VALUES ('2026-05-01', 'Hari Buruh');

INSERT INTO `holidays` (holiday_date, name) VALUES ('2026-05-14', 'Kenaikan Yesus Kristus');

INSERT INTO `holidays` (holiday_date, name) VALUES ('2026-05-27', 'Idul Adha');

INSERT INTO `holidays` (holiday_date, name) VALUES ('2026-05-31', 'Waisak');

INSERT INTO `holidays` (holiday_date, name) VALUES ('2026-06-01', 'Hari Lahir Pancasila');

INSERT INTO `holidays` (holiday_date, name) VALUES ('2026-06-16', 'Tahun Baru Islam');

INSERT INTO `holidays` (holiday_date, name) VALUES ('2026-08-17', 'Kemerdekaan RI');

INSERT INTO `holidays` (holiday_date, name) VALUES ('2026-08-25', 'Maulid Nabi Muhammad');

INSERT INTO `holidays` (holiday_date, name) VALUES ('2026-12-25', 'Natal');

INSERT INTO `holidays` (holiday_date, name) VALUES ('2027-01-01', 'Tahun Baru Masehi');

INSERT INTO `holidays` (holiday_date, name) VALUES ('2027-01-05', 'Isra Mikraj');

INSERT INTO `holidays` (holiday_date, name) VALUES ('2027-02-06', 'Tahun Baru Imlek');

INSERT INTO `holidays` (holiday_date, name) VALUES ('2027-03-08', 'Nyepi');

INSERT INTO `holidays` (holiday_date, name) VALUES ('2027-03-10', 'Idul Fitri');

INSERT INTO `holidays` (holiday_date, name) VALUES ('2027-03-11', 'Idul Fitri');

INSERT INTO `holidays` (holiday_date, name) VALUES ('2027-03-26', 'Wafat Yesus Kristus');

INSERT INTO `holidays` (holiday_date, name) VALUES ('2027-03-28', 'Paskah');

INSERT INTO `holidays` (holiday_date, name) VALUES ('2027-05-01', 'Hari Buruh');

INSERT INTO `holidays` (holiday_date, name) VALUES ('2027-05-06', 'Kenaikan Yesus Kristus');

INSERT INTO `holidays` (holiday_date, name) VALUES ('2027-05-17', 'Idul Adha');

INSERT INTO `holidays` (holiday_date, name) VALUES ('2027-05-20', 'Waisak');

INSERT INTO `holidays` (holiday_date, name) VALUES ('2027-06-01', 'Hari Lahir Pancasila');

INSERT INTO `holidays` (holiday_date, name) VALUES ('2027-06-06', 'Tahun Baru Islam');

INSERT INTO `holidays` (holiday_date, name) VALUES ('2027-08-15', 'Maulid Nabi Muhammad');

INSERT INTO `holidays` (holiday_date, name) VALUES ('2027-08-17', 'Kemerdekaan RI');

INSERT INTO `holidays` (holiday_date, name) VALUES ('2027-12-25', 'Natal');

INSERT INTO `holidays` (holiday_date, name) VALUES ('2027-12-26', 'Isra Mikraj');

INSERT INTO room_facilities (room_id, facility_id) VALUES (1, 1);

INSERT INTO room_facilities (room_id, facility_id) VALUES (2, 1);

INSERT INTO room_facilities (room_id, facility_id) VALUES (3, 1);

INSERT INTO room_facilities (room_id, facility_id) VALUES (4, 1);

INSERT INTO room_facilities (room_id, facility_id) VALUES (5, 1);

INSERT INTO room_facilities (room_id, facility_id) VALUES (6, 1);

INSERT INTO room_facilities (room_id, facility_id) VALUES (7, 1);

INSERT INTO room_facilities (room_id, facility_id) VALUES (8, 1);

INSERT INTO room_facilities (room_id, facility_id) VALUES (9, 1);

INSERT INTO room_facilities (room_id, facility_id) VALUES (1, 2);

INSERT INTO room_facilities (room_id, facility_id) VALUES (3, 2);

INSERT INTO room_facilities (room_id, facility_id) VALUES (4, 2);

INSERT INTO room_facilities (room_id, facility_id) VALUES (5, 2);

INSERT INTO room_facilities (room_id, facility_id) VALUES (6, 2);

INSERT INTO room_facilities (room_id, facility_id) VALUES (7, 2);

INSERT INTO room_facilities (room_id, facility_id) VALUES (8, 2);

INSERT INTO room_facilities (room_id, facility_id) VALUES (9, 2);

INSERT INTO room_facilities (room_id, facility_id) VALUES (2, 3);

INSERT INTO room_facilities (room_id, facility_id) VALUES (4, 3);

INSERT INTO room_facilities (room_id, facility_id) VALUES (5, 3);

INSERT INTO room_facilities (room_id, facility_id) VALUES (6, 3);

INSERT INTO room_facilities (room_id, facility_id) VALUES (7, 3);

INSERT INTO room_facilities (room_id, facility_id) VALUES (8, 3);

INSERT INTO room_facilities (room_id, facility_id) VALUES (9, 3);

INSERT INTO room_facilities (room_id, facility_id) VALUES (1, 4);

INSERT INTO room_facilities (room_id, facility_id) VALUES (2, 4);

INSERT INTO room_facilities (room_id, facility_id) VALUES (3, 4);

INSERT INTO room_facilities (room_id, facility_id) VALUES (4, 4);

INSERT INTO room_facilities (room_id, facility_id) VALUES (5, 4);

INSERT INTO room_facilities (room_id, facility_id) VALUES (6, 4);

INSERT INTO room_facilities (room_id, facility_id) VALUES (7, 4);

INSERT INTO room_facilities (room_id, facility_id) VALUES (8, 4);

INSERT INTO room_facilities (room_id, facility_id) VALUES (9, 4);

INSERT INTO room_facilities (room_id, facility_id) VALUES (7, 5);

INSERT INTO room_facilities (room_id, facility_id) VALUES (8, 5);

INSERT INTO room_facilities (room_id, facility_id) VALUES (9, 5);

INSERT INTO room_facilities (room_id, facility_id) VALUES (1, 6);

INSERT INTO room_facilities (room_id, facility_id) VALUES (2, 6);

INSERT INTO room_facilities (room_id, facility_id) VALUES (3, 6);

INSERT INTO room_facilities (room_id, facility_id) VALUES (4, 6);

INSERT INTO room_facilities (room_id, facility_id) VALUES (5, 6);

INSERT INTO room_facilities (room_id, facility_id) VALUES (6, 6);

INSERT INTO room_facilities (room_id, facility_id) VALUES (7, 6);

INSERT INTO room_facilities (room_id, facility_id) VALUES (8, 6);

INSERT INTO room_facilities (room_id, facility_id) VALUES (9, 6);
