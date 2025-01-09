from enum import Enum
from typing import List, Optional, Union, Dict

from pydantic import BaseModel

from infrastructure.pg_repositories.subscriptions_repository import ConsumptionData


class ClaudeModels(Enum):
    HAIKU_3 = "claude-3-haiku-20240307"
    HAIKU_3_5 = "claude-3-5-haiku-20241022"


class TokensConsumption(BaseModel):
    input_tokens: int
    output_tokens: int
    model: ClaudeModels


class TotalTokensConsumption(BaseModel):
    consumptions: List[TokensConsumption]


class PromptUtils:

    @staticmethod
    def _get_claude_model(model_str: str) -> ClaudeModels:
        """
        Maps a Claude model string to the corresponding ClaudeModels enum value.
        Raises ValueError if no matching enum is found.
        """
        for model in ClaudeModels:
            if model.value == model_str:
                return model
        raise ValueError(f"Unsupported model string: {model_str}")

    @staticmethod
    def get_tokens_consumption(model: str, input_tokens_consumed: int,
                               output_tokens_consumed: int) -> TokensConsumption:
        """
        Creates a TokensConsumption object from a ClaudeResponse.
        Automatically matches the model string to the corresponding enum value.
        """
        try:
            model = PromptUtils._get_claude_model(model)
        except ValueError as e:
            # You might want to handle this differently depending on your needs
            raise ValueError(f"Error processing response: {e}")

        return TokensConsumption(
            input_tokens=input_tokens_consumed,
            output_tokens=output_tokens_consumed,
            model=model
        )

    @staticmethod
    def calculate_total_tokens_consumption(
            consumption: TokensConsumption,
            previously_consumed: Optional[TotalTokensConsumption] = None
    ) -> TotalTokensConsumption:
        # If no previous consumption, create new TotalTokensConsumption with single entry
        if previously_consumed is None:
            return TotalTokensConsumption(consumptions=[consumption])

        # Find existing consumption for the same model if it exists
        for existing_consumption in previously_consumed.consumptions:
            if existing_consumption.model == consumption.model:
                # Update existing consumption
                existing_consumption.input_tokens += consumption.input_tokens
                existing_consumption.output_tokens += consumption.output_tokens
                return previously_consumed

        # If no matching model found, add new consumption to the list
        previously_consumed.consumptions.append(consumption)
        return previously_consumed

    @staticmethod
    def convert_grpc_tokens_consumption(grpc_response) -> Optional[TotalTokensConsumption]:
        try:
            # Return None if no tokens consumption data
            if not hasattr(grpc_response, 'tokens_consumed') or not grpc_response.tokens_consumed:
                return None

            total_consumption = None

            # Process each consumption entry
            for consumption in grpc_response.tokens_consumed.consumptions:
                # Create TokensConsumption object for current entry
                current_consumption = PromptUtils.get_tokens_consumption(
                    model=consumption.model,
                    input_tokens_consumed=consumption.input_tokens,
                    output_tokens_consumed=consumption.output_tokens
                )

                # Calculate running total
                total_consumption = PromptUtils.calculate_total_tokens_consumption(
                    consumption=current_consumption,
                    previously_consumed=total_consumption
                )

            return total_consumption

        except (AttributeError, ValueError) as e:
            raise ValueError(f"Error converting gRPC tokens consumption: {str(e)}")

    @staticmethod
    def convert_subscription_consumption(consumption_data: List[Union[Dict, ConsumptionData]]) -> Optional[
        TotalTokensConsumption]:
        if not consumption_data or len(consumption_data) == 0:
            return None

        total_consumption = None

        for consumption in consumption_data:
            # Handle both ConsumptionData objects and raw dictionaries
            if isinstance(consumption, ConsumptionData):
                model = consumption.model
                input_tokens = consumption.input_tokens
                output_tokens = consumption.output_tokens
            else:
                model = consumption.get('model')
                input_tokens = consumption.get('input_tokens')
                output_tokens = consumption.get('output_tokens')

            if not all([model, input_tokens is not None, output_tokens is not None]):
                continue

            # Create TokensConsumption object for current entry
            current_consumption = PromptUtils.get_tokens_consumption(
                model=model,
                input_tokens_consumed=input_tokens,
                output_tokens_consumed=output_tokens
            )

            # Calculate running total
            total_consumption = PromptUtils.calculate_total_tokens_consumption(
                consumption=current_consumption,
                previously_consumed=total_consumption
            )

        return total_consumption


    @staticmethod
    def convert_to_pg_consumption_data(total_consumption: TotalTokensConsumption) -> List[ConsumptionData]:
        return [
            ConsumptionData(
                input_tokens=consumption.input_tokens,
                output_tokens=consumption.output_tokens,
                model=consumption.model.value
            )
            for consumption in total_consumption.consumptions
        ]