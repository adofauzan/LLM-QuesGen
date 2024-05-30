from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
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

("system", """You are a quiz generator. Your job is to create question to test the competency of the question taker. When creating the question, ensure that the question demands critical thinking and an in-depth understanding of the subject matter. Additionally, provide detailed answers for each question to offer clarity and accuracy in evaluation.
Use the following pieces of context along with your already known knowledge to create the question.
If the given context does not help in creating the question, don't use it. Don't change the subject of the created question from the subject asked.
{context}"""),
("human", "Make {amount} a {q_type} question about the subject {subject}. Write it in {language}."),
MessagesPlaceholder("extra", optional=True),
("system", "Format Instruction:{format_instructions}")
    

def chat_rag(self, extra, q_type, subject, lang, vector_db):
        retrieval = vector_db.similarity_search_with_score(subject, k=5)
        context = "\n\n---\n\n".join([doc.page_content for doc, _score in retrieval])

        if lang == "ENG":
            template = templates[0][1]
        elif lang == "INA":
            template = templates[1][1]
        
        if q_type == "single":
            q_object = MultipleChoice()
        elif q_type == "text":
            ques_type = Essay()
        elif q_type == "multiple-answer":
            ques_type = MultipleAnswer()
            
        chat_template=ChatPromptTemplate.from_messages(template)
        prompt = chat_template.format_messages(amount = "5",q_type=ques_type, subject=subject, language=lang, extra=extra, context=context)
        
        model = self.gpu_llm
        parser = JsonOutputParser(pydantic_object=q_object)

        chain = chat_template | model | parser.get_format_instructions()
        
        response_text = model.invoke({
            "extra":"", 
            "q_type": "", 
            "subject": ("human", extra), 
            "lang": ""
        })

        formatted_response = f"{response_text}"
        return(formatted_response)