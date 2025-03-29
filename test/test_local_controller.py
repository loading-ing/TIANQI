from inference.local.controller import ClientController

clientController=ClientController()
content="你是谁"
response=clientController.chat(content)
print(response)