from celery import Celery
import requests
from app.database.database import SessionLocal
from app.database.models import Image, Request
import time

celery = Celery("worker", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0")

WEBHOOK_URL = "https://webhook.site/your-webhook-url"

@celery.task
def process_images_task(request_id):
    db = SessionLocal()
    try:
        images = db.query(Image).filter(Image.request_id == request_id, Image.status == "pending").all()

        if not images:
            return {"request_id": request_id, "status": "no images found"}

        for image in images:
            time.sleep(2)  # Simulate processing
            processed_url = image.input_url.replace("public-image", "public-image-output")

            image.output_url = processed_url
            image.status = "complete"
            db.commit()

        request = db.query(Request).filter(Request.request_id == request_id).first()
        if request:
            request.status = "complete"
            db.commit()

        requests.post(WEBHOOK_URL, json={"request_id": request_id, "status": "complete"})
        return {"request_id": request_id, "status": "complete"}

    except Exception as e:
        db.rollback()
        return {"request_id": request_id, "error": str(e)}

    finally:
        db.close()
