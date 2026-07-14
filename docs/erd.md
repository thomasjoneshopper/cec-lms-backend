```mermaid
%%{init: {
  'theme': 'neutral',
  'er': {
    'layout': 'elk',
    'direction': 'TB'
  }
}}%%

erDiagram
    courses
    users

    modules
    quizzes
    progress

    paragraphs
    attempts

    completion

    courses ||--o{ progress : ""
    courses ||--|{ modules : ""
    courses ||--|{ quizzes : ""
    users ||--o{ progress : ""
    progress ||--o{ attempts : ""
    progress ||--o{ completion : ""
    modules ||--|{ paragraphs : ""
    quizzes ||--o{ attempts: ""
    paragraphs ||--o{ completion: ""
```

```mermaid
erDiagram
    courses
    users

    quizzes
    progress
    paragraphs
    
    attempts
    completion

    courses ||--o{ progress: ""
    users ||--o{ progress: ""

    progress ||--o{ attempts : ""
    quizzes ||--o{ attempts: ""
    progress ||--o{ completion : ""
    paragraphs ||--o| completion : ""
```