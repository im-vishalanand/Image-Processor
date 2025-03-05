from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
import uuid
import csv
import logging
from database import SessionLocal, engine, Base
from models import Request, Image
from worker import process_images_task
from schemas import StatusResponse
from sqlalchemy.orm import Session

app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/upload/")
async def upload_csv(file: UploadFile = File(...), background_tasks: BackgroundTasks = BackgroundTasks()):
    """
    Uploads a CSV file, validates the format, stores metadata, and initiates async image processing.
    """
    # Ensure it's a CSV file
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    request_id = str(uuid.uuid4())
    db: Session = SessionLocal()

    try:
        # Read CSV content
        content = await file.read()
        decoded_content = content.decode("utf-8").splitlines()
        csv_reader = csv.reader(decoded_content)

        # Skip header
        next(csv_reader, None)

        # Create request entry
        new_request = Request(request_id=request_id, status="processing")
        db.add(new_request)
        db.commit()

        images_to_process = []

        for row in csv_reader:
            if len(row) < 3:
                continue  # Skip invalid rows

            serial_number, product_name, input_urls = row[0], row[1], row[2]
            urls = [url.strip() for url in input_urls.split(",") if url.strip()]

            for url in urls:
                new_image = Image(
                    request_id=request_id,
                    product_name=product_name.strip(),
                    input_url=url,
                    status="pending"
                )
                db.add(new_image)

        db.commit()
        db.close()

        logger.info(f"Request {request_id} added. Processing started...")

        # Trigger background task
        background_tasks.add_task(process_images_task, request_id)

        return {"request_id": request_id}

    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.get("/status/{request_id}", response_model=StatusResponse)
def check_status(request_id: str):
    """
    Checks the processing status using request ID.
    """
    db: Session = SessionLocal()
    request = db.query(Request).filter(Request.request_id == request_id).first()

    if not request:
        db.close()
        raise HTTPException(status_code=404, detail="Request ID not found.")

    images = db.query(Image).filter_by(request_id=request_id).all()
    db.close()

    # Check if all images are processed
    if all(img.status == "complete" for img in images):
        request.status = "complete"
        db.commit()
    
    return {
        "request_id": request_id,
        "status": request.status,
        "images": [{"input": img.input_url, "output": img.output_url or "processing"} for img in images]
    }

@app.post("/webhook/")
def webhook(payload: dict):
    """
    Webhook endpoint that gets triggered when processing is complete.
    """
    logger.info(f"Webhook received: {payload}")
    return {"message": "Webhook received successfully."}
