from __future__ import annotations

from typing import Any
from typing import Callable

import allure
from psycopg import connect


def db_query_listener(func: Callable[..., Any]) -> Callable[..., Any]:
    def wrapper(*args, **kwargs) -> Any:
        result = func(*args, **kwargs)
        with allure.step(title='Query to DataBase: '):
            allure.attach(kwargs['query'], name='Query to DataBase', attachment_type=allure.attachment_type.TEXT)
        with allure.step(title='Result of query: '):
            allure.attach(str(result), name='Query Result', attachment_type=allure.attachment_type.TEXT)
        return result

    return wrapper


class DBClient:
    def __init__(self, connection_string: str) -> None:
        self.connection_string = connection_string

    @db_query_listener
    def get_list(self, query: str, params: dict[str, Any] | None = None) -> list[Any]:
        """
            Args:
                query (str): The SQL query to execute.
                params (dict[str, Any] | None, optional): The parameters to substitute in the query.
                    Defaults to None.
        """
        return [value[0] for value in self.select_all(query=query, params=params)]

    @db_query_listener
    def get_dict(self, query: str, params: dict[str, Any] | None = None) -> dict[Any, Any] | None:
        """
            Args:
                query (str): The SQL query to execute.
                params (dict[str, Any] | None, optional): The parameters to substitute in the query.
                    Defaults to None.
        """
        result = self.select_all(query=query)
        if not result and len(result) < 1:
            return None
        return {value[0]: value[1] for value in self.select_all(query=query, params=params)}

    @db_query_listener
    def select_all(self, query: str, params: dict[str, Any] | None = None) -> list[tuple]:
        """
            Args:
                query (str): The SQL query to execute.
                params (dict[str, Any] | None, optional): The parameters to substitute in the query.
                    Defaults to None.
        """
        self.cursor.execute(query=query, params=params)
        result = self.cursor.fetchall()
        return result

    @db_query_listener
    def get_first_value(self, query: str, params: dict[str, Any] | None = None) -> Any:
        """
            Args:
                query (str): The SQL query to execute.
                params (dict[str, Any] | None, optional): The parameters to substitute in the query.
                    Defaults to None.
        """
        result = self.get_first_row(query=query, params=params)
        if not result:
            return None
        return result[0]

    @db_query_listener
    def get_first_row(self, query: str, params: dict[str, Any] | None = None) -> Any:
        """
            Args:
                query (str): The SQL query to execute.
                params (dict[str, Any] | None, optional): The parameters to substitute in the query.
                    Defaults to None.
        """
        self.cursor.execute(query=query, params=params)
        result = self.cursor.fetchone()
        return result

    @db_query_listener
    def execute(self, query: str, params: dict[str, Any] | None = None) -> None:
        """
            Args:
                query (str): The SQL query to execute.
                params (dict[str, Any] | None, optional): The parameters to substitute in the query.
                    Defaults to None.
        """
        self.cursor.execute(query=query, params=params)
        self.connection.commit()
        return

    def __enter__(self) -> DBClient:
        self.connection = connect(self.connection_string)
        self.cursor = self.connection.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.cursor.close()
        self.connection.close()
        return
