-- Основной скрипт
CREATE DATABASE cinemavaib_db;

\c cinemavaib_db

CREATE TABLE roles (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    login VARCHAR(50) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    role_id INT DEFAULT 1
        CONSTRAINT fk_role_id
        REFERENCES roles(role_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    status VARCHAR(50) CHECK (status IN ('Active', 'Inactive')) DEFAULT 'Active' NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_login TIMESTAMP DEFAULT NULL
);

CREATE TABLE movies (
    movie_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    movie_image BYTEA NOT NULL,
    base_price DECIMAL(8,2) DEFAULT 300.00 NOT NULL,
    rating DECIMAL(2,1) DEFAULT 0.0 NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE genres (
    genre_id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE director (
    director_id SERIAL PRIMARY KEY,
    fullname VARCHAR(255) NOT NULL,
    photo BYTEA NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE actor (
    actor_id SERIAL PRIMARY KEY,
    fullname VARCHAR(255) NOT NULL,
    photo BYTEA NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE movie_genre (
    movie_id INT NOT NULL
        REFERENCES movies(movie_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    genre_id INT NOT NULL
        REFERENCES genres(genre_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    PRIMARY KEY (movie_id, genre_id)
);

CREATE TABLE movie_director (
    movie_id INT NOT NULL
        REFERENCES movies(movie_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    director_id INT NOT NULL
        REFERENCES director(director_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    PRIMARY KEY (movie_id, director_id)
);

CREATE TABLE movie_actor (
    movie_id INT NOT NULL
        REFERENCES movies(movie_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    actor_id INT NOT NULL
        REFERENCES actor(actor_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    role VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (movie_id, actor_id)
);

CREATE TABLE review (
    review_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL
        REFERENCES users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    movie_id INT NOT NULL
        REFERENCES movies(movie_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    rating INT CHECK(rating BETWEEN 0 AND 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE watchlist (
    watchlist_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL
        REFERENCES users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    movie_id INT NOT NULL
        REFERENCES movies(movie_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    status VARCHAR(50) DEFAULT 'Planned' NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE hall (
    hall_id SERIAL PRIMARY KEY,
    hall_number INT NOT NULL,
    hall_name VARCHAR(100),
    hall_type VARCHAR(100),
    hall_extra_price DECIMAL(8,2) DEFAULT 0.00 NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE seat (
    seat_id SERIAL PRIMARY KEY,
    hall_id INT NOT NULL
        REFERENCES hall(hall_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    row_number INT NOT NULL,
    seat_number INT NOT NULL,
    seat_extra_price DECIMAL(8,2) DEFAULT 0.00 NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE session (
    session_id SERIAL PRIMARY KEY,
    movie_id INT NOT NULL
        REFERENCES movies(movie_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    hall_id INT NOT NULL
        REFERENCES hall(hall_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    session_time TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE ticket (
    ticket_id SERIAL PRIMARY KEY,
    session_id INT NOT NULL
        REFERENCES session(session_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    user_id INT NOT NULL
        REFERENCES users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    seat_id INT NOT NULL
        REFERENCES seat(seat_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    percent_discount DECIMAL(5,2) DEFAULT 0.00 NOT NULL,
    final_price DECIMAL(8,2) NOT NULL,
    final_price_discount DECIMAL(8,2),
    purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE activity_log (
    log_id SERIAL PRIMARY KEY,
    user_id INT
        REFERENCES users(user_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    actor_role VARCHAR(100),
    action_type VARCHAR(100),
    entity_id INT,
    description TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

INSERT INTO roles (role_name)
VALUES ('User'),
       ('Admin');

INSERT INTO users (login, password_hash, email, role_id)
VALUES ('admin', '$argon2id$v=19$m=65536,t=3,p=4$SG7R9AcsFOVGzcI3tx3zCA$GgaEHUQkeXIyflp3sPmxqKwWPGsfLSuEId4xcU5k+uo', 'vaganogannsan@gmail.com', 2);

-- Функции
-- Функция обновления updated_at
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at := CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION calc_ticket_price()
RETURNS TRIGGER AS $$
DECLARE
    v_base       DECIMAL(8,2);
    v_hall_extra DECIMAL(8,2);
    v_seat_extra DECIMAL(8,2);
BEGIN
    SELECT m.base_price, h.hall_extra_price, s.seat_extra_price
    INTO v_base, v_hall_extra, v_seat_extra
    FROM session se
    JOIN movies m ON m.movie_id = se.movie_id
    JOIN hall   h ON h.hall_id  = se.hall_id
    JOIN seat   s ON s.seat_id  = NEW.seat_id
    WHERE se.session_id = NEW.session_id;

    NEW.final_price := COALESCE(v_base, 0)
                     + COALESCE(v_hall_extra, 0)
                     + COALESCE(v_seat_extra, 0);

    NEW.final_price_discount := NEW.final_price
                              - (NEW.final_price * COALESCE(NEW.percent_discount, 0) / 100);

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Триггеры
CREATE TRIGGER trg_set_updated_at_users
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_set_updated_at_movies
BEFORE UPDATE ON movies
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_set_updated_at_genres
BEFORE UPDATE ON genres
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_set_updated_at_director
BEFORE UPDATE ON director
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_set_updated_at_actor
BEFORE UPDATE ON actor
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_set_updated_at_movie_actor
BEFORE UPDATE ON movie_actor
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_set_updated_at_review
BEFORE UPDATE ON review
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_set_updated_at_watchlist
BEFORE UPDATE ON watchlist
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_set_updated_at_hall
BEFORE UPDATE ON hall
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_set_updated_at_seat
BEFORE UPDATE ON seat
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_set_updated_at_session
BEFORE UPDATE ON session
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_set_updated_at_ticket
BEFORE UPDATE ON ticket
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_calc_ticket_price
BEFORE INSERT OR UPDATE ON ticket
FOR EACH ROW
EXECUTE FUNCTION calc_ticket_price();