import copy
import time
from typing import Dict, List, Literal, Optional, Union

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dashscope import Generation

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ModelCard(BaseModel):
    id: str
    object: str = "model"
    created: int = Field(default_factory=lambda: int(time.time()))
    owned_by: str = "owner"
    root: Optional[str] = None
    parent: Optional[str] = None
    permission: Optional[list] = None


class ModelList(BaseModel):
    object: str = "list"
    data: List[ModelCard] = []


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system", "function"]
    content: Optional[str]
    function_call: Optional[Dict] = None


class DeltaMessage(BaseModel):
    role: Optional[Literal["user", "assistant", "system"]] = None
    content: Optional[str] = None


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    functions: Optional[List[Dict]] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    max_length: Optional[int] = None
    stream: Optional[bool] = False
    stop: Optional[List[str]] = None


class ChatCompletionResponseChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: Literal["stop", "length", "function_call"]


class ChatCompletionResponseStreamChoice(BaseModel):
    index: int
    delta: DeltaMessage
    finish_reason: Optional[Literal["stop", "length"]]


class ChatCompletionResponse(BaseModel):
    model: str
    object: Literal["chat.completion", "chat.completion.chunk"]
    choices: List[
        Union[ChatCompletionResponseChoice, ChatCompletionResponseStreamChoice]
    ]
    created: Optional[int] = Field(default_factory=lambda: int(time.time()))


@app.get("/v1/models", response_model=ModelList)
async def list_models():
    global model_args
    model_card = ModelCard(id="qwen-max")
    return ModelList(data=[model_card])


def parse_messages(messages):
    if all(m.role != "user" for m in messages):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid request: Expecting at least one user message.",
        )

    messages = copy.deepcopy(messages)

    _messages = messages
    messages = []
    for m_idx, m in enumerate(_messages):
        role, content = m.role, m.content
        if content:
            content = content.lstrip("\n").rstrip()
        if role == "system":
            messages.append(
                {"role":role, "content":content.lstrip("\n").rstrip()}
            )
        elif role == "assistant":
            if messages[-1].role == "user":
                messages.append(
                    {"role":role, "content":content.lstrip("\n").rstrip()}
                )
            else:
                messages[-1].content += content
        elif role == "user":
            messages.append(
                {"role":role, "content":content.lstrip("\n").rstrip()}
            )
        else:
            raise HTTPException(
                status_code=400, detail=f"Invalid request: Incorrect role {role}."
            )
    return messages



@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def create_chat_completion(request: ChatCompletionRequest):

    if request.stop:
        stop_list = request.stop
    else:
        stop_list = []

    messages = parse_messages(request.messages)

    response = Generation.call(
                "qwen-max",
                messages=messages,
                result_format='message',
                stop = stop_list
            )

    response = response.output.choices[0].message.content

    print(f"<chat>\n{messages}\n<!-- *** -->\n{response}\n</chat>")

    choice_data = ChatCompletionResponseChoice(
            index=0,
            message=ChatMessage(role="assistant", content=response),
            finish_reason="stop",
        )

    return ChatCompletionResponse(
        model=request.model, choices=[choice_data], object="chat.completion"
    )


if __name__ == "__main__":

    api_key = ""

    uvicorn.run(app, host='0.0.0.0', port=8006, workers=1)