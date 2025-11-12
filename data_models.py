class N8nRequest:
    def __init__(self, chat_input, session_id, intent = None, params = None):
        self.chat_input = chat_input
        self.session_id = session_id
        self.intent = intent
        self.params = params if params is not None else {}

class N8nRequest: 
    def __init__(self, ok, message = None, data = None, error = None):
        self.ok = ok
        self.message = message
        self.data = data
        self.error = error