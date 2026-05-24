import json


class PipefyClient:

    @staticmethod
    def simulate_create_card(
        nome: str, email: str, valor_patrimonio: float
    ):
        mutation = """
        mutation CreateCard($input: CreateCardInput!) {
          createCard(input: $input) {
            card {
              id
              title
            }
          }
        }
        """
        variables = {
            "input": {
                "pipe_id": "234440912",  # supondo que seja o id do pipe dentro do pipefy
                "title": f"Análise - {nome}",
                "fields_attributes": [
                    {"field_id": "cliente_email", "field_value": email},
                    {"field_id": "valor_patrimonio", "field_value": str(valor_patrimonio)},
                ],
            }
        }

        # Retorna a string formatada para simular o payload que seria enviado no corpo HTTP
        return json.dumps(
            {"query": mutation, "variables": variables}, indent=2, ensure_ascii=False
        )
        
    @staticmethod
    def simulate_update_card_field(card_id: str, prioridade: str) -> str:
        mutation = """
        mutation UpdateCardField($input: UpdateCardFieldInput!) {
          updateCardField(input: $input) {
            card {
              id
            }
          }
        }
        """
        variables = {
            "input": {
                "card_id": card_id,
                "field_id": "prioridade",
                "new_value": prioridade
            }
        }
        return json.dumps({"query": mutation, "variables": variables}, indent=2, ensure_ascii=False)
