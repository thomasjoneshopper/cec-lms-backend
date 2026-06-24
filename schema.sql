CREATE TABLE IF NOT EXISTS Users (
    user_id         INTEGER PRIMARY KEY,
    employee_number TEXT NOT NULL UNIQUE,
    name            TEXT NOT NULL,
    last_sign_in    DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Courses (
    course_id   integer primary key
);

CREATE TABLE IF NOT EXISTS Modules (
    module_id       INTEGER PRIMARY KEY,
    course_id       INTEGER,
    name            TEXT,
    number          INTEGER,
    paragraph_count INTEGER
);

CREATE TABLE IF NOT EXISTS UserParagraphCompletion (
    user_id             INTEGER,
    module_id           INTEGER,
    paragraph_number    INTEGER NOT NULL,
    completion_time     DATETIME DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (user_id, module_id, paragraph_number),
    FOREIGN KEY user_id REFERENCES Users(user_id)
    FOREIGN KEY module_id REFERENCES Modules(module_id)
);