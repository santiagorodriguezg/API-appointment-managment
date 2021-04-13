-- Test script
-- Author: Santiago Andres Rodriguez

SET client_encoding TO 'UTF8';
CREATE EXTENSION IF NOT EXISTS unaccent;

-- user table

INSERT INTO public."user" (id, password, last_login, is_superuser, role, first_name, last_name, identification_type,
                           identification_number, username, email, phone, picture, city, neighborhood, address,
                           is_active, is_staff, created_at, updated_at)
VALUES (1, 'argon2$argon2id$v=19$m=102400,t=2,p=8$b2JSRExFU3E5YWgyazZTUUh4d0w4YQ$HXkzz+zSJt9WdBEZy75Fcg',
        '2021-04-13 15:10:42.660823', true, 'ADMIN', 'Luis', 'Gómez', 'CC', '1234567', 'luis', 'luis@gmail.com',
        '3144823086', '', 'Tunja', null, null, true, true, '2021-03-25 23:24:20.752790', '2021-04-06 16:18:09.497649'),
       (2, 'argon2$argon2id$v=19$m=102400,t=2,p=8$Z0xRSXlQZlZBMU9KcjdUc0hEa1hQVA$NQruGAhdQgdqZOyDhfM3jQ',
        '2021-04-13 15:26:45.766843', false, 'DOC', 'Carlos', 'Perez', 'CC', '54632189', 'carlos',
        'carlos@gmail.com', '3123456789', '', 'Sogamoso', null, null, true, false, '2021-03-25 22:27:34.940033',
        '2021-04-06 16:19:24.743649'),
       (3, 'argon2$argon2id$v=19$m=102400,t=2,p=8$bXNlR3AxanV4Y1hvYlFGZ3I0MVpISA$UtXFvptFX3bpziHXniXKhg',
        '2021-04-13 15:24:36.629052', false, 'USR', 'Juan', 'Moreno', 'CC', '7456123', 'juan', 'juan@gmail.com',
        '3124567898', '', 'Duitama', null, null, true, false, '2021-03-25 22:27:34.940033',
        '2021-04-06 16:19:56.661574');


-- appointment table

INSERT INTO public.appointment (id, children, aggressor, description, audio, start_date, end_date, created_at,
                                updated_at, doctor_id, user_id)
VALUES (1, '[
  {
    "age": 14,
    "name": "Maria Hernandez"
  },
  {
    "age": 8,
    "name": "Ana Hernandez"
  }
]', 'Actualizar datos aggressor', 'No tengo datos', '', null, null, '2021-04-12 13:41:53.275415',
        '2021-04-12 22:56:04.356851', null, 3),
       (2, null, 'Pedro Martinez', 'Violencia intrafamiliar', '', null, null, '2021-04-11 15:48:40.920204',
        '2021-04-12 22:40:30.033680', 2, 3);



SELECT setval('user_id_seq', 3);
SELECT setval('appointment_id_seq', 2);
