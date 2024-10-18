from langchain_core.prompts import ChatPromptTemplate
from utils.helper import llm,model_gpt_4o_mini
from langchain_core.output_parsers import StrOutputParser
from prompts.prompt import qa_system_prompt


qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", qa_system_prompt),
        ("human", "{question}"),
    ]
)

output_parser = StrOutputParser()



ans_chain=qa_prompt | llm | output_parser


def bot(question):
    ans=ans_chain.invoke({"question": question})
    print(ans)
    return ans