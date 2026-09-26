from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate


class TaskNotFoundError(Exception):
    pass


class NotAuthorizedError(Exception):
    pass


async def create_task(db: AsyncSession, owner_id: int, data: TaskCreate) -> Task:
    task = Task(**data.model_dump(), owner_id=owner_id)
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def list_tasks(
    db: AsyncSession,
    owner_id: int,
    status_filter: TaskStatus | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[Task]:
    query = select(Task).where(Task.owner_id == owner_id)
    if status_filter:
        query = query.where(Task.status == status_filter)
    query = query.limit(limit).offset(offset).order_by(Task.created_at.desc())

    result = await db.execute(query)
    return list(result.scalars().all())


async def _get_owned_task(db: AsyncSession, task_id: int, owner_id: int) -> Task:
    """
    Shared helper enforcing the rule that matters most here: a user can
    only ever touch their own tasks. Centralizing this in one place means
    every route that needs it gets the check for free, instead of each
    route re-implementing (and potentially forgetting) it.
    """
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if task is None:
        raise TaskNotFoundError(f"Task {task_id} not found")
    if task.owner_id != owner_id:
        raise NotAuthorizedError("You do not have access to this task")

    return task


async def get_task(db: AsyncSession, task_id: int, owner_id: int) -> Task:
    return await _get_owned_task(db, task_id, owner_id)


async def update_task(db: AsyncSession, task_id: int, owner_id: int, data: TaskUpdate) -> Task:
    task = await _get_owned_task(db, task_id, owner_id)

    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(task, field, value)

    await db.commit()
    await db.refresh(task)
    return task


async def delete_task(db: AsyncSession, task_id: int, owner_id: int) -> None:
    task = await _get_owned_task(db, task_id, owner_id)
    await db.delete(task)
    await db.commit()
