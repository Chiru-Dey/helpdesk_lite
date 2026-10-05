from app import create_app
from app.extensions import db
from app.models.user import Role, User
from app.models.category import Category
from app.models.ticket import Ticket
from app.models.comment import Comment


def seed():
    app = create_app()
    with app.app_context():
        # Prevent duplicate seeding
        if Role.query.first():
            print("Database already seeded. Skipping.")
            return

        # 1. Create Roles
        print("Creating roles...")
        role_admin = Role(name="admin", description="Administrator")
        role_agent = Role(name="agent", description="Support Agent")
        role_customer = Role(name="customer", description="Customer")
        db.session.add_all([role_admin, role_agent, role_customer])
        db.session.commit()

        # 2. Create Users
        print("Creating users...")
        admin = User(email="admin@example.com", name="Admin User")
        admin.set_password("password123")
        admin.roles.append(role_admin)

        agent = User(email="agent@example.com", name="Agent User")
        agent.set_password("password123")
        agent.roles.append(role_agent)

        customer = User(email="customer@example.com", name="Customer User")
        customer.set_password("password123")
        customer.roles.append(role_customer)

        db.session.add_all([admin, agent, customer])
        db.session.commit()

        # 3. Create Categories
        print("Creating categories...")
        cat_billing = Category(name="Billing", description="Issues related to invoices and payments")
        cat_tech = Category(name="Technical Issue", description="Bugs, errors, and technical support")
        cat_account = Category(name="Account Access", description="Login issues and password resets")
        cat_feature = Category(name="Feature Request", description="Suggestions for new features")
        db.session.add_all([cat_billing, cat_tech, cat_account, cat_feature])
        db.session.commit()

        # 4. Create Sample Ticket
        print("Creating sample ticket...")
        ticket = Ticket(
            subject="Cannot login to my account",
            description="I keep getting an invalid password error even after resetting it.",
            status="open",
            priority="high",
            customer_id=customer.id,
            category_id=cat_account.id,
        )
        db.session.add(ticket)
        db.session.commit()

        # 5. Create Sample Comment
        print("Creating sample comment...")
        comment = Comment(
            body="Hi, I have checked the logs and it seems your account was locked. I've unlocked it. Please try again.",
            ticket_id=ticket.id,
            author_id=agent.id,
        )
        db.session.add(comment)
        db.session.commit()

        print("Seeding completed successfully!")


if __name__ == "__main__":
    seed()