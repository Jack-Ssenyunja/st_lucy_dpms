from database.repository import Repository

repository = Repository(
    table="learning_resources",
    primary_key="resource_id",
    fields=("title", "category", "description", "url", "active"),
    form_fields=(
        ("title", "Title", True, "text"),
        ("category", "Category", True, "text"),
        ("description", "Description", False, "text"),
        ("url", "Web address", True, "url"),
        ("active", "Active", True, "boolean"),
    ),
    headers=(("resource_id", "ID"), ("title", "Resource"), ("category", "Category"),
             ("description", "Description"), ("url", "Web address"), ("active", "Active")),
    list_sql="""SELECT resource_id, title, category, description, url, active
                FROM learning_resources ORDER BY category, title""",
    public_list_sql="""SELECT resource_id, title, category, description, url, active
                       FROM learning_resources WHERE active = TRUE ORDER BY category, title""",
)
