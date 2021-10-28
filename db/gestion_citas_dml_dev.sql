-- Test script
-- Author: Santiago Andres Rodriguez

SET client_encoding TO 'UTF8';
CREATE EXTENSION IF NOT EXISTS unaccent;

-- auth_group table
INSERT INTO public.auth_group(id, name)
VALUES (1, 'Users'),
       (2, 'Doctors');


-- auth_group_permissions table
INSERT INTO public.auth_group_permissions (id, group_id, permission_id)
VALUES (1, 1, 38),
       (2, 1, 39),
       (3, 1, 41),
       (4, 1, 50),
       (5, 1, 53),
       (6, 1, 54),
       (7, 1, 55),
       (8, 1, 56),
       (9, 1, 57),
       (10, 1, 58),
       (11, 1, 59),
       (12, 1, 60),
       (13, 1, 61),
       (14, 2, 32),
       (15, 2, 41),
       (16, 2, 50),
       (17, 2, 53),
       (18, 2, 54),
       (19, 2, 55),
       (20, 2, 56),
       (21, 2, 57),
       (22, 2, 58),
       (23, 2, 59),
       (24, 2, 60),
       (25, 2, 61);


-- user table
INSERT INTO public."user" (id, password, last_login, is_superuser, role, first_name, last_name, identification_type,
                           identification_number, username, email, phone, picture, city, neighborhood, address,
                           is_active, is_staff, created_at, updated_at)
VALUES (1, 'argon2$argon2id$v=19$m=102400,t=2,p=8$b2JSRExFU3E5YWgyazZTUUh4d0w4YQ$HXkzz+zSJt9WdBEZy75Fcg',
        '2021-10-27 14:52:26.822815 +00:00', true, 'ADMIN', 'Luis', 'Gómez', 'CC', '1234567', 'luis',
        'luis@outlook.com', '3144823086', '', 'Tunja', null, null, true, true,
        '2021-03-25 23:24:20.752790 +00:00', '2021-04-06 16:18:09.497649 +00:00'),

       (2, 'argon2$argon2id$v=19$m=102400,t=2,p=8$bXNlR3AxanV4Y1hvYlFGZ3I0MVpISA$UtXFvptFX3bpziHXniXKhg',
        '2021-10-26 00:34:01.602680 +00:00', false, 'USR', 'Ana', 'Hernández', 'CC', '7456123', 'ana', 'ana@gmail.com',
        '3124567898', '', 'Duitama', null, null, true, false, '2021-03-25 22:27:34.940033 +00:00',
        '2021-04-06 16:19:56.661574 +00:00'),

       (3, 'argon2$argon2id$v=19$m=102400,t=2,p=8$WVdqZEp2MHF5Z3dESmtzZ0R2dDlDdA$F84JW0+IH4+6Zlj9frhG6A',
        '2021-10-01 15:38:29.650566 +00:00', false, 'USR', 'Sofia', 'García', 'CC', '2586824', 'sofia', null, null, '',
        null, null, null, true, false, '2021-10-01 15:38:29.652567 +00:00', '2021-10-01 15:38:29.652567 +00:00'),

       (4, 'argon2$argon2id$v=19$m=102400,t=2,p=8$Z0xRSXlQZlZBMU9KcjdUc0hEa1hQVA$NQruGAhdQgdqZOyDhfM3jQ',
        '2021-10-27 14:34:30.851082 +00:00', false, 'DOC', 'Carlos', 'Perez', 'CC', '54632189', 'carlos',
        'luis@gmail.com', '3123456789', '', 'Sogamoso', null, null,
        true, false, '2021-03-25 22:27:34.940033 +00:00', '2021-10-26 16:22:10.625795 +00:00'),

       (5, 'argon2$argon2id$v=19$m=102400,t=2,p=8$SkNnQmFOSzVwN3ZoaW1uQ2JxSG1JNg$LeGodylg9Z9Z2C8ozkiq2g', null, false,
        'DOC', 'Andrea', 'Acero Caro', 'CC', '120348183', 'andrea', 'andrea@gmail.com', '3132238204', '', null, null,
        null, true, false, '2021-10-26 21:03:34.865981 +00:00', '2021-10-26 21:03:34.865981 +00:00'),

       (6, 'argon2$argon2id$v=19$m=102400,t=2,p=8$cmlMNEJ6eDhLOGdPZFFzTG1vaDNFUA$Fiedzlui+WDoyAZNStD+jw', null, false,
        'DOC', 'Camilo', 'Rodríguez', 'CC', '12954820', 'camilo', 'camilo@gmail.com', '3028582481', '', null, null,
        null, true, false, '2021-10-26 21:04:45.061788 +00:00', '2021-10-26 21:04:45.061788 +00:00'),

       (7, 'argon2$argon2id$v=19$m=102400,t=2,p=8$TVFkUjJua3ZudnhncnB1Z1lDQUZPdw$Xwti6ImMCl+4UbVEAzsFAA', null, false,
        'DOC', 'Diana', 'Mendoza', 'CC', '18481042', 'diana', 'diana@hotmail.com', '3245891759', '', null, null, null,
        true, false, '2021-10-26 21:05:42.823624 +00:00', '2021-10-26 21:05:42.823624 +00:00');


