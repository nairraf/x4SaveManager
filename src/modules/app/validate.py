"""Module responsible for application data validation needs
"""

class Validate:
    """responsible for validating all user inputs
    """

    def __init__(self) -> None:
        pass

    @staticmethod
    def text_input(text):
        """validates user text input

        Args:
            text (str): the text input to validate

        Returns:
            str: the validated text input upon success
        """
        text = text.strip()
        if text:
            return text

        return None
