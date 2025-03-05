# --- worker.py (Celery worker for async processing) ---
from celery import Celery
import requests
import time
from database import SessionLocal
from app.database.models import Image, Request

celery = Celery(
    "worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

WEBHOOK_URL = "https://webhook.site/925155cc-322d-4880-ba2f-56e04481bc5d"

@celery.task
def process_images_task(request_id):
    """
    Processes all images related to a request ID and updates the database with output URLs.
    """
    db = SessionLocal()
    try:
        images = db.query(Image).filter(Image.request_id == request_id, Image.status == "pending").all()

        if not images:
            return {"request_id": request_id, "status": "no images found"}

        for image in images:
            time.sleep(2)  # Simulate processing time
            processed_url = image.input_url.replace("public-image", "public-image-output")

            # Update DB
            image.output_url = processed_url
            image.status = "complete"  # Fixed status to match DB
            db.commit()

        # Update request status to "complete" if all images are processed
        request = db.query(Request).filter(Request.request_id == request_id).first()
        if request:
            request.status = "complete"
            db.commit()

        # Send Webhook Notification
        response = requests.post(WEBHOOK_URL, json={"request_id": request_id, "status": "complete"})
        response.raise_for_status()  # Ensure webhook call was successful

        return {"request_id": request_id, "status": "complete"}

    except Exception as e:
        db.rollback()
        return {"request_id": request_id, "error": str(e)}

    finally:
        db.close()
