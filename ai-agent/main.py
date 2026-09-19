import uuid
import json
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from langchain_core.messages import HumanMessage, AIMessageChunk
from langgraph.types import Command

from dotenv import load_dotenv
from psycopg import connect

from graph import agent


# =========================================================
# DATABASE
# =========================================================

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in .env")

db = connect(DATABASE_URL)


# =========================================================
# THREAD TABLE
# =========================================================

with db.cursor() as cursor:

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS aegis_threads (
            thread_id TEXT PRIMARY KEY
        )
    """)

db.commit()


# =========================================================
# FASTAPI
# =========================================================

app = FastAPI(
    title="Aegis AI Operating System"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# PYDANTIC MODELS
# =========================================================

class ChatRequest(BaseModel):
    message: str


class ResumeRequest(BaseModel):
    approved: bool


# =========================================================
# CREATE NEW THREAD
# =========================================================

@app.post("/threads")
def create_thread():

    thread_id = str(uuid.uuid4())

    with db.cursor() as cursor:

        cursor.execute(
            """
            INSERT INTO aegis_threads (thread_id)
            VALUES (%s)
            """,
            (thread_id,)
        )

    db.commit()

    return {
        "thread_id": thread_id
    }


# =========================================================
# GET ALL THREADS
# =========================================================

@app.get("/threads")
def get_threads():

    with db.cursor() as cursor:

        cursor.execute(
            """
            SELECT thread_id
            FROM aegis_threads
            """
        )

        threads = cursor.fetchall()

    return [
        {
            "thread_id": thread[0]
        }
        for thread in threads
    ]


# =========================================================
# GET ONE THREAD
# =========================================================

@app.get("/threads/{thread_id}")
def get_thread(thread_id: str):

    with db.cursor() as cursor:

        cursor.execute(
            """
            SELECT thread_id
            FROM aegis_threads
            WHERE thread_id = %s
            """,
            (thread_id,)
        )

        thread = cursor.fetchone()

    if not thread:

        raise HTTPException(
            status_code=404,
            detail="Thread not found"
        )


    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }


    state = agent.get_state(config)


    messages = []


    for message in state.values.get("messages", []):

        messages.append({
            "type": message.type,
            "content": message.content
        })


    return {
        "thread_id": thread_id,
        "messages": messages
    }


# =========================================================
# CHAT
# =========================================================

@app.post("/threads/{thread_id}/chat")
def chat(
    thread_id: str,
    request: ChatRequest
):

    # -----------------------------------------------------
    # CHECK THREAD
    # -----------------------------------------------------

    with db.cursor() as cursor:

        cursor.execute(
            """
            SELECT thread_id
            FROM aegis_threads
            WHERE thread_id = %s
            """,
            (thread_id,)
        )

        if not cursor.fetchone():

            raise HTTPException(
                status_code=404,
                detail="Thread not found"
            )


    # -----------------------------------------------------
    # LANGGRAPH CONFIG
    # -----------------------------------------------------

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }


    # -----------------------------------------------------
    # STREAM GENERATOR
    # -----------------------------------------------------

    def generate():

        for chunk in agent.stream(

            {
                "messages": [
                    HumanMessage(
                        content=request.message
                    )
                ]
            },

            config=config,

            stream_mode=[
                "messages",
                "updates"
            ],

            version="v2"
        ):


            # =================================================
            # AI MESSAGE STREAM
            # =================================================

            if chunk["type"] == "messages":

                message, metadata = chunk["data"]


                # ---------------------------------------------
                # ONLY STREAM AI MESSAGE CHUNKS
                # ---------------------------------------------

                if (
                    isinstance(message, AIMessageChunk)
                    and isinstance(message.content, str)
                    and message.content
                ):

                    yield json.dumps(
                        {
                            "type": "message",
                            "content": message.content
                        }
                    ) + "\n"


            # =================================================
            # GRAPH UPDATES
            # =================================================

            elif chunk["type"] == "updates":

                # ---------------------------------------------
                # HITL INTERRUPT
                # ---------------------------------------------

                if "__interrupt__" in chunk["data"]:

                    interrupt_data = (
                        chunk["data"]["__interrupt__"][0]
                    )


                    yield json.dumps(
                        {
                            "type": "interrupt",
                            "message": interrupt_data.value
                        }
                    ) + "\n"


                    # -----------------------------------------
                    # STOP STREAM
                    # -----------------------------------------

                    return


    # -----------------------------------------------------
    # RETURN STREAM
    # -----------------------------------------------------

    return StreamingResponse(
        generate(),
        media_type="application/x-ndjson"
    )


# =========================================================
# RESUME INTERRUPTED TASK
# =========================================================

@app.post("/threads/{thread_id}/resume")
def resume(
    thread_id: str,
    request: ResumeRequest
):

    # -----------------------------------------------------
    # CHECK THREAD
    # -----------------------------------------------------

    with db.cursor() as cursor:

        cursor.execute(
            """
            SELECT thread_id
            FROM aegis_threads
            WHERE thread_id = %s
            """,
            (thread_id,)
        )

        if not cursor.fetchone():

            raise HTTPException(
                status_code=404,
                detail="Thread not found"
            )


    # -----------------------------------------------------
    # LANGGRAPH CONFIG
    # -----------------------------------------------------

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }


    # -----------------------------------------------------
    # STREAM GENERATOR
    # -----------------------------------------------------

    def generate():

        for chunk in agent.stream(

            Command(
                resume=request.approved
            ),

            config=config,

            stream_mode=[
                "messages",
                "updates"
            ],

            version="v2"
        ):


            # =================================================
            # AI MESSAGE STREAM
            # =================================================

            if chunk["type"] == "messages":

                message, metadata = chunk["data"]


                # ---------------------------------------------
                # ONLY STREAM AI MESSAGE CHUNKS
                # ---------------------------------------------

                if (
                    isinstance(message, AIMessageChunk)
                    and isinstance(message.content, str)
                    and message.content
                ):

                    yield json.dumps(
                        {
                            "type": "message",
                            "content": message.content
                        }
                    ) + "\n"


            # =================================================
            # GRAPH UPDATES
            # =================================================

            elif chunk["type"] == "updates":

                # ---------------------------------------------
                # ANOTHER HITL INTERRUPT
                # ---------------------------------------------

                if "__interrupt__" in chunk["data"]:

                    interrupt_data = (
                        chunk["data"]["__interrupt__"][0]
                    )


                    yield json.dumps(
                        {
                            "type": "interrupt",
                            "message": interrupt_data.value
                        }
                    ) + "\n"


                    return


    # -----------------------------------------------------
    # RETURN STREAM
    # -----------------------------------------------------

    return StreamingResponse(
        generate(),
        media_type="application/x-ndjson"
    )


# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )