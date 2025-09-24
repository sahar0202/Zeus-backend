from fastapi import FastAPI, Requestfrom pydantic import BaseModelimport requestsimport osimport google.generativeai as genaiInisialisasi aplikasi FastAPIapp = FastAPI()Konfigurasi Gemini API dan SendGrid API Key dari environment variableIni penting untuk keamanan di GitHub dan Rendertry:genai.configure(api_key=os.environ["GEMINI_API_KEY"])SENDGRID_API_KEY = os.environ["SENDGRID_API_KEY"]except KeyError:print("WARNING: Kunci API tidak ditemukan. Pastikan Anda mengaturnya di Render/GitHub Secrets.")SENDGRID_API_KEY = "SG.xxxxx..."  # Placeholder, JANGAN gunakan di produksiInisialisasi modelmodel = genai.GenerativeModel('gemini-1.5-flash')File lokal untuk memoriMEMORY_FILE = "zeus_memories.txt"Model Pydantic untuk validasi dataclass ZeusCommand(BaseModel):prompt: strFungsi untuk menyimpan memori ke filedef store_memory(text_to_store):with open(MEMORY_FILE, "a", encoding='utf-8') as f:f.write(text_to_store + "\n")return f"Ingatan berhasil disimpan: '{text_to_store}'"Fungsi untuk mengambil memori dari filedef retrieve_memory(query):memories = []if os.path.exists(MEMORY_FILE):with open(MEMORY_FILE, "r", encoding='utf-8') as f:memories = f.readlines()relevant_memory = [m.strip() for m in memories if query.lower() in m.lower()]

if relevant_memory:
    return "Saya ingat ini: " + ", ".join(relevant_memory)
else:
    return "Tidak ada ingatan yang relevan ditemukan."
Endpoint untuk memeriksa status backend@app.get("/health")def health():return {"status": "Zeus backend aktif", "owner": "marsyah.ai"}Endpoint utama untuk berinteraksi dengan Zeus@app.post("/ask-zeus")def ask_zeus(data: ZeusCommand):if not data.prompt:return {"response": "Perintah kosong. Mohon berikan perintah yang valid."}# Tambahkan memori ke prompt
memory_context = retrieve_memory(data.prompt)
full_prompt = f"Konteks memori: {memory_context}\n\nPrompt: {data.prompt}"

try:
    response = model.generate_content(full_prompt)
    ai_response = response.text
    
    # Simpan prompt dan respons ke memori
    store_memory(f"Anda: {data.prompt}")
    store_memory(f"Zeus: {ai_response}")
    
    return {"response": ai_response}
except Exception as e:
    return {"response": f"Terjadi kesalahan: {str(e)}"}
Endpoint untuk mengirim email@app.post("/send-email")async def send_email(request: Request):body = await request.json()to = body.get("to")subject = body.get("subject")content = body.get("content")headers = {
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
