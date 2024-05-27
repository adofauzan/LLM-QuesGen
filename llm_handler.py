from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline
from langchain.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder

templates = (
    ("english", [("system", "You are a quiz generator that creates questions. Ensure that the question demands critical thinking and an in-depth understanding of the subject matter. Additionally, provide detailed answers for each question to offer clarity and accuracy in evaluation."),
        MessagesPlaceholder("q_type"),
        ("system", "Use the following context provided to help generate the question."),
        ("system", "{context}"),
        ("human", "Make {amount} a {q_type} question about the subject {subject}. Write it in {language}. {extra}"),
    ]),
    ("indonesia", [("system", "Anda adalah generator kuis yang membuat pertanyaan. Pastikan bahwa pertanyaan tersebut menuntut pemikiran kritis dan pemahaman mendalam tentang materi pelajaran. Selain itu, berikan jawaban terperinci untuk setiap pertanyaan untuk menawarkan kejelasan dan akurasi dalam evaluasi."),
        MessagesPlaceholder("q_type"),
        ("system", "Gunakan konteks berikut untuk membantu membuat pertanyaan"),
        ("system", "{context}"),
        ("human", "Buatlah {amount} pertanyaan {q_type} tentang subjek {subject}. Tulis dalam {language}. {extra}"),
    ])
)
question_type_eng=(
    ("multiple-choice", [("system", """Here is an example output with the desirable context. There will be a question prefixed by ques=, 4 options prefixed by opt_A=/opt_B=/opt_C=/opt_D=, 1 answer from one of the options prefixed by ans=, and an explanation of the answer prefixed by exp=.
        ques=The question
        opt_A=Option 1
        opt_B=Option 2
        opt_C=Option 3
        opt_D=Option 4
        ans=The answer from one of the options
        exp=The explanation of the answer""")
    ]),
    ("essay", [("system", """Here is an example output with the desirable context. There will be a question prefixed with ques= and an answer prefixed with ans=.
        ques=The question
        ans=The answer from one of the options""")
    ]),
    ("multiple-answer", [("system", """Here is an example output with the desirable context. There will be a question prefixed by ques=, 4 options prefixed by opt_A=/opt_B=/opt_C=/opt_D=, multiple answers from the options prefixed by ans_1=/ans_2= or any amount of it, and an explanation of the answer prefixed by exp=.
        ques=The question
        opt_A=Option 1
        opt_B=Option 2
        opt_C=Option 3
        opt_D=Option 4
        ans_1=The answer from the options
        ans_2=The answer from the options
        exp=The explanation of the answer""")
    ])
)
question_type_ina=(
    ("multiple-choice", [("system", """Berikut adalah contoh keluaran dengan konteks yang diinginkan. Akan ada sebuah pertanyaan yang diawali dengan ques=, 4 opsi yang diawali dengan opt_A=/opt_B=/opt_C=/opt_D=, 1 jawaban dari salah satu opsi yang diawali dengan ans=, dan penjelasan dari jawaban yang diawali dengan exp=.
        ques=Pertanyaannya
        opt_A=Opsi 1
        opt_B=Opsi 2
        opt_C=Opsi 3
        opt_D=Opsi 4
        ans=Jawaban dari salah satu opsi
        exp=Penjelasan dari jawaban""")
    ]),
    ("essay", [("system", """Berikut adalah contoh keluaran dengan konteks yang diinginkan. Akan ada sebuah pertanyaan yang diawali dengan ques= dan sebuah jawaban yang diawali dengan ans=.
        ques=Pertanyaannya
        ans=Jawaban dari salah satu opsi""")
    ]),
    ("multiple-answer", [("system", """Berikut adalah contoh keluaran dengan konteks yang diinginkan. Akan ada sebuah pertanyaan yang diawali dengan ques=, 4 opsi yang diawali dengan opt_A=/opt_B=/opt_C=/opt_D=, beberapa jawaban dari opsi yang diawali dengan ans_1=/ans_2= atau sebanyak apapun, dan penjelasan dari jawaban yang diawali dengan exp=.
    ques=Pertanyaannya
        opt_A=Opsi 1
        opt_B=Opsi 2
        opt_C=Opsi 3
        opt_D=Opsi 4
        ans_1=Jawaban dari opsi
        ans_2=Jawaban dari opsi
        exp=Penjelasan dari jawaban""")
    ])
)
mult_question_bank_eng = {
    "hard": """ques=Which of the following neurological conditions is characterized by the presence of abnormal protein aggregates called Lewy bodies, leading to cognitive decline, motor symptoms, and visual hallucinations?
        opt_A=Huntington's disease
        opt_B=Alzheimer's disease
        opt_C=Parkinson's disease with dementia (PDD)
        opt_D=Creutzfeldt-Jakob disease
        asw=C
        exp=The medulla oblongata, located at the base of the brainstem, plays a vital role in regulating autonomic functions, including breathing, heart rate, and blood pressure.""",
     "medium":"""ques=Choose the anatomical topic and definition that is **not** correctly matched.
        opt_A=Gross anatomy: study of structures visible to the eye.
        opt_B=Microscopic anatomy: study of structures too small to be seen by the naked eye.
        opt_C=Developmental anatomy: study of the changes in an individual from birth through old age.
        opt_D= Embryology: study of the changes in an individual from conception to birth.
        asw=C
        exp=Developmental anatomy actually studies the changes in an individual from conception to adulthood, not just from birth through old age.""",
    "easy":"""ques=________ means toward or at the back of the body, behind.
        opt_A=Anterior
        opt_B=Lateral
        opt_C=Distal
        opt_D=Dorsal
        asw=D
        exp="Dorsal" refers to the back side of the body, opposite to "ventral" which refers to the front.""",
    }
