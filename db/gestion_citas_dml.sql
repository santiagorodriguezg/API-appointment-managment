-- user table

INSERT INTO public."user" (id, password, last_login, is_superuser, role, first_name, last_name, identification_type,
                           identification_number, username, email, phone, picture, city, address, is_active, is_staff,
                           created_at, updated_at)
VALUES (1, 'pbkdf2_sha256$260000$tGqaogwlnkO9qXTmFbne8J$gBSrWhphOsirwDBmIikqxHxFISgcdCeCrNxxoi4cpgU=',
        '2021-04-06 16:02:28.542280', true, 'ADMIN', 'Luis', 'Gómez', 'CC', '1234567', 'luisgomez', 'luis@gmail.com',
        '3144823086', '', null, null, true, true, '2021-03-25 23:24:20.752790', '2021-04-06 16:18:09.497649'),
       (2, 'pbkdf2_sha256$260000$vI0EiQOQO0MF3v8yWWH1pr$TkHoIvy1CXZuxsEvWrvThtFe+z8mnWvjl9pu1Y4SqBw=', null, false,
        'DOCTOR', 'Carlos', 'Perez', 'CC', '54632189', 'carlosperez', 'carlos@gmail.com', '3123456789', '', null, null,
        true, false, '2021-03-25 22:27:34.940033', '2021-04-06 16:19:24.743649'),
       (3, 'pbkdf2_sha256$260000$xgwlIzwpybSQuWNhMPeCcU$mQ0gHAIVORLUxQJCHo0ar8Ppwmpj5gtUWTM/T+v1Gks=', null, false,
        'USR', 'Juan', 'Moreno', 'CC', '7456123', 'juanmoreno', 'juan@gmail.com', '3124567898', '', null, null, true,
        false, '2021-03-25 22:27:34.940033', '2021-04-06 16:19:56.661574');


SELECT setval('user_id_seq', 3);