import csv
import os
import re


class PromptConverter:
    """Class to convert instruction templates and CSV data into prompts."""
    
    # Column mapping from placeholder names to CSV column names
    COLUMN_MAPPING = {
        'task_cd': 'TASK_CD',
        'description': 'SUB_TASK_DESC',
        'sub_task_cd': 'SUB_TASK_CD',
        'user_id': 'SYS_USER_ID',
        'sub_task_shortname': 'SUB_TASK_SHRTNM',
        'date': 'MAINFRM_UPLD_DT'
    }
    
    def load_instruction_template(self, prompt_file):
        """
        Load the instruction template from a markdown file.
        
        Args:
            prompt_file: Path to the markdown file containing instructions
            
        Returns:
            The instruction text with placeholders like <variable_name>
        """
        if not os.path.exists(prompt_file):
            raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
        
        with open(prompt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract the Template section
        match = re.search(r'### Template\n(.*?)(?=###|\Z)', content, re.DOTALL)
        if match:
            return match.group(1).strip()
        return content
    
    def load_csv_data(self, csv_file):
        """
        Load data from CSV file.
        
        Args:
            csv_file: Path to the CSV file
            
        Returns:
            List of dictionaries, each representing a row
        """
        if not os.path.exists(csv_file):
            raise FileNotFoundError(f"CSV file not found: {csv_file}")
        
        rows = []
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
        
        return rows
    
    def replace_placeholders(self, template, row_data):
        """
        Replace placeholders in template with values from row data.
        
        Args:
            template: String with placeholders like <variable_name>
            row_data: Dictionary containing variable values
            
        Returns:
            String with placeholders replaced
        """
        result = template
        
        # Find all placeholders in the template
        placeholders = re.findall(r'<(\w+)>', template)
        
        for placeholder in placeholders:
            # Get the CSV column name
            csv_column = self.COLUMN_MAPPING.get(placeholder, placeholder.upper())
            
            # Replace placeholder with value from row data
            if csv_column in row_data:
                value = str(row_data[csv_column]).strip()
                result = result.replace(f'<{placeholder}>', value)
            else:
                # If column not found, replace with empty string
                result = result.replace(f'<{placeholder}>', '')
        
        return result
    
    def generate_prompts(self, prompt_file, csv_file):
        """
        Generate prompts for each row in CSV by replacing placeholders in the instruction template.
        
        Args:
            prompt_file: Path to the markdown file with instruction template
            csv_file: Path to the CSV file with data
            
        Returns:
            Concatenated string of all generated prompts
        """
        # Load instruction template
        instruction_template = self.load_instruction_template(prompt_file)
        
        # Load CSV data
        rows = self.load_csv_data(csv_file)
        
        # Generate prompts for each row
        prompts = []
        for row in rows:
            prompt = self.replace_placeholders(instruction_template, row)
            prompts.append(prompt)
        
        # Concatenate all prompts with separators
        final_prompt = '\n' + ('=' * 80) + '\n'.join(prompts)
        
        return final_prompt


def main():
    """Main function for testing"""
    converter = PromptConverter()
    prompt_file = os.path.join(os.path.dirname(__file__), 'prompts', 'submit_task.md')
    csv_file = os.path.join(os.path.dirname(__file__), 'db', 'data', 'temp_sql_result.csv')
    
    try:
        final_prompt = converter.generate_prompts(prompt_file, csv_file)
        print(final_prompt)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
