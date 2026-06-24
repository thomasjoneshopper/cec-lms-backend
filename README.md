# CEC LMS Backend

Backend API is built in Python with the Flask framework. Database is a Microsoft SQL Server.

## Database Tables

### Users:

| Field | Type |
| ----- | ---- |
| `user_id` | `INT PK` |
| `employee_number` | `TEXT` |
| `name` | `TEXT` |
| `last_sign_in` | `DATETIME` |

### Courses:

| Field | Type |
| ----- | ---- |
| `course_id` | `INT PK` |
| `name` | `TEXT` |

- May add more fields for version information

### UserCourseProgress:

| Field | Type |
| ----- | ---- |
| `user_id` | `INT FK` |
| `course_id` | `INT FK` |
| `active_module_id` | `INT FK` |
| `active_paragraph` | `INT` |

- `(user_id, course_id)` is the primary key

### Modules:

| Field | Type |
| ----- | ---- |
| `module_id` | `INT PK` |
| `course_id` | `INK FK` |
| `name` | `TEXT` |
| `number` | `INT` |
| `paragraph_count` | `INT` |

### UserParagraphCompletion:

| Field | Type |
| ----- | ---- |
| `user_id` | `INT FK` |
| `module_id` | `INT FK` |
| `paragraph_number` | `INT` |
| `completion_time` | `DATETIME` |

- `(user_id, module_id, paragraph_number)` is the primary key

### Quizzes:

| Field | Type |
| ----- | ---- |
| `quiz_id` | `INT PK` |
| `course_id` | `INT FK` |
| `name` | `TEXT` |
| `passing_score` | `INT` |
| `total_questions` | `INT` |

- May add fields to describe connection to module

### UserQuizAttempts:

| Field | Type |
| ----- | ---- |
| `attempt_id` | `INT PK` |
| `user_id` | `INT FK` |
| `quiz_id` | `INT FK` |
| `score` | `INT` |
| `submission_time` | `DATETIME` |

## API Endpoints

    api
    ├── auth
    │   ├── login
    │   ├── logout
    │   └── me
    ├── progress
    │   └── paragraphs
    └── quizzes
        ├── <quiz_id>
        └── final

### `POST /auth/login`:

- upsert `User`
- set jwt cookie

### `POST /auth/logout`:

- clear jwt cookie

### `GET /auth/me`:

- read `User` entry with id from jwt `sub`

### `GET /<course>/progress`:

- read `UserParagraphCompletion`, select all that correspond to current user and course

### `POST /<course>/progress`:

- send paragraph number and course id
- create `UserParagraphCompletion` entry 

### `DELETE /<course>/progress`:

- Admin only

### `GET /<course>/quizzes/<quiz_number>`:

- `quiz_number` either a number or "final"
- response contains last quiz attempt score and maybe time

### `POST /<course>/quizzes/<quiz_number>`:

- request contains score of latest attempt

### `GET /<course>/admin/users`:

- admin only
