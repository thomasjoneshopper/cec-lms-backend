# CEC LMS Backend

Backend API built in Python with the Flask framework. Database is a Microsoft SQL Server.

## Database Tables

### Users:

| Field | Type |
| ----- | ---- |
| `user_id` | `INT PK` |
| `role_title` | `VARCHAR` |
| `employee_number` | `NVARCHAR` |
| `full_name` | `NVARCHAR` |
| `creation_time` | `DATETIME2` |


### Courses:

| Field | Type |
| ----- | ---- |
| `course_id` | `INT PK` |
| `title_en` | `NVARCHAR` |
| `title_es` | `NVARCHAR` |


### Modules:

| Field | Type |
| ----- | ---- |
| `module_id` | `INT PK` |
| `course_id` | `INK FK` |
| `ordinal` | `INT` |
| `title_en` | `NVARCHAR` |
| `title_es` | `NVARCHAR` |


### Paragraphs:

| Field | Type |
| ----- | ---- |
| `paragraph_id` | `INT PK` |
| `module_id` | `INT FK` |
| `ordinal` | `INT` |
| `title_en` | `NVARCHAR` |
| `title_es` | `NVARCHAR` |
| `body_en` | `NVARCHAR` |
| `body_es` | `NVARCHAR` |
| `extras_json` | `NVARCHAR` |


### Quizzes:

| Field | Type |
| ----- | ---- |
| `quiz_id` | `INT PK` |
| `course_id` | `INT FK` |
| `module_id` | `INT FK` |
| `passing_score` | `INT` |


### Questions:

| Field | Type |
| ----- | ---- |
| `question_id` | `INT PK` |
| `quiz_id` | `INT FK` |
| `ordinal` | `INT` |
| `body_en` | `NVARCHAR` |
| `body_es` | `NVARCHAR` |
| `hint_en` | `NVARCHAR` |
| `hint_es` | `NVARCHAR` |


### Answers:

| Field | Type |
| ----- | ---- |
| `answer_id` | `INT PK` |
| `question_id` | `INT FK` |
| `body_en` | `NVARCHAR` |
| `body_es` | `NVARCHAR` |
| `correct` | `BIT` |


### UserCourseProgress:

| Field | Type |
| ----- | ---- |
| `user_id` | `INT FK` |
| `course_id` | `INT FK` |
| `active_module` | `INT FK` |
| `active_paragraph` | `INT FK` |
| `completion_time` | `DATETIME2` |
| `creation_time` | `DATETIME2` |

- `(user_id,  course_id)` is the primary key


### UserParagraphCompletion:

| Field | Type |
| ----- | ---- |
| `user_id` | `INT FK` |
| `course_id` | `INT FK` |
| `module_id` | `INT FK` |
| `paragraph_id` | `INT FK` |
| `completion_time` | `DATETIME2` |

- `(user_id,  paragraph_id)` is the primary key


### UserQuizAttempts:

| Field | Type |
| ----- | ---- |
| `attempt_id` | `INT PK` |
| `user_id` | `INT FK` |
| `course_id` | `INT FK` |
| `quiz_id` | `INT FK` |
| `pass` | `BIT` |
| `submission_time` | `DATETIME2` |


### UserAnswerSelections:

| Field | Type |
| ----- | ---- |
| `attempt_id` | `INT FK` |
| `quiz_id` | `INT FK` |
| `question_id` | `INT FK` |
| `answer_id` | `INT FK` |

- `(attempt_id,  answer_id)` is the primary key


## API Endpoints

```text
/
├── auth/
│   ├── login
│   ├── logout
│   └── me
├── course/<course_id>/
│   ├── progress
│   ├── cursor
│   └── content
├── paragraph/<paragraph_id>/
│   └── completion
├── quiz/<quiz_id>/
│   └── attempts
└── image/<filename>
```


### Auth

```http
POST /auth/login
```
```json
{
    "employee_number": "0TA16****", 
    "full_name": "John Doe"
}
```

- determine `user_id`
- generate `Users` entry if does not exist
- set jwt cookie with `sub = user_id`

<br>

```http
POST /auth/logout
```
- clear jwt cookie

<br>

```http
GET /auth/me
```
- read `User` entry with id from jwt `sub`

<br>


### Course

```http
GET /course/<course_id>/progress
```
- read `UserParagraphCompletion`,  select all that correspond to current user and course

<br>

```http
DELETE /course/<course_id>/progress
```
```json
{
    "user_id": 1
}
```
- Admin only

<br>

```http
GET /course/<course_id>/cursor
```
- returns `active_module` and `active_paragraph`

<br>

```http
GET /course/<course_id>/content
```
- returns all course content

<br>

### Paragraph Completion

```http
POST /paragraph/<paragraph_id>/completion
```
- create `UserCourseProgress` entry if not exists
- create `UserParagraphCompletion` entry 

<br>

### Quiz Attempts

```http
GET /quiz/<quiz_id>/attempts
```
- response contains last quiz attempt score and time

<br>

```http
POST /quiz/<quiz_id>/attempts
```
```json
{
    "answers": [2, 5, 10, 13, 18, 22, 26, 30, 35, 37]
}
```

<br>

### Image

```http
GET /image/<filename>
```
- exposes `src/cec_lms_backend/img`

<br>

## TO DO

- TEST ENDPOINTS
- UPDATE FRONTEND
- add versioning system
- extend to multiple courses
