from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List

class MultipleChoice(BaseModel):
    question : str = Field(description="the question")
    option : List[str]  = Field(description="the option to answer the question with one of them is the correct answer")
    answer : str = Field(description="the correct answer for the question. the answer is from the option")
    explanation : str = Field(description="the explanation for the answer")

class MultipleAnswer(BaseModel):
    question : str = Field(description="the question")
    option : List[str]  = Field(description="the option to answer the question. more than one of them is the correct answer")
    answer : List[str] = Field(description="the correct answer for the question. the answers is from the option")
    explanation : str = Field(description="the explanation for the answers")

class Essay(BaseModel):
    question : str = Field(description="the question")
    answer : str  = Field(description="the answer for the answer")
    explanatoin : str = Field(description="the explanation for the answers")