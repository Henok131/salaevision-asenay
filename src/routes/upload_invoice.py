from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from routes.auth import get_current_user
from utils.db_utils import supabase
from ocr.extract_invoice_data import extract_invoice_fields
from typing import Optional
import io
from PIL import Image
import pytesseract
import os

router = APIRouter()

@router.post('/upload_invoice/{lead_id}')
async def upload_invoice(lead_id: str, file: UploadFile = File(...), user = Depends(get_current_user)):
    sb = supabase()
    # Verify lead exists
    lead = sb.table('leads').select('id').eq('id', lead_id).limit(1).execute()
    if not lead.data:
        raise HTTPException(status_code=404, detail='Lead not found')

    content = await file.read()
    # Upload to Supabase Storage (assumes bucket 'invoices' exists)
    path = f"{lead_id}/{file.filename}"
    try:
        sb.storage.from_('invoices').upload(path, content, {
            'content-type': file.content_type or 'application/octet-stream',
            'upsert': True
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")

    # OCR for image or PDF-first page (PDF OCR simplified)
    text = ''
    try:
        if file.content_type and 'image' in file.content_type:
            img = Image.open(io.BytesIO(content))
            text = pytesseract.image_to_string(img)
        elif file.content_type == 'application/pdf':
            # Placeholder: in production, convert first page to image and OCR
            text = ''
        else:
            text = ''
    except Exception:
        text = ''

    fields = extract_invoice_fields(text or '')

    # Save invoice record
    rec = sb.table('invoices').insert({
        'lead_id': lead_id,
        'file_path': path,
        'parsed_json': fields,
    }).execute()

    # Optional: Google Drive upload using service account (path only; client wiring handled externally)
    if str(os.getenv('ENABLE_DRIVE', 'false')).lower() == 'true':
        # Placeholder: in production, use Google Drive API client with service account JSON
        # Here we just log intent; actual upload should be implemented in a Drive service
        pass

    return { 'invoice_id': rec.data[0]['id'] if rec.data else None, 'file_path': path, 'parsed': fields }
