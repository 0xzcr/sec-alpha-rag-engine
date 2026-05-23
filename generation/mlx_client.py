from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from config import DEFAULT_MODEL_REPO, MODEL_REPO_ENV, MAX_TOKENS, TEMPERATURE, TOP_P


@dataclass
class MlxGenerationConfig:
    model_repo: str
    max_tokens: int = MAX_TOKENS
    temperature: float = TEMPERATURE
    top_p: float = TOP_P


class MlxTextGenerator:
    def __init__(self, config: MlxGenerationConfig | None = None) -> None:
        model_repo = os.getenv(MODEL_REPO_ENV, DEFAULT_MODEL_REPO)
        self.config = config or MlxGenerationConfig(model_repo=model_repo)
        self._model: Any | None = None
        self._tokenizer: Any | None = None

    def load(self) -> None:
        if self._model is not None and self._tokenizer is not None:
            return

        try:
            from mlx_lm import load
        except Exception as error:  # noqa: BLE001
            raise RuntimeError(
                "mlx-lm could not be imported. Install mlx-lm and run this on Apple Silicon with Metal support."
            ) from error

        self._model, self._tokenizer = load(self.config.model_repo)

    def generate(self, messages: list[dict[str, str]]) -> str:
        self.load()
        assert self._model is not None
        assert self._tokenizer is not None

        prompt = self._tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

        try:
            from mlx_lm import generate
            from mlx_lm.sample_utils import make_sampler
        except Exception as error:  # noqa: BLE001
            raise RuntimeError("mlx-lm generation helpers are unavailable.") from error

        sampler = make_sampler(
            temp=self.config.temperature,
            top_p=self.config.top_p,
        )

        return generate(
            self._model,
            self._tokenizer,
            prompt=prompt,
            max_tokens=self.config.max_tokens,
            sampler=sampler,
            verbose=False,
        )
