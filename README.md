Will write soon!

## Development Plan

1.  **Create Database Models:** Add the new tables (`SchoolEvent`, `SchoolInfo`, `SchoolTransaction`, and `Announcement`) to the `app/models.py` file. (Done)
2.  **Generate Migration:** Create a new database migration file using Alembic to reflect the changes in the models. (Done)
3.  **Apply Migration:** Apply the migration to the database to create the new tables. (Done)
4.  **Implement Rate Limiting:**
    *   Install the `slowapi` library. (Done)
    *   Configure rate limiting in the main application file (`main.py`). (Done)
    *   Apply the rate limiter to all routes. (Done)