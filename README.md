# Image Processor - FastAPI & Celery

## 📌 Project Overview
This project is an **asynchronous image processing system** built using **FastAPI** and **Celery**. It allows users to upload a CSV file containing image URLs, process them asynchronously, and retrieve the processed images using a unique request ID. A webhook is triggered when processing is complete.

## 🚀 Tech Stack
- **Backend Framework**: FastAPI
- **Asynchronous Task Queue**: Celery with Redis
- **Database**: MySQL (via SQLAlchemy ORM)
- **Storage**: Local (Can be extended to S3/MinIO)
- **Image Processing**: Pillow (PIL)
- **Environment Variables**: Python-dotenv

---

## 📁 Project Structure
```
Image-Processor/
│── main.py                 # FastAPI app entry point
│── worker.py               # Celery worker for async processing
│── database.py             # Database connection setup
│── models.py               # SQLAlchemy models (Request, Image)
│── schemas.py              # Pydantic schemas for API validation
│── routes.py               # FastAPI endpoints (Upload, Status, Webhook)
│── requirements.txt        # Dependencies list
│── .env                    # Environment variables
│── README.md               # Project documentation
```

---

## ⚙️ Setup & Installation

### 1️⃣ Clone the Repository
```sh
git clone <repo-link>
cd Image-Processor
```

### 2️⃣ Install Dependencies
```sh
python -m pip install -r requirements.txt
```

### 3️⃣ Set Up MySQL Database & Redis
Ensure MySQL and Redis are running. If not:
```sh
sudo service mysql start
redis-server
```

### 4️⃣ Configure Environment Variables (`.env`)
Create a `.env` file and add:
```env
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/image_processor
REDIS_URL=redis://localhost:6379/0
WEBHOOK_URL=https://webhook.site/your-webhook-url
```

### 5️⃣ Start FastAPI Server
```sh
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 6️⃣ Start Celery Worker
```sh
python -m celery -A worker worker --loglevel=info
```

---

## 📌 Database Schema
### **Request Table**
| Column      | Type    | Description                       |
|------------|--------|-----------------------------------|
| id         | INT    | Primary Key (Auto Increment)     |
| request_id | STRING | Unique Identifier for a request  |
| status     | STRING | Request status (`processing`, `complete`) |

### **Image Table**
| Column      | Type    | Description                       |
|------------|--------|-----------------------------------|
| id         | INT    | Primary Key (Auto Increment)     |
| request_id | STRING | Foreign Key (References `requests`) |
| product_name | STRING | Product Name |
| input_url  | STRING | Original Image URL |
| output_url | STRING | Processed Image URL (After compression) |
| status     | STRING | Status (`pending`, `complete`) |

---

## 📌 API Documentation
### **1️⃣ Upload API (CSV Upload & Processing Start)**
**Endpoint:** `POST /upload/`
- **Request:**
```http
POST http://localhost:8000/upload/
Content-Type: multipart/form-data
```
- **Response:**
```json
{
    "request_id": "8f66974a-2d24-4cc4-a8d9-5ed8391cfb6b"
}
```

### **2️⃣ Check Status API**
**Endpoint:** `GET /status/{request_id}`
- **Response:**
```json
{
    "request_id": "8f66974a-2d24-4cc4-a8d9-5ed8391cfb6b",
    "status": "complete",
    "images": [
        {
            "input": "https://example.com/input1.jpg",
            "output": "https://example.com/output1.jpg"
        }
    ]
}
```

### **3️⃣ Webhook API (Triggered after processing is done)**
**Endpoint:** `POST /webhook/`
- **Payload:**
```json
{
    "request_id": "8f66974a-2d24-4cc4-a8d9-5ed8391cfb6b",
    "status": "complete"
}
```

---

## 📌 Asynchronous Workers (Celery)
- **Celery picks up pending image processing tasks**
- **Compresses images by 50%**
- **Stores the processed image URL**
- **Updates MySQL database**
- **Triggers webhook upon completion**

---

## 🔗 Postman Collection
A public Postman collection for testing the API can be found here:
[Postman Collection Link](<https://drive.google.com/file/d/1kiMdNHyNZSFBqUUnL4zOb-9UboilIHXO/view?usp=sharing>)

---
