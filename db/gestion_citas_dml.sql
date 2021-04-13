-- Test script
-- Author: Santiago Andres Rodriguez

SET client_encoding TO 'UTF8';
CREATE EXTENSION IF NOT EXISTS unaccent;

-- user table

INSERT INTO public."user" (id, password, last_login, is_superuser, role, first_name, last_name, identification_type,
                           identification_number, username, email, phone, picture, city, address, is_active, is_staff,
                           created_at, updated_at)
VALUES (1, 'argon2$argon2id$v=19$m=102400,t=2,p=8$b2JSRExFU3E5YWgyazZTUUh4d0w4YQ$HXkzz+zSJt9WdBEZy75Fcg',
        null, true, 'ADMIN', 'Luis', 'Gómez', 'CC', '1234567', 'luisgomez', 'luis@gmail.com', '3144823086', '', 'Tunja',
        null, true, true, '2021-03-25 23:24:20.752790', '2021-04-06 16:18:09.497649'),
       (2, 'argon2$argon2id$v=19$m=102400,t=2,p=8$Z0xRSXlQZlZBMU9KcjdUc0hEa1hQVA$NQruGAhdQgdqZOyDhfM3jQ', null, false,
        'DOC', 'Carlos', 'Perez', 'CC', '54632189', 'carlosperez', 'carlos@gmail.com', '3123456789', '', 'Sogamoso',
        null, true, false, '2021-03-25 22:27:34.940033', '2021-04-06 16:19:24.743649'),
       (3, 'argon2$argon2id$v=19$m=102400,t=2,p=8$bXNlR3AxanV4Y1hvYlFGZ3I0MVpISA$UtXFvptFX3bpziHXniXKhg', null, false,
        'USR', 'Juan', 'Moreno', 'CC', '7456123', 'juanmoreno', 'juan@gmail.com', '3124567898', '', 'Tunja', null, true,
        false, '2021-03-25 22:27:34.940033', '2021-04-06 16:19:56.661574');


SELECT setval('user_id_seq', 3);
