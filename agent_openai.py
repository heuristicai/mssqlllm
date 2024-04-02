from langchain_community.agent_toolkits import create_sql_agent
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain.agents.agent_toolkits import create_retriever_tool
from custom_tool import CustomQuerySQLDataBaseTool
from langchain_core.prompts import (
    ChatPromptTemplate,
    FewShotPromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
    SystemMessagePromptTemplate,
)

import llm_helper
import db_helper
import vectorstore_helper


from langchain.globals import set_debug, set_verbose

set_debug(True)
set_verbose(True)


system_prefix = """You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.
Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most {top_k} results.
You can order the results by a relevant column to return the most interesting examples in the database.
Never query for all the columns from a specific table, only ask for the relevant columns given the question. 

You have access to tools for interacting with the database.
Only use the given tools. Only use the information returned by the tools to construct your final answer.
For any input question, DO NOT makeup table and column names, make sure to use the tools and get metadata about the database table and columns names to find the actual table and column names that are present in the database.

You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

If the question does not seem related to the database, just return "I don't know" as the answer.

Here are some examples of user inputs and their corresponding SQL queries:"""


description = """Use to look up values to filter on. Input is an approximate spelling of the proper noun, output is \
valid proper nouns. Use the noun most similar to the search."""


def get_agent():
    llm = llm_helper.get_llm()
    db = db_helper.get_db()
    vectorstore = vectorstore_helper.get_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    retriever_tool = create_retriever_tool(
        retriever,
        name="search_proper_nouns",
        description=description,
    )
    example_selector = SemanticSimilarityExampleSelector(
        vectorstore=vectorstore, k=2, input_keys=["input"]
    )

    example_prompt = PromptTemplate(
        input_variables=["Question", "SQLQuery"],
        template="\nQuestion: {Question}\nSQLQuery: {SQLQuery}\n",
    )

    few_shot_prompt = FewShotPromptTemplate(
        example_selector=example_selector,
        example_prompt=example_prompt,
        prefix=system_prefix,
        suffix="",
        input_variables=[
            "input",
            "dialect",
            "top_k",
        ],
    )

    full_prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate(prompt=few_shot_prompt),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )

    csv_tool_description = (
        "Input to this tool is a detailed and correct SQL query, output is a "
        "csv or excel file path for the results from the database which are exported or dumped into csv or excel format. If the query is not correct, an error message "
        "will be returned. If an error is returned, rewrite the query, check the "
        "query, and try again. If you encounter an issue with Unknown column "
        f"'xxxx' in 'field list', use sql_db_schema "
        "to query the correct table fields. Do not generate download link in your answer, because the path is for internal use only and filepath may change."
    )
    agent_executor = create_sql_agent(
        llm,
        db=db,
        extra_tools=[
            retriever_tool,
            CustomQuerySQLDataBaseTool(db=db, description=csv_tool_description),
        ],
        prompt=full_prompt,
        agent_type="openai-tools",
        verbose=True,
        agent_executor_kwargs={
            "return_intermediate_steps": True
        },
    )
    return agent_executor
