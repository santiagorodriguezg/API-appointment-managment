-- user table

INSERT INTO public."user" (id, password, last_login, is_superuser, user_type, first_name, last_name,
                           identification_type, identification_number, username, email, phone, picture, city, address,
                           is_active, is_staff, created_at, updated_at)
VALUES (1, 'pbkdf2_sha256$216000$k4q948RP2AuR$4tMDLOx4mhmIZt/LAwFzZvEMB+sYy23Pr8fIWGjqWHg=',
        null, true, 'ADMIN', 'Luis', 'Gómez', 'CC', '1234567', 'luisgomez', 'luis@gmail.com',
        '3144823086', '', null, null, true, true, '2021-03-25 23:24:20.752790', '2021-03-25 22:27:34.940033'),
       (2, 'pbkdf2_sha256$216000$k4q948RP2AuR$4tMDLOx4mhmIZt/LAwFzZvEMB+sYy23Pr8fIWGjqWHg=',
        null, false, 'DOCTOR', 'Carlos', 'Perez', 'CC', '1234567', 'carlosperez', 'carlos@gmail.com',
        '3123456789', '', null, null, true, false, '2021-03-25 22:27:34.940033', '2021-03-25 22:27:34.940033'),
       (3, 'pbkdf2_sha256$216000$k4q948RP2AuR$4tMDLOx4mhmIZt/LAwFzZvEMB+sYy23Pr8fIWGjqWHg=',
        null, false, 'USR', 'Juan', 'Moreno', 'CC', '1234567', 'juanmoreno', 'juan@gmail.com',
        '3124567898', '', null, null, true, false, '2021-03-25 22:27:34.940033', '2021-03-25 22:27:34.940033');



SELECT setval('user_id_seq', 3);