from fastapi import FastAPI, Request
from pydantic import BaseModel
import requests

app = FastAPI()

class ZeusCommand(BaseModel):
    prompt: str

@app.get("/health")
def health():
    return {"status": "Zeus backend aktif", "owner": "marsyah.ai"}

@app.post("/ask-zeus")
def ask_zeus(data: ZeusCommand):
    # Contoh logika sederhana untuk merespons prompt
    response = f"Zeus menerima perintah: {data.prompt}"
    return {"response": response}

@app.post("/send-email")
async def send_email(request: Request):
    body = await request.json()
    to = body.get("to")
    subject = body.get("subject")
    content = body.get("content")

    # Kirim email via SendGrid
    SENDGRID_API_KEY = "SG.xxxxx..."  # Ganti dengan Secrets di Render
    headers = {
        "Authorization": f"Bearer {SENDGRID_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "personalizations": [{"to": [{"email": to}]}],
        "from": {"email": "zeus@marsyah.ai"},
        "subject": subject,
        "content": [{"type": "text/plain", "value": content}]
    }
    r = requests.post("https://api.sendgrid.com/v3/mail/send", json=payload, headers=headers)
    return {"status": r.status_code, "message": "Email dikirim" if r.status_code == 202 else "Gagal mengirim"}
if __name__ == "__main__":
    import uvicorn
    print("🚀 Zeus mencoba bangkit...")
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
