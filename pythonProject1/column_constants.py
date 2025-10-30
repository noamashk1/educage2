# Column names constants for Educage experiment
# Centralizes all column name definitions to ensure consistency across the application


class ColumnNames:
    """Central definition of all column names used in the Educage experiment"""

    # Main table columns (first table in levels_table_creating.py)
    LEVEL_NAME = "Level Name"
    NUMBER_OF_STIMULI = "Number of Stimuli"

    # Stimuli table/levels CSV columns
    STIMULUS_PATH = "Stimulus Path"
    PROBABILITY = "Probability"
    VALUE = "Value"
    INDEX = "Index"

    # CSV header columns (for saving files)
    @classmethod
    def get_csv_headers(cls):
        """Returns the CSV headers in the correct order"""
        return [cls.LEVEL_NAME, cls.STIMULUS_PATH, cls.PROBABILITY, cls.VALUE, cls.INDEX]

    # Treeview columns (for GUI_sections.py)
    @classmethod
    def get_treeview_columns(cls):
        """Returns the treeview columns tuple"""
        return (cls.LEVEL_NAME, cls.STIMULUS_PATH, cls.PROBABILITY, cls.VALUE, cls.INDEX)

    # Column widths for GUI
    COLUMN_WIDTHS = {
        LEVEL_NAME: 50,
        STIMULUS_PATH: 200,
        PROBABILITY: 50,
        VALUE: 50,
        INDEX: 50,
    }