mult_question_bank_ina = {
    "hard":"""ques=Manakah dari kondisi neurologis berikut yang ditandai dengan adanya agregat protein abnormal yang disebut badan Lewy, yang menyebabkan penurunan kognitif, gejala motorik, dan halusinasi visual?
        opt_A=Penyakit Huntington
        opt_B=Penyakit Alzheimer
        opt_C=Penyakit Parkinson dengan demensia (PDD)
        opt_D=Penyakit Creutzfeldt-Jakob
        asw=C
        exp=Medula oblongata, yang terletak di dasar batang otak, berperan penting dalam mengatur fungsi otonom, termasuk pernapasan, detak jantung, dan tekanan darah.""",
    "medium":"""ques=Pilih topik anatomi dan definisi yang **tidak** cocok.
        opt_A=Anatomi kasar: studi tentang struktur yang terlihat oleh mata.
        opt_B=Anatomi mikroskopis: studi tentang struktur yang terlalu kecil untuk dilihat dengan mata telanjang.
        opt_C=Anatomi perkembangan: studi tentang perubahan dalam individu dari lahir hingga usia tua.
        opt_D=Embriologi: studi tentang perubahan dalam individu dari konsepsi hingga kelahiran.
        asw=C
        exp=Anatomi perkembangan sebenarnya mempelajari perubahan dalam individu dari konsepsi hingga dewasa, bukan hanya dari lahir hingga usia tua.""",
    "easy":"""ques=________ berarti menuju atau di bagian belakang tubuh, di belakang.
        opt_A=Anterior
        opt_B=Lateral
        opt_C=Distal
        opt_D=Dorsal
        asw=D
        exp="Dorsal" mengacu pada sisi belakang tubuh, berlawanan dengan "ventral" yang mengacu pada sisi depan.""",
    }

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
                pipeline_kwargs={"max_new_tokens": 2000} 
            )
            self.is_initialized = True  
        except Exception as e:
            print(f"An error occurred during initialization: {e}")
    
    def chat_rag(self, extra, q_type, subject, lang, vector_db):   
        #I think this should be seperate
        retrieval = vector_db.similarity_search_with_score(subject, k=5)
        context = "\n\n---\n\n".join([doc.page_content for doc, _score in retrieval])

        if lang == "ENG":
            template = templates[0][1]
            if q_type == "multiple-choice":
                ques_type = question_type_eng[0][1]
            elif q_type == "essay":
                ques_type = question_type_eng[1][1]
            elif q_type == "multiple-answer":
                ques_type = question_type_eng[2][1]
        elif lang == "INA":
            template = templates[1][1]
            if q_type == "multiple-choice":
                ques_type = question_type_ina[0][1]
            elif q_type == "essay":
                ques_type = question_type_ina[1][1]
            elif q_type == "multiple-answer":
                ques_type = question_type_ina[2][1]

        chat_template=ChatPromptTemplate.from_messages(template)
        prompt = chat_template.format_messages(amount = "5",q_type=ques_type, subject=subject, language=lang, extra=extra, context=context)
        
        model = self.gpu_llm
        response_text = model.invoke(prompt)

        formatted_response = f"{response_text}"
        return(formatted_response)
    
    def chat(self, query):
        model = self.gpu_llm
        response_text = model.invoke(query)
        return (response_text)