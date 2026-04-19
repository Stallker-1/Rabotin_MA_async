from fastapi import APIRouter, BackgroundTasks

router = APIRouter(prefix="/notify", tags=["notifications"])


def send_email(email: str, message: str):
    import time
    time.sleep(2)
    print(f"Email sent to {email}: {message}")


@router.post("/email")
async def notify_email(
    email: str,
    message: str,
    background_tasks: BackgroundTasks,
):
    background_tasks.add_task(send_email, email, message)

    return {"status": "email will be sent in background"}