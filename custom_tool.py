from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from typing import Any, Dict, Optional, Sequence, Type, Union
from sqlalchemy.engine import Result
from langchain.pydantic_v1 import BaseModel, Field
from langchain.callbacks.manager import CallbackManagerForToolRun

import pandas as pd
class CustomQuerySQLDataBaseToolInput(BaseModel):
    query: str = Field(..., description="A detailed and correct SQL query.")


class CustomQuerySQLDataBaseTool(QuerySQLDataBaseTool):
    """Tool for generating csv or excel file by querying a SQL database and dump the results in excel or csv file"""

    name: str = "sql_db__csv_result"
    description: str = """
    Execute a SQL query against the database and generate a csv file containing the result of SQL query..
    If the query is not correct, an error message will be returned.
    If an error is returned, rewrite the query, check the query, and try again.
    """
    args_schema: Type[BaseModel] = CustomQuerySQLDataBaseToolInput

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Union[str, Sequence[Dict[str, Any]], Result]:
        """Execute the query, return the results or an error message."""
        connection = self.db._engine.connect()
        df = pd.read_sql(query, con = connection)
        connection.commit()
        connection.close()
        file_name = "Export.csv"
        # This is the local path on the server, should be either Azure Storage or a mechanism for periodic cleanup of the files
        file_path = "Export.csv"
        df.to_csv(file_path)
        return {'name': file_name, 'path':file_path}