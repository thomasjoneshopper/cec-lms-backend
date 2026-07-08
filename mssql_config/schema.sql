IF OBJECT_ID('dbo.Roles', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.Roles (
        role_id     INT             NOT NULL,
        title       NVARCHAR(128)   NOT NULL,

        CONSTRAINT PK_Roles 
            PRIMARY KEY (role_id),
        CONSTRAINT UQ_Roles_title 
            UNIQUE (title)
    );

    INSERT INTO dbo.Roles (role_id, title)
    VALUES (1, 'reader'), (2, 'admin');
END;

IF OBJECT_ID('dbo.Users', 'U') IS NULL 
BEGIN
    CREATE TABLE dbo.Users (
        user_id         INT             NOT NULL IDENTITY(1,1),
        role_id         INT             NOT NULL DEFAULT (1),
        employee_number NVARCHAR(16)    NOT NULL,
        full_name       NVARCHAR(128)   NOT NULL,
        creation_time   DATETIME2       NOT NULL DEFAULT SYSDATETIME(),
        
        CONSTRAINT PK_Users 
            PRIMARY KEY (user_id),
        CONSTRAINT FK_Users_Roles 
            FOREIGN KEY (role_id) 
            REFERENCES dbo.Roles (role_id),
        CONSTRAINT UQ_Users_employee_number 
            UNIQUE (employee_number)
    );
END;

IF OBJECT_ID('dbo.Courses', 'U') IS NULL 
BEGIN
    CREATE TABLE dbo.Courses (
        course_id       INT             NOT NULL IDENTITY(1,1),
        title           NVARCHAR(128)   NOT NULL,

        CONSTRAINT PK_Courses
            PRIMARY KEY (course_id)
    );
END;

IF OBJECT_ID('dbo.Modules', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.Modules (
        module_id       INT             NOT NULL IDENTITY(1,1),
        course_id       INT             NOT NULL,
        title           NVARCHAR(128)   NOT NULL,
        ordinal         INT             NOT NULL,
        paragraph_count INT             NOT NULL,

        CONSTRAINT PK_Modules 
            PRIMARY KEY (module_id),
        CONSTRAINT AK_Modules_Courses
            UNIQUE (course_id, module_id),
        CONSTRAINT FK_Modules_Courses 
            FOREIGN KEY (course_id) 
            REFERENCES dbo.Courses (course_id),
        CONSTRAINT UQ_Modules_ordinal 
            UNIQUE (course_id, ordinal),
        CONSTRAINT CK_Modules_ordinal
            CHECK (ordinal >= 0),
        CONSTRAINT CK_Modules_paragraph_count
            CHECK (paragraph_count >= 0)
    );
END;

IF OBJECT_ID('dbo.Quizzes', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.Quizzes (
        quiz_id         INT NOT NULL IDENTITY(1,1),
        course_id       INT NOT NULL,
        module_id       INT NULL,       -- NULL for final quizzes
        passing_score   INT NOT NULL,   -- Out of 100
        question_count  INT NOT NULL,

        CONSTRAINT PK_Quizzes
            PRIMARY KEY (quiz_id),
        CONSTRAINT FK_Quizzes_course 
            FOREIGN KEY (course_id)
            REFERENCES dbo.Courses (course_id),
        CONSTRAINT FK_Quizzes_module 
            FOREIGN KEY (module_id)
            REFERENCES dbo.Modules (module_id),
        CONSTRAINT UQ_Quizzes_Courses
            UNIQUE (course_id, quiz_id),
        CONSTRAINT CK_Quizzes_passing_score
            CHECK (passing_score BETWEEN 0 AND 100),
        CONSTRAINT CK_Quizzes_question_count
            CHECK (question_count > 0)
    );
END;

IF OBJECT_ID('dbo.UserCourseProgress', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.UserCourseProgress (
        user_id             INT NOT NULL,
        course_id           INT NOT NULL,
        active_module       INT NULL,
        active_paragraph    INT NULL,
        complete            BIT NOT NULL DEFAULT (0),

        CONSTRAINT PK_Progress 
            PRIMARY KEY (user_id, course_id),
        CONSTRAINT FK_Progress_user 
            FOREIGN KEY (user_id)
            REFERENCES dbo.Users (user_id) 
            ON DELETE CASCADE,
        CONSTRAINT FK_Progress_course 
            FOREIGN KEY (course_id)
            REFERENCES dbo.Courses (course_id),
        CONSTRAINT FK_Progress_active_module 
            FOREIGN KEY (course_id, active_module)
            REFERENCES dbo.Modules (course_id, module_id),
        CONSTRAINT CK_Progress_active_paragraph
            CHECK (active_paragraph >= 0)
    );
END;

IF OBJECT_ID('dbo.UserParagraphCompletion', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.UserParagraphCompletion (
        user_id             INT         NOT NULL,
        course_id           INT         NOT NULL,
        module_id           INT         NOT NULL,
        paragraph_number    INT         NOT NULL,
        completion_time     DATETIME2   NOT NULL DEFAULT SYSDATETIME(),

        CONSTRAINT PK_Completion 
            PRIMARY KEY (user_id, module_id, paragraph_number),
        CONSTRAINT FK_Completion_progress 
            FOREIGN KEY (user_id, course_id)
            REFERENCES dbo.UserCourseProgress (user_id, course_id) 
            ON DELETE CASCADE,
        CONSTRAINT FK_Completion_module 
            FOREIGN KEY (course_id, module_id)
            REFERENCES dbo.Modules (course_id, module_id),
        CONSTRAINT CK_Completion_paragraph_number
            CHECK (paragraph_number >= 0)
    );
END;


IF OBJECT_ID('dbo.UserQuizAttempts', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.UserQuizAttempts (
        attempt_id          INT         NOT NULL IDENTITY(1,1),
        user_id             INT         NOT NULL,
        course_id           INT         NOT NULL,
        quiz_id             INT         NOT NULL,
        score               INT         NOT NULL,
        correct_answers     INT         NOT NULL,
        submission_time     DATETIME2   NOT NULL DEFAULT SYSDATETIME(),

        CONSTRAINT PK_Attempts 
            PRIMARY KEY (attempt_id),
        CONSTRAINT FK_Attempts_progress 
            FOREIGN KEY (user_id, course_id)
            REFERENCES dbo.UserCourseProgress (user_id, course_id) 
            ON DELETE CASCADE,
        CONSTRAINT FK_Attempts_quiz 
            FOREIGN KEY (course_id, quiz_id)
            REFERENCES dbo.Quizzes (course_id, quiz_id),
        CONSTRAINT CK_Attempts_score
            CHECK (score BETWEEN 0 AND 100),
        CONSTRAINT CK_Attempts_correct_answers
            CHECK (correct_answers >= 0)
    );
END;