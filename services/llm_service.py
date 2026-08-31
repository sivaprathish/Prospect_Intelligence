"""Gemini service for structured prospect analysis."""

from __future__ import annotations

import json
import os
from typing import Any

from google import genai
from google.genai import errors, types


class GeminiService:
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        key = api_key or os.getenv("GEMINI_API_KEY")
        if not key:
            raise ValueError("GEMINI_API_KEY is missing")
        self.model = (model or os.getenv("GEMINI_MODEL") or "gemini-2.5-flash").removeprefix("models/")
        self.client = genai.Client(api_key=key)

    def generate_json(
        self,
        prompt: str,
        response_schema: dict[str, Any] | None = None,
        temperature: float = 0.1,
    ) -> Any:
        config: dict[str, Any] = {
            "temperature": temperature,
            "response_mime_type": "application/json",
        }
        if response_schema:
            config["response_json_schema"] = response_schema
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(**config),
            )
        except errors.ClientError as error:
            if "404" in str(error) or "not found" in str(error).lower():
                raise RuntimeError(
                    f"Gemini model '{self.model}' is unavailable. Set GEMINI_MODEL=gemini-2.5-flash"
                ) from error
            raise RuntimeError(f"Gemini request failed: {error}") from error

        if not response.text:
            raise RuntimeError("Gemini returned an empty response")
        try:
            return json.loads(response.text)
        except json.JSONDecodeError as error:
            raise RuntimeError("Gemini returned invalid JSON") from error
