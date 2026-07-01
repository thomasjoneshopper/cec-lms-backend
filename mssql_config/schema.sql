IF OBJECT_ID('dbo.Users', 'U') IS NULL 
BEGIN
    CREATE TABLE dbo.Users (
        user_id         INT             NOT NULL IDENTITY(1,1),
        employee_number NVARCHAR(16)    NOT NULL,
        name            NVARCHAR(128)   NOT NULL,
        last_sign_in    DATETIME2       NULL,
        created_at      DATETIME2       NOT NULL DEFAULT SYSDATETIME(),
        
        CONSTRAINT PK_Users PRIMARY KEY (user_id),
        CONSTRAINT UQ_employee_number UNIQUE (employee_number)
    );
END;

IF OBJECT_ID('dbo.Courses', 'U') IS NULL 
BEGIN
    CREATE TABLE dbo.Courses (
        course_id       INT             IDENTITY(1,1),
        name            NVARCHAR(128)   NOT NULL,

        CONSTRAINT PK_Courses PRIMARY KEY (course_id)
    );
END;

IF OBJECT_ID('dbo.Modules', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.Modules (
        module_id       INT             NOT NULL IDENTITY(1,1),
        course_id       INT             NOT NULL,
        name            NVARCHAR(128)   NOT NULL,
        number          INT             NOT NULL,
        paragraph_count INT             NOT NULL,

        CONSTRAINT PK_Modules PRIMARY KEY (module_id),
        CONSTRAINT FK_Modules_course FOREIGN KEY (course_id) 
        REFERENCES dbo.Courses(course_id) ON DELETE CASCADE
    );
END;

IF OBJECT_ID('dbo.Quizzes', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.Quizzes (
        quiz_id         INT             NOT NULL IDENTITY(1,1),
        course_id       INT             NOT NULL,
        module_id       INT             NULL, -- NULL for final quizzes
        passing_score   INT             NOT NULL, -- Out of 100
        question_count  INT             NOT NULL,

        CONSTRAINT PK_Quizzes PRIMARY KEY (quiz_id),
        CONSTRAINT FK_Quizzes_course FOREIGN KEY (course_id)
        REFERENCES dbo.Courses(course_id) ON DELETE CASCADE,
        CONSTRAINT FK_Quizzes_modules FOREIGN KEY (module_id)
        REFERENCES dbo.Modules(module_id)
    );
END;

