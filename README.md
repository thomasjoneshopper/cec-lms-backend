# CEC LMS Backend

Backend API is built in Python with the Flask framework. Database is a Microsoft SQL Server.

## Database Tables

### Users:

| Field | Type |
| ----- | ---- |
| `user_id` | `INT PK` |
| `employee_number` | `NVARCHAR` |
| `name` | `NVARCHAR` |
| `created_at` | `DATETIME2` |

### Courses:

| Field | Type |
| ----- | ---- |
| `course_id` | `INT PK` |
| `name` | `NVARCHAR` |

- May add more fields for version information

### Modules:

| Field | Type |
| ----- | ---- |
| `module_id` | `INT PK` |
| `course_id` | `INK FK` |
| `name` | `NVARCHAR` |
| `number` | `INT` |
| `paragraph_count` | `INT` |

### Quizzes:

| Field | Type |
| ----- | ---- |
| `quiz_id` | `INT PK` |
| `course_id` | `INT FK` |
| `name` | `NVARCHAR` |
| `passing_score` | `INT` |
| `question_count` | `INT` |

- May add fields to describe connection to module

### UserCourseProgress:

| Field | Type |
| ----- | ---- |
| `user_id` | `INT FK` |
| `course_id` | `INT FK` |
| `active_module_id` | `INT FK` |
| `active_paragraph` | `INT` |
| `complete` | `BIT` |

- `(user_id, course_id)` is the primary key

### UserParagraphCompletion:

| Field | Type |
| ----- | ---- |
| `user_id` | `INT FK` |
| `module_id` | `INT FK` |
| `paragraph_number` | `INT` |
| `completion_time` | `DATETIME2` |

- `(user_id, module_id, paragraph_number)` is the primary key

### UserQuizAttempts:

| Field | Type |
| ----- | ---- |
| `attempt_id` | `INT PK` |
| `user_id` | `INT FK` |
| `quiz_id` | `INT FK` |
| `score` | `INT` |
| `correct_answers` | `INT` |
| `submission_time` | `DATETIME2` |

## API Endpoints

```text
api/
├── auth/
│   ├── login
│   ├── logout
│   └── me
├── course/<course_id>/
│   └── progress
└── quiz/<quiz_id>/
    └── attempt
```



### Auth

```http
POST /auth/login
```
- upsert `User`
- set jwt cookie

```http
POST /auth/logout
```
- clear jwt cookie

```http
GET /auth/me
```
- read `User` entry with id from jwt `sub`


### Course Progress
```http
GET /course/<course_id>/progress
```
- read `UserParagraphCompletion`, select all that correspond to current user and course


```http
POST /course/<course_id>/progress
```
- send paragraph number and course id
- create `UserParagraphCompletion` entry 

```http
DELETE /course/<course_id>/progress
```
- Admin only


### Quiz Attempt

```http
GET /quiz/<quiz_id>/attempt
```
- `quiz_number` either a number or "final"
- response contains last quiz attempt score and maybe time

```http
POST /quiz/<quiz_id>/attempt
```
- request contains score of latest attempt
