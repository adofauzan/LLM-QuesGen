from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser

class MultipleChoice(BaseModel):
    question : str = Field(description="the question")
    option : List[str]  = Field