-- user_groups table
INSERT INTO user_groups(id, user_id, group_id)
VALUES (1, 2, 1),
       (2, 3, 1),
       (3, 4, 2),
       (4, 5, 2),
       (5, 6, 2),
       (6, 7, 2);


-- appointment table
INSERT INTO public.appointment (id, type, children, aggressor, description, audio, start_date, end_date, created_at,
                                updated_at, user_id)
VALUES (1, 'PSY,LEG', '[
  {
    "name": "Maria Hernández",
    "age": 14
  },
  {
    "name": "Paula Hernández",
    "age": 8
  }
]', '{
  "name": "Juan Moreno",
  "identification_number": 1834802567,
  "phone": 3143498163,
  "address": "Tunja",
  "more_info": "Lugar de trabajo: Claro"
}', 'No tengo datos', '', null, null, '2021-04-12 13:41:53.275415', '2021-04-12 22:56:04.356851', 2),
       (2, 'LEG', null, null, 'Violencia intrafamiliar', '', null, null, '2021-09-10 21:16:37.951541 +00:00',
        '2021-09-10 21:16:37.951541 +00:00', 3);


-- appointment_doctor table
INSERT INTO public.appointment_doctors(id, appointment_id, user_id)
VALUES (1, 1, 4);


-- room table
INSERT INTO public.room (id, name, created_at, user_owner_id, user_receiver_id)
VALUES (1, 'roomtest1', '2021-04-17 19:16:04.510000', 1, 3),
       (2, 'roomtest2', '2021-04-17 19:16:58.066000', 3, 2);


-- message table
-- INSERT INTO public.message (id, type, content, _content_data, created_at, updated_at, room_id, user_id)
-- VALUES (1, 'TXT', 'Tiene una nueva cita', '', '2021-04-17 19:16:41.491000', '2021-04-17 19:16:41.491000', 1, 1),
--        (2, 'TXT', 'Buenos dias', '', '2021-04-17 19:17:27.622000', '2021-04-17 19:17:27.622000', 2, 3),
--        (3, 'TXT', 'Cuando es la cita?', '', '2021-04-17 19:18:03.754000', '2021-04-17 19:18:03.754000', 1, 3);

SELECT setval('auth_group_id_seq', 2);
SELECT setval('auth_group_permissions_id_seq', 25);
SELECT setval('user_id_seq', 7);
SELECT setval('user_groups_id_seq', 3);
SELECT setval('appointment_id_seq', 2);
SELECT setval('appointment_doctors_id_seq', 1);
SELECT setval('room_id_seq', 2);
-- SELECT setval('message_id_seq', 3);
