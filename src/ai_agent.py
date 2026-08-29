import os

from langchain_openai import ChatOpenAI
from pydantic import BaseModel


class FieldContext(BaseModel):
    crop_type: str
    temperature_c: float
    heat_index_c: float
    farmer_question: str


class AgriAdvisorAgent:
    """LangChain/OpenAI powered advisor with safe local fallback."""

    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.2) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = model
        self.temperature = temperature
        self._llm = None

        if self.api_key:
            self._llm = ChatOpenAI(model=self.model, temperature=self.temperature)

    def _fallback(self, context: FieldContext) -> str:
        if context.heat_index_c >= 40:
            window = "early morning (05:00-07:00) and late evening (18:30-20:00)"
            action = "apply mulching immediately and prioritize shaded irrigation cycles"
        elif context.heat_index_c >= 32:
            window = "morning (06:00-08:00)"
            action = "split irrigation into 2 lighter cycles and monitor leaf rolling"
        else:
            window = "morning (06:00-08:30)"
            action = "keep a normal irrigation cadence with moisture checks"

        return (
            f"For {context.crop_type} at {context.temperature_c:.1f}°C and heat index "
            f"{context.heat_index_c:.1f}°C: {action}. Recommended watering window: {window}. "
            f"Farmer question noted: '{context.farmer_question}'."
        )

    def get_recommendation(
        self,
        crop_type: str,
        temperature_c: float,
        heat_index_c: float,
        farmer_question: str,
    ) -> str:
        context = FieldContext(
            crop_type=crop_type,
            temperature_c=temperature_c,
            heat_index_c=heat_index_c,
            farmer_question=farmer_question,
        )

        if not self._llm:
            return self._fallback(context)

        prompt = (
            "You are AgriCool, a precision-farming advisor for heat stress. "
            "Provide practical, concise guidance for irrigation scheduling, "
            "crop heat protection, and field actions.\n\n"
            f"Crop: {context.crop_type}\n"
            f"Temperature (C): {context.temperature_c}\n"
            f"Heat Index (C): {context.heat_index_c}\n"
            f"Farmer Question: {context.farmer_question}\n"
            "Answer in clear bullet points with one suggested watering schedule."
        )

        try:
            result = self._llm.invoke(prompt)
            return result.content
        except Exception:
            return self._fallback(context)
