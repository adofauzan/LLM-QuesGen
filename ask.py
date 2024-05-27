from chromaDB import query_chroma
template1 = """
    Answer the question based only on the following context:

    {context}

    ---

    Answer the question based on the above context: {question}
    Additionally create 2 multiple choice questions about it.
    """



template2 = """Informasi: {information}
Buatkan beberapa pertanyaan pilihan ganda dari informasi tersebut"""

def give_information(prompt, gpu_llm):
    prompt = PromptTemplate.from_template(template)
    gpu_chain = prompt | gpu_llm | output_parser
    information = prompt
    return(gpu_chain.invoke({"information": information}))

def ask_question(prompt, gpu_llm):
    return gpu_llm.invoke(prompt)

