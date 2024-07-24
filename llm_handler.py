from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline
from langchain.prompts import ChatPromptTemplate, PromptTemplate,MessagesPlaceholder
from langchain_core.output_parsers import JsonOutputParser
from question_type import MultipleAnswer, SingleAnswer, Essay
from langchain_core.pydantic_v1 import BaseModel, Field

template = [
        ("system", """You are a quiz generator that create questions. 
        You are tasked to create {amount} questions based on the subjects asked.
        Create the question in {language}
        The questions created are based on the model pre-knowledge with the help of the context given.
        If the context given does not help, don't use the context.
        Only output the questions.
        
        Output format= {output_format}
        Context = {context}"""),
        ("user","Create questions about {subject} with the topic {instruction}"),
        ("ai", "Generated Questions=")
]

class LLMHandler:
    def __init__(self):
        self.is_initialized = False
        self.model = None
        self.gpu_llm = None
        self.initialize_mistral()

    def initialize_mistral(self):
        try:
            self.gpu_llm = None
            self.gpu_llm = HuggingFacePipeline.from_model_id(
                model_id="./data/Mistral-7B-Instruct-v0.2",
                task="text-generation",  
                device=0,  # replace with device_map="auto" to use the accelerate library.
                pipeline_kwargs={"max_new_tokens": 3000} 
            )
            self.is_initialized = True
            self.model = "Mistral"
        except Exception as e:
            print(f"An error occurred during initialization: {e}")
            
    def initialize_llama(self):
        try:
            self.gpu_llm = None
            self.gpu_llm = HuggingFacePipeline.from_model_id(
                model_id="./data/Meta-Llama-3-8B",
                task="text-generation",  
                device=0,  # replace with device_map="auto" to use the accelerate library.
                pipeline_kwargs={"max_new_tokens": 3000} 
            )
            self.is_initialized = True 
            self.model = "Llama"
        except Exception as e:
            print(f"An error occurred during initialization: {e}")
    
    def chat_rag(self, q_type, instruction, subject, lang, vector_db):   
        retrieval = vector_db.similarity_search_with_score(instruction, k=3)
        chunks = "\n---\n".join([doc.page_content for doc, _score in retrieval])
        
        if q_type == "single":
            output_parser = JsonOutputParser(pydantic_object=SingleAnswer)
        elif q_type == "multiple":
            output_parser = JsonOutputParser(pydantic_object=MultipleAnswer)
        else:
            output_parser = JsonOutputParser(pydantic_object=Essay)
        
        chat_template = ChatPromptTemplate.from_messages(template)
        chat_template = chat_template.partial(amount="5", context=chunks, 
                                              output_format=output_parser.get_format_instructions())
        
        chain = chat_template | self.gpu_llm
        
        return(chain.invoke({
            "subject": subject,
            "instruction": instruction,
            "language": lang
        }))
    
    def chat(self, query):
        model = self.gpu_llm
        response_text = model.invoke(query)
        return (response_text)
    
    def joke(self, query) -> dict:
        class Joke(BaseModel):
            setup: str = Field(description="question to set up a joke")
            punchline: str = Field(description="answer to resolve the joke")

        model = self.gpu_llm

        # Set up a parser + inject instructions into the prompt template.
        parser = JsonOutputParser(pydantic_object=Joke)

        prompt = PromptTemplate(
            template="Answer the user query.\n{format_instructions}\n{query}\n",
            input_variables=["query"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        chain = prompt | model | parser
        response_text = chain.invoke({"query": query})
        return (response_text)
