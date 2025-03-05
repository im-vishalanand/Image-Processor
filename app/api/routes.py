from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
import uuid
import csv
from app.database.database import SessionLocal
from app.database.models import Request, Image
from app.worker.tasks import process_images_task
from app.schemas.response import StatusResponse
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/upload/")
async def upload_csv(file: UploadFile = File(...), background_tasks: BackgroundTasks = BackgroundTasks()):
    """
    Uploads a CSV file, validates the format, stores metadata, and initiates async image processing.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    request_id = str(uuid.uuid4())
    db: Session = SessionLocal()

    try:
        content = await file.read()
        decoded_content = content.decode("utf-8").splitlines()
        csv_reader = csv.reader(decoded_content)
        next(csv_reader, None)  # Skip header

        new_request = Request(request_id=request_id, status="processing")
        db.add(new_request)
        db.commit()

        for row in csv_reader:
            if len(row) < 3:
                continue
            serial_number, product_name, input_urls = row[0], row[1], row[2]
            urls = input_urls.split(",")

            for url in urls:
                new_image = Image(
                    request_id=request_id,
                    product_name=product_name.strip(),
                    input_url=url.strip(),
                    status="pending"
                )
                db.add(new_image)

        db.commit()
        db.close()

        background_tasks.add_task(process_images_task, request_id)

        return {"request_id": request_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.get("/status/{request_id}", response_model=StatusResponse)
def check_status(request_id: str):
    db: Session = SessionLocal()
    request = db.query(Request).filter(Request.request_id == request_id).first()
    
    if not request:
        db.close()
        raise HTTPException(status_code=404, detail="Request ID not found.")

    images = db.query(Image).filter_by(request_id=request_id).all()
    db.close()

    return {
        "request_id": request_id,
        "status": request.status,
        "images": [{"input": img.input_url, "output": img.output_url or "processing"} for img in images]
    }
