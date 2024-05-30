from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline
from langchain.prompts import ChatPromptTemplate
from question_type import MultipleAnswer, MultipleChoice, Essay
from langchain_core.output_parsers import JsonOutputParser

templates = (
    ("english", [("system", """You are a quiz generator. Your job is to create question to test the competency of the question taker. When creating the question, ensure that the question demands critical thinking and an in-depth understanding of the subject matter. Additionally, provide detailed answers for each question to offer clarity and accuracy in evaluation.
Use the following pieces of context along with your already known knowledge to create the question.
If the given context does not help in creating the question, don't use it. Don't change the subject of the created question from the subject asked.
{context}"""),
("human", "Make {amount} {q_type} question about the subject {subject}. Write it in {language}.{extra}"),
("system", "Format Instruction:{format_instructions}")
]),
    ("indonesia", [("system", """Anda adalah generator kuis. Tugas Anda adalah membuat pertanyaan untuk menguji kompetensi peserta kuis. Saat membuat pertanyaan, pastikan bahwa pertanyaan tersebut menuntut pemikiran kritis dan pemahaman mendalam tentang materi yang ditanyakan. Selain itu, berikan jawaban terperinci untuk setiap pertanyaan untuk memberikan kejelasan dan akurasi dalam evaluasi.
Gunakan potongan konteks berikut bersama dengan pengetahuan yang sudah Anda ketahui untuk membuat pertanyaan.
Jika konteks yang diberikan tidak membantu dalam membuat pertanyaan, jangan gunakan konteks tersebut. Jangan mengubah subjek pertanyaan yang dibuat dari subjek yang diminta.
{context}"""),
("human", "Buatlah {amount} pertanyaan {q_type} tentang subjek {subject}. Tulis dalam bahasa {language}.{extra}"),
("system", "Instruksi Format:{format_instructions}")
    ])
)

class LLMHandler:
    def __init__(self):
        self.is_initialized = False
        self.gpu_llm = None
        self.initialize()

    def initialize(self):
        try:
            self.gpu_llm = HuggingFacePipeline.from_model_id(
                model_id="./Mistral-7B-Instruct-v0.2",
                task="text-generation",  
                device=0,  # replace with device_map="auto" to use the accelerate library.
                pipeline_kwargs={"max_new_tokens": 3000} 
            )
            self.is_initialized = True  
        except Exception as e:
            print(f"An error occurred during initialization: {e}")
    
    def chat_rag(self, extra, q_type, subject, lang, vector_db): 
        retrieval = vector_db.similarity_search_with_score(subject, k=3)
        context = "\n\n---\n\n".join([doc.page_content for doc, _score in retrieval])

        if lang == "ENG":
            template = templates[0][1]
        elif lang == "INA":
            template = templates[1][1]

        if q_type == "single":
            parser = JsonOutputParser(pydantic_object=MultipleChoice)
        elif q_type == "text":
            parser = JsonOutputParser(pydantic_object=Essay)
        elif q_type == "multiple-answer":
            parser = JsonOutputParser(pydantic_object=MultipleAnswer)


        chat_template=ChatPromptTemplate.from_messages(template)
        prompt = chat_template.format_messages(
            amount = "5",
            q_type=q_type, 
            subject=subject, 
            language=lang, 
            extra=extra, 
            context=context, 
            format_instructions=parser.get_format_instructions()
        )
        
        model = self.gpu_llm
        response_text = model.invoke(prompt)

        formatted_response = f"{response_text}"
        return(formatted_response)
    
    def chat(self, query):
        model = self.gpu_llm
        response_text = model.invoke(query)
        return (response_text)