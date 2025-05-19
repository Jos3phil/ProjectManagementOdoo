{
    "name": "Project Management",
    "version": "1.0",
    "category": "Project",
    "summary": "Module for managing projects and tasks with user roles.",
    "description": """
        This module provides a comprehensive project management system, allowing users to create and manage projects and tasks, assign roles, and track progress.
    """,
    "author": "Timothy Calderon",
    "website": "https://yourwebsite.com",
    "depends": ["base", "mail"],
    "data": [
        "security/project_security.xml",
        "security/ir.model.access.csv",
        "views/project_views.xml",
        "views/task_views.xml",
        "views/role_views.xml",
        "views/menu_views.xml",
        "data/project_data.xml"
    ],
    "images": ["static/description/banner.png"],
    "installable": True,
    "application": True,  # Esto es crucial
    "auto_install": False,
}