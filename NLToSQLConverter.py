import re
from typing import Dict, List, Optional, Tuple

class NLToSQLConverter:
    def __init__(self):
        self.keywords = {
            'create': ['create', 'make', 'new', 'setup'],
            'select': ['show', 'display', 'get', 'find', 'select', 'list'],
            'insert': ['add', 'insert', 'put'],
            'update': ['update', 'modify', 'change'],
            'delete': ['delete', 'remove', 'drop'],
            'join': ['join', 'combine', 'merge'],
            'group': ['group', 'aggregate', 'summarize'],
            'order': ['order', 'sort', 'arrange']
        }
        
        self.data_types = {
            'text': 'VARCHAR(255)',
            'string': 'VARCHAR(255)',
            'number': 'INT',
            'integer': 'INT',
            'decimal': 'DECIMAL(10,2)',
            'date': 'DATE',
            'email': 'VARCHAR(255)',
            'phone': 'VARCHAR(20)'
        }
        
        self.aggregates = {
            'count': 'COUNT',
            'sum': 'SUM',
            'average': 'AVG',
            'minimum': 'MIN',
            'maximum': 'MAX'
        }
        
        self.join_types = {
            'inner': 'INNER JOIN',
            'left': 'LEFT JOIN',
            'right': 'RIGHT JOIN',
            'outer': 'OUTER JOIN'
        }

    def parse_input(self, user_input: str) -> Dict:
        """Parse the natural language input to identify operation type and details."""
        user_input = user_input.lower().strip()
        
        # Identify operation type
        operation = None
        for op, keywords in self.keywords.items():
            if any(keyword in user_input for keyword in keywords):
                operation = op
                break
        
        if not operation:
            raise ValueError("Could not identify the operation type")
            
        return {
            'operation': operation,
            'input': user_input
        }

    def extract_table_info(self, input_text: str) -> Tuple[str, List[Tuple[str, str]]]:
        """Extract table name and columns from create table requests."""
        # Try to find table name
        table_match = re.search(r'table (?:for |named )?(\w+)', input_text)
        if not table_match:
            raise ValueError("Could not identify table name")
        
        table_name = table_match.group(1)
        
        # Extract columns and their types
        columns = []
        # Look for column names in various formats
        col_matches = re.findall(r'(?:with|having|containing)?\s*([\w\s,]+)(?=\s|$)', input_text)
        
        if col_matches:
            # Split potential comma-separated columns
            col_list = []
            for match in col_matches:
                cols = [c.strip() for c in match.split(',')]
                col_list.extend(cols)
            
            # Clean up column names and infer types
            for col in col_list:
                if col and col not in ['table', 'with', 'and']:
                    # Infer type based on column name
                    col_type = 'VARCHAR(255)'  # default type
                    for type_keyword, sql_type in self.data_types.items():
                        if type_keyword in col:
                            col_type = sql_type
                            break
                    columns.append((col.strip(), col_type))
        
        return table_name, columns

    def parse_join_condition(self, input_text: str) -> Tuple[str, str, str, str]:
        """Parse join conditions from the input text."""
        # Try to identify join type
        join_type = 'INNER JOIN'  # default
        for key, value in self.join_types.items():
            if key in input_text:
                join_type = value
                break
        
        # Extract tables and joining columns
        tables_match = re.search(r'join (\w+) (?:with|and) (\w+)', input_text)
        if not tables_match:
            raise ValueError("Could not identify tables to join")
        
        table1, table2 = tables_match.groups()
        
        # Try to find joining columns
        join_cols_match = re.search(r'using (\w+)', input_text) or \
                         re.search(r'on (\w+)\.(\w+) ?= ?(\w+)\.(\w+)', input_text)
        
        if join_cols_match:
            if len(join_cols_match.groups()) == 1:
                # USING clause
                join_column = join_cols_match.group(1)
                return join_type, table1, table2, f"USING ({join_column})"
            else:
                # ON clause
                t1, c1, t2, c2 = join_cols_match.groups()
                return join_type, table1, table2, f"ON {t1}.{c1} = {t2}.{c2}"
        
        return join_type, table1, table2, "ON primary_key = foreign_key"

    def parse_group_by(self, input_text: str) -> Tuple[List[str], List[str]]:
        """Parse GROUP BY columns and aggregate functions."""
        group_cols = []
        aggregates = []
        
        # Extract GROUP BY columns
        group_match = re.search(r'group by (\w+(?:,\s*\w+)*)', input_text)
        if group_match:
            group_cols = [col.strip() for col in group_match.group(1).split(',')]
        
        # Extract aggregate functions
        for agg_key, agg_func in self.aggregates.items():
            agg_match = re.search(f'{agg_key} (?:of|on|for) (\w+)', input_text)
            if agg_match:
                column = agg_match.group(1)
                aggregates.append(f"{agg_func}({column})")
        
        return group_cols, aggregates

    def parse_order_by(self, input_text: str) -> List[Tuple[str, str]]:
        """Parse ORDER BY clauses."""
        order_cols = []
        
        # Look for ordering instructions
        order_match = re.search(r'order by (\w+(?:,\s*\w+)*)', input_text)
        if order_match:
            cols = [col.strip() for col in order_match.group(1).split(',')]
            for col in cols:
                direction = 'DESC' if 'descending' in input_text or 'desc' in input_text else 'ASC'
                order_cols.append((col, direction))
        
        return order_cols

    def generate_select_query(self, input_text: str) -> str:
        """Generate SELECT query with support for JOINs, GROUP BY, and ORDER BY."""
        # Extract base table name
        table_match = re.search(r'from (\w+)|(\w+) table', input_text)
        if not table_match:
            raise ValueError("Could not identify table name")
            
        table_name = table_match.group(1) or table_match.group(2)
        query_parts = [f"SELECT"]
        
        # Handle columns and aggregates
        group_cols, aggregates = self.parse_group_by(input_text)
        if group_cols or aggregates:
            select_items = group_cols + aggregates
            query_parts.append(', '.join(select_items) if select_items else '*')
        else:
            query_parts.append('*')
        
        query_parts.append(f"FROM {table_name}")
        
        # Handle JOINs
        if any(join_word in input_text for join_word in ['join', 'combine', 'merge']):
            try:
                join_type, table1, table2, join_condition = self.parse_join_condition(input_text)
                query_parts.append(f"{join_type} {table2} {join_condition}")
            except ValueError as e:
                pass  # Skip join if we can't parse it properly
        
        # Handle WHERE conditions
        if 'where' in input_text:
            condition_match = re.search(r'where\s+(\w+)\s*(=|>|<|like)\s*(\w+)', input_text)
            if condition_match:
                column, operator, value = condition_match.groups()
                query_parts.append(f"WHERE {column} {operator} '{value}'")
        
        # Add GROUP BY
        if group_cols:
            query_parts.append(f"GROUP BY {', '.join(group_cols)}")
        
        # Add ORDER BY
        order_cols = self.parse_order_by(input_text)
        if order_cols:
            order_parts = [f"{col} {direction}" for col, direction in order_cols]
            query_parts.append(f"ORDER BY {', '.join(order_parts)}")
        
        return f"{' '.join(query_parts)};"

    def generate_create_query(self, input_text: str) -> str:
        """Generate CREATE TABLE query."""
        table_name, columns = self.extract_table_info(input_text)
        
        if not columns:
            raise ValueError("No columns identified")
            
        columns_sql = ', '.join([f"{col_name} {col_type}" for col_name, col_type in columns])
        return f"CREATE TABLE {table_name} ({columns_sql});"

    def generate_insert_query(self, input_text: str) -> str:
        """Generate INSERT query with support for multiple values."""
        # Extract table name
        table_match = re.search(r'(?:into |to )?(\w+)', input_text)
        if not table_match:
            raise ValueError("Could not identify table name")
            
        table_name = table_match.group(1)
        
        # Look for specific columns and values
        columns_match = re.search(r'columns? ?(?:is|are|:)? ?(\w+(?:,\s*\w+)*)', input_text)
        values_match = re.search(r'values? ?(?:is|are|:)? ?([^.]+)', input_text)
        
        if columns_match and values_match:
            columns = [col.strip() for col in columns_match.group(1).split(',')]
            values = [val.strip() for val in values_match.group(1).split(',')]
            
            return f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(values)});"
        
        return f"INSERT INTO {table_name} VALUES (value1, value2, ...);"

    def generate_update_query(self, input_text: str) -> str:
        """Generate UPDATE query with enhanced condition support."""
        # Extract table name
        table_match = re.search(r'(\w+) table|table (\w+)', input_text)
        if not table_match:
            raise ValueError("Could not identify table name")
            
        table_name = table_match.group(1) or table_match.group(2)
        
        # Look for SET values
        set_matches = re.findall(r'set (\w+) to (\w+)', input_text)
        if set_matches:
            set_clauses = [f"{col} = '{val}'" for col, val in set_matches]
            
            # Look for WHERE condition
            where_clause = ""
            condition_match = re.search(r'where\s+(\w+)\s*(=|>|<|like)\s*(\w+)', input_text)
            if condition_match:
                column, operator, value = condition_match.groups()
                where_clause = f" WHERE {column} {operator} '{value}'"
            
            return f"UPDATE {table_name} SET {', '.join(set_clauses)}{where_clause};"
        
        return f"UPDATE {table_name} SET column = value WHERE condition;"

    def generate_delete_query(self, input_text: str) -> str:
        """Generate DELETE query."""
        # Extract table name
        table_match = re.search(r'from (\w+)|(\w+) table', input_text)
        if not table_match:
            raise ValueError("Could not identify table name")
            
        table_name = table_match.group(1) or table_match.group(2)
        
        if 'where' in input_text:
            condition_match = re.search(r'where\s+(\w+)\s*(=|>|<|like)\s*(\w+)', input_text)
            if condition_match:
                column, operator, value = condition_match.groups()
                return f"DELETE FROM {table_name} WHERE {column} {operator} '{value}';"
        
        return f"DELETE FROM {table_name};"

    def generate_query(self, user_input: str) -> str:
        """Main method to generate SQL query from natural language input."""
        try:
            parsed = self.parse_input(user_input)
            
            if parsed['operation'] == 'create':
                return self.generate_create_query(parsed['input'])
            elif parsed['operation'] == 'select':
                return self.generate_select_query(parsed['input'])
            elif parsed['operation'] == 'insert':
                return self.generate_insert_query(parsed['input'])
            elif parsed['operation'] == 'update':
                return self.generate_update_query(parsed['input'])
            elif parsed['operation'] == 'delete':
                return self.generate_delete_query(parsed['input'])
            else:
                raise ValueError("Unsupported operation")
                
        except ValueError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Error: Unable to generate query - {str(e)}"

def main():
    converter = NLToSQLConverter()
    
    print("Enhanced Natural Language to MySQL Query Converter")
    print("Enter 'quit' to exit")
    print("\nExample commands:")
    print("- Create a table for customers with name, email, and phone")
    print("- Show all records from customers")
    print("- Join orders with customers using customer_id")
    print("- Show total sales grouped by category")
    print("- Select from products where price > 100 order by price desc")
    print("- Add new record to customers with columns name, email values John, john@email.com")
    print("- Update customers set status to active where id = 1")
    print("- Delete from customers where id = 1")
    
    while True:
        user_input = input("\nEnter your request: ")
        
        if user_input.lower() == 'quit':
            break
            
        query = converter.generate_query(user_input)
        print("\nGenerated MySQL Query:")
        print(query)

if __name__ == "__main__":
    main()





