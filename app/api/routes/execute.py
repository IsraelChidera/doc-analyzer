import os
import tempfile

from dotenv import load_dotenv
from fastapi import APIRouter, File, Form, UploadFile
from google import genai
from enum import Enum

load_dotenv(".env.local")

API_KEY = os.environ["API_KEY"]

router = APIRouter()
client = genai.Client(api_key=API_KEY)

subject = """
            You are a file analysis assistant.

            Your job is to carefully analyze the file provided by the user.

            Answer questions using information from the file.

            If the answer cannot be found in the file, clearly say that the information is not available in the file.

            Do not invent facts.

            When useful, organize your answer with headings and bullet points.
        """

class ScopeEnum(str, Enum):
    ANALYSE = "analyse"
    SUMMARISE = "summarise"
    EXTRACT = "extract"
    EXPLAIN = "explain"
    CLASSIFY = "classify"
    EVALUATE = "evaluate"


@router.post("/execute")
async def execute(file: UploadFile = File(...), scope_name: ScopeEnum = "Analyse"):
    suffix = os.path.splitext(file.filename or "")[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        my_file = client.files.upload(file=tmp_path)

        interaction = client.interactions.create(
            model="gemini-3.8-flash",
            input=[
                {"type": "text", "text": subject},
                {"type": "text", "text": scope_name},
                {"type": "document", "uri": my_file.uri, "mime_type": my_file.mime_type}
            ]
        )

        return {"output": interaction.output_text}

    except Exception as e:
        return {"error": str(e)}

    finally:
        os.remove(tmp_path)
