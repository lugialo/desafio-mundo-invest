import json


class PipefyClient:

    @staticmethod
    def simulate_create_card(nome: str, email: str, valor_patrimonio: float):
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
                "pipe_id": "234440912",
                "title": f"Análise - {nome}",
                "fields_attributes": [
                    {"field_id": "cliente_email", "field_value": email},
                    {"field_id": "valor_patrimonio", "field_value": str(valor_patrimonio)},
                ],
            }
        }
        return json.dumps(
            {"query": mutation, "variables": variables}, indent=2, ensure_ascii=False
        )

    @staticmethod
    def simulate_update_card_fields(card_id: str, status: str, prioridade: str) -> str:
        batch_mutation = """
        mutation UpdateFieldsValues($input: UpdateFieldsValuesInput!) {
          updateFieldsValues(input: $input) {
            success
            userErrors {
              field
              message
            }
          }
        }
        """
        batch_variables = {
            "input": {
                "nodeId": card_id,
                "values": [
                    {"fieldId": "status", "value": status},
                    {"fieldId": "prioridade", "value": prioridade},
                ],
            }
        }

        individual_mutation = """
        mutation UpdateCardField($input: UpdateCardFieldInput!) {
          updateCardField(input: $input) {
            success
            card {
              id
            }
          }
        }
        """
        individual_variables_status = {
            "input": {
                "card_id": card_id,
                "field_id": "status",
                "new_value": status,
            }
        }
        individual_variables_prioridade = {
            "input": {
                "card_id": card_id,
                "field_id": "prioridade",
                "new_value": prioridade,
            }
        }

        payloads = {
            "preferred_batch_mutation": {
                "query": batch_mutation.strip(),
                "variables": batch_variables,
            },
            "alternative_individual_mutations": [
                {
                    "description": "Atualiza o status do cliente",
                    "query": individual_mutation.strip(),
                    "variables": individual_variables_status,
                },
                {
                    "description": "Atualiza a prioridade calculada",
                    "query": individual_mutation.strip(),
                    "variables": individual_variables_prioridade,
                },
            ],
        }
        return json.dumps(payloads, indent=2, ensure_ascii=False)