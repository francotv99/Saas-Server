"""
Seed script for local testing.
Creates sample organizations, users, and tasks.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.models.organization import Organization
from app.models.task import Task, TaskStatus, TaskPriority
from app.core.security import get_password_hash


async def seed_data():
    """Seed the database with sample data."""
    async with AsyncSessionLocal() as session:
        try:
            # Create Organization 1: Acme Corp
            org1 = Organization(
                name="Acme Corp",
                slug="acme-corp"
            )
            session.add(org1)
            await session.flush()
            
            # Create users for Org 1
            admin1 = User(
                email="admin@acme.com",
                hashed_password=get_password_hash("admin123"),
                full_name="Admin User",
                role=UserRole.ADMIN,
                organization_id=org1.id
            )
            member1 = User(
                email="member@acme.com",
                hashed_password=get_password_hash("member123"),
                full_name="Member User",
                role=UserRole.MEMBER,
                organization_id=org1.id
            )
            session.add_all([admin1, member1])
            await session.flush()
            
            # Create tasks for Org 1
            tasks_org1 = [
                Task(
                    title="Setup CI/CD pipeline",
                    description="Configure GitHub Actions for automated testing",
                    status=TaskStatus.IN_PROGRESS,
                    priority=TaskPriority.HIGH,
                    organization_id=org1.id,
                    assignee_id=admin1.id
                ),
                Task(
                    title="Write API documentation",
                    description="Document all endpoints with OpenAPI",
                    status=TaskStatus.TODO,
                    priority=TaskPriority.MEDIUM,
                    organization_id=org1.id,
                    assignee_id=member1.id
                ),
                Task(
                    title="Review code changes",
                    description="Review PR #42",
                    status=TaskStatus.DONE,
                    priority=TaskPriority.LOW,
                    organization_id=org1.id,
                    assignee_id=admin1.id
                ),
            ]
            session.add_all(tasks_org1)
            
            # Create Organization 2: TechStart Inc
            org2 = Organization(
                name="TechStart Inc",
                slug="techstart-inc"
            )
            session.add(org2)
            await session.flush()
            
            # Create users for Org 2
            admin2 = User(
                email="admin@techstart.com",
                hashed_password=get_password_hash("admin123"),
                full_name="TechStart Admin",
                role=UserRole.ADMIN,
                organization_id=org2.id
            )
            member2 = User(
                email="dev@techstart.com",
                hashed_password=get_password_hash("dev123"),
                full_name="Developer",
                role=UserRole.MEMBER,
                organization_id=org2.id
            )
            session.add_all([admin2, member2])
            await session.flush()
            
            # Create tasks for Org 2
            tasks_org2 = [
                Task(
                    title="Design database schema",
                    description="Create ERD for new feature",
                    status=TaskStatus.TODO,
                    priority=TaskPriority.HIGH,
                    organization_id=org2.id,
                    assignee_id=admin2.id
                ),
                Task(
                    title="Implement authentication",
                    description="Add JWT-based auth",
                    status=TaskStatus.IN_PROGRESS,
                    priority=TaskPriority.HIGH,
                    organization_id=org2.id,
                    assignee_id=member2.id
                ),
            ]
            session.add_all(tasks_org2)
            
            await session.commit()
            print("✅ Seed data created successfully!")
            print("\nSample users:")
            print("  Org 1 (Acme Corp):")
            print("    - admin@acme.com / admin123 (ADMIN)")
            print("    - member@acme.com / member123 (MEMBER)")
            print("  Org 2 (TechStart Inc):")
            print("    - admin@techstart.com / admin123 (ADMIN)")
            print("    - dev@techstart.com / dev123 (MEMBER)")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error seeding data: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(seed_data())
