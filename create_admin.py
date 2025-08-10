from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Role, SchoolClass, Subject # Import SchoolClass and Subject
from fastapi_users.password import PasswordHelper

def create_admin_user():
    db: Session
    for db in get_db(): # Use get_db as a dependency
        password_helper = PasswordHelper()

        # Check if admin user already exists
        admin_user = db.query(User).filter(User.email == "admin").first()
        if admin_user:
            print("Admin user already exists.")
            return

        # Create admin user
        hashed_password = password_helper.hash("admin_password") # Replace with a strong password
        admin_user = User(
            name="admin",
            email="admin",
            hashed_password=hashed_password,
            role=Role.admin,
            is_active=True,
            is_verified=True,
            is_superuser=True,
            is_staff=True
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        print(f"Admin user created: {admin_user.email}")

        # Define subjects for each class
        class_subjects = {
            8: ["English", "Nepali", "Social", "C math", "Omath", "Health", "Science"],
            9: ["English", "Nepali", "Social", "C math", "Omath", "Accountancy", "Science"],
            10: ["English", "Nepali", "Social", "C math", "Omath", "Accountancy", "Science"]
        }

        for class_name, subjects_list in class_subjects.items():
            # Check if class exists, create if not
            school_class = db.query(SchoolClass).filter(SchoolClass.name == str(class_name)).first()
            if not school_class:
                school_class = SchoolClass(name=str(class_name), section="A") # Default section to A
                db.add(school_class)
                db.commit()
                db.refresh(school_class)
                print(f"Class {class_name} created.")

            # Add subjects to the class
            for subject_name in subjects_list:
                subject = db.query(Subject).filter(Subject.name == subject_name).first()
                if not subject:
                    subject = Subject(name=subject_name)
                    db.add(subject)
                    db.commit()
                    db.refresh(subject)
                    print(f"Subject {subject_name} created.")
                
                # Add subject to class if not already associated
                if subject not in school_class.subjects:
                    school_class.subjects.append(subject)
                    db.commit()
                    db.refresh(school_class)
                    print(f"Associated {subject_name} with Class {class_name}.")

if __name__ == "__main__":
    create_admin_user()
